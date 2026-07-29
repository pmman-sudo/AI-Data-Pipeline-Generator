import time
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import DatasetPropertiesClass

def write_generation_metadata(table_name: str, artifact_path: str, prompt: str, commit_hash: str):
    """Writes the generation metadata back to the dataset in DataHub."""
    
    # Connect to the local DataHub GMS
    emitter = DatahubRestEmitter('http://localhost:8080')
    
    # Construct the unique URN for the table (assuming the 'hive' platform and 'PROD' env from your sample data)
    dataset_urn = make_dataset_urn("hive", table_name, "PROD")

    # Define the custom properties to write back, including your name as required by the guide
    properties = DatasetPropertiesClass(
        customProperties={
            "generated_artifact": artifact_path,
            "generated_by": "Paul Iyen",
            "generated_at": str(time.time()),
            "llm_prompt": prompt,
            "github_commit": commit_hash
        }
    )

    # Wrap it in a Metadata Change Proposal (MCP)
    mcp = MetadataChangeProposalWrapper(
        entityType="dataset",
        changeType="UPSERT",
        entityUrn=dataset_urn,
        aspectName="datasetProperties",
        aspect=properties
    )

    # Emit the data back to DataHub
    emitter.emit(mcp)
    return True