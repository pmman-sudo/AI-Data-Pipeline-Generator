import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.datahub.client import MetadataService


def test_get_table_context_not_found(mocker):
    # Create a fake DataHub graph
    fake_graph = MagicMock()
    fake_graph.get_aspect.return_value = None

    # Mock DataHubGraph so MetadataService uses our fake graph
    mocker.patch(
        "app.datahub.client.DataHubGraph",
        return_value=fake_graph
    )

    # Pretend DATAHUB_GMS is configured
    mocker.patch(
        "os.getenv",
        return_value="http://fake-datahub:8080"
    )

    service = MetadataService()

    with pytest.raises(HTTPException) as excinfo:
        service.get_table_context("non_existent_table")

    assert excinfo.value.status_code == 404