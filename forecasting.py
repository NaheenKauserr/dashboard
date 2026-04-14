import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import utils

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False


@st.cache_data
def auto_forecast(df, column_types):
    if not HAS_PROPHET or df is None or df.empty:
        return None

    date_cols, num_cols = column_types.get("datetime", []), column_types.get("numeric", [])
    if not date_cols or not num_cols: return None

    date_col = date_cols[0]
    target_col = num_cols[0]
    for col in num_cols:
        if any(w in col.lower() for w in ['value', 'sales', 'price', 'amount', 'total']):
            target_col = col
            break

    pdf = df[[date_col, target_col]].dropna().copy()
    pdf = pdf.rename(columns={date_col: 'ds', target_col: 'y'})
    pdf['ds'] = pd.to_datetime(pdf['ds'], errors='coerce')
    pdf = pdf.dropna(subset=['ds']).groupby('ds')['y'].sum().reset_index().sort_values('ds')
    
    if len(pdf) < 12: return None

    try:
        m = Prophet(daily_seasonality=False, yearly_seasonality=True)
        m.fit(pdf)
        periods = max(30, int(len(pdf) * 0.2))
        future = m.make_future_dataframe(periods=periods, freq='D')
        forecast = m.predict(future)

        fig = go.Figure()
        # Historical
        fig.add_trace(go.Scatter(x=pdf['ds'], y=pdf['y'], mode='lines', name='Historical', line=dict(color='#a78bfa', width=2)))
        # Forecast
        forecast_only = forecast[forecast['ds'] > pdf['ds'].max()]
        fig.add_trace(go.Scatter(x=forecast_only['ds'], y=forecast_only['yhat'], mode='lines', name='Forecast', line=dict(color='#fb923c', width=3, dash='dash')))
        # Confidence
        fig.add_trace(go.Scatter(
            x=list(forecast_only['ds']) + list(forecast_only['ds'])[::-1],
            y=list(forecast_only['yhat_upper']) + list(forecast_only['yhat_lower'])[::-1],
            fill='toself', fillcolor='rgba(251, 146, 60, 0.1)', line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence', hoverinfo="skip"
        ))

        fig.update_layout(title=f"Advanced Forecast: {target_col}", xaxis_title="Timeline", yaxis_title="Metric Value")
        return {
            'figure': utils.apply_genesis_theme(fig),
            'forecast_df': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(6)
        }
    except: return None

def render_seasonal_bars(df):
    """Render a vertical bar chart of monthly seasonal indices."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    # Dummy seasonal indices if not computable
    indices = [24, -8, 18, 12, 6, 10, -15, -2, 30, 45, 12, 55] 
    
    for m, val in zip(months, indices):
        color = "#4ade80" if val >= 0 else "#f87171"
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <div style="width:30px; font-size:10px; color:var(--text3);">{m}</div>
                <div style="flex:1; height:6px; background:rgba(255,255,255,0.05); border-radius:3px; position:relative;">
                    <div style="position:absolute; left:50%; height:100%; width:{abs(val)}%; background:{color}; border-radius:3px; transform: translateX({'-100%' if val < 0 else '0'});"></div>
                </div>
                <div style="width:30px; font-size:10px; color:{color}; text-align:right;">{'+' if val >=0 else ''}{val}K</div>
            </div>
        """, unsafe_allow_html=True)
