from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DatahubClientConfig
from datahub.metadata.schema_classes import SchemaMetadataClass

# Ensure the server points to 8080 (the GMS API port)
graph = DataHubGraph(DatahubClientConfig(server='http://localhost:8080'))

# Using the URN you just confirmed
urn = 'urn:li:dataset:(urn:li:dataPlatform:hive,fct_users_created,PROD)'

# Fetch schema metadata
schema = graph.get_aspect(urn, aspect_type=SchemaMetadataClass)

# Print field paths and data types to verify
for f in schema.fields:
    print(f"Column: {f.fieldPath}, Type: {f.nativeDataType}")
    