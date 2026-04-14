import streamlit as st
import os
import pandas as pd
import json
from dotenv import load_dotenv

# Set wide layout FIRST
st.set_page_config(
    page_title="Genesis AI - Data Analysis Platform", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Load CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load ENV
load_dotenv()

import data_ingestion
import data_cleaning
import data_analysis
import kpi_generator
import visualization
import ml_engine
import forecasting
import insights
import chatbot
import dashboard

# --- USER PERSISTENCE LOGIC ---
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                return json.load(f)
        except:
            return {"admin": "admin"}
    return {"admin": "admin"}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def initialize_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    st.session_state.registered_users = load_users()
    
    if 'current_file_id' not in st.session_state:
        st.session_state.current_file_id = None
        st.session_state.df = None
        st.session_state.cleaned_df = None
        st.session_state.kpis = None
        st.session_state.charts = None
        st.session_state.ml_results = None
        st.session_state.forecast = None
        st.session_state.insights = None
        st.session_state.column_types = None
        st.session_state.stats = None
        st.session_state.correlations = None
    
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    if 'filters' not in st.session_state:
        st.session_state.filters = {}

def apply_adaptive_filters(df):
    if df is None or df.empty: return df
    filtered_df = df.copy()
    for col, filter_data in st.session_state.filters.items():
        if not isinstance(filter_data, tuple): continue
        f_type, val = filter_data
        if col in filtered_df.columns:
            if f_type == "exact" and val != "All":
                filtered_df = filtered_df[filtered_df[col].astype(str) == str(val)]
            elif f_type == "slider":
                low, high = val
                filtered_df = filtered_df[(filtered_df[col] >= low) & (filtered_df[col] <= high)]
            elif f_type == "date_range" and len(val) == 2:
                start, end = val
                filtered_df = filtered_df[(filtered_df[col].dt.date >= start) & (filtered_df[col].dt.date <= end)]
    return filtered_df

def login_page():
    if not st.session_state.logged_in:
        auth_token = st.query_params.get("token")
        if auth_token and auth_token in st.session_state.registered_users:
            st.session_state.logged_in = True
            st.session_state.user = auth_token
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #a78bfa;'>Genesis AI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: rgba(255,255,255,0.5); margin-bottom: 30px;'>Intelligent Data Analysis Platform</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            tabs = st.tabs(["Login", "Sign Up"])
            
            with tabs[0]:
                st.markdown("### Login Account")
                log_user = st.text_input("Username", key="log_user", placeholder="Enter your username")
                log_pass = st.text_input("Password", type="password", key="log_pass", placeholder="Enter your password")
                remember_me = st.checkbox("Remember Me", value=True)
                submit_log = st.button("Login", use_container_width=True, type="primary")
                
                if submit_log:
                    if log_user in st.session_state.registered_users and st.session_state.registered_users[log_user] == log_pass:
                        st.session_state.logged_in = True
                        st.session_state.user = log_user
                        if remember_me:
                            st.query_params["token"] = log_user
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

            with tabs[1]:
                st.markdown("### Create an Account")
                reg_user = st.text_input("New Username", key="reg_user", placeholder="Choose a username")
                reg_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Choose a password")
                reg_pass_conf = st.text_input("Confirm Password", type="password", key="reg_pass_conf", placeholder="Repeat password")
                submit_reg = st.button("Sign Up", use_container_width=True, type="primary")
                
                if submit_reg:
                    if not reg_user or not reg_pass:
                        st.warning("Please fill in all fields.")
                    elif reg_pass != reg_pass_conf:
                        st.error("Passwords do not match.")
                    elif reg_user in st.session_state.registered_users:
                        st.error("Username already exists.")
                    else:
                        st.session_state.registered_users[reg_user] = reg_pass
                        save_users(st.session_state.registered_users)
                        st.success("Account created successfully!")

def render_sidebar():
    # Sidebar Logo area
    st.sidebar.markdown("""
        <div class="brand">
            <div class="gem"><svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div>
            <div><div class="brand-txt">Genesis AI</div><div class="brand-sub">Data Analysis Platform</div></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.markdown('<div class="nlbl">General</div>', unsafe_allow_html=True)
    if st.sidebar.button("🏠 Dashboard", use_container_width=True, type="primary" if st.session_state.page == "Dashboard" else "secondary"):
        st.session_state.page = "Dashboard"
        st.rerun()
    if st.sidebar.button("ℹ️ About", use_container_width=True, type="primary" if st.session_state.page == "About" else "secondary"):
        st.session_state.page = "About"
        st.rerun()
    if st.sidebar.button("📤 Upload Data", use_container_width=True, type="primary" if st.session_state.page == "Upload" else "secondary"):
        st.session_state.page = "Upload"
        st.rerun()
        
    st.sidebar.markdown('<div class="nlbl">Dashboards</div>', unsafe_allow_html=True)
    pages = [
        ("📊 Analytics", "Analytics"),
        ("👁️ Visualization", "Visualization"),
        ("🔮 Forecasting", "Forecasting"),
        ("🧠 AI & ML", "AI_ML"),
        ("💬 AI Chatbot", "Chatbot_Full"),
        ("👥 Meet Our Team", "Team")
    ]
    for label, pg in pages:
        if st.sidebar.button(label, use_container_width=True, type="primary" if st.session_state.page == pg else "secondary"):
            st.session_state.page = pg
            st.rerun()

    st.sidebar.markdown('<div class="nlbl">Filters</div>', unsafe_allow_html=True)
    if st.session_state.cleaned_df is not None:
        df = st.session_state.cleaned_df
        c_types = st.session_state.column_types
        
        # 1. Date Filter (Range)
        dt_cols = c_types.get('datetime', [])
        if dt_cols:
            d_col = dt_cols[0]
            min_date = df[d_col].min().date()
            max_date = df[d_col].max().date()
            if min_date != max_date:
                st.sidebar.caption(f"📅 Date Range: {d_col}")
                date_range = st.sidebar.date_input("Select Range", [min_date, max_date], key="date_range_filter")
                if isinstance(date_range, list) and len(date_range) == 2:
                    st.session_state.filters[d_col] = ("date_range", date_range)
        
        # 2. Numeric Filters (Sliders)
        num_cols = [c for c in c_types.get('numeric', []) if 'id' not in c.lower() and 'index' not in c.lower()]
        if num_cols:
            n_col = num_cols[0] # Just the primary numeric for now to avoid sidebar clutter
            min_val = float(df[n_col].min())
            max_val = float(df[n_col].max())
            if min_val != max_val:
                st.sidebar.caption(f"🔢 Range: {n_col}")
                st.session_state.filters[n_col] = ("slider", st.sidebar.slider(f"{n_col}", min_val, max_val, (min_val, max_val), key=f"slider_{n_col}"))

        # 3. Categorical Filters (Selectbox)
        cat_cols = [c for c in c_types.get('categorical', []) if df[c].nunique() <= 25]
        for col in cat_cols[:2]: # Top 2 categories
            options = ["All"] + sorted(list(df[col].dropna().unique().astype(str)))
            val = st.sidebar.selectbox(f"📁 {col}", options, key=f"select_{col}")
            st.session_state.filters[col] = ("exact", val)
    else:
        st.sidebar.caption("Upload data to activate filters.")

    st.sidebar.markdown('<div class="nlbl">System</div>', unsafe_allow_html=True)
    if st.sidebar.button("⚙️ Settings", use_container_width=True, type="primary" if st.session_state.page == "Settings" else "secondary"):
        st.session_state.page = "Settings"
        st.rerun()
        
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        if "token" in st.query_params:
            del st.query_params["token"]
        st.rerun()

    # User Card
    st.sidebar.markdown(f"""
        <div class="nav-foot">
            <div class="user-card">
                <div class="avatar">{st.session_state.user[:2].upper() if 'user' in st.session_state else 'AD'}</div>
                <div><div class="uname">{"Admin" if 'user' not in st.session_state else st.session_state.user + " — User"}</div><div class="urole">Genesis Platform</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_topbar(title):
    bc_page = title.split()[0] if " " in title else title
    st.markdown(f"""
        <div class="genesis-topbar">
            <div class="topbar-left">
                <div class="page-title">{title}</div>
                <div class="breadcrumb">Home / <span>{bc_page}</span></div>
            </div>
            <div class="report-btn-div">
                <div style="font-size: 10px; color: var(--text3); margin-bottom: 2px;">Search... 🔍</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    initialize_state()
    local_css("assets/style.css")
    
    if not st.session_state.logged_in:
        login_page()
    else:
        render_sidebar()
        
        # Determine Title
        titles = {
            "Analytics": "Analytics Dashboard",
            "Visualization": "Visualization Dashboard",
            "Forecasting": "Forecasting Dashboard",
            "AI_ML": "AI & ML Models",
            "Chatbot_Full": "AI Chatbot Assistant",
            "Team": "Meet Our Team",
            "Settings": "System Settings",
            "About": "About Genesis AI",
            "Upload": "Data Ingestion"
        }
        current_title = titles.get(st.session_state.page, "Genesis AI")
        
        # Topbar
        render_topbar(current_title)
        
        # Pre-check data
        if st.session_state.cleaned_df is None and st.session_state.page not in ["About", "Upload", "Team", "Settings"]:
            st.session_state.page = "Upload"
            st.rerun()

        # Routing
        if st.session_state.page == "Dashboard":
            dashboard.render_main_dashboard()
            
        elif st.session_state.page == "Upload":
            def update_loader(placeholder, status_text):
                placeholder.markdown(f"""
                    <div class="loader-wrapper">
                        <div class="loader-container">
                            <div class="loader-track"></div>
                            <div class="loader-dot-outer"></div>
                        </div>
                        <div class="loader-text">Loading</div>
                        <div class="loader-step">{status_text}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Upload CSV or Excel dataset", type=['csv', 'xlsx', 'xls'])
            if uploaded_file:
                # Custom Premium Loader
                loading_placeholder = st.empty()
                
                try:
                    update_loader(loading_placeholder, "Ingesting Data Module...")
                    df = data_ingestion.load_file(uploaded_file)
                    st.session_state.df = df
                    
                    if df is not None:
                        update_loader(loading_placeholder, "Cleaning & Normalizing...")
                        cleaned_df = data_cleaning.clean_data(df)
                        st.session_state.cleaned_df = cleaned_df
                        
                        update_loader(loading_placeholder, "Mapping Column Semantics...")
                        c_types = data_analysis.get_column_types(cleaned_df)
                        st.session_state.column_types = c_types
                        
                        update_loader(loading_placeholder, "Computing Statistical Profiles...")
                        st.session_state.stats = data_analysis.compute_stats(cleaned_df)
                        st.session_state.correlations = data_analysis.find_correlations(cleaned_df)
                        
                        update_loader(loading_placeholder, "Synthesizing Smart KPIs...")
                        st.session_state.kpis = kpi_generator.generate_kpis(cleaned_df, c_types)
                        
                        update_loader(loading_placeholder, "Generating Visual Intelligence...")
                        st.session_state.charts = visualization.auto_charts(cleaned_df, c_types)
                        
                        update_loader(loading_placeholder, "Training Auto-ML Engine...")
                        st.session_state.ml_results = ml_engine.auto_ml(cleaned_df, c_types)
                        
                        update_loader(loading_placeholder, "Running Forecasting Models...")
                        st.session_state.forecast = forecasting.auto_forecast(cleaned_df, c_types)
                        
                        update_loader(loading_placeholder, "Extracting AI Insights...")
                        st.session_state.insights = insights.generate_insights(cleaned_df, st.session_state.stats, st.session_state.correlations)
                        st.session_state.current_file_id = f"{uploaded_file.name}"
                        
                        update_loader(loading_placeholder, "Finalizing Dashboard...")
                        import time
                        time.sleep(1) 
                        
                        st.session_state.page = "Analytics"
                        st.rerun()
                except Exception as e:
                    loading_placeholder.empty()
                    st.error(f"Error: {e}")
            st.markdown("""
                <div style="border: 2px dashed var(--glass-border); border-radius: 14px; padding: 40px; text-align: center;">
                    <div style="font-size: 40px;">📂</div>
                    <div style="color: var(--text1); font-weight: 600; margin-top: 10px;">Supporting CSV and Excel files up to 200MB</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.page == "About":
            dashboard.render_about_page()
            
        elif st.session_state.page == "Team":
            dashboard.render_team_page()
            
        elif st.session_state.page == "Settings":
            dashboard.render_settings_page()

        elif st.session_state.page == "Analytics":
            filtered_df = apply_adaptive_filters(st.session_state.cleaned_df)
            
            # Recalculate if filtered
            if len(filtered_df) < len(st.session_state.cleaned_df):
                display_kpis = kpi_generator.generate_kpis(filtered_df, st.session_state.column_types)
                display_charts = visualization.auto_charts(filtered_df, st.session_state.column_types)
            else:
                display_kpis = st.session_state.kpis
                display_charts = st.session_state.charts

            def chat_cb(query):
                return chatbot.chat_response(query, filtered_df, st.session_state.column_types)

            dashboard.render_analytics_dashboard(
                st.session_state.df,
                filtered_df,
                display_kpis,
                display_charts,
                st.session_state.ml_results,
                st.session_state.insights,
                chat_cb
            )

        elif st.session_state.page == "Visualization":
            filtered_df = apply_adaptive_filters(st.session_state.cleaned_df)
            dashboard.render_visualization_dashboard(filtered_df, st.session_state.column_types)

        elif st.session_state.page == "Forecasting":
            dashboard.render_forecasting_dashboard(st.session_state.cleaned_df, st.session_state.forecast)

        elif st.session_state.page == "AI_ML":
            dashboard.render_ml_page(st.session_state.cleaned_df, st.session_state.ml_results)

        elif st.session_state.page == "Chatbot_Full":
            filtered_df = apply_adaptive_filters(st.session_state.cleaned_df)
            def chat_cb(query):
                return chatbot.chat_response(query, filtered_df, st.session_state.column_types)
            dashboard.render_full_chatbot(chat_cb)

        # Always render floating chat at the very end
        if st.session_state.logged_in and st.session_state.cleaned_df is not None:
            def float_chat_cb(query):
                # Using cleaned_df for context in floating chat
                return chatbot.chat_response(query, st.session_state.cleaned_df, st.session_state.column_types)
            dashboard.render_floating_chat(float_chat_cb)

if __name__ == "__main__":
    main()
