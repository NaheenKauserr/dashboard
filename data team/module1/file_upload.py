import streamlit as st
import pandas as pd
import time

# ─── CUSTOM CSS ──────────────────────────────────────────────
def apply_styles():
    st.markdown("""
        <style>
        /* Main background */
        .stApp {
            background-color: #F0F4FA;
        }

        /* Title */
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1A73E8;
            text-align: center;
            margin-bottom: 0.2rem;
        }

        /* Subtitle */
        .sub-title {
            font-size: 1rem;
            color: #555555;
            text-align: center;
            margin-bottom: 2rem;
        }

        /* Upload box */
        .upload-box {
            background-color: #FFFFFF;
            border: 2px dashed #1A73E8;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }

        /* Metric cards */
        .metric-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #1A73E8;
        }

        .metric-label {
            font-size: 0.85rem;
            color: #888888;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1A73E8;
        }

        /* Success banner */
        .success-banner {
            background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
            border-left: 5px solid #34A853;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            font-size: 1rem;
            color: #1B5E20;
            font-weight: 600;
            margin-bottom: 1.5rem;
            animation: fadeIn 0.8s ease-in-out;
        }

        /* Fade-in animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* Section header */
        .section-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1A73E8;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 2px solid #E0EAFF;
            padding-bottom: 0.3rem;
        }

        /* Divider */
        hr {
            border: none;
            border-top: 1px solid #E0EAFF;
            margin: 1.5rem 0;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# ─── CONSTANTS ───────────────────────────────────────────────
SUPPORTED_FORMATS = ["csv", "xlsx", "xls", "json"]
MAX_FILE_SIZE_MB = 200

# ─── VALIDATION ──────────────────────────────────────────────
def validate_file(file):
    ext = file.name.split(".")[-1].lower()
    if ext not in SUPPORTED_FORMATS:
        return False, f"Unsupported format '.{ext}'. Please upload CSV, Excel, or JSON."
    file_size_mb = file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f} MB) exceeds the 200MB limit."
    return True, "Valid"

# ─── CONVERSION ──────────────────────────────────────────────
def convert_to_dataframe(file):
    ext = file.name.split(".")[-1].lower()
    try:
        if ext == "csv":
            df = pd.read_csv(file)
        elif ext in ["xlsx", "xls"]:
            df = pd.read_excel(file, engine="openpyxl")
        elif ext == "json":
            df = pd.read_json(file)
        if df.empty:
            st.error("❌ The uploaded file is empty.")
            return None
        return df
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        return None

# ─── MAIN ────────────────────────────────────────────────────
def file_upload_section():
    apply_styles()

    # Header
    st.markdown('<div class="main-title">📂 Genesis – Data Upload</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Upload your dataset to begin analysis · CSV · Excel · JSON · Max 200MB</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Upload Box
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Drag and drop your file here or click to browse",
        type=SUPPORTED_FORMATS,
        help="Supported: CSV, Excel (.xlsx, .xls), JSON — Max 200MB",
        key="main_uploader"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:

        # Validation
        is_valid, message = validate_file(uploaded_file)
        if not is_valid:
            st.error(f"❌ {message}")
            return None

        # Progress bar animation
        progress = st.progress(0, text="Processing your file...")
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1, text=f"Loading... {i+1}%")
        progress.empty()

        # Convert
        df = convert_to_dataframe(uploaded_file)

        if df is not None:
            st.session_state["uploaded_df"] = df
            st.session_state["file_name"] = uploaded_file.name

            # Animated success banner
            st.markdown(f"""
                <div class="success-banner">
                    ✅ File uploaded successfully — <b>{uploaded_file.name}</b> is ready for analysis!
                </div>
            """, unsafe_allow_html=True)

            # Metrics
            st.markdown('<div class="section-header">📊 Dataset Summary</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">📄 File Name</div>
                        <div class="metric-value" style="font-size:1rem;">{uploaded_file.name}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">🔢 Total Rows</div>
                        <div class="metric-value">{df.shape[0]}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">📊 Total Columns</div>
                        <div class="metric-value">{df.shape[1]}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Data Preview
            st.markdown('<div class="section-header">🔍 Data Preview (First 5 Rows)</div>', unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)

            return df

    return None

