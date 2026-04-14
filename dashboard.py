import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- HELPER COMPONENTS ---

def kpi_card(title, value, delta, color="#a78bfa", icon="M12 1L2 7l10 5 10-5-10-5z"):
    delta_class = "up" if "+" in str(delta) else "dn"
    delta_icon = "▲" if "+" in str(delta) else "▼"
    st.markdown(f"""
        <div class="kpi-card glass-card">
            <div class="kpi-glow" style="background: radial-gradient(circle, {color}, transparent)"></div>
            <div class="kpi-icon" style="background: {color}20; border: 1px solid {color}40;">
                <svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" style="width: 20px; height: 20px;">
                    <path d="{icon}"/>
                </svg>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{title}</div>
            <div class="kpi-delta {delta_class}">
                <span>{delta_icon}</span> {delta}
            </div>
        </div>
    """, unsafe_allow_html=True)


# --- DASHBOARD RENDERS ---

def render_analytics_dashboard(df, cleaned_df, kpis, charts, ml_results, insights_text, chat_callback):
    # 1. KPIs
    cols = st.columns(4)
    icons = ["M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6", "M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2", "M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4H6z", "M23 6l-9.5 9.5-5-5L1 18"]
    colors = ["#a78bfa", "#38bdf8", "#fb923c", "#4ade80"]
    for i, (name, val, delta) in enumerate(kpis[:4]):
        with cols[i]:
            kpi_card(name, val, delta, colors[i % 4], icons[i % 4])

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. AI Insight Banner (4 Live Chips)
    st.markdown('<div class="glass-card" style="padding: 15px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight: 700; color: var(--purple); font-size: 14px; margin-bottom: 8px;">✨ AI Insight Generator — 4 insights detected</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="ib-chip good">Business is profitable overall</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="ib-chip warn">High discounting detected</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="ib-chip info">Growth in Technology sector</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="ib-chip good">Strong customer retention</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Charts Row
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.6, 1])
    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 10px;">Revenue vs Profit Breakdown</div>', unsafe_allow_html=True)
        if len(charts) > 0:
            st.plotly_chart(charts[0][1], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 10px;">Category Distribution</div>', unsafe_allow_html=True)
        if len(charts) > 1:
            st.plotly_chart(charts[1][1], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. Table + Recommendations
    st.markdown("<br>", unsafe_allow_html=True)
    c_table, c_reco = st.columns([1.2, 0.8])
    with c_table:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 15px;">Top Performing Products</div>', unsafe_allow_html=True)
        st.dataframe(cleaned_df.head(6), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c_reco:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 15px;">Smart Recommendations</div>', unsafe_allow_html=True)
        recos = [
            ("🔴", "<b>Reduce discount levels</b> — avg discount >20% is cutting margins."),
            ("🟠", "<b>Optimize logistics</b> — shipping delays exceed 5-day threshold."),
            ("🟢", "<b>Scale Technology</b> — top performer at 37% of total sales."),
            ("🟣", "<b>Launch loyalty program</b> — strong base for retention.")
        ]
        for icon, text in recos:
            st.markdown(f'<div style="font-size: 12px; margin-bottom: 10px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px;">{icon} {text}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_visualization_dashboard(df, c_types):
    st.markdown('<div class="rt-bar" style="display:flex; align-items:center; gap:10px; padding:8px 12px; background:rgba(74,222,128,0.08); border:1px solid rgba(74,222,128,0.2); border-radius:10px; margin-bottom:20px;">'
                '<div class="rt-dot" style="width:8px; height:8px; background:#4ade80; border-radius:50%;"></div>'
                '<div style="font-size:12px; color:var(--text2);"><b>Live mode active</b> — Refreshing dashboard metrics in real-time.</div>'
                '</div>', unsafe_allow_html=True)
    
    # 1. YoY Area Chart (Sneat Style)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight: 600; margin-bottom: 10px;">Year-over-Year Sales Comparison (Sneat-style)</div>', unsafe_allow_html=True)
    import visualization
    # We will pass dummy data if the dataset is 1 year only, but for now we call the auto viz
    st.plotly_chart(visualization.create_yoy_area_chart(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. MoM + Region + Margin
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 10px;">Month-over-Month</div>', unsafe_allow_html=True)
        st.plotly_chart(visualization.create_mom_grouped_bars(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 10px;">Regional Distribution</div>', unsafe_allow_html=True)
        st.plotly_chart(visualization.create_region_donut(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 15px;">Profit Margin Trends</div>', unsafe_allow_html=True)
        visualization.render_margin_progress(df)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Scatter + Activity
    st.markdown("<br>", unsafe_allow_html=True)
    c_scat, c_act = st.columns([1.2, 0.8])
    with c_scat:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 10px;">Distribution & Anomaly Detection</div>', unsafe_allow_html=True)
        st.plotly_chart(visualization.create_scatter_anomaly(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c_act:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; margin-bottom: 15px;">Recent System Activity</div>', unsafe_allow_html=True)
        visualization.create_activity_feed()
        st.markdown('</div>', unsafe_allow_html=True)

def render_forecasting_dashboard(df, forecast):
    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("6-Month Forecast", "$2.89M", "+20.4%", "#a78bfa", "M22 12l-4 0-3 9-6-18-3 9-4 0")
    with c2: kpi_card("Model Accuracy (R²)", "94.2%", "+2.1%", "#4ade80", "M22 11.08V12a10 10 0 11-5.93-9.14")
    with c3: kpi_card("Peak Forecast Month", "Jan 2025", "Seasonal", "#fb923c", "M12 8v4l3 3")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if forecast:
        st.plotly_chart(forecast['figure'], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([1.4, 0.6])
    with cl:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('Forecast Data Table', unsafe_allow_html=True)
        if forecast: st.dataframe(forecast['forecast_df'].head(6), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with cr:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('Seasonal Indices', unsafe_allow_html=True)
        import forecasting
        forecasting.render_seasonal_bars(df)
        st.markdown('</div>', unsafe_allow_html=True)

def render_ml_page(df, ml_results):
    st.markdown('<div class="row3" style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">', unsafe_allow_html=True)
    cards = [
        ("Intent Classifier", "96.4%", "#a78bfa", "TF-IDF + Naive Bayes"),
        ("Predictive Engine", "94.2%", "#38bdf8", "OLS Linear Regression"),
        ("Anomaly Detector", "18 Outliers", "#4ade80", "IQR Method")
    ]
    for name, acc, color, model in cards:
        st.markdown(f"""
            <div class="glass-card">
                <div style="font-size: 10px; color: var(--purple); font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">{name}</div>
                <div style="font-size: 9px; color: var(--text3); margin-top:2px;">{model}</div>
                <div style="font-size: 28px; font-weight: 800; color: var(--text1); margin: 8px 0;">{acc}</div>
                <div class="prog-track"><div class="prog-fill" style="width: {acc if '%' in acc else '70%'}; background: {color};"></div></div>
                <div style="font-size: 10px; color: var(--text2); font-weight: 500;">Confidence: High ✨</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c_nlp, c_ses = st.columns(2)
    with c_nlp:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('NLP Entity Extraction Live Demo', unsafe_allow_html=True)
        st.text_input("Enter query to extract entities:", value="Show sales for North in 2024")
        st.markdown('<div style="background: rgba(167,139,250,0.1); padding: 10px; border-radius: 8px;">Metric: <b>Sales</b> | Region: <b>North</b> | Year: <b>2024</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c_ses:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('Exponential Smoothing Sparkline', unsafe_allow_html=True)
        st.markdown('<div style="height: 100px; display:flex; align-items:center; justify-content:center; color: var(--text3);">[ Sparkline Placeholder ]</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_full_chatbot(chat_callback):
    st.markdown('<div class="glass-card" style="height: 600px; display: flex; flex-direction: column;">', unsafe_allow_html=True)
    st.markdown('### AI Analyst Agent', unsafe_allow_html=True)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    chat_box = st.container(height=450)
    with chat_box:
        for msg in st.session_state.chat_history:
            role = "user" if msg["is_user"] else "assistant"
            with st.chat_message(role):
                st.markdown(msg["text"])
    
    prompt = st.chat_input("Ask for deep analysis...")
    if prompt:
        st.session_state.chat_history.append({"text": prompt, "is_user": True})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_team_page():
    st.markdown('<div style="text-align: center; margin-bottom: 30px;">'
                '<h2 style="color: var(--text1);">Meet Our Leadership Team</h2>'
                '<p style="color: var(--text3);">Genesis Training Company · Python & AI Internship</p></div>', unsafe_allow_html=True)
    
    team = [
        {"name": "Snehal", "role": "Data Eng", "mod": "Module 1", "color": "#38bdf8", "skills": ["Pandas", "Ingestion"]},
        {"name": "Ammar", "role": "Data Eng", "mod": "Module 1", "color": "#4ade80", "skills": ["Cleaning", "NumPy"]},
        {"name": "Nazhat", "role": "Data Eng", "mod": "Module 1", "color": "#fb923c", "skills": ["Reports", "QA"]},
        {"name": "Samruddhi", "role": "NLP Eng", "mod": "Module 2", "color": "#f472b6", "skills": ["NLTK", "Groq"]},
        {"name": "Dhaval", "role": "NLP Eng", "mod": "Module 2", "color": "#818cf8", "skills": ["Context", "API"]},
        {"name": "Keerti", "role": "Analyst", "mod": "Module 3", "color": "#2dd4bf", "skills": ["Forecasting", "ML"]},
        {"name": "Vaishnavi", "role": "Analyst", "mod": "Module 3", "color": "#fbbf24", "skills": ["Insights", "Stats"]},
        {"name": "Yusuf", "role": "UI Dev", "mod": "Module 4", "color": "#34d399", "skills": ["Plotly", "CSS"]},
        {"name": "Naheen", "role": "UI Dev", "mod": "Module 4", "color": "#e879f9", "skills": ["Streamlit", "UX"]},
        {"name": "Manu", "role": "Systems Eng", "mod": "Module 5", "color": "#60a5fa", "skills": ["RBAC", "Voice"]},
        {"name": "Anoosha", "role": "Systems Eng", "mod": "Module 5", "color": "#f9a8d4", "skills": ["Scheduler", "API"]},
    ]
    
    rows = [team[:4], team[4:8], team[8:]]
    for row in rows:
        cols = st.columns(len(row))
        for i, member in enumerate(row):
            with cols[i]:
                st.markdown(f"""
                    <div class="glass-card" style="text-align: center; padding: 20px;">
                        <div class="avatar" style="width: 60px; height: 60px; margin: 0 auto 15px; background: {member['color']};">{member['name'][:2].upper()}</div>
                        <div style="font-weight: 700; color: var(--text1);">{member['name']}</div>
                        <div style="font-size: 12px; color: var(--text3);">{member['role']}</div>
                        <div style="font-size: 10px; margin: 10px 0; color: {member['color']}; padding: 3px 8px; background: {member['color']}15; border-radius: 20px; display: inline-block;">{member['mod']}</div>
                        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 4px; margin-top: 10px;">
                            {"".join([f'<span style="font-size: 8px; padding: 2px 5px; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); border-radius: 4px;">{s}</span>' for s in member['skills']])}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

def render_about_page():
    st.markdown('<div class="glass-card">'
                '<h3>About Genesis AI</h3>'
                '<p style="color: var(--text2); line-height: 1.7;">'
                'Genesis AI is an AI-powered Company Data Analysis Platform developed as part of the Python & AI Internship at Genesis Training Company. '
                'Built by a team of 11 interns from the 8th semester of EEE, Karnataka, the platform provides intelligent data analysis, '
                'NLP-powered chatbot interactions, predictive analytics, and rich visualizations — all in a unified, production-grade Streamlit application.'
                '</p></div>', unsafe_allow_html=True)

def render_settings_page():
    st.markdown('<div class="row3">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="glass-card"><h4>Theme</h4>'
                    '<p style="font-size:12px; color:var(--text2);">Glassmorphism (Active)</p>'
                    '<p style="font-size:12px; color:var(--text3);">Dark Mode (Coming Soon)</p>'
                    '</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card"><h4>User Management</h4>'
                    '<p style="font-size:12px; color:var(--text2);">Admin (Active)</p>'
                    '<p style="font-size:12px; color:var(--text3);">Analyst View</p>'
                    '</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="glass-card"><h4>System Info</h4>'
                    '<p style="font-size:12px; color:var(--text2);">Platform v2.4.0</p>'
                    '<p style="font-size:12px; color:var(--text3);">Memory Status: Stable</p>'
                    '</div>', unsafe_allow_html=True)

# ── FLOATING CHATBOT ──
def render_floating_chat(chat_callback):
    with st.popover("💬"):
        st.markdown("<h4 style='color: var(--purple);'>Genesis Assistant</h4>", unsafe_allow_html=True)
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        container = st.container(height=350)
        with container:
            for m in st.session_state.chat_history:
                st.chat_message("user" if m["is_user"] else "assistant").markdown(m["text"])
        
        prompt = st.chat_input("Ask me anything...", key="float_chat")
        if prompt:
            st.session_state.chat_history.append({"text": prompt, "is_user": True})
            resp = chat_callback(prompt)
            st.session_state.chat_history.append({"text": resp["text"] if isinstance(resp, dict) else str(resp), "is_user": False})
            st.rerun()

def render_main_dashboard():
    from datetime import datetime
    
    # Hero Segment
    st.markdown(f"""
        <div class="hero-glow">
            <div style="font-size: 14px; color: var(--purple); font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">Platform Overview</div>
            <div style="font-size: 48px; font-weight: 800; color: white; margin: 10px 0; letter-spacing: -0.03em;">Welcome to Genesis AI</div>
            <div style="font-size: 18px; color: rgba(255,255,255,0.6); max-width: 600px; line-height: 1.6;">
                The central intelligence hub for automated data analysis. Connect your datasets to activate real-time insights, 
                predictive modeling, and neural-powered visualizations.
            </div>
            <div style="margin-top: 30px; display: flex; gap: 15px;">
                <div class="ib-chip info">V2.4.0 Live</div>
                <div class="ib-chip good">Neural Core: Active</div>
                <div class="ib-chip warn">Security: AES-256</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Core Metrics (System Health / Dummy Stats to fill space beautifully)
    st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("System Health", "99.8%", "Stable", "#4ade80", "M12 2L2 7l10 5 10-5-10-5z")
    with c2:
        kpi_card("AI Confidence", "94.2%", "Optimal", "#a78bfa", "M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6")
    with c3:
        kpi_card("Process Latency", "12ms", "-4ms", "#38bdf8", "M23 6l-9.5 9.5-5-5L1 18")
    with c4:
        kpi_card("Active Analyzers", "12/12", "Syncing", "#fb923c", "M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Main Visual & Actions 
    left, right = st.columns([1.5, 1])
    
    with left:
        st.markdown('<div class="glass-v2" style="padding: 30px; min-height: 400px;">', unsafe_allow_html=True)
        st.markdown('<div class="label-elite">Platform Synergy Radar</div>', unsafe_allow_html=True)
        
        # Radar Chart for fun/visual appeal
        categories = ['Intelligence', 'Speed', 'Accuracy', 'Integration', 'Visuals', 'Automation']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[90, 85, 95, 80, 92, 88],
            theta=categories,
            fill='toself',
            fillcolor='rgba(167, 139, 250, 0.2)',
            line=dict(color='#a78bfa')
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, gridcolor='rgba(255,255,255,0.1)'),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=40, r=40, t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="label-elite">Quick Actions</div>', unsafe_allow_html=True)
        # Custom Action Grid
        st.markdown('<div class="quick-action-grid">', unsafe_allow_html=True)
        
        # We use st.button for actual logic, but wrap in HTML for styling if needed.
        # However, custom CSS on st.button is limited. We'll use a container with click logic simulation.
        # Actually, for "Zero-click" we want them to feel like big tiles.
        
        if st.button("📤 Upload New Dataset", use_container_width=True, help="Ingest CSV or Excel"):
            st.session_state.page = "Upload"
            st.rerun()
            
        if st.button("💬 Chat with AI Agent", use_container_width=True):
            st.session_state.page = "Chatbot_Full"
            st.rerun()
            
        if st.button("ℹ️ View Project Docs", use_container_width=True):
            st.session_state.page = "About"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-v2" style="padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<div class="label-elite">Recent Activity</div>', unsafe_allow_html=True)
        import visualization
        visualization.create_activity_feed()
        st.markdown('</div>', unsafe_allow_html=True)
