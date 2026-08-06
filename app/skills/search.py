from app.datahub.client import MetadataService
from .base import BaseSkill


class SearchSkill(BaseSkill):

    name = "search"

    def execute(self, context):

        dataset = context["dataset"]

        metadata = MetadataService().get_table_context(dataset)

        context["asset_found"] = True
        context["owner"] = metadata.owners
        context["tags"] = metadata.tags
        context["columns"] = metadata.columns

        return context