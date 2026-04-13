import streamlit as st
from module1.file_upload import file_upload_section
from module1.dataset_profiling import dataset_profiling_section
from module1.data_quality import data_quality_section

st.set_page_config(page_title="AI Chatbot - Data Analysis", page_icon="🤖", layout="wide")

st.sidebar.title("🤖 AI Chatbot System")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate to:",
    ["📁 File Upload", "📊 Dataset Profiling", "🔍 Data Quality Assessment"]
)

if page == "📁 File Upload":
    file_upload_section()

elif page == "📊 Dataset Profiling":
    if "uploaded_df" not in st.session_state or st.session_state["uploaded_df"] is None:
        st.warning("⚠️ Please upload a dataset first using the File Upload page.")
    else:
        dataset_profiling_section(st.session_state["uploaded_df"])

elif page == "🔍 Data Quality Assessment":
    if "uploaded_df" not in st.session_state or st.session_state["uploaded_df"] is None:
        st.warning("⚠️ Please upload a dataset first using the File Upload page.")
    else:
        data_quality_section(st.session_state["uploaded_df"])
