import os
import tempfile
import unittest
from unittest import TestCase
from unittest.mock import Mock, patch

import torch
from torch.distributed.checkpoint.planner import WriteItemType

from amzn_sagemaker_checkpointing.checkpointing.filesystem.filesystem import (
    SageMakerTieredStorageReader,
    SageMakerTieredStorageWriter,
    _get_step_val,
)
from amzn_sagemaker_checkpointing.config.sagemaker_checkpoint_config import (
    SageMakerCheckpointConfig,
)
from amzn_sagemaker_checkpointing.checkpointing.filesystem.exceptions import (
    SageMakerTieredStorageError,
    SageMakerTieredStorageConfigError,
)


# Global AWS mocking decorator
def mock_aws_calls(test_func):
    """Decorator to mock AWS calls for all test methods."""

    @patch("boto3.client")
    def wrapper(*args, **kwargs):
        # Get the mock_boto3_client from the arguments
        mock_boto3_client = args[-1]  # Last argument is the mock

        # Set up AWS client mocks
        mock_sts_client = Mock()
        mock_sts_client.get_caller_identity.return_value = {"Account": "123456789012"}

        mock_s3_client = Mock()
        mock_s3_client.get_bucket_location.return_value = {
            "LocationConstraint": "us-west-2"
        }

        def mock_client_factory(service_name, **kwargs):
            if service_name == "sts":
                return mock_sts_client
            elif service_name == "s3":
                return mock_s3_client
            return Mock()

        mock_boto3_client.side_effect = mock_client_factory

        # Call the original test function
        return test_func(*args[:-1], **kwargs)  # Remove the mock from args

    return wrapper


class TestStepValueExtractionAdditional(TestCase):
    def test_step_extraction_edge_cases(self):
        """Test edge cases for step extraction."""
        # Test with explicit step values (should always return the explicit value)
        test_cases = [
            (0, "/any/path/step_999", 0),
            (42, "/path/step_123/file", 42),
            (999999, "/step_0/checkpoint", 999999),
        ]

        for explicit_step, path, expected in test_cases:
            with self.subTest(explicit_step=explicit_step, path=path):
                result = _get_step_val(explicit_step, path)
                self.assertEqual(result, expected)

    def test_step_extraction_from_complex_paths(self):
        """Test step extraction from complex path structures."""
        complex_paths = [
            ("/root/training/experiment_1/step_42/model.pt", 42),
            ("/very/long/nested/path/with/many/dirs/step_12345/checkpoint.bin", 12345),
            (
                "/path/with/step_100/nested/step_200/file.txt",
                100,
            ),  # Should get first occurrence
            ("./relative/path/step_5/data", 5),
            ("/step_0/beginning", 0),
            ("/end/step_999999", 999999),
        ]

        for path, expected_step in complex_paths:
            with self.subTest(path=path):
                result = _get_step_val(-1, path)
                self.assertEqual(result, expected_step)

    def test_step_extraction_invalid_formats(self):
        """Test step extraction with invalid path formats."""
        invalid_paths = [
            "/no/step/pattern/here",
            "/path/step_/incomplete",
            "/path/step_abc/invalid_number",
            "",
            None,
        ]

        for invalid_path in invalid_paths:
            with self.subTest(path=invalid_path):
                with self.assertRaises(SageMakerTieredStorageError):
                    _get_step_val(-1, invalid_path)

        # Test cases that might not raise ValueError but should be handled
        edge_cases = [
            "/path/step_-5/negative",  # Negative numbers might be parsed as valid
            "/path/step_12.5/float",  # Float might be parsed as int
        ]

        for edge_case in edge_cases:
            with self.subTest(path=edge_case):
                try:
                    result = _get_step_val(-1, edge_case)
                    # If it doesn't raise an error, verify the result is reasonable
                    self.assertIsInstance(result, int)
                except SageMakerTieredStorageError:
                    # It's also acceptable if it raises ValueError
                    pass


class TestConfigurationValidationAdditional(TestCase):
    def test_valid_configuration_variations(self):
        """Test various valid configuration combinations."""
        valid_configs = [
            # Minimal valid config
            {
                "namespace": "test",
                "world_size": 1,
            },
            # Config with all optional parameters
            {
                "namespace": "full-test",
                "world_size": 8,
                "disk_tier_base_path": "/tmp/checkpoints",
                "s3_tier_base_path": "s3://my-bucket/checkpoints",
                "save_to_s3": True,
                "save_to_disk": True,
            },
            # Config with special characters in namespace
            {
                "namespace": "test-with-dashes_and_underscores",
                "world_size": 4,
            },
            # Config with large world size
            {
                "namespace": "large-scale",
                "world_size": 1000,
            },
        ]

        for config_dict in valid_configs:
            with self.subTest(config=config_dict):
                config = SageMakerCheckpointConfig(**config_dict)
                self.assertEqual(config.namespace, config_dict["namespace"])
                self.assertEqual(config.world_size, config_dict["world_size"])

    @mock_aws_calls
    def test_invalid_configuration_variations(self):
        """Test various invalid configuration combinations."""
        invalid_configs = [
            # Empty namespace
            {"namespace": "", "world_size": 1},
            # None namespace
            {"namespace": None, "world_size": 1},
            # Zero world size
            {"namespace": "test", "world_size": 0},
            # Negative world size
            {"namespace": "test", "world_size": -1},
            # Very large negative world size
            {"namespace": "test", "world_size": -999999},
            # pass save_to_s3 flag without s3_tier_base_path
            {"namespace": "test", "world_size": 1, "save_to_s3": True},
            # pass save_to_s3 flag with  empty s3_tier_base_path
            {
                "namespace": "test",
                "world_size": 1,
                "save_to_s3": True,
                "s3_tier_base_path": "",
            },
        ]

        for config_dict in invalid_configs:
            with self.subTest(config=config_dict):
                with self.assertRaises(SageMakerTieredStorageConfigError):
                    config = SageMakerCheckpointConfig(**config_dict)
                    # Try to create a writer to trigger validation
                    SageMakerTieredStorageWriter(config, path="step_1", step=-1)


class TestWriterInitializationAdditional(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.valid_config = SageMakerCheckpointConfig(
            namespace="test-init",
            world_size=2,
            disk_tier_base_path=self.temp_dir,
            s3_tier_base_path="s3://test-bucket/checkpoints",
            save_to_s3=True,
            save_to_disk=False,
        )

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    @patch("boto3.client")
    @patch("torch.distributed.get_rank", return_value=0)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.is_available", return_value=True)
    @mock_aws_calls
    @patch("torch.distributed.get_rank", return_value=0)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.is_available", return_value=True)
    def test_writer_initialization_with_various_steps(self, *_):
        """Test writer initialization with various step values."""
        step_test_cases = [
            # (path, explicit_step, expected_step)
            ("step_0", -1, 0),
            ("step_1", -1, 1),
            ("step_100", -1, 100),
            ("step_999999", -1, 999999),
            ("/path/to/step_42/checkpoint", -1, 42),
            ("any_path", 0, 0),
            ("any_path", 123, 123),
            ("step_999", 42, 42),  # Explicit step overrides path
        ]

        for path, explicit_step, expected_step in step_test_cases:
            with self.subTest(path=path, explicit_step=explicit_step):
                writer = SageMakerTieredStorageWriter(
                    self.valid_config, path=path, step=explicit_step
                )
                self.assertEqual(writer.step, expected_step)
                self.assertEqual(writer.rank, 0)

    @mock_aws_calls
    @patch("torch.distributed.get_rank", return_value=3)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.is_available", return_value=True)
    def test_writer_initialization_different_ranks(self, *_):
        """Test writer initialization with different ranks."""
        writer = SageMakerTieredStorageWriter(
            self.valid_config, path="step_10", step=-1
        )
        self.assertEqual(writer.rank, 3)
        self.assertEqual(writer.step, 10)

    @mock_aws_calls
    @patch("torch.distributed.get_rank", return_value=0)
    @patch("torch.distributed.is_initialized", return_value=False)
    @patch("torch.distributed.is_available", return_value=True)
    def test_writer_initialization_distributed_not_initialized(self, *_):
        """Test writer initialization when distributed is not initialized."""
        writer = SageMakerTieredStorageWriter(self.valid_config, path="step_5", step=-1)
        self.assertEqual(writer.rank, 0)  # Should default to 0
        self.assertEqual(writer.step, 5)

    @mock_aws_calls
    @patch("torch.distributed.get_rank", return_value=0)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.is_available", return_value=False)
    def test_writer_initialization_distributed_not_available(self, *_):
        """Test writer initialization when distributed is not available."""
        writer = SageMakerTieredStorageWriter(self.valid_config, path="step_7", step=-1)
        self.assertEqual(writer.rank, 0)  # Should default to 0
        self.assertEqual(writer.step, 7)


class TestReaderInitializationAdditional(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.valid_config = SageMakerCheckpointConfig(
            namespace="test-reader-init",
            world_size=4,
            disk_tier_base_path=self.temp_dir,
            s3_tier_base_path="s3://test-bucket/checkpoints",
            save_to_disk=False,
            save_to_s3=False,
        )

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    @mock_aws_calls
    @patch("torch.distributed.get_rank", return_value=0)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.is_available", return_value=True)
    def test_reader_initialization_with_various_steps(self, *_):
        """Test reader initialization with various step values."""
        step_values = [0, 1, 10, 100, 999999, None]

        for step in step_values:
            with self.subTest(step=step):
                reader = SageMakerTieredStorageReader(self.valid_config, step=step)
                self.assertEqual(reader.step, step)
                self.assertEqual(reader.rank, 0)

    @mock_aws_calls
    @patch("torch.distributed.get_rank", return_value=2)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.is_available", return_value=True)
    def test_reader_initialization_different_ranks(self, *_):
        """Test reader initialization with different ranks."""
        reader = SageMakerTieredStorageReader(self.valid_config, step=50)
        self.assertEqual(reader.rank, 2)
        self.assertEqual(reader.step, 50)


class TestErrorScenarios(TestCase):
    def test_invalid_path_scenarios(self):
        """Test writer creation with invalid paths."""
        config = SageMakerCheckpointConfig(namespace="test-errors", world_size=1)

        invalid_paths = [
            "/no/step/in/path",
            "/path/step_/incomplete",
            "/path/step_abc/invalid",
            "",
        ]

        for invalid_path in invalid_paths:
            with self.subTest(path=invalid_path):
                with self.assertRaises(SageMakerTieredStorageError):
                    SageMakerTieredStorageWriter(config, path=invalid_path, step=-1)


class TestConfigurationProperties(TestCase):
    def test_configuration_property_defaults(self):
        """Test that configuration properties have correct defaults."""
        config = SageMakerCheckpointConfig(namespace="test-defaults", world_size=2)

        # Test that required properties are set
        self.assertEqual(config.namespace, "test-defaults")
        self.assertEqual(config.world_size, 2)

        # Test that optional properties have reasonable defaults or None
        # (The actual defaults depend on the implementation)
        self.assertIsNotNone(config.save_to_disk)
        self.assertIsNotNone(config.save_to_s3)

    def test_configuration_property_assignment(self):
        """Test that configuration properties are correctly assigned."""
        config = SageMakerCheckpointConfig(
            namespace="test-assignment",
            world_size=8,
            disk_tier_base_path="/custom/local/path",
            s3_tier_base_path="s3://custom-bucket/path",
            save_to_disk=True,
            save_to_s3=True,
        )

        self.assertEqual(config.namespace, "test-assignment")
        self.assertEqual(config.world_size, 8)
        self.assertEqual(config.disk_tier_base_path, "/custom/local/path")
        self.assertEqual(config.s3_tier_base_path, "s3://custom-bucket/path")
        self.assertEqual(config.save_to_disk, True)
        self.assertEqual(config.save_to_s3, True)


class TestSageMakerTieredStorageWriter(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.namespace = "test-namespace"
        self.world_size = 4
        self.config = SageMakerCheckpointConfig(
            namespace=self.namespace,
            world_size=self.world_size,
            disk_tier_base_path=self.temp_dir,
            s3_tier_base_path="s3://test-bucket/checkpoints",
            save_to_disk=True,
            save_to_s3=True,
        )

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    @mock_aws_calls
    @patch("torch.distributed.is_available", return_value=True)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.get_rank", return_value=0)
    def test_init_with_valid_config(self, *_):
        writer = SageMakerTieredStorageWriter(
            checkpoint_config=self.config, path="/some/path", step=42
        )
        self.assertEqual(writer.step, 42)
        self.assertEqual(writer.rank, 0)

        writer = SageMakerTieredStorageWriter(
            checkpoint_config=self.config, path="/some/path/step_123/checkpoint"
        )
        self.assertEqual(writer.step, 123)
        self.assertEqual(writer.rank, 0)

    @mock_aws_calls
    def test_init_with_invalid_config(self):
        invalid_config = SageMakerCheckpointConfig(
            namespace="", world_size=self.world_size
        )
        with self.assertRaises(SageMakerTieredStorageError):
            SageMakerTieredStorageWriter(checkpoint_config=invalid_config)

        invalid_config = SageMakerCheckpointConfig(
            namespace=self.namespace, world_size=0
        )
        with self.assertRaises(SageMakerTieredStorageError):
            SageMakerTieredStorageWriter(checkpoint_config=invalid_config)

    @mock_aws_calls
    def test_invalid_step(self):
        with self.assertRaises(SageMakerTieredStorageError):
            SageMakerTieredStorageWriter(
                checkpoint_config=self.config, path="/no/step/path"
            )


class TestStepValueExtraction(TestCase):
    def test_explicit_step_value(self):
        self.assertEqual(_get_step_val(42, "/some/path"), 42)
        self.assertEqual(_get_step_val(0, "/some/path"), 0)
        self.assertEqual(_get_step_val(999999, "/some/path"), 999999)
        self.assertEqual(_get_step_val(42, "/some/path/step_100/checkpoint"), 42)

    def test_step_from_path(self):
        self.assertEqual(_get_step_val(-1, "/some/path/step_123/checkpoint"), 123)
        self.assertEqual(_get_step_val(-1, "/some/path/step_456"), 456)
        self.assertEqual(_get_step_val(-1, "/some/path/step_0/checkpoint"), 0)
        self.assertEqual(_get_step_val(-1, "/some/path/step_999999/checkpoint"), 999999)
        self.assertEqual(
            _get_step_val(-1, os.path.join("/some/path", "step_789", "checkpoint")), 789
        )

    def test_invalid_step_scenarios(self):
        with self.assertRaises(SageMakerTieredStorageError):
            _get_step_val(-1, "/some/path/without/step")
        with self.assertRaises(SageMakerTieredStorageError):
            _get_step_val(-1, "")
        with self.assertRaises(SageMakerTieredStorageError):
            _get_step_val(-1, None)
        with self.assertRaises(SageMakerTieredStorageError):
            _get_step_val(-1, "/some/path/step_abc/checkpoint")
        with self.assertRaises(SageMakerTieredStorageError):
            _get_step_val(-1, "/some/path/step_/checkpoint")

    def test_edge_cases(self):
        self.assertEqual(_get_step_val(-1, "/path/step_100/nested/step_200"), 100)
        self.assertEqual(_get_step_val(-1, "/path/step_100123/checkpoint"), 100123)
        self.assertEqual(
            _get_step_val(-1, "/root/parent/child/grandchild/step_42/file.txt"), 42
        )


class TestSageMakerTieredStorageReader(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.namespace = "test-namespace"
        self.world_size = 4
        self.config = SageMakerCheckpointConfig(
            namespace=self.namespace,
            world_size=self.world_size,
            disk_tier_base_path=self.temp_dir,
            s3_tier_base_path="s3://test-bucket/checkpoints",
            save_to_disk=True,
            save_to_s3=True,
        )

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    @mock_aws_calls
    def test_init_with_invalid_config(self):
        invalid_config = SageMakerCheckpointConfig(
            namespace="", world_size=self.world_size
        )
        with self.assertRaises(SageMakerTieredStorageConfigError):
            SageMakerTieredStorageReader(checkpoint_config=invalid_config)

        invalid_config = SageMakerCheckpointConfig(
            namespace=self.namespace, world_size=0
        )
        with self.assertRaises(SageMakerTieredStorageError):
            SageMakerTieredStorageReader(checkpoint_config=invalid_config)


class DummyItem:
    def __init__(self, index):
        self.type = WriteItemType.TENSOR
        self.index = index


class DummyPlanner:
    def resolve_data(self, item):
        return torch.tensor([1, 2, 3])


class DummySavePlan:
    def __init__(self):
        self.items = [DummyItem(0)]


class ErrorThrowingClient:
    def put_checkpoint(self, *args, **kwargs):
        raise RuntimeError("Simulated failure")


class TestErrorHandlingInCheckpointing(unittest.TestCase):
    def setUp(self):
        self.config = SageMakerCheckpointConfig(
            namespace="test-ns",
            world_size=2,
            disk_tier_base_path="/tmp",
            s3_tier_base_path="s3://dummy",
            save_to_disk=True,
            save_to_s3=True,
        )

    @mock_aws_calls
    @patch("torch.distributed.get_rank", return_value=0)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.is_available", return_value=True)
    def test_write_data_failure(self, *_):
        writer = SageMakerTieredStorageWriter(self.config, path="step_50", step=-1)
        writer.client = ErrorThrowingClient()

        # Mock S3 client to also fail
        writer.s3_client = Mock()
        writer.s3_client.create_write_stream = Mock(
            side_effect=RuntimeError("S3 write failed")
        )

        plan = DummySavePlan()
        planner = DummyPlanner()

        # The enhanced write_data method should raise an exception when both in-memory and S3 fail
        future = writer.write_data(plan, planner)
        with self.assertRaises(Exception) as context:
            future.wait()

        # The error message should indicate S3 checkpoint save failure
        self.assertIn("Failed to write checkpoint to S3", str(context.exception))


if __name__ == "__main__":
    unittest.main()


class TestFindLatestCompleteStep(TestCase):
    def setUp(self):
        self.config = SageMakerCheckpointConfig(
            namespace="test-namespace",
            world_size=2,
            s3_tier_base_path="s3://test-bucket/checkpoints",
            save_to_s3=True,
        )

    @mock_aws_calls
    @patch("torch.distributed.is_available", return_value=True)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.get_rank", return_value=0)
    def test_find_latest_complete_step_with_prefix(self, *_):
        """Test finding latest complete step with S3 prefix"""
        reader = SageMakerTieredStorageReader(self.config)
        reader.region = "us-west-2"

        # Mock S3 client and paginator
        mock_s3_client = Mock()
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator

        # Mock S3 response with step directories for both ranks
        mock_pages = [
            {
                "CommonPrefixes": [
                    {"Prefix": "checkpoints/test-namespace/rank_0/step_100/"},
                    {"Prefix": "checkpoints/test-namespace/rank_0/step_200/"},
                    {"Prefix": "checkpoints/test-namespace/rank_0/step_300/"},
                ]
            }
        ]
        mock_paginator.paginate.return_value = mock_pages

        with patch("boto3.client", return_value=mock_s3_client):
            result = reader._find_latest_complete_step()

        self.assertEqual(result, 300)

    @mock_aws_calls
    @patch("torch.distributed.is_available", return_value=True)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.get_rank", return_value=0)
    def test_find_latest_complete_step_bucket_only(self, *_):
        """Test finding latest complete step with bucket-only S3 path"""
        config = SageMakerCheckpointConfig(
            namespace="test-namespace",
            world_size=2,
            s3_tier_base_path="s3://test-bucket",
            save_to_s3=True,
        )
        reader = SageMakerTieredStorageReader(config)
        reader.region = "us-west-2"

        # Mock S3 client and paginator
        mock_s3_client = Mock()
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator

        # Mock S3 response for bucket-only path
        mock_pages = [
            {
                "CommonPrefixes": [
                    {"Prefix": "test-namespace/rank_0/step_50/"},
                    {"Prefix": "test-namespace/rank_0/step_100/"},
                ]
            }
        ]
        mock_paginator.paginate.return_value = mock_pages

        with patch("boto3.client", return_value=mock_s3_client):
            result = reader._find_latest_complete_step()

        self.assertEqual(result, 100)

    @mock_aws_calls
    @patch("torch.distributed.is_available", return_value=True)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.get_rank", return_value=0)
    def test_find_latest_complete_step_no_region(self, *_):
        """Test that method returns None when region is empty"""
        reader = SageMakerTieredStorageReader(self.config)
        reader.region = ""

        result = reader._find_latest_complete_step()
        self.assertIsNone(result)

    @mock_aws_calls
    @patch("torch.distributed.is_available", return_value=True)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.get_rank", return_value=0)
    def test_find_latest_complete_step_invalid_s3_path(self, *_):
        """Test that method returns None for invalid S3 path"""
        reader = SageMakerTieredStorageReader(self.config)
        reader.region = "us-west-2"

        # Directly modify the s3_tier_base_path to test invalid path handling
        reader.checkpoint_config.s3_tier_base_path = "invalid://not-s3"

        result = reader._find_latest_complete_step()
        self.assertIsNone(result)

    @mock_aws_calls
    @patch("torch.distributed.is_available", return_value=True)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.get_rank", return_value=0)
    def test_find_latest_complete_step_incomplete_ranks(self, *_):
        """Test finding steps when not all ranks have same steps"""
        reader = SageMakerTieredStorageReader(self.config)
        reader.region = "us-west-2"

        # Mock S3 client and paginator
        mock_s3_client = Mock()
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator

        # Mock different responses for different ranks
        def mock_paginate(Bucket, Prefix, Delimiter):
            if "rank_0" in Prefix:
                return [
                    {
                        "CommonPrefixes": [
                            {"Prefix": "checkpoints/test-namespace/rank_0/step_100/"},
                            {"Prefix": "checkpoints/test-namespace/rank_0/step_200/"},
                        ]
                    }
                ]
            elif "rank_1" in Prefix:
                return [
                    {
                        "CommonPrefixes": [
                            {"Prefix": "checkpoints/test-namespace/rank_1/step_100/"}
                        ]
                    }
                ]
            return [{}]

        mock_paginator.paginate.side_effect = mock_paginate

        with patch("boto3.client", return_value=mock_s3_client):
            result = reader._find_latest_complete_step()

        # Should return 100 as it's complete across all ranks
        self.assertEqual(result, 100)

    @mock_aws_calls
    @patch("torch.distributed.is_available", return_value=True)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.get_rank", return_value=0)
    def test_find_latest_complete_step_no_steps(self, *_):
        """Test when no steps are found"""
        reader = SageMakerTieredStorageReader(self.config)
        reader.region = "us-west-2"

        # Mock S3 client with empty response
        mock_s3_client = Mock()
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [{"CommonPrefixes": []}]

        with patch("boto3.client", return_value=mock_s3_client):
            result = reader._find_latest_complete_step()

        self.assertIsNone(result)

    @mock_aws_calls
    @patch("torch.distributed.is_available", return_value=True)
    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.distributed.get_rank", return_value=0)
    def test_find_latest_complete_step_s3_exception(self, *_):
        """Test handling of S3 exceptions"""
        reader = SageMakerTieredStorageReader(self.config)
        reader.region = "us-west-2"

        # Mock S3 client to raise exception
        with patch("boto3.client", side_effect=Exception("S3 error")):
            result = reader._find_latest_complete_step()

        self.assertIsNone(result)
