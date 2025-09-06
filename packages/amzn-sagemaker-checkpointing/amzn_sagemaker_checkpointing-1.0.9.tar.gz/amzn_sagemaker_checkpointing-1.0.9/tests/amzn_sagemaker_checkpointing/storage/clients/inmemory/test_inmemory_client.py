from unittest.mock import MagicMock, patch

import pytest
from requests.models import Response

from amzn_sagemaker_checkpointing.config.in_memory_client import InMemoryClientConfig
from amzn_sagemaker_checkpointing.storage.clients.inmemory.exceptions import (
    InMemoryRequestError,
    InMemoryStorageError
)
from amzn_sagemaker_checkpointing.storage.clients.inmemory.inmemory_client import (
    InMemoryCheckpointClient,
)


@pytest.fixture
def mock_client():
    config = InMemoryClientConfig(base_url="http://mockserver")
    client = InMemoryCheckpointClient(
        namespace="test-ns", rank="0", world_size="1", config=config
    )
    return client


def mock_response(status_code=200, json_data=None, content=b"", headers=None):
    response = MagicMock(spec=Response)
    response.status_code = status_code
    response.content = content
    response.headers = headers or {}
    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.side_effect = ValueError("No JSON")
    return response


def test_get_or_create_namespace_creates_if_missing(mock_client):
    with patch.object(mock_client, "_make_request") as mock_req:
        mock_req.side_effect = [
            mock_response(status_code=404),
            mock_response(status_code=200),
            mock_response(status_code=200, json_data={"namespace": "test-ns"}),
        ]
        result = mock_client.get_or_create_namespace()
        assert result == {"namespace": "test-ns"}
        assert mock_req.call_count == 3


def test_get_namespace_config_success(mock_client):
    with patch.object(mock_client, "_make_request") as mock_req:
        mock_req.return_value = mock_response(
            status_code=200, json_data={"steps_retained": 5}
        )
        config = mock_client.get_namespace_config()
        assert config["steps_retained"] == 5


def test_get_namespace_config_404_returns_empty(mock_client):
    with patch.object(mock_client, "_make_request") as mock_req:
        mock_req.return_value = mock_response(status_code=404)
        config = mock_client.get_namespace_config()
        assert config == {}


def test_get_namespace_config_invalid_json_raises(mock_client):
    with patch.object(mock_client, "_make_request") as mock_req:
        mock_req.return_value = mock_response(status_code=200)
        with pytest.raises(InMemoryStorageError):
            mock_client.get_namespace_config()


def test_delete_namespace_succeeds(mock_client):
    with patch.object(mock_client, "_make_request") as mock_req:
        mock_req.return_value = mock_response(status_code=200)
        mock_client.delete_namespace()
        mock_req.assert_called_once()
        assert mock_req.call_args[0][0] == "DELETE"
