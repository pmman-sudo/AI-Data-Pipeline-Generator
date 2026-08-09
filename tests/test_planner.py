import json
import os

from app.planner.planner import Planner
from app.planner.schemas import Skill


def mock_generate(mocker, steps):
    return mocker.patch(
        "app.planner.planner.generate",
        return_value=json.dumps({
            "steps": steps
        }),
    )


def test_planner_selects_airflow(mocker):
    mock_generate(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_airflow",
                "reason": "Generate Airflow DAG",
            },
            {
                "skill": "validate",
                "reason": "Validate generated DAG",
            },
        ],
    )

    planner = Planner()

    plan = planner.create_plan(
        "Generate an Airflow DAG for the fct_users_created table"
    )

    skills = [step.skill for step in plan.steps]

    assert Skill.METADATA_LOOKUP in skills
    assert Skill.GENERATE_AIRFLOW in skills
    assert Skill.VALIDATE in skills

    assert skills.index(Skill.METADATA_LOOKUP) < \
        skills.index(Skill.GENERATE_AIRFLOW)

    assert skills.index(Skill.GENERATE_AIRFLOW) < \
        skills.index(Skill.VALIDATE)


def test_planner_selects_terraform(mocker):
    mock_generate(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_terraform",
                "reason": "Generate Terraform infrastructure",
            },
            {
                "skill": "validate",
                "reason": "Validate generated Terraform",
            },
        ],
    )

    planner = Planner()

    plan = planner.create_plan(
        "Generate Terraform infrastructure for the fct_users_created table"
    )

    skills = [step.skill for step in plan.steps]

    assert Skill.METADATA_LOOKUP in skills
    assert Skill.GENERATE_TERRAFORM in skills
    assert Skill.VALIDATE in skills

    assert skills.index(Skill.METADATA_LOOKUP) < \
        skills.index(Skill.GENERATE_TERRAFORM)

    assert skills.index(Skill.GENERATE_TERRAFORM) < \
        skills.index(Skill.VALIDATE)


def test_planner_adds_git_commit_when_requested(mocker):
    mock_generate(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_airflow",
                "reason": "Generate Airflow DAG",
            },
            {
                "skill": "validate",
                "reason": "Validate generated DAG",
            },
            {
                "skill": "git_commit",
                "reason": "Commit generated artifact to Git",
            },
        ],
    )

    planner = Planner()

    plan = planner.create_plan(
        "Generate an Airflow DAG for the fct_users_created table "
        "and commit it to Git"
    )

    skills = [step.skill for step in plan.steps]

    assert Skill.GENERATE_AIRFLOW in skills
    assert Skill.VALIDATE in skills
    assert Skill.GIT_COMMIT in skills

    assert skills.index(Skill.VALIDATE) < \
        skills.index(Skill.GIT_COMMIT)


def test_planner_does_not_add_git_commit_when_not_requested(mocker):
    mock_generate(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_airflow",
                "reason": "Generate Airflow DAG",
            },
            {
                "skill": "validate",
                "reason": "Validate generated DAG",
            },
        ],
    )

    planner = Planner()

    plan = planner.create_plan(
        "Generate an Airflow DAG for the fct_users_created table"
    )

    skills = [step.skill for step in plan.steps]

    assert Skill.GIT_COMMIT not in skills
    assert Skill.GENERATE_AIRFLOW in skills
    assert Skill.VALIDATE in skills


def test_planner_does_not_confuse_terraform_with_yaml(mocker):
    mock_generate(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_terraform",
                "reason": "Generate Terraform infrastructure",
            },
            {
                "skill": "validate",
                "reason": "Validate generated Terraform",
            },
        ],
    )

    planner = Planner()

    plan = planner.create_plan(
        "Generate Terraform infrastructure for the fct_users_created table"
    )

    skills = [step.skill for step in plan.steps]

    assert Skill.GENERATE_TERRAFORM in skills
    assert Skill.GENERATE_YAML not in skills


def test_planner_does_not_confuse_airflow_with_sql(mocker):
    mock_generate(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_airflow",
                "reason": "Generate Airflow DAG",
            },
            {
                "skill": "validate",
                "reason": "Validate generated DAG",
            },
        ],
    )

    planner = Planner()

    plan = planner.create_plan(
        "Generate an Airflow DAG for the fct_users_created table"
    )

    skills = [step.skill for step in plan.steps]

    assert Skill.GENERATE_AIRFLOW in skills
    assert Skill.GENERATE_SQL not in skills


def test_planner_builds_correct_commit_workflow(mocker):
    mock_generate(
        mocker,
        [
            {
                "skill": "metadata_lookup",
                "reason": "Need table schema",
            },
            {
                "skill": "generate_terraform",
                "reason": "Generate Terraform infrastructure",
            },
            {
                "skill": "validate",
                "reason": "Validate generated Terraform",
            },
            {
                "skill": "git_commit",
                "reason": "Commit generated artifact to Git",
            },
        ],
    )

    planner = Planner()

    plan = planner.create_plan(
        "Generate Terraform infrastructure for the "
        "fct_users_created table and commit it to Git"
    )

    skills = [step.skill for step in plan.steps]

    assert skills.index(Skill.METADATA_LOOKUP) < \
        skills.index(Skill.GENERATE_TERRAFORM)

    assert skills.index(Skill.GENERATE_TERRAFORM) < \
        skills.index(Skill.VALIDATE)

    assert skills.index(Skill.VALIDATE) < \
        skills.index(Skill.GIT_COMMIT)

       