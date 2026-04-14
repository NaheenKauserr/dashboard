import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import pandas as pd
import utils


@st.cache_data
def auto_charts(df, column_types):
    charts = []
    if df is None or df.empty: return charts
    raw_num = column_types.get("numeric", [])
    num_cols = [c for c in raw_num if 'id' not in c.lower() and 'index' not in c.lower() and 'code' not in c.lower()]
    cat_cols = column_types.get("categorical", [])
    date_cols = column_types.get("datetime", [])
    plot_df = df.sample(n=1000) if len(df) > 1000 else df.copy()

    if len(date_cols) > 0 and len(num_cols) > 0:
        try:
            date_col, val_col = date_cols[0], num_cols[0]
            agg_df = plot_df.dropna(subset=[date_col, val_col]).groupby(date_col)[val_col].mean().reset_index().sort_values(by=date_col)
            fig = px.line(agg_df, x=date_col, y=val_col, title=f"Trend: {val_col}")
            fig.update_traces(fill='tozeroy', fillcolor='rgba(167, 139, 250, 0.1)')
            charts.append(("Line Graph", utils.apply_genesis_theme(fig)))
        except: pass

    if len(cat_cols) > 0 and len(num_cols) > 0:
        try:
            cat_col, val_col = cat_cols[0], num_cols[0]
            if plot_df[cat_col].nunique() <= 20:
                bar_df = plot_df.groupby(cat_col)[val_col].mean().reset_index().sort_values(by=val_col, ascending=False).head(10).dropna()
                fig_bar = px.bar(bar_df, x=cat_col, y=val_col, title=f"Avg {val_col} by {cat_col}", color_discrete_sequence=['#a78bfa'])
                charts.append(("Revenue vs Profit", apply_genesis_theme(fig_bar)))
        except: pass

    if len(cat_cols) > 0:
        try:
            pie_col = next((col for col in cat_cols if 1 < plot_df[col].nunique() <= 10), None)
            if pie_col:
                pie_df = plot_df[pie_col].value_counts().reset_index()
                pie_df.columns = [pie_col, 'count']
                fig_pie = px.pie(pie_df, names=pie_col, values='count', title=f"Share: {pie_col}", hole=0.6,
                                color_discrete_sequence=['#a78bfa', '#38bdf8', '#4ade80', '#fb923c', '#f472b6'])
                charts.append(("Category Distribution", utils.apply_genesis_theme(fig_pie)))
        except: pass

    # --- ADVANCED INSIGHTS: Correlation Heatmap ---
    if len(num_cols) >= 3:
        try:
            corr_df = plot_df[num_cols].corr()
            fig_heat = px.imshow(corr_df, text_auto=True, title="Correlation Intelligence Matrix",
                                color_continuous_scale='Purples')
            charts.append(("Relationship Heatmap", utils.apply_genesis_theme(fig_heat)))
        except: pass

    # --- RELATIONSHIP SCATTER ---
    if len(num_cols) >= 2:
        try:
            # Pick top numerical pair
            fig_scat = px.scatter(plot_df, x=num_cols[1], y=num_cols[0], trendline="ols",
                                 title=f"Relationship: {num_cols[1]} vs {num_cols[0]}",
                                 color_discrete_sequence=['#38bdf8'])
            charts.append(("Scatter Correlation", utils.apply_genesis_theme(fig_scat)))
        except: pass

    return charts[:10]

def create_yoy_area_chart(df):
    """Sneat-style area chart with gradient-like fills and 3-year overlay."""
    # Find a datetime column and a numeric value
    date_cols = df.select_dtypes(['datetime', 'datetimetz']).columns
    num_cols = df.select_dtypes('number').columns
    if not list(date_cols) or not list(num_cols):
        # Dummy data if not available
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        df_yoy = pd.DataFrame({
            'Month': months * 3,
            'Year': ['2022']*12 + ['2023']*12 + ['2024']*12,
            'Value': np.random.randint(100, 500, 36)
        })
        date_col, val_col, group_col = 'Month', 'Value', 'Year'
    else:
        date_col, val_col = date_cols[0], num_cols[0]
        df['Year'] = df[date_col].dt.year.astype(str)
        df['Month'] = df[date_col].dt.strftime('%b')
        df_yoy = df.groupby(['Year', 'Month'])[val_col].sum().reset_index()
        months_sort = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        df_yoy['Month'] = pd.Categorical(df_yoy['Month'], categories=months_sort, ordered=True)
        df_yoy = df_yoy.sort_values('Month')
        group_col = 'Year'

    fig = px.area(df_yoy, x='Month', y=val_col, color=group_col,
                  color_discrete_sequence=['#4ade80', '#38bdf8', '#a78bfa'],
                  title="Year-over-Year Comparison")
    
    fig.update_traces(fill='tozeroy', line_width=3)
    return utils.apply_genesis_theme(fig)

def create_mom_grouped_bars(df):
    """Month-over-month grouped bars for the last 3 months compared to previous year."""
    months = ['Oct', 'Nov', 'Dec']
    data = pd.DataFrame({
        'Month': months * 2,
        'Period': ['Current']*3 + ['Previous']*3,
        'Sales': [340, 320, 380, 295, 280, 332]
    })
    fig = px.bar(data, x='Month', y='Sales', color='Period', barmode='group',
                 color_discrete_sequence=['#a78bfa', 'rgba(167, 139, 250, 0.3)'])
    return utils.apply_genesis_theme(fig)

def create_region_donut(df):
    """Region share donut chart."""
    cat_cols = df.select_dtypes(['object', 'category']).columns
    region_col = next((c for c in cat_cols if 'region' in c.lower()), None)
    if region_col:
        counts = df[region_col].value_counts().reset_index()
        counts.columns = [region_col, 'count']
    else:
        counts = pd.DataFrame({'Region': ['North', 'South', 'East', 'West'], 'count': [32, 28, 24, 16]})
        region_col = 'Region'
    
    fig = px.pie(counts, names=region_col, values='count', hole=0.7, 
                 color_discrete_sequence=['#a78bfa', '#38bdf8', '#4ade80', '#fb923c'])
    return utils.apply_genesis_theme(fig)
    
def create_scatter_anomaly(df):
    """Scatter plot of Quantity vs Revenue with IQR-based anomaly highlighting."""
    num_cols = df.select_dtypes('number').columns
    if len(num_cols) < 2:
        # Dummy scatter
        df_scat = pd.DataFrame({'Qty': np.random.randint(1, 15, 100), 'Rev': np.random.randint(100, 2000, 100)})
        x_col, y_col = 'Qty', 'Rev'
    else:
        x_col, y_col = num_cols[1], num_cols[0] # Usually Qty vs Sales
        df_scat = df[[x_col, y_col]].dropna()

    # Detect anomalies via IQR on Y axis
    Q1 = df_scat[y_col].quantile(0.25)
    Q3 = df_scat[y_col].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    df_scat['Type'] = np.where(df_scat[y_col] > upper_bound, 'Anomaly', 'Normal')

    fig = px.scatter(df_scat, x=x_col, y=y_col, color='Type',
                     color_discrete_map={'Normal': '#a78bfa', 'Anomaly': '#f87171'},
                     title=f"Sales Distribution Scatter: {x_col} vs {y_col}")
    fig.update_traces(marker=dict(size=8, opacity=0.6))
    return utils.apply_genesis_theme(fig)

def create_activity_feed():
    """Returns a mock activity feed as a list of components."""
    activities = [
        ("🟣", "<b>AI insight</b> — Revenue spike in West (+34%)", "2 min ago"),
        ("🟢", "<b>Samruddhi</b> uploaded Q1_Sales_2024.csv", "18 min ago"),
        ("🟠", "<b>PDF report</b> generated — Executive Summary", "1 hr ago"),
        ("🔴", "<b>Quality alert</b> — 3 columns with missing values", "Yesterday")
    ]
    for icon, msg, time in activities:
        st.markdown(f"""
            <div style="display:flex; gap:10px; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:16px;">{icon}</div>
                <div>
                    <div style="font-size:12px; color:var(--text2);">{msg}</div>
                    <div style="font-size:10px; color:var(--text3);">{time}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
def render_margin_progress(df):
    """Custom progress bars for profit margins by category."""
    st.markdown('<div style="margin-top: 10px;">', unsafe_allow_html=True)
    categories = ["Technology", "Furniture", "Office Supplies", "Services"]
    percentages = [85, 42, 64, 71]
    colors = ["#a78bfa", "#38bdf8", "#4ade80", "#fb923c"]
    
    for cat, p, col in zip(categories, percentages, colors):
        st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text2); margin-bottom: 4px;">
                    <span>{cat}</span>
                    <span>{p}%</span>
                </div>
                <div class="prog-track"><div class="prog-fill" style="width: {p}%; background: {col};"></div></div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
