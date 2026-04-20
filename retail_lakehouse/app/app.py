import streamlit as st
from pathlib import Path

from retail_lakehouse.core.agent import RetailAgent
from retail_lakehouse.cbs_to_lakehouse import load_from_cbs_to_lakehouse

_DB_PATH = Path(__file__).parents[1] / "data/duckdb/lakehouse.duckdb"

st.title("🇳🇱 Retail Lakehouse Agent")

if not _DB_PATH.exists():
    with st.status("First time loading app data", expanded=True) as status:
        load_from_cbs_to_lakehouse()
        status.update(label="APP is Ready! Please Ask me!", state="complete", expanded=False)

if "agent" not in st.session_state:
    st.session_state.agent = RetailAgent()

user_input = st.text_input(
    "Ask your data a question:",
    placeholder="e.g. Which industry grew most last month?",
)

if user_input:
    with st.spinner("Agent is thinking"):
        result = st.session_state.agent.query(user_input)

    if not result["success"]:
        st.error(f"SQL Error: {result['error']}")
        st.code(result["sql"], language="sql")
    else:
        st.success(f"Query successful in {result['attempts']} attempt(s)!")
        st.subheader("Results")
        st.dataframe(result["data"])
        with st.expander("Show Generated SQL"):
            st.code(result["sql"], language="sql")
