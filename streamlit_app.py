import streamlit as st
import requests
from pathlib import Path

API_URL = "https://ai-data-pipeline-generator.onrender.com"

# ==========================================
# Helper Functions
# ==========================================

def get_table_metadata(table_name):
    url = f"{API_URL}/schema/{table_name}"

    try:
        response = requests.get(url, timeout=(10, 60))
        response.raise_for_status()
        return response.json()

    except Exception as e:
        st.error(f"Unable to retrieve metadata: {e}")
        return None

# ==========================================
# Streamlit Configuration
# ==========================================

st.set_page_config(
    page_title="AI Data Pipeline Generator",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Data Pipeline Generator")

st.markdown(
    """
Generate Airflow DAGs, dbt models, SQL, YAML configs,
and other pipeline artifacts using **DataHub metadata + AI**.
"""
)

st.divider()

# ==========================================
# Backend Health
# ==========================================

try:

    health = requests.get(
        f"{API_URL}/health",
        timeout=5
    )

    if health.status_code == 200:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Not Ready")

except Exception:
    st.error("❌ Cannot connect to FastAPI backend")

st.divider()

# ==========================================
# Metadata Explorer
# ==========================================

st.header("📊 Metadata Explorer")

table_name = st.text_input(
    "Table Name",
    value="fct_users_created",
    help="Enter the DataHub table you want to inspect."
)

preview = st.button(
    "🔍 Preview Metadata",
    use_container_width=True
)

if preview:

    with st.spinner("Loading metadata..."):

        metadata = get_table_metadata(table_name)

        if metadata:

            st.success("Metadata loaded successfully.")

            tab1, tab2, tab3, tab4 = st.tabs(
                [
                    "📋 Columns",
                    "👤 Owners",
                    "🏷 Tags",
                    "🔗 Lineage"
                ]
            )

            with tab1:
                st.json(metadata["columns"])

            with tab2:
                st.write(metadata["owners"])

            with tab3:
                st.write(metadata["tags"])

            with tab4:
                st.write(metadata["lineage"])

        else:

            st.error(
                "Unable to retrieve metadata. "
                "Check that DataHub is running."
            )

st.divider()

# ==========================================
# Pipeline Generator
# ==========================================

st.header("🤖 AI Pipeline Generator")

artifact_type = st.selectbox(
    "Artifact Type",
    [
        "Generate Complete Pipeline",
        "airflow",
        "sql",
        "dbt",
        "yaml",
        "readme"
    ]
)

task = st.text_area(
    "Describe what you want to generate",
    height=180,
    placeholder=(
        "Example:\n\n"
        "Generate an Airflow DAG for the "
        "fct_users_created table"
    )
)

generate = st.button(
    "🚀 Generate Pipeline",
    type="primary",
    use_container_width=True
)

# ==========================================
# Generate Pipeline
# ==========================================

if generate:

    if not task.strip():
        st.warning("Please enter a task.")
        st.stop()

    with st.spinner("Generating pipeline..."):

        try:

            response = requests.post(
                f"{API_URL}/generate",
                json={
                    "task": task,
                    "artifact_type": (
                        "all"
                        if artifact_type == "Generate Complete Pipeline"
                        else artifact_type
                    )
                },
                timeout=120
            )

            if response.status_code == 200:

                result = response.json()

                st.success("✅ Pipeline generated successfully!")

                st.divider()

                # ==========================================
                # Generated Artifact
                # ==========================================

                artifact_path = result["artifact"]

                st.subheader("📄 Generated Artifact")
                st.code(artifact_path)

                # ==========================================
                # Display Generated Artifact
                # ==========================================

                if artifact_path.endswith(".zip"):

                    st.subheader("📦 Complete Pipeline Package")

                    download_url = (
                        f"{API_URL}/download?path={artifact_path}"
                    )

                    st.link_button(
                        "⬇ Download Complete Pipeline",
                        download_url
                    )

                else:

                    download_url = f"{API_URL}/download?path={artifact_path}"

                    try:

                        response = requests.get(download_url, timeout=(10, 60))
                        response.raise_for_status()

                        generated_code = response.text

                        st.subheader("💻 Generated Code")

                        language_map = {
                            "airflow": "python",
                            "sql": "sql",
                            "dbt": "sql",
                            "yaml": "yaml",
                            "readme": "markdown"
                        }

                        st.code(
                            generated_code,
                            language=language_map.get(
                                artifact_type,
                                "text"
                            )
                        )

                        st.download_button(
                            label="⬇ Download Artifact",
                            data=generated_code,
                            file_name=Path(artifact_path).name,
                            mime="text/plain"
                        )

                    except Exception as e:

                        st.warning(
                            f"Could not download generated artifact:\n\n{e}"
                        )

                # ==========================================
                # Security Policy
                # ==========================================

                st.subheader("🔒 Security Policy")

                st.code(
                    result["security_policy"],
                    language="json"
                )

                # ==========================================
                # Validation
                # ==========================================

                st.subheader("🛡 Validation")

                validation = result["validation"]

                if validation["status"] == "pass":

                    st.success("✅ Validation Passed")

                else:

                    st.error("❌ Validation Failed")

                st.json(validation)

                # ==========================================
                # Git Commit
                # ==========================================

                st.subheader("🔗 Git Commit")

                st.code(result["commit"])

            else:

                st.error(response.text)

        except Exception as e:

            st.error(f"Error:\n\n{e}")
