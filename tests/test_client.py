import pytest
from fastapi import HTTPException
from app.datahub.client import MetadataService

def test_get_table_context_not_found(mocker):
    # Initialize our new service
    service = MetadataService()
    
    # Mock the graph client to return None, simulating a missing table
    mocker.patch.object(service.graph, 'get_aspect', return_value=None)
    
    # Assert that calling the method throws a 404 HTTPException
    with pytest.raises(HTTPException) as excinfo:
        service.get_table_context("non_existent_table")
    
    assert excinfo.value.status_code == 404