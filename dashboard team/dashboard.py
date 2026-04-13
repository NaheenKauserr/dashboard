"""
MODULE 4 — Visualization & Dashboard System
Genesis AI Chatbot — Company Data Analysis Platform

Advanced Features:
  1. Advanced Data Visualization Layer
  2. Interactive Dashboard Builder
  3. Real-Time Dashboard Refresh
  4. Automated Report Generator (with AI narrative)

Integrates outputs from:
  - Module 1 (data_quality, dataset_profiling, file_upload)  → session_state["uploaded_df"]
  - Module 2 (nlp_processor, data_processor, response_generator) → generate_suggestions, process_query, execute_query
  - Module 3 (RetailDataAnalyzer, SalesPredictiveEngine, generate_ai_insights, generate_smart_recommendations)

Author   : NK (Team Lead) + Yusuf, Naheen
Module   : 4 — Dashboard & Visualization
Phase    : 2 (Advanced Features)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import time
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# SAFE IMPORTS FROM OTHER MODULES
# (wrapped so dashboard still runs even if a module is missing)
# ─────────────────────────────────────────────────────────────

def _try_import_module2():
    try:
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), "nlp"))
        from nlp_processor import process_query
        from data_processor import execute_query
        from response_generator import generate_response
        # generate_suggestions lives in Module 2's app.py — we replicate
        # the logic here so we don't depend on that app's entry point
        return process_query, execute_query, generate_response
    except Exception:
        return None, None, None

def _try_import_module3():
    try:
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), "analytics"))
        from analysis import RetailDataAnalyzer
        from insights import generate_ai_insights
        from my_recommendations import generate_smart_recommendations
        from predictive_engine import SalesPredictiveEngine
        return RetailDataAnalyzer, generate_ai_insights, generate_smart_recommendations, SalesPredictiveEngine
    except Exception:
        return None, None, None, None

process_query, execute_query, generate_response = _try_import_module2()
RetailDataAnalyzer, generate_ai_insights, generate_smart_recommendations, SalesPredictiveEngine = _try_import_module3()

# ─────────────────────────────────────────────────────────────
# THEME & CSS
# ─────────────────────────────────────────────────────────────

THEME = {
    "primary"    : "#7C3AED",
    "secondary"  : "#A855F7",
    "accent"     : "#C084FC",
    "bg_dark"    : "#0E1117",
    "bg_card"    : "#1A1D24",
    "bg_sidebar" : "#12151B",
    "text_main"  : "#E2E8F0",
    "text_muted" : "#94A3B8",
    "success"    : "#22C55E",
    "warning"    : "#F59E0B",
    "danger"     : "#EF4444",
    "info"       : "#3B82F6",
}

def apply_dashboard_css():
    st.markdown(f"""
    <style>
    /* ── Global ─────────────────────────────── */
    .stApp {{ background-color: {THEME['bg_dark']} !important; }}
    p, div, span, label {{ color: {THEME['text_main']}; }}
    h1, h2, h3 {{ color: {THEME['secondary']} !important; }}

    /* ── Sidebar ─────────────────────────────── */
    [data-testid="stSidebar"] {{ background-color: {THEME['bg_sidebar']} !important; }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{ color: {THEME['accent']} !important; }}
    [data-testid="stMetricValue"] {{ color: {THEME['secondary']} !important; }}

    /* ── KPI Card ────────────────────────────── */
    .kpi-card {{
        background: linear-gradient(135deg, {THEME['bg_card']}, #1e2130);
        border: 1px solid {THEME['primary']}44;
        border-left: 4px solid {THEME['primary']};
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 20px rgba(124,58,237,0.15);
        transition: transform 0.2s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 28px rgba(124,58,237,0.25); }}
    .kpi-label {{ font-size: 0.78rem; color: {THEME['text_muted']}; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.35rem; }}
    .kpi-value {{ font-size: 1.9rem; font-weight: 800; color: {THEME['secondary']}; line-height: 1; }}
    .kpi-delta-pos {{ font-size: 0.82rem; color: {THEME['success']}; margin-top: 0.3rem; }}
    .kpi-delta-neg {{ font-size: 0.82rem; color: {THEME['danger']}; margin-top: 0.3rem; }}
    .kpi-delta-neu {{ font-size: 0.82rem; color: {THEME['text_muted']}; margin-top: 0.3rem; }}

    /* ── Insight Banner ──────────────────────── */
    .insight-banner {{
        background: linear-gradient(135deg, #1e1040, #2d1b69);
        border: 1px solid {THEME['primary']}66;
        border-left: 5px solid {THEME['secondary']};
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin: 0.8rem 0 1.2rem 0;
        animation: slideIn 0.5s ease;
    }}
    @keyframes slideIn {{ from {{ opacity:0; transform:translateY(-8px); }} to {{ opacity:1; transform:translateY(0); }} }}
    .insight-title {{ font-size: 0.85rem; color: {THEME['accent']}; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem; }}
    .insight-item {{ font-size: 0.92rem; color: {THEME['text_main']}; margin: 0.25rem 0; }}

    /* ── Section Headers ─────────────────────── */
    .section-title {{
        font-size: 1.05rem; font-weight: 700;
        color: {THEME['accent']}; letter-spacing: 0.04em;
        border-bottom: 1px solid {THEME['primary']}44;
        padding-bottom: 0.4rem; margin: 1.2rem 0 0.8rem 0;
    }}

    /* ── Suggest Button ──────────────────────── */
    .stButton > button {{
        background: linear-gradient(135deg, {THEME['primary']}, {THEME['secondary']}) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important; padding: 0.35rem 0.8rem !important;
        font-size: 0.82rem !important; transition: opacity 0.2s;
    }}
    .stButton > button:hover {{ opacity: 0.85; }}

    /* ── Tabs ────────────────────────────────── */
    [data-testid="stTab"] {{ color: {THEME['text_muted']} !important; }}
    [aria-selected="true"] {{ color: {THEME['secondary']} !important; border-bottom: 2px solid {THEME['secondary']} !important; }}

    /* ── Expander ────────────────────────────── */
    [data-testid="stExpander"] {{
        background-color: {THEME['bg_card']} !important;
        border: 1px solid {THEME['primary']}33 !important;
        border-radius: 10px !important;
    }}

    /* ── Refresh Indicator ───────────────────── */
    .refresh-dot {{
        display: inline-block; width: 8px; height: 8px;
        background: {THEME['success']}; border-radius: 50%;
        animation: pulse 1.5s ease-in-out infinite;
        margin-right: 6px;
    }}
    @keyframes pulse {{
        0%,100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.4; transform: scale(0.8); }}
    }}

    /* ── Report card ─────────────────────────── */
    .report-box {{
        background: {THEME['bg_card']}; border: 1px solid {THEME['primary']}33;
        border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
    }}

    /* ── Hide Streamlit chrome ───────────────── */
    #MainMenu {{ visibility: hidden; }}
    footer    {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "uploaded_df"        : None,
        "file_name"          : "",
        "chat_history"       : [],
        "queued_query"       : None,
        "dashboard_layouts"  : {},          # saved custom layouts
        "active_layout"      : "default",
        "auto_refresh"       : False,
        "refresh_interval"   : 30,
        "last_refresh"       : time.time(),
        "chat_input_trigger" : None,        # chat→dashboard sync
        "kpis_cache"         : None,
        "insights_cache"     : None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
# HELPER: COMPUTE KPIs FROM ANY DATAFRAME
# ─────────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Compute KPIs dynamically from whatever dataset is uploaded.
    Tries to detect Sales / Profit / Revenue / Quantity columns.
    Falls back gracefully for non-retail datasets.
    """
    kpis = {}
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    def find_col(*candidates):
        for c in candidates:
            for col in df.columns:
                if col.lower() == c.lower():
                    return col
        return None

    sales_col   = find_col("Sales", "Revenue", "Amount", "Total")
    profit_col  = find_col("Profit", "Net Profit", "Net Income")
    qty_col     = find_col("Quantity", "Qty", "Units", "Volume")
    order_col   = find_col("Order ID", "OrderID", "Transaction ID", "ID")
    cust_col    = find_col("Customer ID", "CustomerID", "Customer", "Client ID")

    kpis["total_rows"]   = len(df)
    kpis["total_cols"]   = len(df.columns)

    if sales_col:
        kpis["total_sales"]     = df[sales_col].sum()
        kpis["avg_sale"]        = df[sales_col].mean()
        kpis["max_sale"]        = df[sales_col].max()
        kpis["sales_col"]       = sales_col
    else:
        # Use first numeric col as proxy
        if numeric_cols:
            kpis["total_sales"] = df[numeric_cols[0]].sum()
            kpis["avg_sale"]    = df[numeric_cols[0]].mean()
            kpis["max_sale"]    = df[numeric_cols[0]].max()
            kpis["sales_col"]   = numeric_cols[0]
        else:
            kpis["total_sales"] = kpis["avg_sale"] = kpis["max_sale"] = 0
            kpis["sales_col"]   = None

    if profit_col:
        kpis["total_profit"] = df[profit_col].sum()
        kpis["profit_margin"] = (kpis["total_profit"] / kpis["total_sales"] * 100) if kpis["total_sales"] else 0
        kpis["profit_col"]   = profit_col
    else:
        kpis["total_profit"] = kpis["profit_margin"] = 0
        kpis["profit_col"]   = None

    if qty_col:
        kpis["total_qty"] = int(df[qty_col].sum())
    else:
        kpis["total_qty"] = 0

    kpis["total_orders"]    = df[order_col].nunique() if order_col else len(df)
    kpis["unique_customers"] = df[cust_col].nunique() if cust_col else 0
    kpis["avg_order_value"] = kpis["total_sales"] / kpis["total_orders"] if kpis["total_orders"] else 0

    # Discount
    disc_col = find_col("Discount")
    kpis["avg_discount"] = df[disc_col].mean() if disc_col else 0

    # Shipping delay
    ship_col = find_col("shipping_delay_days", "Shipping Delay", "Delay")
    kpis["avg_shipping_delay"] = df[ship_col].mean() if ship_col else 0

    return kpis


# ─────────────────────────────────────────────────────────────
# HELPER: RULE-BASED INSIGHTS (fallback when Module 3 absent)
# ─────────────────────────────────────────────────────────────

def local_insights(kpis: dict) -> list:
    insights = []
    if kpis.get("total_profit", 0) < 0:
        insights.append("⚠️ The business is currently running at a loss.")
    elif kpis.get("total_profit", 0) > 0:
        insights.append("✅ The business is profitable overall.")
    if kpis.get("avg_discount", 0) > 0.2:
        insights.append("⚠️ High discounting (>20%) is compressing profit margins.")
    elif kpis.get("avg_discount", 0) > 0.1:
        insights.append("📉 Moderate discounting detected — monitor impact on margins.")
    if kpis.get("avg_shipping_delay", 0) > 5:
        insights.append("🚚 Shipping delays exceed 5 days — logistics optimization needed.")
    if kpis.get("unique_customers", 0) > 500:
        insights.append("📈 Strong and diverse customer base contributing to revenue.")
    if kpis.get("avg_order_value", 0) > 400:
        insights.append("💰 High average order value indicates strong sales performance.")
    if not insights:
        insights.append("📊 Dataset loaded successfully. Run analysis for deeper insights.")
    return insights

def local_recommendations(kpis: dict) -> list:
    recs = []
    if kpis.get("avg_discount", 0) > 0.2:
        recs.append("Reduce discount levels to improve profitability.")
    if kpis.get("avg_shipping_delay", 0) > 5:
        recs.append("Optimise logistics to reduce shipping delays below 5 days.")
    if kpis.get("total_profit", 0) > 0:
        recs.append("Scale high-performing product categories to boost revenue.")
    if kpis.get("avg_order_value", 0) > 400:
        recs.append("Introduce premium product bundles to increase revenue further.")
    if kpis.get("unique_customers", 0) > 500:
        recs.append("Leverage customer loyalty programmes to improve retention.")
    return recs


# ─────────────────────────────────────────────────────────────
# HELPER: SMART QUERY SUGGESTIONS (replicated from Module 2)
# ─────────────────────────────────────────────────────────────

def generate_suggestions(df: pd.DataFrame, chat_history=None) -> list:
    suggestions = []
    numeric_cols     = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    time_cols = [c for c in df.columns if any(k in c.lower() for k in ["year","date","time","month"])]

    metrics    = [c for c in numeric_cols     if c not in time_cols][:3]
    categories = [c for c in categorical_cols if c not in time_cols][:3]

    if not metrics:
        return ["Show all data points"]

    primary = metrics[0]

    if chat_history:
        for msg in reversed(chat_history):
            if msg.get("role") == "assistant" and msg.get("parsed_query"):
                last = msg["parsed_query"]
                intent = last.get("intent")
                metric = last.get("metric") or primary
                if intent == "trend":
                    suggestions += [f"Compare {metric.lower()} across categories",
                                    f"Which category has the highest {metric.lower()}?"]
                elif intent == "comparison":
                    suggestions += [f"Show historical trend for {metric.lower()}"]
                    if len(metrics) > 1:
                        suggestions.append(f"How does {metric.lower()} compare to {metrics[1].lower()}?")
                elif intent in ["profiling", "quality", "summary"]:
                    suggestions.append(f"Show {metric.lower()} trend over time")
                break

    if len(suggestions) < 3:
        if f"What is the total {primary.lower()}?" not in suggestions:
            suggestions.append(f"What is the total {primary.lower()}?")
        if categories:
            suggestions.append(f"Compare {primary.lower()} across {categories[0].lower()}s")
        if time_cols:
            suggestions.append(f"Show {primary.lower()} trend over {time_cols[0].lower()}")

    return list(dict.fromkeys(suggestions))[:5]


# ─────────────────────────────────────────────────────────────
# FEATURE 1 — ADVANCED DATA VISUALIZATION LAYER
# ─────────────────────────────────────────────────────────────

def render_visualization_layer(df: pd.DataFrame, kpis: dict):
    st.markdown('<div class="section-title">📊 Advanced Data Visualization</div>', unsafe_allow_html=True)

    numeric_cols     = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    time_cols        = [c for c in df.columns if any(k in c.lower() for k in ["year","date","month","time"])]

    if not numeric_cols:
        st.info("No numeric columns found for visualization.")
        return

    # ── Chart Recommendation Engine
    st.markdown("#### 🧠 Chart Recommendation Engine")
    rec_col = kpis.get("sales_col") or numeric_cols[0]

    rec_tabs = st.tabs(["📈 Trend", "📊 Distribution", "🗂️ Category Breakdown", "🔥 Correlation", "🌍 Geographic"])

    # TAB 1 – TREND
    with rec_tabs[0]:
        if time_cols:
            time_col = time_cols[0]
            try:
                temp = df.copy()
                temp[time_col] = pd.to_datetime(temp[time_col], errors="coerce")
                temp = temp.dropna(subset=[time_col])
                temp["_period"] = temp[time_col].dt.to_period("M").dt.to_timestamp()
                trend_df = temp.groupby("_period")[rec_col].sum().reset_index()
                trend_df.columns = [time_col, rec_col]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trend_df[time_col], y=trend_df[rec_col],
                    mode="lines+markers",
                    line=dict(color=THEME["secondary"], width=2.5),
                    marker=dict(size=6, color=THEME["accent"]),
                    fill="tozeroy", fillcolor=f"rgba(168,85,247,0.12)",
                    name=rec_col
                ))
                # Rolling average overlay
                if len(trend_df) >= 3:
                    trend_df["_rolling"] = trend_df[rec_col].rolling(3, min_periods=1).mean()
                    fig.add_trace(go.Scatter(
                        x=trend_df[time_col], y=trend_df["_rolling"],
                        mode="lines", line=dict(color=THEME["warning"], width=1.5, dash="dot"),
                        name="3-period Moving Avg"
                    ))
                fig.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=THEME["text_main"]), legend=dict(bgcolor="rgba(0,0,0,0)"),
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#2d2d3a"),
                    margin=dict(l=0, r=0, t=30, b=0), height=340
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"💡 *AI Tip: The chart shows {rec_col} over time with a 3-period moving average to smooth short-term fluctuations.*")
            except Exception as e:
                st.warning(f"Trend chart skipped: {e}")
        else:
            st.info("No date/time column detected for trend analysis.")

    # TAB 2 – DISTRIBUTION
    with rec_tabs[1]:
        sel_col = st.selectbox("Select column for distribution:", numeric_cols, key="dist_col")
        fig = make_subplots(rows=1, cols=2, subplot_titles=["Histogram", "Box Plot"])
        fig.add_trace(go.Histogram(x=df[sel_col].dropna(), marker_color=THEME["secondary"], opacity=0.8, name="Histogram"), row=1, col=1)
        fig.add_trace(go.Box(y=df[sel_col].dropna(), marker_color=THEME["accent"], boxpoints="outliers", name="Distribution"), row=1, col=2)
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=THEME["text_main"]), showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0), height=340
        )
        st.plotly_chart(fig, use_container_width=True)
        # Outlier annotation
        q1, q3 = df[sel_col].quantile(0.25), df[sel_col].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[sel_col] < q1 - 1.5*iqr) | (df[sel_col] > q3 + 1.5*iqr)]
        if len(outliers):
            st.markdown(f'<div style="color:{THEME["warning"]};font-size:0.85rem">⚠️ <b>{len(outliers)} outliers</b> detected in <b>{sel_col}</b> using IQR method.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:{THEME["success"]};font-size:0.85rem">✅ No outliers detected in <b>{sel_col}</b>.</div>', unsafe_allow_html=True)

    # TAB 3 – CATEGORY BREAKDOWN
    with rec_tabs[2]:
        if categorical_cols:
            cat_sel  = st.selectbox("Group by:", categorical_cols, key="cat_col")
            num_sel  = st.selectbox("Metric:", numeric_cols, key="cat_num")
            agg_mode = st.radio("Aggregation:", ["Sum", "Mean", "Count"], horizontal=True, key="agg_mode")
            agg_fn   = {"Sum": "sum", "Mean": "mean", "Count": "count"}[agg_mode]
            cat_df   = df.groupby(cat_sel)[num_sel].agg(agg_fn).reset_index().sort_values(num_sel, ascending=False)

            c1, c2 = st.columns(2)
            with c1:
                fig_bar = px.bar(cat_df, x=cat_sel, y=num_sel, text_auto=".2s",
                                 color=num_sel, color_continuous_scale="Purples",
                                 template="plotly_dark")
                fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                      coloraxis_showscale=False, margin=dict(l=0,r=0,t=20,b=0), height=300)
                st.plotly_chart(fig_bar, use_container_width=True)
            with c2:
                fig_pie = px.pie(cat_df, names=cat_sel, values=num_sel,
                                 hole=0.45, color_discrete_sequence=px.colors.sequential.Purples_r,
                                 template="plotly_dark")
                fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=20,b=0), height=300, showlegend=False)
                st.plotly_chart(fig_pie, use_container_width=True)

            # Top & Bottom performers
            top = cat_df.head(3)[cat_sel].tolist()
            bot = cat_df.tail(3)[cat_sel].tolist()
            st.markdown(f'<div style="font-size:0.85rem;color:{THEME["success"]}">🏆 Top performers: <b>{", ".join(map(str,top))}</b></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.85rem;color:{THEME["warning"]}">⚠️ Underperformers: <b>{", ".join(map(str,bot))}</b></div>', unsafe_allow_html=True)
        else:
            st.info("No categorical columns found for grouping.")

    # TAB 4 – CORRELATION HEATMAP
    with rec_tabs[3]:
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.columns,
                colorscale="Purp", text=corr.round(2).values.astype(str),
                texttemplate="%{text}", zmin=-1, zmax=1,
                colorbar=dict(title="Correlation")
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0,r=0,t=20,b=0), height=380
            )
            st.plotly_chart(fig, use_container_width=True)
            # AI tip
            corr_pairs = [(corr.columns[i], corr.columns[j], corr.iloc[i,j])
                          for i in range(len(corr)) for j in range(i+1, len(corr))]
            if corr_pairs:
                strongest = max(corr_pairs, key=lambda x: abs(x[2]))
                st.caption(f"💡 Strongest correlation: **{strongest[0]}** ↔ **{strongest[1]}** (r = {strongest[2]:.2f})")
        else:
            st.info("Need at least 2 numeric columns for correlation analysis.")

    # TAB 5 – GEOGRAPHIC
    with rec_tabs[4]:
        geo_cols = [c for c in df.columns if any(k in c.lower() for k in ["country","state","region","city","location","geo"])]
        if geo_cols and numeric_cols:
            geo_col = st.selectbox("Geographic column:", geo_cols, key="geo_col")
            geo_num = st.selectbox("Metric:", numeric_cols, key="geo_num")
            geo_df  = df.groupby(geo_col)[geo_num].sum().reset_index().sort_values(geo_num, ascending=True)
            fig = px.bar(geo_df, x=geo_num, y=geo_col, orientation="h",
                         color=geo_num, color_continuous_scale="Purples",
                         text_auto=".2s", template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               coloraxis_showscale=False, margin=dict(l=0,r=0,t=20,b=0),
                               height=max(300, len(geo_df) * 30))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No geographic column detected (Country / State / Region / City).")


# ─────────────────────────────────────────────────────────────
# FEATURE 2 — INTERACTIVE DASHBOARD BUILDER
# ─────────────────────────────────────────────────────────────

def render_dashboard_builder(df: pd.DataFrame):
    st.markdown('<div class="section-title">🛠️ Interactive Dashboard Builder</div>', unsafe_allow_html=True)

    numeric_cols     = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    time_cols        = [c for c in df.columns if any(k in c.lower() for k in ["year","date","month","time"])]
    all_cols         = df.columns.tolist()

    st.markdown("Build your own layout — choose widgets and arrange them below.")

    # ── Layout template
    col_tmpl, col_name, col_save = st.columns([2, 2, 1])
    with col_tmpl:
        template = st.selectbox(
            "Start from template:",
            ["Blank", "Sales Overview", "Operations Review", "Executive Summary"],
            key="db_template"
        )
    with col_name:
        layout_name = st.text_input("Save layout as:", value="My Dashboard", key="layout_name")
    with col_save:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Layout"):
            st.session_state["dashboard_layouts"][layout_name] = {
                "template": template,
                "saved_at": datetime.now().strftime("%d %b %Y %H:%M"),
            }
            st.success(f"✅ Layout '{layout_name}' saved!")

    # Saved layouts
    if st.session_state["dashboard_layouts"]:
        st.markdown("**📁 Saved Layouts:**")
        for name, meta in st.session_state["dashboard_layouts"].items():
            st.markdown(f'<span style="color:{THEME["accent"]};font-size:0.85rem">📌 {name} — saved {meta["saved_at"]}</span>', unsafe_allow_html=True)

    st.divider()

    # ── Widget builder
    st.markdown("#### ➕ Add Widgets to Your Dashboard")
    num_widgets = st.slider("Number of widgets:", 1, 6, 3, key="num_widgets")
    widget_configs = []
    widget_cols_row = st.columns(min(num_widgets, 3))

    for i in range(num_widgets):
        with widget_cols_row[i % 3]:
            st.markdown(f'<div class="report-box">', unsafe_allow_html=True)
            chart_type = st.selectbox(
                f"Widget {i+1} type:",
                ["KPI Card", "Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Data Table"],
                key=f"wtype_{i}"
            )
            col_choice = st.selectbox(f"Column:", all_cols, key=f"wcol_{i}")
            widget_configs.append({"type": chart_type, "col": col_choice})
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🖥️ Render My Dashboard", type="primary"):
        st.markdown("---")
        st.markdown("### 🖥️ Your Custom Dashboard")
        render_cols = st.columns(min(num_widgets, 3))
        for i, cfg in enumerate(widget_configs):
            with render_cols[i % 3]:
                _render_widget(df, cfg["type"], cfg["col"], i)


def _render_widget(df, chart_type, col, idx):
    try:
        if chart_type == "KPI Card":
            val = df[col].sum() if pd.api.types.is_numeric_dtype(df[col]) else df[col].nunique()
            label = "Sum" if pd.api.types.is_numeric_dtype(df[col]) else "Unique"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label} of {col}</div>
                <div class="kpi-value">{val:,.0f}</div>
            </div>""", unsafe_allow_html=True)

        elif chart_type == "Bar Chart" and pd.api.types.is_numeric_dtype(df[col]):
            cat_cols = df.select_dtypes("object").columns
            if len(cat_cols):
                gdf = df.groupby(cat_cols[0])[col].sum().reset_index()
                fig = px.bar(gdf, x=cat_cols[0], y=col, color_discrete_sequence=[THEME["secondary"]],
                             template="plotly_dark", height=260)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(df[col])

        elif chart_type == "Line Chart" and pd.api.types.is_numeric_dtype(df[col]):
            fig = px.line(df.reset_index(), x="index", y=col,
                          color_discrete_sequence=[THEME["secondary"]], template="plotly_dark", height=260)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               margin=dict(l=0,r=0,t=20,b=0))
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie Chart":
            if not pd.api.types.is_numeric_dtype(df[col]):
                vc = df[col].value_counts().head(8).reset_index()
                vc.columns = [col, "count"]
                fig = px.pie(vc, names=col, values="count", hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Purples_r,
                             template="plotly_dark", height=260)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pie chart works best with categorical columns.")

        elif chart_type == "Scatter Plot":
            num_cols = df.select_dtypes(include=np.number).columns.tolist()
            if len(num_cols) >= 2:
                fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                                 color_discrete_sequence=[THEME["accent"]],
                                 template="plotly_dark", height=260, opacity=0.7)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Data Table":
            st.dataframe(df[[col]].head(10), use_container_width=True, height=260)

    except Exception as e:
        st.caption(f"Widget {idx+1}: {e}")


# ─────────────────────────────────────────────────────────────
# FEATURE 3 — REAL-TIME DASHBOARD REFRESH
# ─────────────────────────────────────────────────────────────

def render_realtime_refresh(df: pd.DataFrame, kpis: dict):
    st.markdown('<div class="section-title">⚡ Real-Time Dashboard Refresh</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        auto = st.toggle("Enable Auto-Refresh", value=st.session_state["auto_refresh"], key="auto_toggle")
        st.session_state["auto_refresh"] = auto
    with c2:
        interval = st.selectbox("Interval:", [10, 30, 60, 120], index=1, key="refresh_interval_sel")
        st.session_state["refresh_interval"] = interval
    with c3:
        if st.button("🔄 Refresh Now"):
            st.session_state["last_refresh"] = time.time()
            st.rerun()

    # Live status bar
    elapsed = int(time.time() - st.session_state["last_refresh"])
    next_in = max(0, interval - elapsed)
    status_color = THEME["success"] if elapsed < interval else THEME["warning"]
    st.markdown(f"""
    <div style="background:{THEME['bg_card']};border:1px solid {status_color}44;border-radius:10px;
                padding:0.7rem 1.2rem;margin:0.5rem 0;display:flex;align-items:center;gap:1rem;">
        <span class="refresh-dot" style="background:{status_color}"></span>
        <span style="font-size:0.85rem;color:{THEME['text_muted']}">
            Last refreshed: <b style="color:{THEME['text_main']}">{elapsed}s ago</b>
            &nbsp;|&nbsp; Next refresh in: <b style="color:{status_color}">{next_in}s</b>
            &nbsp;|&nbsp; Dataset: <b style="color:{THEME['accent']}">{st.session_state.get('file_name','—')}</b>
            &nbsp;|&nbsp; Rows: <b style="color:{THEME['accent']}">{len(df):,}</b>
        </span>
    </div>""", unsafe_allow_html=True)

    # Live KPI ticker row
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()[:4]
    if numeric_cols:
        st.markdown("##### 📡 Live KPI Snapshot")
        tick_cols = st.columns(len(numeric_cols))
        for i, col in enumerate(numeric_cols):
            with tick_cols[i]:
                val = df[col].sum()
                mean = df[col].mean()
                delta_pct = ((val - mean * len(df) * 0.9) / (mean * len(df) * 0.9) * 100) if mean else 0
                delta_cls = "kpi-delta-pos" if delta_pct >= 0 else "kpi-delta-neg"
                delta_sym = "▲" if delta_pct >= 0 else "▼"
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{col}</div>
                    <div class="kpi-value">{val:,.0f}</div>
                    <div class="{delta_cls}">{delta_sym} {abs(delta_pct):.1f}%</div>
                </div>""", unsafe_allow_html=True)

    # Auto-trigger rerun
    if auto and elapsed >= interval:
        st.session_state["last_refresh"] = time.time()
        time.sleep(0.2)
        st.rerun()


# ─────────────────────────────────────────────────────────────
# FEATURE 4 — AUTOMATED REPORT GENERATOR
# ─────────────────────────────────────────────────────────────

def render_report_generator(df: pd.DataFrame, kpis: dict, insights: list, recommendations: list):
    st.markdown('<div class="section-title">📄 Automated Report Generator</div>', unsafe_allow_html=True)

    st.markdown("Generate a structured business report from your dataset — with narrative, KPIs, and recommendations.")

    c1, c2, c3 = st.columns(3)
    with c1:
        report_title = st.text_input("Report Title:", value="Genesis Data Analysis Report")
    with c2:
        analyst_name = st.text_input("Analyst Name:", value="NK — Genesis Team")
    with c3:
        report_type = st.selectbox("Report Type:", ["Executive Summary", "Full Analysis", "KPI Report", "Quick Snapshot"])

    include_charts  = st.checkbox("Include Chart Summaries", value=True)
    include_recs    = st.checkbox("Include Recommendations", value=True)

    if st.button("🚀 Generate Report", type="primary"):
        with st.spinner("Building your report..."):
            time.sleep(0.8)  # simulates processing

        # ── Narrative block
        total_s = kpis.get("total_sales", 0)
        total_p = kpis.get("total_profit", 0)
        avg_ov  = kpis.get("avg_order_value", 0)
        margin  = kpis.get("profit_margin", 0)
        rows    = kpis.get("total_rows", len(df))
        orders  = kpis.get("total_orders", 0)
        custs   = kpis.get("unique_customers", 0)

        narrative = f"""
This report presents a comprehensive analysis of the dataset **{st.session_state.get('file_name', 'Uploaded Dataset')}**
containing **{rows:,} records** across **{kpis.get('total_cols', len(df.columns))} columns**.

The dataset reveals a total {kpis.get('sales_col','revenue')} of **{total_s:,.2f}** across **{orders:,} transactions**
from **{custs:,} unique customers**, yielding an average order value of **{avg_ov:,.2f}**.
{f"Profitability stands at **{total_p:,.2f}** with a margin of **{margin:.2f}%**." if total_p else ""}

{"The key concern areas identified include high discount rates and shipping delays which are compressing margins." if kpis.get("avg_discount",0) > 0.2 or kpis.get("avg_shipping_delay",0) > 5 else "Overall data quality and business metrics appear within healthy ranges."}
"""

        # ── Report preview card
        now = datetime.now().strftime("%d %B %Y, %H:%M")
        st.markdown(f"""
        <div class="report-box">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                <div>
                    <div style="font-size:1.3rem;font-weight:800;color:{THEME['secondary']}">{report_title}</div>
                    <div style="font-size:0.8rem;color:{THEME['text_muted']}">Type: {report_type} &nbsp;|&nbsp; Analyst: {analyst_name} &nbsp;|&nbsp; Generated: {now}</div>
                </div>
                <div style="font-size:2rem">📊</div>
            </div>
            <hr style="border-color:{THEME['primary']}33;">
            <div style="font-size:0.9rem;line-height:1.7;color:{THEME['text_main']}">{narrative}</div>
        </div>
        """, unsafe_allow_html=True)

        # KPI table
        st.markdown("**📌 Key Metrics Summary**")
        kpi_display = {
            "Total Records": f"{rows:,}",
            f"Total {kpis.get('sales_col','Sales')}": f"{total_s:,.2f}",
            "Total Profit": f"{total_p:,.2f}",
            "Profit Margin": f"{margin:.2f}%",
            "Avg Order Value": f"{avg_ov:,.2f}",
            "Total Orders": f"{orders:,}",
            "Unique Customers": f"{custs:,}",
        }
        kdf = pd.DataFrame(list(kpi_display.items()), columns=["Metric", "Value"])
        st.dataframe(kdf, use_container_width=True, hide_index=True)

        # AI Insights
        if insights:
            st.markdown("**🔍 AI-Detected Insights**")
            for ins in insights:
                st.markdown(f'<div class="insight-item">• {ins}</div>', unsafe_allow_html=True)

        # Recommendations
        if include_recs and recommendations:
            st.markdown("**💡 Smart Recommendations**")
            for r in recommendations:
                st.markdown(f'<div class="insight-item" style="color:{THEME["accent"]}">→ {r}</div>', unsafe_allow_html=True)

        st.success("✅ Report generated successfully!")

        # ── CSV Download
        csv_buf = io.StringIO()
        kdf.to_csv(csv_buf, index=False)
        st.download_button(
            "📥 Download Report as CSV",
            data=csv_buf.getvalue(),
            file_name=f"genesis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )


# ─────────────────────────────────────────────────────────────
# PROACTIVE INSIGHT BANNER (Module 3 integration)
# ─────────────────────────────────────────────────────────────

def render_insight_banner(insights: list):
    if not insights:
        return
    items_html = "".join(f'<div class="insight-item">• {i}</div>' for i in insights[:4])
    st.markdown(f"""
    <div class="insight-banner">
        <div class="insight-title">⚡ AI-Detected Insights</div>
        {items_html}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# KPI CARDS ROW
# ─────────────────────────────────────────────────────────────

def render_kpi_cards(kpis: dict):
    st.markdown('<div class="section-title">📌 Key Performance Indicators</div>', unsafe_allow_html=True)
    sales_label = kpis.get("sales_col", "Sales")

    cards = [
        (f"Total {sales_label}", kpis.get("total_sales",0),     f"Avg/order: {kpis.get('avg_order_value',0):,.0f}",       "pos"),
        ("Total Profit",         kpis.get("total_profit",0),    f"Margin: {kpis.get('profit_margin',0):.1f}%",             "pos" if kpis.get("total_profit",0)>0 else "neg"),
        ("Total Orders",         kpis.get("total_orders",0),    f"Avg discount: {kpis.get('avg_discount',0)*100:.1f}%",    "neu"),
        ("Unique Customers",     kpis.get("unique_customers",0),f"Avg ship delay: {kpis.get('avg_shipping_delay',0):.1f}d","neu"),
    ]

    cols = st.columns(4)
    for i, (label, val, sub, cls) in enumerate(cards):
        with cols[i]:
            fmt_val = f"{val:,.0f}" if abs(val) < 1e7 else f"{val/1e6:,.1f}M"
            delta_html = f'<div class="kpi-delta-{cls}">{sub}</div>'
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{fmt_val}</div>
                {delta_html}
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

def render_sidebar(df):
    with st.sidebar:
        st.markdown(f'<h2 style="color:{THEME["secondary"]}">🧠 Genesis Dashboard</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:{THEME["text_muted"]};font-size:0.8rem">AI-Powered Company Data Analysis</p>', unsafe_allow_html=True)
        st.divider()

        # Dataset summary
        if df is not None:
            st.markdown(f'<div style="font-size:0.78rem;color:{THEME["text_muted"]}">📂 {st.session_state.get("file_name","Dataset")}</div>', unsafe_allow_html=True)
            sb1, sb2 = st.columns(2)
            sb1.metric("Rows",    f"{len(df):,}")
            sb2.metric("Columns", len(df.columns))
            st.divider()

            # Sidebar filters
            st.markdown("**🔍 Global Filters**")
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            cat_cols     = df.select_dtypes(include="object").columns.tolist()

            filtered_df = df.copy()

            if cat_cols:
                for cat in cat_cols[:2]:
                    options = ["All"] + sorted(df[cat].dropna().unique().tolist())
                    sel = st.selectbox(f"{cat}:", options, key=f"filter_{cat}")
                    if sel != "All":
                        filtered_df = filtered_df[filtered_df[cat] == sel]

            if numeric_cols:
                primary_num = numeric_cols[0]
                min_v, max_v = float(df[primary_num].min()), float(df[primary_num].max())
                if min_v < max_v:
                    range_sel = st.slider(f"{primary_num} Range:", min_v, max_v, (min_v, max_v), key="num_range")
                    filtered_df = filtered_df[(filtered_df[primary_num] >= range_sel[0]) &
                                              (filtered_df[primary_num] <= range_sel[1])]

            st.caption(f"Showing {len(filtered_df):,} of {len(df):,} rows")
            st.divider()

            # Smart query suggestions
            st.markdown("**💡 Smart Queries**")
            suggestions = generate_suggestions(filtered_df, st.session_state["chat_history"])
            for sug in suggestions:
                if st.button(f"🔍 {sug}", use_container_width=True, key=f"sug_{sug[:20]}"):
                    st.session_state["chat_input_trigger"] = sug
                    st.rerun()

            st.session_state["_filtered_df"] = filtered_df
        else:
            st.info("Upload a dataset to get started.")
            st.session_state["_filtered_df"] = None


# ─────────────────────────────────────────────────────────────
# PREDICTIVE ANALYTICS SECTION (Module 3 bridge)
# ─────────────────────────────────────────────────────────────

def render_predictive_section(df: pd.DataFrame):
    st.markdown('<div class="section-title">🔮 Predictive Analytics (Module 3 Bridge)</div>', unsafe_allow_html=True)

    date_col = next((c for c in df.columns if any(k in c.lower() for k in ["order date","date","time"])), None)
    sales_col = next((c for c in df.columns if c.lower() in ["sales","revenue","amount"]), None)

    if not date_col or not sales_col:
        st.info("Predictive analytics requires a date column and a Sales/Revenue column. These weren't detected in your dataset.")
        return

    forecast_periods = st.slider("Forecast periods (months):", 3, 12, 6, key="forecast_periods")

    if st.button("▶️ Run Forecast", type="primary"):
        if SalesPredictiveEngine:
            try:
                engine = SalesPredictiveEngine(df=df)
                if not engine.load_data():
                    st.error("Could not load data into predictive engine.")
                    return
                engine.build_monthly_series()
                decomp = engine.decompose_trend_seasonality()
                lr_df  = engine.linear_regression_forecast(periods=forecast_periods)

                if not lr_df.empty:
                    st.success("✅ Forecast complete!")
                    lr_df_reset = lr_df.reset_index()
                    fig = go.Figure()
                    # Historical
                    hist = engine.monthly_sales
                    fig.add_trace(go.Scatter(
                        x=hist["YearMonth_dt"].astype(str), y=hist["Sales"],
                        mode="lines+markers", name="Historical",
                        line=dict(color=THEME["secondary"], width=2),
                        marker=dict(size=5)
                    ))
                    # Forecast
                    fig.add_trace(go.Scatter(
                        x=lr_df_reset["Period"], y=lr_df_reset["Predicted Sales"],
                        mode="lines+markers", name="Forecast",
                        line=dict(color=THEME["warning"], width=2, dash="dot"),
                        marker=dict(size=7, symbol="diamond")
                    ))
                    # Confidence band
                    fig.add_trace(go.Scatter(
                        x=list(lr_df_reset["Period"]) + list(lr_df_reset["Period"])[::-1],
                        y=list(lr_df_reset["Upper Bound (95%)"]) + list(lr_df_reset["Lower Bound (95%)"])[::-1],
                        fill="toself", fillcolor=f"rgba(245,158,11,0.12)",
                        line=dict(color="rgba(0,0,0,0)"), name="95% Confidence Band"
                    ))
                    fig.update_layout(
                        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=THEME["text_main"]), height=380,
                        legend=dict(bgcolor="rgba(0,0,0,0)"),
                        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#2d2d3a"),
                        margin=dict(l=0, r=0, t=20, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(lr_df, use_container_width=True)

                    # Trend summary
                    if decomp:
                        gr = decomp.get("avg_growth_rate", 0) * 100
                        direction = "📈 UPWARD" if gr > 2 else ("📉 DOWNWARD" if gr < -2 else "➡️ STABLE")
                        st.markdown(f"""
                        <div class="insight-banner">
                            <div class="insight-title">📊 Forecast Summary</div>
                            <div class="insight-item">Trend Direction: <b>{direction}</b></div>
                            <div class="insight-item">Avg Monthly Growth Rate: <b>{gr:+.2f}%</b></div>
                            <div class="insight-item">Forecast Horizon: <b>{forecast_periods} months ahead</b></div>
                        </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Predictive engine error: {e}")
        else:
            # Lightweight fallback if Module 3 not importable
            st.warning("Module 3 not found — showing lightweight trend forecast.")
            try:
                temp = df.copy()
                temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
                temp = temp.dropna(subset=[date_col])
                temp["_period"] = temp[date_col].dt.to_period("M").dt.to_timestamp()
                monthly = temp.groupby("_period")[sales_col].sum().reset_index()
                monthly.columns = ["Period", "Sales"]

                X = np.arange(len(monthly), dtype=float)
                coeffs = np.polyfit(X, monthly["Sales"].values, 1)
                slope, intercept = coeffs

                last_period = monthly["Period"].iloc[-1]
                future_dates = [last_period + pd.DateOffset(months=i) for i in range(1, forecast_periods+1)]
                future_sales = [max(0, slope * (len(monthly)+i) + intercept) for i in range(1, forecast_periods+1)]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=monthly["Period"].astype(str), y=monthly["Sales"],
                                         mode="lines+markers", name="Historical",
                                         line=dict(color=THEME["secondary"], width=2)))
                fig.add_trace(go.Scatter(x=[str(d) for d in future_dates], y=future_sales,
                                         mode="lines+markers", name="Forecast",
                                         line=dict(color=THEME["warning"], width=2, dash="dot"),
                                         marker=dict(symbol="diamond", size=7)))
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                   plot_bgcolor="rgba(0,0,0,0)", height=360,
                                   font=dict(color=THEME["text_main"]),
                                   margin=dict(l=0,r=0,t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Fallback forecast error: {e}")


# ─────────────────────────────────────────────────────────────
# MAIN DASHBOARD ENTRY POINT
# ─────────────────────────────────────────────────────────────

def dashboard_section():
    """
    Main entry point for Module 4.
    Call this from main_app.py when the user navigates to the Dashboard page.
    """
    apply_dashboard_css()
    init_session_state()

    df = st.session_state.get("_filtered_df") or st.session_state.get("uploaded_df")

    if df is None or df.empty:
        st.markdown(f"""
        <div style="text-align:center;padding:4rem 2rem;">
            <div style="font-size:3rem">📊</div>
            <h2 style="color:{THEME['secondary']}">No Dataset Loaded</h2>
            <p style="color:{THEME['text_muted']}">Please upload a dataset using the <b>Data Upload</b> page first.</p>
        </div>""", unsafe_allow_html=True)
        return

    # ── Compute KPIs & Insights
    kpis = compute_kpis(df)
    st.session_state["kpis_cache"] = kpis

    if generate_ai_insights:
        try:
            insights = generate_ai_insights(kpis)
        except Exception:
            insights = local_insights(kpis)
    else:
        insights = local_insights(kpis)

    if generate_smart_recommendations:
        try:
            recommendations = generate_smart_recommendations(kpis)
        except Exception:
            recommendations = local_recommendations(kpis)
    else:
        recommendations = local_recommendations(kpis)

    st.session_state["insights_cache"] = insights

    # ── Page header
    fname = st.session_state.get("file_name", "Dataset")
    st.markdown(f'<h1 style="margin-bottom:0.2rem">📊 Genesis Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{THEME["text_muted"]};font-size:0.88rem">Dataset: <b style="color:{THEME["accent"]}">{fname}</b> &nbsp;|&nbsp; {len(df):,} rows × {len(df.columns)} columns &nbsp;|&nbsp; Last updated: {datetime.now().strftime("%d %b %Y, %H:%M")}</p>', unsafe_allow_html=True)

    # ── Proactive Insight Banner
    render_insight_banner(insights)

    # ── KPI Cards
    render_kpi_cards(kpis)

    st.divider()

    # ── Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visualizations",
        "🛠️ Dashboard Builder",
        "⚡ Live Refresh",
        "🔮 Predictive Analytics",
        "📄 Report Generator",
    ])

    with tab1:
        render_visualization_layer(df, kpis)

        # Recommendations from Module 3
        if recommendations:
            st.divider()
            st.markdown('<div class="section-title">💡 Smart Recommendations</div>', unsafe_allow_html=True)
            rec_cols = st.columns(min(len(recommendations), 3))
            for i, rec in enumerate(recommendations):
                with rec_cols[i % 3]:
                    st.markdown(f"""
                    <div class="kpi-card" style="border-left-color:{THEME['warning']}">
                        <div style="font-size:0.88rem;color:{THEME['text_main']}">💡 {rec}</div>
                    </div>""", unsafe_allow_html=True)

    with tab2:
        render_dashboard_builder(df)

    with tab3:
        render_realtime_refresh(df, kpis)

    with tab4:
        render_predictive_section(df)

    with tab5:
        render_report_generator(df, kpis, insights, recommendations)


# ─────────────────────────────────────────────────────────────
# STANDALONE RUN (for testing Module 4 independently)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    st.set_page_config(
        page_title="Genesis Dashboard | Module 4",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()
    apply_dashboard_css()

    # Sidebar — file upload when run standalone
    with st.sidebar:
        from module1.file_upload import file_upload_section  # type: ignore
        file_upload_section()

    render_sidebar(st.session_state.get("uploaded_df"))
    dashboard_section()
