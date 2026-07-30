import streamlit as st
import requests

# ==========================================
# FastAPI Backend
# ==========================================

API_URL = "http://127.0.0.1:8000"


# ==========================================
# Helper Functions
# ==========================================

def get_table_metadata(table_name: str):
    """
    Fetch metadata for a table from FastAPI.
    """

    try:
        response = requests.get(
            f"{API_URL}/schema/{table_name}",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return None

    except Exception:
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
# Metadata Preview
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
# Generate
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
                    "task": task
                },
                timeout=120
            )

            if response.status_code == 200:

                result = response.json()

                st.success("✅ Pipeline generated successfully!")

                st.divider()

                # -------------------------
                # Artifact
                # -------------------------

                st.subheader("📄 Generated Artifact")

                st.code(
                    result["artifact"],
                    language="text"
                )

                # -------------------------
                # Security Policy
                # -------------------------

                st.subheader("🔒 Security Policy")

                st.code(
                    result["security_policy"],
                    language="text"
                )

                # -------------------------
                # Validation
                # -------------------------

                st.subheader("🛡 Validation")

                st.json(result["validation"])

                # -------------------------
                # Git Commit
                # -------------------------

                st.subheader("🔗 Git Commit")

                st.code(result["commit"])

            else:

                st.error(response.text)

        except Exception as e:

            st.error(str(e))