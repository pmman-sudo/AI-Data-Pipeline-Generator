from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Skill(str, Enum):

    METADATA_LOOKUP = "metadata_lookup"

    GENERATE_SQL = "generate_sql"
    GENERATE_AIRFLOW = "generate_airflow"
    GENERATE_DBT = "generate_dbt"
    GENERATE_YAML = "generate_yaml"
    GENERATE_README = "generate_readme"

    GENERATE_TERRAFORM = "generate_terraform"
    GENERATE_IAM = "generate_iam"

    VALIDATE = "validate"
    GIT_COMMIT = "git_commit"
    DOWNLOAD_ARTIFACTS = "download_artifacts"


class PlanStep(BaseModel):

    skill: Skill
    reason: Optional[str] = None


class ExecutionPlan(BaseModel):

    steps: List[PlanStep]