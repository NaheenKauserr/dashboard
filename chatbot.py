import os
from groq import Groq
import streamlit as st
import json

def chat_response(query, df, column_types):
    """
    Handles the chatbot responses and visualization generation.
    Returns: dict {"text": string, "code": string/None}
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        return {"text": "⚠️ Add GROQ_API_KEY to .env to enable the chatbot.", "code": None}
        
    if df is None or df.empty:
        return {"text": "No dataset is currently loaded.", "code": None}

    try:
        client = Groq(api_key=api_key)
        
        # Prepare Data Context
        col_names = list(df.columns)
        row_cnt = len(df)
        
        # Only take a tiny sample
        sample_df = df.head(5)
        sample_csv = sample_df.to_csv(index=False)
        
        system_instructions = (
            "You are an expert Data Analyst AI for a premium glassmorphism dashboard. "
            "You are provided with a dataset context. The user will ask questions.\n"
            "If the question requires a visual chart, you MUST generate valid python code using 'plotly.express as px' to create a figure named `fig`.\n"
            "IMPORTANT DASHBOARD STYLING (GENESIS THEME):\n"
            "- Set paper_bgcolor='rgba(0,0,0,0)' and plot_bgcolor='rgba(0,0,0,0)'.\n"
            "- Use font color 'rgba(255,255,255,0.9)'.\n"
            "- Use color scale 'Viridis' or discrete colors: ['#a78bfa', '#38bdf8', '#4ade80', '#fb923c'].\n"
            "- Remove gridlines: fig.update_xaxes(showgrid=False), fig.update_yaxes(showgrid=False).\n"
            "Wrap ONLY your code tightly in a ```python block."
        )
        
        context = (
            f"Dataset context:\n"
            f"- Columns: {col_names}\n"
            f"- Shape: {row_cnt} rows\n"
            f"- Sample data:\n{sample_csv}\n\n"
        )
        
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": context + f"User Question: {query}"}
        ]
        
        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
        )
        text_resp = response.choices[0].message.content
        
        # Parse for code
        import re
        code_match = re.search(r'```python(.*?)```', text_resp, re.DOTALL)
        code = None
        if code_match:
            code = code_match.group(1).strip()
            # Remove the code block from the text response
            text_resp = text_resp.replace(code_match.group(0), "").strip()
            if not text_resp:
                text_resp = "Here is the visualization you requested:"
                
        return {"text": text_resp, "code": code}
        
    except Exception as e:
        return {"text": f"⚠️ Chat error: {str(e)}", "code": None}


