import streamlit as st
import requests
from pathlib import Path

API_URL = "https://ai-data-pipeline-generator.onrender.com"


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI Data Pipeline Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# CUSTOM HEADER
# ==========================================================

st.title("🤖 AI Data Pipeline Agent")

st.markdown(
    """
    **Autonomous AI Data Engineering**

    Describe what you need. The agent determines the required
    skills, retrieves metadata, generates the artifact, validates it,
    and optionally commits or prepares it for download.
    """
)

st.divider()


# ==========================================================
# BACKEND CONNECTION
# ==========================================================

def check_backend():
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=10,
        )

        return response.status_code == 200

    except Exception:
        return False


backend_online = check_backend()


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("🤖 Agent Status")

    if backend_online:
        st.success("Backend Online")
    else:
        st.error("Backend Offline")

    st.divider()

    st.markdown("### 🧠 Agent Capabilities")

    st.markdown(
        """
        ✓ Metadata Lookup  
        ✓ SQL Generation  
        ✓ Airflow Generation  
        ✓ dbt Generation  
        ✓ YAML Generation  
        ✓ README Generation  
        ✓ Terraform Generation  
        ✓ IAM Generation  
        ✓ Artifact Validation  
        ✓ Git Commit  
        ✓ Artifact Download
        """
    )

    st.divider()

    st.caption(
        "AI Data Pipeline Generator"
    )


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_table_metadata(table_name):

    try:

        response = requests.get(
            f"{API_URL}/schema/{table_name}",
            timeout=(10, 60),
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        st.error(
            f"Unable to retrieve metadata: {e}"
        )

        return None


def get_artifact_content(artifact_path):

    try:

        response = requests.get(
            f"{API_URL}/download",
            params={
                "path": artifact_path
            },
            timeout=(10, 60),
        )

        response.raise_for_status()

        return response.text

    except Exception as e:

        st.warning(
            f"Could not retrieve generated artifact: {e}"
        )

        return None


def skill_label(skill):

    labels = {

        "metadata_lookup": "📊 Metadata Lookup",

        "generate_sql": "🗄 Generate SQL",

        "generate_airflow": "🌬 Generate Airflow DAG",

        "generate_dbt": "🔷 Generate dbt Model",

        "generate_yaml": "⚙️ Generate YAML",

        "generate_readme": "📚 Generate README",

        "generate_terraform": "☁️ Generate Terraform",

        "generate_iam": "🔐 Generate IAM",

        "validate": "🛡 Validate Artifact",

        "git_commit": "🔗 Commit to Git",

        "download_artifacts": "⬇️ Prepare Download",
    }

    return labels.get(
        skill,
        skill,
    )


# ==========================================================
# METADATA EXPLORER
# ==========================================================

st.header("📊 Metadata Explorer")

table_name = st.text_input(
    "Table Name",
    value="customer_orders",
    help="Enter the DataHub table you want to inspect.",
)

if st.button(
    "🔍 Preview Metadata",
    use_container_width=True,
):

    with st.spinner(
        "Retrieving DataHub metadata..."
    ):

        metadata = get_table_metadata(
            table_name
        )

    if metadata:

        st.success(
            "Metadata loaded successfully."
        )

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📋 Columns",
                "👤 Owners",
                "🏷 Tags",
                "🔗 Lineage",
            ]
        )

        with tab1:

            columns = metadata.get(
                "columns",
                [],
            )

            if columns:
                st.dataframe(
                    columns,
                    use_container_width=True,
                )
            else:
                st.info(
                    "No column metadata available."
                )

        with tab2:

            owners = metadata.get(
                "owners",
                [],
            )

            if owners:
                for owner in owners:
                    st.write(f"👤 {owner}")
            else:
                st.info("No owners found.")

        with tab3:

            tags = metadata.get(
                "tags",
                [],
            )

            if tags:
                for tag in tags:
                    st.write(f"🏷 {tag}")
            else:
                st.info("No tags found.")

        with tab4:

            lineage = metadata.get(
                "lineage",
                [],
            )

            if lineage:
                for item in lineage:
                    st.write(f"🔗 {item}")
            else:
                st.info(
                    "No lineage information available."
                )


st.divider()


# ==========================================================
# AI AGENT
# ==========================================================

st.header("🧠 Autonomous AI Agent")

st.markdown(
    """
    Instead of manually selecting a pipeline tool, describe your
    objective. The planning agent decides which skills should run.
    """
)


task = st.text_area(
    "What do you want the agent to do?",
    height=160,
    placeholder=(
        "Examples:\n"
        "• Generate SQL for customer_orders\n"
        "• Generate an Airflow DAG for customer_orders\n"
        "• Generate Terraform infrastructure for customer_orders "
        "and commit it to Git\n"
        "• Generate Terraform infrastructure for customer_orders "
        "and make it available for download"
    ),
)


generate = st.button(
    "🚀 Execute AI Agent",
    type="primary",
    use_container_width=True,
)


# ==========================================================
# AGENT EXECUTION
# ==========================================================

if generate:

    if not task.strip():

        st.warning(
            "Please describe what you want the agent to do."
        )

        st.stop()

    st.divider()

    # ------------------------------------------------------
    # Agent execution
    # ------------------------------------------------------

    with st.spinner(
        "🤖 Agent is planning and executing..."
    ):

        try:

            response = requests.post(
                f"{API_URL}/generate",

                json={
                    "task": task,
                    "artifact_type": None,
                },

                timeout=180,
            )

        except Exception as e:

            st.error(
                f"Agent request failed:\n\n{e}"
            )

            st.stop()


    # ======================================================
    # HANDLE RESPONSE
    # ======================================================

    if response.status_code != 200:

        st.error(
            "❌ Agent execution failed"
        )

        st.code(
            response.text
        )

        st.stop()


    result = response.json()


    # ======================================================
    # SUCCESS HEADER
    # ======================================================

    st.success(
        "✅ Agent completed successfully"
    )


    # ======================================================
    # AGENT PLAN
    # ======================================================

    st.subheader(
        "🧠 Agent Execution Plan"
    )

    plan = result.get(
        "plan",
        [],
    )


    if plan:

        for index, step in enumerate(
            plan,
            start=1,
        ):

            skill = step.get(
                "skill",
                "unknown",
            )

            reason = step.get(
                "reason",
                "",
            )

            with st.container(
                border=True
            ):

                col1, col2 = st.columns(
                    [1, 5]
                )

                with col1:

                    st.markdown(
                        f"### {index}"
                    )

                with col2:

                    st.markdown(
                        f"**{skill_label(skill)}**"
                    )

                    if reason:

                        st.caption(
                            reason
                        )

    else:

        st.info(
            "No execution plan was returned."
        )


    # ======================================================
    # EXECUTION RESULTS
    # ======================================================

    st.subheader(
        "⚙️ Agent Execution"
    )

    execution_results = result.get(
        "execution_results",
        {},
    )


    if execution_results:

        for skill, skill_result in execution_results.items():

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {skill_label(skill)}"
                )

                if isinstance(
                    skill_result,
                    dict,
                ):

                    status = skill_result.get(
                        "status"
                    )

                    validation_status = skill_result.get(
                        "validation"
                    )

                    if status == "success":

                        st.success(
                            "Completed successfully"
                        )

                    elif validation_status == "pass":

                        st.success(
                            "Validation passed"
                        )

                    else:

                        st.json(
                            skill_result
                        )

                    with st.expander(
                        "View details"
                    ):

                        st.json(
                            skill_result
                        )

                else:

                    st.write(
                        skill_result
                    )

    else:

        st.info(
            "No execution results returned."
        )


    # ======================================================
    # RESULTS SUMMARY
    # ======================================================

    st.subheader(
        "📊 Results"
    )

    artifact_path = result.get(
        "artifact"
    )

    validation = result.get(
        "validation",
        {},
    )

    commit = result.get(
        "commit",
        "Not committed",
    )

    security_policy = result.get(
        "security_policy",
        "Not generated",
    )


    col1, col2, col3 = st.columns(
        3
    )


    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    with col1:

        if validation.get(
            "status"
        ) == "pass":

            st.success(
                "🛡 Validation Passed"
            )

        else:

            st.error(
                "❌ Validation Failed"
            )


    # ------------------------------------------------------
    # Git
    # ------------------------------------------------------

    with col2:

        if commit and commit not in [
            "Not committed",
            "pending",
        ]:

            st.success(
                f"🔗 Git Commit\n\n`{commit}`"
            )

        else:

            st.info(
                "🔗 Not committed"
            )


    # ------------------------------------------------------
    # Artifact
    # ------------------------------------------------------

    with col3:

        if artifact_path:

            st.success(
                "📦 Artifact Generated"
            )

        else:

            st.error(
                "❌ No artifact"
            )


    # ======================================================
    # VALIDATION DETAILS
    # ======================================================

    st.subheader(
        "🛡 Validation Details"
    )

    st.json(
        validation
    )


    # ======================================================
    # GENERATED ARTIFACT
    # ======================================================

    if artifact_path:

        st.subheader(
            "📄 Generated Artifact"
        )

        st.code(
            artifact_path
        )


        # --------------------------------------------------
        # Retrieve generated file
        # --------------------------------------------------

        artifact_content = None

        if not artifact_path.endswith(
            ".zip"
        ):

            artifact_content = get_artifact_content(
                artifact_path
            )


        # --------------------------------------------------
        # Display code
        # --------------------------------------------------

        if artifact_content:

            extension = Path(
                artifact_path
            ).suffix.lower()


            language_map = {

                ".py": "python",

                ".sql": "sql",

                ".yaml": "yaml",

                ".yml": "yaml",

                ".md": "markdown",

                ".json": "json",

                ".tf": "hcl",

            }


            st.subheader(
                "💻 Generated Code"
            )

            st.code(
                artifact_content,
                language=language_map.get(
                    extension,
                    "text",
                ),
            )


            # ------------------------------------------------
            # Download button
            # ------------------------------------------------

            st.download_button(
                label="⬇️ Download Artifact",

                data=artifact_content,

                file_name=Path(
                    artifact_path
                ).name,

                mime="text/plain",

                use_container_width=True,
            )


        elif artifact_path.endswith(
            ".zip"
        ):

            st.subheader(
                "📦 Complete Pipeline Package"
            )

            download_url = (
                f"{API_URL}/download"
                f"?path={artifact_path}"
            )

            st.link_button(
                "⬇️ Download Complete Pipeline",
                download_url,
                use_container_width=True,
            )


    # ======================================================
    # SECURITY POLICY
    # ======================================================

    if security_policy not in [
        None,
        "",
        "Not generated",
    ]:

        st.subheader(
            "🔐 Security Policy"
        )

        st.code(
            security_policy,
            language="text",
        )


    # ======================================================
    # FINAL STATUS
    # ======================================================

    st.divider()

    st.success(
        "🎉 Agent workflow completed."
    )