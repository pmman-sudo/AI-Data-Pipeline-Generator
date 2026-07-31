import os
import shutil
from datetime import datetime


def create_pipeline_package(table_name: str) -> tuple[str, str]:
    """
    Creates a pipeline package folder and returns:

    (package_directory, zip_path)
    """

    date = datetime.now().strftime("%Y%m%d")

    package_name = f"{table_name}_pipeline_{date}"

    package_dir = os.path.join(
        "generated",
        package_name
    )

    folders = [
        "airflow",
        "sql",
        "dbt",
        "configs",
        "iam"
    ]

    for folder in folders:
        os.makedirs(
            os.path.join(package_dir, folder),
            exist_ok=True
        )

    return package_dir