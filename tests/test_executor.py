from app.planner.executor import Executor
from app.planner.schemas import ExecutionPlan, PlanStep, Skill


def test_executor_runs_skills_in_order(mocker):

    executor = Executor()

    mock_metadata = mocker.patch.object(
        executor.registry,
        "metadata_lookup",
        return_value={
            "status": "success",
            "table": "fct_users_created",
        },
    )

    mock_airflow = mocker.patch.object(
        executor.registry,
        "generate_airflow",
        return_value={
            "status": "success",
            "artifact_path": "generated/airflow/test.py",
        },
    )

    mock_validate = mocker.patch.object(
        executor.registry,
        "validate",
        return_value={
            "status": "success",
            "validation": "pass",
            "artifact_path": "generated/airflow/test.py",
        },
    )

    plan = ExecutionPlan(
        steps=[
            PlanStep(
                skill=Skill.METADATA_LOOKUP,
                reason="Need table metadata",
            ),
            PlanStep(
                skill=Skill.GENERATE_AIRFLOW,
                reason="Generate Airflow DAG",
            ),
            PlanStep(
                skill=Skill.VALIDATE,
                reason="Validate generated DAG",
            ),
        ]
    )

    results = executor.execute(
        plan,
        {
            "task": (
                "Generate an Airflow DAG "
                "for fct_users_created"
            ),
            "table": "fct_users_created",
        },
    )

    assert results["metadata_lookup"]["status"] == "success"
    assert results["generate_airflow"]["status"] == "success"
    assert results["validate"]["validation"] == "pass"

    mock_metadata.assert_called_once()
    mock_airflow.assert_called_once()
    mock_validate.assert_called_once()


def test_executor_stops_when_skill_fails(mocker):

    executor = Executor()

    mock_metadata = mocker.patch.object(
        executor.registry,
        "metadata_lookup",
        return_value={
            "status": "failed",
            "reason": "Metadata lookup failed",
        },
    )

    mock_airflow = mocker.patch.object(
        executor.registry,
        "generate_airflow",
    )

    plan = ExecutionPlan(
        steps=[
            PlanStep(
                skill=Skill.METADATA_LOOKUP,
                reason="Need table metadata",
            ),
            PlanStep(
                skill=Skill.GENERATE_AIRFLOW,
                reason="Generate Airflow DAG",
            ),
        ]
    )

    results = executor.execute(
        plan,
        {
            "task": "Generate an Airflow DAG",
            "table": "fct_users_created",
        },
    )

    assert results["metadata_lookup"]["status"] == "failed"
    assert "generate_airflow" not in results

    mock_metadata.assert_called_once()
    mock_airflow.assert_not_called()


def test_executor_blocks_git_commit_after_failed_validation(mocker):

    executor = Executor()

    mock_metadata = mocker.patch.object(
        executor.registry,
        "metadata_lookup",
        return_value={
            "status": "success",
            "table": "fct_users_created",
        },
    )

    mock_airflow = mocker.patch.object(
        executor.registry,
        "generate_airflow",
        return_value={
            "status": "success",
            "artifact_path": "generated/airflow/test.py",
        },
    )

    mock_validate = mocker.patch.object(
        executor.registry,
        "validate",
        return_value={
            "status": "failed",
            "validation": "fail",
            "details": "Unsafe artifact",
            "artifact_path": "generated/airflow/test.py",
        },
    )

    mock_commit = mocker.patch.object(
        executor.registry,
        "git_commit",
    )

    plan = ExecutionPlan(
        steps=[
            PlanStep(skill=Skill.METADATA_LOOKUP),
            PlanStep(skill=Skill.GENERATE_AIRFLOW),
            PlanStep(skill=Skill.VALIDATE),
            PlanStep(skill=Skill.GIT_COMMIT),
        ]
    )

    results = executor.execute(
        plan,
        {
            "task": "Generate an Airflow DAG",
            "table": "fct_users_created",
        },
    )

    assert results["validate"]["validation"] == "fail"
    assert "git_commit" not in results

    mock_metadata.assert_called_once()
    mock_airflow.assert_called_once()
    mock_validate.assert_called_once()
    mock_commit.assert_not_called()