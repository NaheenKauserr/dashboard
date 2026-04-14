import os
from groq import Groq
import streamlit as st

def generate_rule_based_insights(df, stats, correlations):
    """Fallback generator for insights if API is unavailable."""
    insights_list = ["**Automated Local Analysis (API Unavailable/Quota Full):**"]
    
    # Volume insight
    insights_list.append(f"- **Data Architecture**: The dataset contains **{len(df):,}** distinct records spread across **{len(df.columns)}** metric profiles, establishing a solid foundation for robust machine learning models.")
    
    # Correlation insight
    if correlations:
        top_corr = correlations[0]
        insights_list.append(f"- **Key Driver Identified**: A significant correlation (Score: **{top_corr['score']:.2f}**) exists between `{top_corr['col1']}` and `{top_corr['col2']}`. This strong proportional relationship suggests that fluctuations in one metric reliably predict shifts in the other.")
        
    # Categorical dominant entity insight
    cat_cols = list(df.select_dtypes(['object', 'category']).columns)
    if cat_cols:
        primary_cat = cat_cols[0]
        try:
            top_val = df[primary_cat].mode().iloc[0]
            insights_list.append(f"- **Dominant Segment**: Within the `{primary_cat}` categorical division, the value **'{top_val}'** is the most frequently occurring baseline, representing the primary driving segment of your underlying operations.")
        except Exception:
            pass

    # Numeric insight
    num_cols = list(df.select_dtypes('number').columns)
    if num_cols:
        target_num = num_cols[0]
        try:
            mean_val = df[target_num].mean()
            insights_list.append(f"- **Central Tendency Focus**: The average moving baseline for `{target_num}` normalizes around **{mean_val:,.2f}**. Sharp deviations from this center point in future data payloads should trigger automatic review workflows.")
        except Exception:
            pass
            
    return "\n".join(insights_list)

@st.cache_data
def generate_insights(df, stats, correlations):
    """
    Generates AI-powered insights from data summary.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    
    if df is None or df.empty:
        return "No data available to analyze."
        
    if not api_key or api_key == "your_key_here":
        return generate_rule_based_insights(df, stats, correlations)

    try:
        client = Groq(api_key=api_key)
        
        # Prepare context data
        rows = len(df)
        cols = len(df.columns)
        numeric_cols = list(df.select_dtypes('number').columns)
        cat_cols = list(df.select_dtypes(['object', 'category']).columns)
        
        # Format stats specifically to avoid sending overly huge string
        stats_str = stats.to_csv() if not stats.empty else "None"
        import json
        corr_str = json.dumps(correlations) if correlations else "None"
        
        prompt = (
            f"Analyze this dataset summary: {rows} rows, {cols} columns, "
            f"numeric: {numeric_cols}, categorical: {cat_cols}, "
            f"key stats (describe): {stats_str}, correlations: {corr_str}. "
            "Give 3-5 bullet point insights highlighting interesting patterns or anomalies. Do not just restate the numbers, infer potential business or real-world meanings."
        )
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"API Failed: {e}")
        return generate_rule_based_insights(df, stats, correlations)


@st.cache_data(show_spinner=False)
def generate_full_report(df_shape, stats_str, cleaning_report_str, correlations_str, kpis_str, ml_results_str):
    """
    Generates a massive 10-point comprehensive report using Groq based on specific business instructions.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        return "⚠️ Add GROQ_API_KEY to generate the full comprehensive report."

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        system_prompt = (
            "You are an expert Data Scientist and Executive Analyst. "
            "Your task is to write a highly professional, comprehensive Executive Data Report following EXACTLY this structure:\n\n"
            "2. Data Overview\n"
            "- Provide a clear summary of the dataset, including number of rows and columns\n"
            "- Describe key features and their significance in the analysis\n"
            "- Specify data types (numerical, categorical, datetime, etc.)\n"
            "- Identify data quality issues such as missing values, duplicates, and inconsistencies\n\n"
            "3. Data Preparation and Cleaning\n"
            "- Summarize all preprocessing steps performed on the dataset\n"
            "- Explain how missing values were handled (removal, imputation, etc.)\n"
            "- Describe duplicate handling and data validation steps\n"
            "- Mention any feature transformations, encoding, or scaling applied\n\n"
            "4. Exploratory Data Analysis (EDA)\n"
            "- Present statistical summaries of important variables\n"
            "- Analyze distributions and variability of data\n"
            "- Identify trends, seasonality, and patterns (if applicable)\n"
            "- Perform correlation analysis and highlight significant relationships\n"
            "- Point out any anomalies or outliers observed\n\n"
            "5. Key Insights\n"
            "- Derive meaningful and non-trivial insights from the analysis\n"
            "- Focus on explaining underlying patterns, causes, and business impact\n"
            "- Avoid generic observations; prioritize high-value findings\n\n"
            "6. KPI Metrics\n"
            "- Define and compute relevant key performance indicators (KPIs)\n"
            "- Explain the significance of each KPI in a business context\n"
            "- Highlight performance trends and comparisons where applicable\n\n"
            "7. Machine Learning Insights (if applicable)\n"
            "- Specify the model(s) used and their purpose\n"
            "- Report performance metrics (e.g., accuracy, precision, recall, RMSE)\n"
            "- Identify the most influential features driving predictions\n"
            "- Briefly interpret model behavior and reliability\n\n"
            "8. Dashboard Summary\n"
            "- Describe the structure and components of the dashboard\n"
            "- Explain key visualizations and their purpose\n"
            "- Mention available filters, controls, and interactivity features\n\n"
            "9. Business Recommendations\n"
            "- Provide clear, actionable, and data-driven recommendations\n"
            "- Focus on improving outcomes, optimizing processes, or solving key problems\n"
            "- Prioritize recommendations based on impact and feasibility\n\n"
            "10. Conclusion\n"
            "- Summarize the overall findings concisely\n"
            "- Highlight the most critical insights and their implications\n"
            "- Emphasize the potential business value derived from the analysis\n\n"
            "Additional Instructions:\n"
            "- Ensure the output is structured, professional, and easy to understand using Markdown headings\n"
            "- Focus on insights and decision-making rather than just data description\n"
            "- Avoid unnecessary technical complexity\n"
            "- Maintain clarity, conciseness, and logical flow throughout the report\n"
            "- ALWAYS start with heading '## 2. Data Overview' and proceed through '## 10. Conclusion'.\n"
        )
        
        context = (
            f"Here is the raw data context for the report:\n"
            f"- DataFrame Shape (Rows, Cols): {df_shape}\n"
            f"- Summary Statistics: {stats_str}\n"
            f"- Cleaning Report (Missing values handled etc): {cleaning_report_str}\n"
            f"- Top Correlations Found: {correlations_str}\n"
            f"- Calculated KPIs (Name, Value, Description): {kpis_str}\n"
            f"- Best ML Model Insights: {ml_results_str}\n"
        )
        
        # 70B model handles 10-point complex instructions significantly better
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            model="llama-3.3-70b-versatile", 
        )
        return "# 1. Executive Summary\n\nThis fully automated Executive Report details the structural properties, statistical derivations, and actionable business intelligence extracted from the provided dataset.\n\n" + response.choices[0].message.content
        
    except Exception as e:
        return f"⚠️ Report Generation Error: {str(e)}\n\n*(Check if your GROQ API limit allows llama-3.3-70b-versatile)*"

