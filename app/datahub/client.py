import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict
from fastapi import HTTPException

load_dotenv()

# Import the direct SDK client tools you used on Day 2
from datahub.ingestion.graph.client import DataHubGraph, DatahubClientConfig
from datahub.metadata.schema_classes import (
    SchemaMetadataClass, 
    OwnershipClass, 
    GlobalTagsClass, 
    UpstreamLineageClass
)

# Define the dataclass as outlined in the Day 3/Day 4 instructions
@dataclass
class TableMetadata:
    name: str
    columns: List[Dict[str, str]]
    owners: List[str]
    tags: List[str]
    lineage: List[str]

class MetadataService:
    def __init__(self):
        gms = os.getenv("DATAHUB_GMS")

        if gms:
            try:
                self.graph = DataHubGraph(
                    DatahubClientConfig(server=gms)
                )
            except Exception as e:
                print(f"DataHub unavailable: {e}")
                self.graph = None
        else:
            self.graph = None

        self.platform = "hive"
        self.env = "PROD"

    def get_table_context(self, table_name: str) -> TableMetadata:
        """Fetches metadata from DataHub and maps it to the TableMetadata dataclass."""

        if self.graph is None:
            return TableMetadata(
                name=table_name,
                columns=[
                    {
                        "name": "user_id",
                        "type": "BIGINT",
                        "description": "Primary key"
                    },
                    {
                        "name": "created_at",
                        "type": "TIMESTAMP",
                        "description": "Record creation timestamp"
                    },
                    {
                        "name": "email",
                        "type": "STRING",
                        "description": "User email address"
                    }
                ],
                owners=["Demo"],
                tags=["Demo"],
                lineage=[]
            )

        # Construct the URN string format that DataHub expects
        urn = f"urn:li:dataset:(urn:li:dataPlatform:{self.platform},{table_name},{self.env})"
        
        try:
            # Fetch the raw aspects using the graph client
            schema = self.graph.get_aspect(urn, aspect_type=SchemaMetadataClass)
            ownership = self.graph.get_aspect(urn, aspect_type=OwnershipClass)
            tags_aspect = self.graph.get_aspect(urn, aspect_type=GlobalTagsClass)
            lineage_aspect = self.graph.get_aspect(urn, aspect_type=UpstreamLineageClass)
            
            # Error Handling: 404 if the table URN is unknown (Schema is None)
            if not schema:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Table '{table_name}' not found. Please check for similar table names."
                )

            # Map the Data: Extract columns as a list of dictionaries
            columns = [
                {
                    "name": field.fieldPath, 
                    "type": field.nativeDataType, 
                    "description": field.description or ""
                } 
                for field in schema.fields
            ]
            
            # Map the Data: Extract owners
            owners = []
            if ownership:
                owners = [owner.owner for owner in ownership.owners]
                
            # Map the Data: Extract tags
            tags = []
            if tags_aspect:
                tags = [tag.tag for tag in tags_aspect.tags]
                
            # Map the Data: Extract upstream lineage URNs
            lineage = []
            if lineage_aspect:
                lineage = [upstream.dataset for upstream in lineage_aspect.upstreams]

            # Return the populated dataclass
            return TableMetadata(
                name=table_name,
                columns=columns,
                owners=owners,
                tags=tags,
                lineage=lineage
            )
            
        except HTTPException:
            # Re-raise the 404 so it isn't caught by the broad exception below
            raise

        except Exception as e:
            print(f"Metadata fetch failed: {e}")

            # Fallback metadata when DataHub is unavailable
            return TableMetadata(
                name=table_name,
                columns=[
                    {
                        "name": "user_id",
                        "type": "BIGINT",
                        "description": "Primary key"
                    },
                    {
                        "name": "created_at",
                        "type": "TIMESTAMP",
                        "description": "Record creation timestamp"
                    },
                    {
                        "name": "email",
                        "type": "STRING",
                        "description": "User email address"
                    }
                ],
                owners=["Demo"],
                tags=["Demo"],
                lineage=[]
            )