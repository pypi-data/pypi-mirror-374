# Copyright 2025 Amazon.com, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import logging
import os
import pickle
import threading
import time
from dataclasses import dataclass
from logging import FileHandler
from typing import Any, Union

import boto3  # type: ignore[import-untyped]
import torch
import torch.distributed as dist
from torch.distributed._shard._utils import narrow_tensor_by_index
from torch.distributed.checkpoint.metadata import Metadata, StorageMeta
from torch.distributed.checkpoint.planner import (
    LoadItemType,
    LoadPlan,
    LoadPlanner,
    ReadItem,
    SavePlan,
    SavePlanner,
    WriteItemType,
)
from torch.distributed.checkpoint.storage import (
    StorageReader,
    StorageWriter,
    WriteResult,
)
from torch.futures import Future

from amzn_sagemaker_checkpointing.config.sagemaker_checkpoint_config import (
    SageMakerCheckpointConfig,
)
from amzn_sagemaker_checkpointing.storage.clients.inmemory.exceptions import (
    InMemoryServerError,
)
from amzn_sagemaker_checkpointing.storage.clients.inmemory.inmemory_client import (
    InMemoryCheckpointClient,
)
from amzn_sagemaker_checkpointing.storage.clients.s3.s3_client import (
    s3_retry_with_jitter,
)
from amzn_sagemaker_checkpointing.storage.clients.s3.s3_client_manager import (
    S3ClientManager,
)
from amzn_sagemaker_checkpointing.utils.logging_utils import (
    CheckpointFilter,
    SageMakerCheckpointingLoggerAdapter,
)
from amzn_sagemaker_checkpointing.checkpointing.filesystem.exceptions import (
    SageMakerInMemoryTierError,
    SageMakerS3TierError,
    SageMakerTieredStorageConfigError,
    SageMakerTieredStorageError,
)

__all__ = ["SageMakerTieredStorageWriter", "SageMakerTieredStorageReader"]

METADATA_INDEX = 0


@dataclass
class _SageMakerStorageInfo:
    rank: int
    offset: int
    length: int


def _get_step_val(step: int, path: str | os.PathLike) -> int:
    """
    Extract or validate the checkpoint step number.

    Parameters
    ----------
    step : int
        The step number explicitly provided.
    path : str or os.PathLike
        The checkpoint path potentially containing the step number.

    Returns
    -------
    int
        The resolved step number.

    Raises
    ------
    SageMakerTieredStorageError
        If a valid step value cannot be determined from the provided arguments.
    """
    if step != -1:
        return step
    elif path and "step_" in str(path):
        try:
            return int(str(path).split("step_")[1].split("/")[0])
        except (IndexError, ValueError):
            pass
    raise SageMakerTieredStorageError(f"Invalid step value, step:{step}. path:{path}")


def _is_valid_s3_path(s3_path: str) -> bool:
    return s3_path is not None and s3_path.startswith("s3://")


def _get_checkpoint_config(
    checkpoint_config: SageMakerCheckpointConfig,
) -> SageMakerCheckpointConfig:
    if not checkpoint_config.namespace:
        raise SageMakerTieredStorageConfigError(
            "Namespace in SageMakerCheckpointConfig cannot be empty"
        )
    if checkpoint_config.world_size <= 0:
        raise SageMakerTieredStorageConfigError(
            f"Invalid world size:{checkpoint_config.world_size}, expecting a positive integer"
        )

    if checkpoint_config.save_to_s3 and not _is_valid_s3_path(
        checkpoint_config.s3_tier_base_path
    ):
        raise SageMakerTieredStorageConfigError(
            "Invalid S3 tier base path, should start with s3://"
        )
    return checkpoint_config


def _get_bucket_location(
    s3_base_path,
    logger: Union[logging.Logger, "SageMakerCheckpointingLoggerAdapter"] | None,
) -> str:
    """
    Get S3 bucket location from an S3 base path.

    Args:
        s3_base_path (str): S3 path like 's3://bucket-name' or 's3://bucket-name/prefix/path'

    Returns:
        str: AWS region where the bucket is located
    """
    try:
        # Remove 's3://' prefix and split by '/'
        path_parts = s3_base_path[5:].split("/")
        bucket_name = path_parts[0]

        if not bucket_name:
            raise SageMakerS3TierError("Invalid S3 path: bucket name is empty")

        # Create S3 client
        s3_client = boto3.client("s3")
        # Get bucket location
        response = s3_client.get_bucket_location(Bucket=bucket_name)

        location = response["LocationConstraint"]
        if location is None:
            location = "us-east-1"
        s3_client.close()
        return location
    except Exception as e:
        error_msg = f"Unable to fetch region for the bucket {s3_base_path}"
        logger.error(f"{error_msg}: {e}")  # type: ignore
        raise SageMakerS3TierError(error_msg) from e

def _setup_checkpointing_logger(
    logger_name: str, namespace: str, provided_logger: logging.Logger | None = None
) -> logging.Logger | SageMakerCheckpointingLoggerAdapter:
    """
    Set up logger with namespace-specific host path and checkpointing filtering.

    Returns CheckpointAdapter to ensure logs have the filtering attribute.
    """
    base_log_dir: str = "/var/log/sagemaker_checkpointing"
    host_log_path = f"{base_log_dir}/{namespace}_checkpointing.log"
    # Use provided logger or create new one
    if provided_logger is not None:
        base_logger = provided_logger
    else:
        base_logger = logging.getLogger(logger_name)
        # Add console handler only if no existing handlers
        if not base_logger.handlers:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                f"[%(asctime)s] [{namespace}] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            base_logger.addHandler(console_handler)

    # Check if file handler already exists (avoid duplicates)
    has_checkpointing_handler = False
    for handler in base_logger.handlers:
        if (
            isinstance(handler, FileHandler)
            and hasattr(handler, "baseFilename")
            and handler.baseFilename == os.path.abspath(host_log_path)
        ):
            has_checkpointing_handler = True
            break

    if not has_checkpointing_handler:
        try:
            # Create directory
            log_dir = os.path.dirname(host_log_path)
            os.makedirs(log_dir, exist_ok=True)
            # Create file handler
            file_handler = FileHandler(host_log_path, mode="a", encoding="utf-8")
            # Add our checkpoint filter
            file_handler.addFilter(CheckpointFilter())
            # Set formatter
            formatter = logging.Formatter(
                f"[%(asctime)s] [{namespace}] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
            )
            file_handler.setFormatter(formatter)
            # Add to logger
            base_logger.addHandler(file_handler)
            # Use adapter to log success message (will have attribute and go to file)
            adapter = SageMakerCheckpointingLoggerAdapter(base_logger, {})
            adapter.info(
                f"SageMaker checkpointing file logging enabled: {host_log_path}"
            )
        except Exception as e:
            base_logger.warning(f"Failed to setup checkpointing file logging: {e}")

    # Return adapter to ensure all logs have the filtering attribute
    return SageMakerCheckpointingLoggerAdapter(base_logger, {})


class SageMakerTieredStorageWriter(StorageWriter):
    """
    Storage writer implementation for SageMaker's tiered in-memory checkpoint storage.

    Manages writing checkpoint data and metadata using an in-memory distributed storage backend.
    """

    def __init__(
        self,
        checkpoint_config: SageMakerCheckpointConfig,
        path: str | os.PathLike = "",
        step: int = -1,
        *args: Any,
        **kwargs: Any,
    ):
        """
        Initialize the storage writer.

        Parameters
        ----------
        checkpoint_config : SageMakerCheckpointConfig
            Configuration object containing checkpoint storage parameters.
        path : str or os.PathLike, optional
            Path indicating the checkpoint location, by default "".
        step : int, optional
            Training step associated with the checkpoint, by default -1.

        Raises
        ------
        SageMakerTieredStorageConfigError
            Errors related to checkpoint configuration
        SageMakerS3TierError
            Erorr in initializing S3 client
        """
        super().__init__()
        self.step = _get_step_val(step, path)
        self.rank = (
            dist.get_rank() if dist.is_available() and dist.is_initialized() else 0
        )
        self.checkpoint_config = _get_checkpoint_config(checkpoint_config)
        logger_name = f"sagemaker.checkpointing.writer.rank_{self.rank}"
        self.logger = _setup_checkpointing_logger(
            logger_name=logger_name,
            namespace=self.checkpoint_config.namespace,
            provided_logger=checkpoint_config.logger,
        )
        # Only setup S3 clients if S3 is configured
        self.s3_base_path = self.checkpoint_config.s3_tier_base_path
        if self.checkpoint_config.save_to_s3:
            self.region = _get_bucket_location(
                s3_base_path=self.s3_base_path, logger=self.logger
            )
            try:
                self._s3_client_manager = S3ClientManager(logger=self.logger)
                self.s3_client = self._s3_client_manager.get_client(
                    region=self.region, rank=self.rank
                )
            except Exception as e:
                error_msg = (
                    f"[Rank {self.rank}] Step {self.step}: S3 client creation failed"
                )
                self.logger.error(f"{error_msg}:{e}")
                raise SageMakerS3TierError(error_msg) from e
            stats = self._s3_client_manager.get_client_stats()
            self.logger.info(f"S3 client stats: {stats}")
        else:
            self.region = ""

        try:
            self.client = InMemoryCheckpointClient(
                namespace=self.checkpoint_config.namespace,
                rank=str(self.rank),
                world_size=str(self.checkpoint_config.world_size),
                metadata_file_count=1,
                logger=self.logger,
            )
        except Exception as e:
            self.logger.error(f"In-memory client creation failed: {e}")

        self.logger.debug(
            f"Initialized StorageWriter for rank {self.rank} at step {self.step}"
        )
        self.in_memory_success = True
        self.s3_success = False

    def reset(self, checkpoint_id: str | os.PathLike | None = None) -> None:
        """
        Reset the writer's internal state for a new checkpoint operation.

        Parameters
        ----------
        checkpoint_id : str or os.PathLike, optional
            Identifier for the new checkpoint operation.
        """

    def set_up_storage_writer(self, is_coordinator: bool) -> None:
        """
        Set up the storage writer and initialize namespace if the instance is coordinator.

        Parameters
        ----------
        is_coordinator : bool
            Indicates if the current instance coordinates the checkpoint.
        """
        self.logger.debug(
            f"[Rank {self.rank}] Step {self.step}: Setting up storage writer (is_coordinator={is_coordinator})"
        )
        self.is_coordinator = is_coordinator
        try:
            if is_coordinator:
                self.client.get_or_create_namespace()
        except Exception as e:
            self.logger.error(
                f"[Rank {self.rank}] Step {self.step}: In-memory client failed: {e}"
            )

    def prepare_local_plan(self, plan: SavePlan) -> SavePlan:
        """
        Process and return the local save plan without modifications.

        Parameters
        ----------
        plan : SavePlan
            Local save plan to execute.

        Returns
        -------
        SavePlan
            Unmodified local save plan.
        """
        return plan

    def prepare_global_plan(self, plans: list[SavePlan]) -> list[SavePlan]:
        """
        Process and return global save plans without modifications.

        Parameters
        ----------
        plans : List[SavePlan]
            Global save plans from all ranks.

        Returns
        -------
        List[SavePlan]
            Unmodified global save plans.
        """
        return plans

    def write_data(
        self, plan: SavePlan, planner: SavePlanner
    ) -> Future[list[WriteResult]]:

        @s3_retry_with_jitter(max_attempts=3, base_delay=2.0, max_delay=60.0)
        def _write_data_to_s3(buffer: io.BytesIO):
            try:
                s3_uri = f"{self.s3_base_path}/{self.checkpoint_config.namespace}/rank_{self.rank}/step_{self.step}/checkpoint.pt"
                self.logger.debug(
                    f"[Rank {self.rank}] Step {self.step}: Starting S3 upload"
                )

                with self.s3_client.create_write_stream(s3_uri=s3_uri) as writer:
                    # Write in 32MB chunks
                    chunk_size = 32 * 1024 * 1024
                    total_written = 0
                    chunk_count = 0

                    for i in range(0, len(buffer.getvalue()), chunk_size):
                        chunk = buffer.getvalue()[i : i + chunk_size]
                        bytes_written = writer.write(chunk)
                        total_written += bytes_written
                        chunk_count += 1

            except Exception as e:
                error_msg = f"Failed to write checkpoint to S3 for rank:{self.rank} and step:{self.step}"
                self.logger.error(f"{error_msg}:{e}")
                raise SageMakerS3TierError(error_msg) from e

        def _write_data(future: Future, plan: SavePlan, planner: SavePlanner):
            """
            Enhanced checkpoint data writing with tiered storage and complete consistency.

            Features:
            - Always attempts In-memory write first for all items
            - Writes to S3 at specified frequency regardless of In-memory status
            - Chunked S3 uploads for large data
            - Complete checkpoint consistency across storage tiers

            Parameters
            ----------
            plan : SavePlan
                Local save plan containing items to save.
            planner : SavePlanner
                Planner to resolve checkpoint data items.

            Returns
            -------
            List[WriteResult]]
                A list of WriteResult instances representing checkpoint storage metadata.
            """
            try:
                buffer = io.BytesIO()
                write_results: list[WriteResult] = []
                total_start = time.time()
                self.logger.info(
                    f"[Rank {self.rank}] Step {self.step}: Starting checkpoint write "
                    f"({len(plan.items)} items)"
                )

                for item in plan.items:
                    try:
                        offset = buffer.tell()
                        data = planner.resolve_data(item)

                        if item.type == WriteItemType.BYTE_IO:
                            if not isinstance(data, io.BytesIO):
                                raise TypeError(
                                    f"[Rank {self.rank}] Step {self.step}: Expected BytesIO for BYTE_IO item, got {type(data)}"
                                )
                            buffer.write(data.getbuffer())
                        else:
                            if not isinstance(data, torch.Tensor):
                                raise TypeError(f"Expected Tensor, got {type(data)}")
                            # Ensure tensor is on CPU and contiguous
                            data = data.detach().contiguous().cpu()
                            torch.save(data, buffer)

                        length = buffer.tell() - offset
                        write_results.append(
                            WriteResult(
                                index=item.index,
                                size_in_bytes=length,
                                storage_data=_SageMakerStorageInfo(
                                    rank=self.rank,
                                    offset=offset,
                                    length=length,
                                ),
                            )
                        )
                    except Exception as e:
                        error_msg = f"[Rank {self.rank}] Step {self.step}: Could not write item {item.index}"
                        self.logger.error(f"{error_msg}:{e}")
                        raise SageMakerTieredStorageError(error_msg) from e

                in_memory_write_time = time.time()
                in_memory_start = time.time()
                try:
                    self.client.put_checkpoint(
                        step=self.step, data=buffer.getvalue(), rank=self.rank
                    )
                    in_memory_write_time = time.time() - in_memory_start
                    self.logger.info(
                        f"[Rank {self.rank}] Step {self.step}: In-memory write completed "
                        f"in {in_memory_write_time:.3f}s ({len(buffer.getvalue()) / (1024*1024) / in_memory_write_time:.1f} MB/s)"
                    )
                except Exception as e:
                    self.in_memory_success = False
                    error_msg = (
                        f"[Rank {self.rank}] Step {self.step}: In-memory write failed"
                    )
                    self.logger.error(f"{error_msg}:{e}")
                    if self.checkpoint_config.save_to_s3:
                        self.logger.warning(
                            f"[Rank {self.rank}] Step {self.step}: Checkpoint might be saved "
                            f"to {self.s3_base_path} based on configuration"
                        )
                    else:
                        raise SageMakerInMemoryTierError(error_msg) from e

                # Execute S3 writes if needed
                if self.checkpoint_config.save_to_s3:
                    try:
                        self.logger.info(
                            f"[Rank {self.rank}] Step {self.step}: Scheduled S3 write - "
                            f"writing all {len(plan.items)} items to S3 "
                        )
                        s3_batch_start = time.time()
                        _write_data_to_s3(buffer=buffer)
                        self.s3_success = True
                        s3_batch_time = time.time() - s3_batch_start
                        s3_batch_speed = (
                            (buffer.tell() / (1024 * 1024)) / s3_batch_time
                            if buffer.tell() > 0
                            else 0
                        )
                        self.logger.info(
                            f"[Rank {self.rank}] Step {self.step}: S3 batch write completed "
                            f"in {s3_batch_time:.3f}s ({buffer.tell() / (1024*1024):.1f}MB total, "
                            f"{s3_batch_speed:.1f} MB/s average)"
                        )
                    except Exception as e:
                        error_msg = f"[Rank {self.rank}] Step {self.step}: S3 checkpoint save failed after in-memory failure: {e}"
                        self.logger.error(error_msg)
                        future.set_exception(e)
                        return future

                total_time = time.time() - total_start
                total_size_mb = sum(
                    result.size_in_bytes for result in write_results
                ) / (1024 * 1024)

                self.logger.info(
                    f"[Rank {self.rank}] Step {self.step}: Checkpoint write completed "
                    f"in {total_time:.3f}s ({total_size_mb:.1f}MB total, "
                    f"{total_size_mb / total_time:.1f} MB/s average)"
                )

                future.set_result(write_results)

            except Exception as e:
                error_msg = f"[Rank {self.rank}] Step {self.step}: Checkpoint write failed across tiers: {e}"
                self.logger.error(error_msg)
                future.set_exception(e)
                return future

        future: Future[list[WriteResult]] = Future()
        t = threading.Thread(target=_write_data, args=(future, plan, planner))
        t.start()
        return future

    def finish(self, metadata: Metadata, results: list[list[WriteResult]]) -> None:
        """
        Consolidate and serialize checkpoint metadata, then store it in the in-memory storage.

        Parameters
        ----------
        metadata : Metadata
            Metadata object containing detailed checkpoint information.
        results : List[List[WriteResult]]
            Nested list of WriteResults from checkpoint write operations across all ranks.
        """

        self.logger.info(
            f"[Rank {self.rank}] Step {self.step}: Finishing checkpoint write"
        )
        storage_md = {}
        for wr_list in results:
            for wr in wr_list:
                storage_md[wr.index] = wr.storage_data

        metadata.storage_data = storage_md
        metadata.storage_meta = self.storage_meta()
        metadata_buffer = pickle.dumps(metadata, protocol=pickle.HIGHEST_PROTOCOL)
        self.logger.info(
            f"[Rank {self.rank}] Step {self.step}:Created checkpoint metadata, "
            f"size:{len(metadata_buffer)} bytes"
        )
        try:
            self.client.put_checkpoint(
                step=self.step, data=metadata_buffer, metadata_index=METADATA_INDEX
            )
            self.logger.info(
                f"[Rank {self.rank}] Step {self.step}: Checkpoint metadata written successfully in-memory"
            )
        except Exception as e:
            error_msg = f"[Rank {self.rank}] Step {self.step}: Checkpoint metadata failed saving in-memory"
            self.logger.error(f"{error_msg}:{e}")
            if self.checkpoint_config.save_to_s3:
                self.logger.warning(
                    f"[Rank {self.rank}] Step {self.step}: Checkpoint metadata might be saved "
                    "to S3 based on configuration"
                )
            else:
                raise SageMakerInMemoryTierError(error_msg) from e

        if self.checkpoint_config.save_to_s3:
            try:
                s3_uri = f"{self.s3_base_path}/{self.checkpoint_config.namespace}/rank_{self.rank}/step_{self.step}/metadata.metadata"
                with self.s3_client.create_write_stream(s3_uri=s3_uri) as writer:
                    writer.write(metadata_buffer)
                self.logger.info(
                    f"[Rank {self.rank}] Step {self.step}: Checkpoint metadata written successfully to S3"
                )
            except Exception as e:
                error_msg = (
                    f"[Rank {self.rank}] Metadata checkpoint failed saving to S3"
                )
                self.logger.error(f"{error_msg}:{e}")
                raise SageMakerS3TierError(error_msg) from e

    @classmethod
    def validate_checkpoint_id(cls, checkpoint_id: str | os.PathLike) -> bool:
        """
        Validate checkpoint ID for storage compatibility. Currently always returns True.

        Parameters
        ----------
        checkpoint_id : str or os.PathLike
            Checkpoint identifier to validate.

        Returns
        -------
        bool
            Always True, indicating compatibility.
        """
        return True

    def storage_meta(self) -> StorageMeta | None:
        """
        Provide basic storage metadata associated with this checkpoint operation.

        Returns
        -------
        StorageMeta
            Basic storage metadata object.
        """
        return StorageMeta()


class SageMakerTieredStorageReader(StorageReader):
    """
    Storage reader implementation for SageMaker's tiered in-memory checkpoint storage.

    Manages reading checkpoint data and metadata using an in-memory distributed storage backend.
    """

    def __init__(
        self, checkpoint_config: SageMakerCheckpointConfig, step: int | None = None
    ):
        """
        Initialize the storage reader.

        Parameters
        ----------
        checkpoint_config : SageMakerCheckpointConfig
            Configuration object containing checkpoint storage parameters.
        step : int
            Training step associated with the checkpoint.

        Raises
        ------
        SageMakerTieredStorageConfigError
            Errors related to checkpoint configuration
        SageMakerS3TierError
            Error in initializing S3 client
        """
        super().__init__()
        self.checkpoint_config = _get_checkpoint_config(checkpoint_config)
        self.rank = (
            dist.get_rank() if dist.is_available() and dist.is_initialized() else 0
        )
        self.step = step
        logger_name = f"sagemaker.checkpointing.reader.rank_{self.rank}"
        self.logger = _setup_checkpointing_logger(
            logger_name=logger_name,
            namespace=self.checkpoint_config.namespace,
            provided_logger=checkpoint_config.logger,
        )

        # Only setup S3 clients if S3 is configured
        self.s3_base_path = self.checkpoint_config.s3_tier_base_path
        if self.s3_base_path:
            self.region = _get_bucket_location(
                s3_base_path=self.s3_base_path, logger=self.logger
            )
            try:
                self._s3_client_manager = S3ClientManager(logger=self.logger)
                self.s3_client = self._s3_client_manager.get_client(
                    region=self.region, rank=self.rank
                )
            except Exception as e:
                error_msg = (
                    f"[Rank {self.rank}] Step {self.step}: S3 client creation failed"
                )
                self.logger.error(f"{error_msg}:{e}")
                raise SageMakerS3TierError(error_msg) from e
            stats = self._s3_client_manager.get_client_stats()
            self.logger.info(f"S3 client stats: {stats}")
        else:
            self.region = ""

        try:
            self.client = InMemoryCheckpointClient(
                namespace=self.checkpoint_config.namespace,
                rank=str(self.rank),
                world_size=str(self.checkpoint_config.world_size),
                metadata_file_count=1,
                logger=self.logger,
            )
        except Exception as e:
            self.logger.error(f"In-memory client creation failed: {e}")
        self.logger.info(
            f"Initialized StorageReader for rank {self.rank} at step {self.step}"
        )

    def reset(self, checkpoint_id: str | os.PathLike | None = None) -> None:
        """
        Reset the reader's internal state for a new checkpoint operation.

        Parameters
        ----------
        checkpoint_id : str or os.PathLike, optional
            Identifier for the new checkpoint operation.
        """
        self.logger.debug(
            f"[Rank {self.rank}] Step {self.step}: Reset called with checkpoint_id={checkpoint_id}"
        )

    def set_up_storage_reader(self, metadata: Metadata, is_coordinator: bool) -> None:
        """
        Store the provided metadata and coordinator status for later use.

        Parameters
        ----------
        metadata : Metadata
            Metadata object containing checkpoint schema and details.
        is_coordinator : bool
            Indicates if the current instance coordinates the checkpoint.
        """
        self.logger.debug(
            f"[Rank {self.rank}] Step {self.step}: Setting up reader (is_coordinator={is_coordinator})"
        )
        self.metadata = metadata
        self.is_coordinator = is_coordinator
        self.storage_data = metadata.storage_data

    def prepare_local_plan(self, plan: LoadPlan) -> LoadPlan:
        """
        Process and return the local load plan without modifications.

        Parameters
        ----------
        plan : LoadPlan
            Local load plan to execute.

        Returns
        -------
        LoadPlan
            Unmodified local load plan.
        """
        self.logger.debug(
            f"[Rank {self.rank}] Step {self.step}: Preparing local load plan with {len(plan.items)} items"
        )
        return plan

    def prepare_global_plan(self, plans: list[LoadPlan]) -> list[LoadPlan]:
        """
        Process and return global load plans without modifications.

        Parameters
        ----------
        plans : List[LoadPlan]
            Global load plans from all ranks.

        Returns
        -------
        List[LoadPlan]
            Unmodified global load plans.
        """
        self.logger.debug(
            f"[Rank {self.rank}] Step {self.step}: Preparing global load plan with {len(plans)} plans"
        )
        return plans

    def read_metadata(self) -> Metadata:
        """
        Retrieve and deserialize checkpoint metadata from the in-memory storage.

        Returns
        -------
        Metadata
            Metadata object containing checkpoint information.

        Raises
        ------
        RuntimeError
            If metadata retrieval fails.
        """
        # Use provided step or find latest available
        if self.step is None:
            self.step = self._find_latest_complete_step_across_tiers()

        if not self.step:
            self.logger.info(
                f"[Rank {self.rank}] Step {self.step}: No checkpoints found"
            )
            return Metadata({})

        # Try in-memory first (faster)
        metadata_buffer = self._try_read_md_from_memory(self.step)
        if metadata_buffer:
            self.logger.info(
                f"[Rank {self.rank}] Step {self.step}: Successfully read metadata from memory, size={len(metadata_buffer)} bytes"
            )
            return pickle.loads(metadata_buffer)

        self.logger.info(
            f"[Rank {self.rank}] Step {self.step}: In-memory metadata not found"
        )
        # Fallback to S3
        if self.s3_base_path:
            self.logger.info(
                f"[Rank {self.rank}] Step {self.step}: Attempting metadata read from S3"
            )
            metadata_buffer = self._try_read_md_from_s3(self.step)
            if metadata_buffer:
                self.logger.info(
                    f"[Rank {self.rank}] Step {self.step}: Successfully read metadata from S3, size={len(metadata_buffer)} bytes"
                )
                return pickle.loads(metadata_buffer)
        return Metadata({})

    def read_data(self, plan: LoadPlan, planner: LoadPlanner) -> Future[None]:
        """
        Enhanced checkpoint data reading with tiered storage fallback and multi-item support.

        Features:
        - Always attempts In-memory read first for all items
        - Falls back to S3 if In-memory read fails or data not found
        - Handles multiple items individually with proper error handling
        - Automatic fallback handling with comprehensive retry logic
        - Latest step discovery for missing checkpoints

        Parameters
        ----------
        plan : LoadPlan
            Local load plan specifying items to load.
        planner : LoadPlanner
            Planner to load checkpoint data items into memory.

        Returns
        -------
        Future[None]
            A completed future object indicating data loading completion.
        """

        @s3_retry_with_jitter(max_attempts=3, base_delay=2.0, max_delay=60.0)
        def _read_data_from_s3(rank):
            blob = b""
            try:
                s3_base_path = self.checkpoint_config.s3_tier_base_path
                s3_uri = f"{s3_base_path}/{self.checkpoint_config.namespace}/rank_{rank}/step_{self.step}/checkpoint.pt"
                self.logger.debug(
                    f"[Rank {rank}] Step {self.step}: Reading from S3: {s3_uri}"
                )
                # Read from S3 in chunks to avoid memory issues
                with self.s3_client.create_read_stream(s3_uri) as reader:
                    chunks = []
                    chunk_size = 32 * 1024 * 1024  # 32MB chunks
                    total_read = 0

                    while True:
                        chunk = reader.read(chunk_size)
                        if not chunk:
                            break
                        chunks.append(chunk)
                        total_read += len(chunk)

                        if len(chunks) % 10 == 0:  # Log every 10 chunks
                            self.logger.debug(
                                f"[Rank {rank}] Step {self.step}: S3 read progress {total_read / (1024*1024):.1f}MB ({len(chunks)} chunks)"
                            )

                    blob = b"".join(chunks)
                return blob
            except Exception as e:
                error_msg = f"Failed to read checkpoint from S3 for rank:{self.rank} and step: {self.step}"
                self.logger.error(f"{error_msg}:{e}")
                raise SageMakerS3TierError(error_msg) from e

        def _read_data(future: Future, plan: LoadPlan, planner: LoadPlanner):
            try:
                self.logger.info(f"[Rank {self.rank}] Step {self.step}: Reading data")
                if self.step is None:
                    raise SageMakerTieredStorageError(
                        f"[Rank {self.rank}] Step {self.step}: Step must be set before calling read_data"
                    )

                total_start = time.time()
                self.logger.info(
                    f"[Rank {self.rank}] Step {self.step}: Starting checkpoint read ({len(plan.items)} items)"
                )

                in_memory_read_success = True
                per_rank: dict[int, list[ReadItem]] = {}
                in_memory_ckpt_read_size = 0

                for read_item in plan.items:
                    storage_info: _SageMakerStorageInfo = self.storage_data[
                        read_item.storage_index
                    ]
                    per_rank.setdefault(storage_info.rank, []).append(read_item)

                for rank, items in per_rank.items():
                    try:
                        blob = self.client.get_checkpoint(step=self.step, rank=rank)  # type: ignore
                        if blob is None:
                            self.logger.info(
                                f"[Rank {self.rank}] Step {self.step}: get_check_point returned empty blob"
                            )
                            in_memory_read_success = False
                        if blob:
                            in_memory_ckpt_read_size += len(blob)
                            for read_item in items:
                                try:
                                    storage_info = self.storage_data[
                                        read_item.storage_index
                                    ]
                                    item_data = blob[storage_info.offset : storage_info.offset + storage_info.length]  # type: ignore

                                    if read_item.type == LoadItemType.BYTE_IO:
                                        stream = io.BytesIO(item_data)
                                        planner.load_bytes(read_item, stream)
                                        stream.close()
                                    else:
                                        stream = io.BytesIO(item_data)
                                        tensor = torch.load(stream, map_location="cpu")
                                        if hasattr(
                                            read_item, "storage_offsets"
                                        ) and hasattr(read_item, "lengths"):
                                            tensor = narrow_tensor_by_index(
                                                tensor,
                                                read_item.storage_offsets,
                                                read_item.lengths,
                                            )

                                        target_tensor = planner.resolve_tensor(
                                            read_item
                                        ).detach()
                                        if target_tensor.size() != tensor.size():
                                            raise SageMakerTieredStorageError(
                                                f"[Rank {self.rank}] Step {self.step}: Size mismatch for {read_item.storage_index}: "
                                                f"expected {target_tensor.size()}, got {tensor.size()}"
                                            )

                                        target_tensor.copy_(tensor)
                                        planner.commit_tensor(read_item, target_tensor)
                                        stream.close()
                                except EOFError:
                                    break
                                except Exception as e:
                                    error_msg = f"[Rank {self.rank}] Step {self.step}: Checkpoint load in to state_dict failed"
                                    self.logger.error(f"{error_msg}:{e}")
                                    raise SageMakerTieredStorageError(error_msg) from e
                    except Exception as e:
                        in_memory_read_success = False
                        error_msg = f"[Rank {self.rank}] Step {self.step}: In-memory read failed"
                        self.logger.error(f"{error_msg}:{e}")
                        if self.s3_base_path:
                            break
                        else:
                            raise SageMakerInMemoryTierError(error_msg) from e

                if not in_memory_read_success:
                    s3_read_start_time = time.time()
                    s3_ckpt_read_size = 0
                    for rank, items in per_rank.items():
                        try:
                            s3_read_start_time = time.time()
                            blob = _read_data_from_s3(rank)
                            s3_ckpt_read_size += len(blob)
                            s3_read_time_taken = time.time() - s3_read_start_time
                            s3_speed = (
                                (len(blob) / (1024 * 1024)) / s3_read_time_taken
                                if s3_read_time_taken > 0
                                else 0
                            )
                            self.logger.info(
                                f"[Rank {self.rank}] Step {self.step}:  "
                                f"read from S3 in {s3_read_time_taken:.3f}s ({len(blob) / (1024*1024):.1f}MB, "
                                f"{s3_speed:.1f} MB/s, {len(blob)} blob)"
                            )

                            for read_item in items:
                                try:
                                    storage_info = self.storage_data[
                                        read_item.storage_index
                                    ]
                                    item_data = blob[storage_info.offset : storage_info.offset + storage_info.length]  # type: ignore

                                    if read_item.type == LoadItemType.BYTE_IO:
                                        stream = io.BytesIO(item_data)
                                        planner.load_bytes(read_item, stream)
                                        stream.close()
                                    else:
                                        stream = io.BytesIO(item_data)
                                        tensor = torch.load(stream, map_location="cpu")

                                        if hasattr(
                                            read_item, "storage_offsets"
                                        ) and hasattr(read_item, "lengths"):
                                            tensor = narrow_tensor_by_index(
                                                tensor,
                                                read_item.storage_offsets,
                                                read_item.lengths,
                                            )

                                        target_tensor = planner.resolve_tensor(
                                            read_item
                                        ).detach()
                                        if target_tensor.size() != tensor.size():
                                            raise SageMakerTieredStorageError(
                                                f"[Rank {self.rank}] Step {self.step}: Size mismatch for {read_item.storage_index}: "
                                                f"expected {target_tensor.size()}, got {tensor.size()}"
                                            )

                                        target_tensor.copy_(tensor)
                                        planner.commit_tensor(read_item, target_tensor)
                                        stream.close()
                                except EOFError:
                                    break
                                except Exception as e:
                                    error_msg = f"[Rank {self.rank}] Step {self.step}: Checkpoint load in to state_dict failed"
                                    self.logger.error(f"{error_msg}:{e}")
                                    raise SageMakerTieredStorageError(error_msg) from e

                        except Exception as e:
                            self.logger.error(
                                f"[Rank {self.rank}] Step {self.step}: S3 read failed:{e}"
                            )
                            future.set_exception(e)
                            return future
                # Final logging and statistics
                total_time = time.time() - total_start
                self.logger.info(
                    f"[Rank {self.rank}] Step {self.step}: Checkpoint read completed in {total_time:.3f}s"
                )
                future.set_result(None)
            except Exception as e:
                error_msg = (
                    f"[Rank {self.rank}] Step {self.step}: Checkpoint load failed"
                )
                self.logger.error(f"{error_msg}:{e}")
                future.set_exception(e)
                return future

        future: Future = Future()
        t = threading.Thread(target=_read_data, args=(future, plan, planner))
        t.start()
        return future

    @classmethod
    def validate_checkpoint_id(cls, checkpoint_id: str | os.PathLike) -> bool:
        """
        Validate checkpoint ID for storage compatibility. Currently always returns True.

        Parameters
        ----------
        checkpoint_id : str or os.PathLike
            Checkpoint identifier to validate.

        Returns
        -------
        bool
            Always True, indicating compatibility.
        """
        return True

    def _find_latest_complete_step_across_tiers(self) -> int | None:
        """Find latest step from both storage tiers."""
        memory_step = self.client.get_latest_checkpoints(limit=1)
        s3_step = self._find_latest_complete_step()
        latest_step = None
        if not memory_step:
            latest_step = s3_step
        elif not s3_step:
            latest_step = memory_step[0]
        else:
            latest_step = max(memory_step[0], s3_step)
        self.logger.info(
            f"[Rank {self.rank}] Step {self.step}: Latest steps: "
            f"memory:{memory_step}, s3:{s3_step}, across_tiers:{latest_step}"
        )
        return latest_step

    def _try_read_md_from_memory(self, step: int) -> bytes | None:
        """Try reading metadata from in-memory storage."""
        try:
            return self.client.get_checkpoint(step=step, metadata_index=METADATA_INDEX)
        except Exception as e:
            self.logger.error(f"Memory read failed for step {step}: {e}")
            return None

    def _try_read_md_from_s3(self, step: int) -> bytes | None:
        """Try reading metadata from S3 storage."""
        try:
            return self._read_item_from_s3(step, "", is_metadata=True)
        except Exception as e:
            self.logger.error(f"S3 metadata read failed for step {step}: {e}")
            return None

    def _find_latest_complete_step(self) -> int | None:
        """
        Find the latest step that is complete across ALL ranks in S3.

        Returns
        -------
        Optional[int]
            The latest step number available for all ranks, or None if no complete steps found.
        """
        try:
            s3_base_path = self.checkpoint_config.s3_tier_base_path
            # Parse S3 path to extract bucket and prefix
            path_without_s3 = s3_base_path[5:]  # Remove 's3://'
            if "/" in path_without_s3:
                bucket, base_prefix = path_without_s3.split("/", 1)
                base_prefix = base_prefix.rstrip(
                    "/"
                )  # Remove trailing slash if present
            else:
                bucket = path_without_s3
                base_prefix = ""

            if base_prefix:
                full_base_prefix = f"{base_prefix}/{self.checkpoint_config.namespace}"
            else:
                full_base_prefix = self.checkpoint_config.namespace

            s3_client = boto3.client("s3", region_name=self.region)

            # Collect steps for each rank
            rank_steps: dict[int, set[int]] = {}
            self.logger.info(
                f"[Rank {self.rank}] Searching bucket: {bucket}, full_base_prefix: {full_base_prefix}"
            )

            for rank in range(self.checkpoint_config.world_size):
                rank_prefix = f"{full_base_prefix}/rank_{rank}/"
                self.logger.debug(
                    f"[Rank {self.rank}] Searching with rank_prefix: '{rank_prefix}'"
                )

                paginator = s3_client.get_paginator("list_objects_v2")
                rank_steps[rank] = set()

                for page in paginator.paginate(
                    Bucket=bucket, Prefix=rank_prefix, Delimiter="/"
                ):
                    prefixes = page.get("CommonPrefixes", [])
                    for prefix_info in prefixes:
                        prefix = prefix_info["Prefix"]
                        if "/step_" in prefix:
                            try:
                                step_part = prefix.split("/step_")[1].rstrip("/")
                                step_num = int(step_part)
                                rank_steps[rank].add(step_num)
                            except (ValueError, IndexError):
                                continue
                self.logger.debug(
                    f"[Rank {self.rank}] Final steps for rank {rank}: {rank_steps[rank]}"
                )

            s3_client.close()
            # Find intersection of all rank steps (steps present in ALL ranks)
            if not rank_steps:
                return None

            all_complete_steps = (
                set.intersection(*rank_steps.values()) if rank_steps else set()
            )

            if all_complete_steps:
                latest_complete_step = max(all_complete_steps)
                self.logger.info(
                    f"[Rank {self.rank}] Step {self.step}: Latest complete step across all {self.checkpoint_config.world_size} ranks: {latest_complete_step}"
                )
                return latest_complete_step
            else:
                self.logger.warning(
                    f"[Rank {self.rank}] Step {self.step}: No steps found that are complete across all ranks"
                )
                return None

        except Exception as e:
            self.logger.error(
                f"[Rank {self.rank}] Step {self.step}: Failed to find latest complete step: {e}"
            )
            return None

    def _read_item_from_s3(
        self, step: int, item_index: str = "", is_metadata: bool = False
    ) -> bytes | None:
        """
        Read a specific item from S3 for the given step.

        Parameters
        ----------
        item_index : str
            The item index to read.
        step : int
            The step number to read from.

        Returns
        -------
        Optional[bytes]
            The item data as bytes, or None if not found.
        """
        try:
            s3_base_path = self.checkpoint_config.s3_tier_base_path
            if not is_metadata:
                s3_uri = f"{s3_base_path}/{self.checkpoint_config.namespace}/rank_{self.rank}/step_{step}/item_{item_index}.pt"
            else:
                s3_uri = f"{s3_base_path}/{self.checkpoint_config.namespace}/rank_0/step_{step}/metadata.metadata"
            self.logger.debug(
                f"[Rank {self.rank}] Step {self.step}: Reading item {item_index} from {s3_uri}"
            )

            # Read from S3 in chunks
            with self.s3_client.create_read_stream(s3_uri=s3_uri) as reader:
                chunks = []
                chunk_size = 32 * 1024 * 1024  # 32MB chunks
                total_read = 0

                while True:
                    chunk = reader.read(chunk_size)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    total_read += len(chunk)

                return b"".join(chunks)

        except Exception as e:
            self.logger.debug(
                f"[Rank {self.rank}] Failed to read item {item_index} from step {step}: {e}"
            )
            return None
