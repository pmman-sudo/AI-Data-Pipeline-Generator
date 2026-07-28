from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DatahubClientConfig
from datahub.metadata.schema_classes import SchemaMetadataClass, OwnershipClass, GlobalTagsClass
import json

graph = DataHubGraph(DatahubClientConfig(server='http://localhost:8080'))
urn = 'urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)'

# Fetch aspects
schema = graph.get_aspect(urn, aspect_type=SchemaMetadataClass)
ownership = graph.get_aspect(urn, aspect_type=OwnershipClass)
tags = graph.get_aspect(urn, aspect_type=GlobalTagsClass)

# Structure the data
data_blob = {
    "urn": urn,
    "schema": [f.fieldPath for f in schema.fields] if schema else [],
    "owners": str(ownership) if ownership else "None",
    "tags": str(tags) if tags else "None"
}

# Print as JSON
print(json.dumps(data_blob, indent=2))