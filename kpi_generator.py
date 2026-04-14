import streamlit as st
import numpy as np
import pandas as pd
import data_analysis
import utils

def format_kpi_value(col_name, value):
    """
    Formats the value appropriately (percentage, currency, or standard format)
    depending on the column name semantics.
    """
    col_lower = str(col_name).lower()
    
    # Check for percentage-like fields
    if any(keyword in col_lower for keyword in ['percentage', 'rate', 'margin', 'discount']):
        # If float looks like a fraction (e.g. 0.15), multiply by 100
        if pd.notna(value) and abs(value) <= 1.0 and value != 0:
            return f"{value * 100:.1f}%"
        return f"{value:.1f}%"
        
    val_str = utils.format_number(value)
    
    # Check for monetary fields
    if any(keyword in col_lower for keyword in ['price', 'cost', 'revenue', 'sales', 'amount', 'profit', 'budget']):
        return f"${val_str}"
        
    return val_str

def generate_kpis(df, column_types):
    """
    Generates dynamic, logically accurate KPIs grouping metrics by Volumes (Sums),
    Averages, Categories, and Timeline metrics.
    Returns: list of tuples (name, value, delta_or_caption)
    """
    kpis = []
    
    if df is None or df.empty:
        return kpis
        
    import data_cleaning
    report = data_cleaning.get_cleaning_report()
    
    # --- Group 1: Dataset Health ---
    kpis.append(("Total Records", f"{len(df):,}", "Rows analyzed in dataset"))
    
    if report.get("missing_filled", 0) > 0:
        kpis.append(("Missing Data Repaired", f"{report['missing_filled']:,}", "Imputed preserving data integrity"))

    raw_numeric_cols = column_types.get("numeric", [])
    # Exclude strict IDs from aggregations
    numeric_cols = [c for c in raw_numeric_cols if 'id' not in c.lower() and 'index' not in c.lower() and 'code' not in c.lower()]
    cat_cols = column_types.get("categorical", [])
    date_cols = column_types.get("datetime", [])
    
    used_num_cols = set()

    # --- Group 2: Volume Metrics (Total / SUM) ---
    # Metrics where accumulating the values makes business sense 
    volume_keywords = ['sales', 'revenue', 'profit', 'amount', 'total', 'cost', 'qty', 'quantity', 'volume', 'budget']
    sum_candidates = [c for c in numeric_cols if any(word in c.lower() for word in volume_keywords)]
        
    for col in sum_candidates[:3]: # Cap at 3 volume metrics
        total_sum = df[col].sum()
        avg_val = df[col].mean()
        
        val_str = format_kpi_value(col, total_sum)
        avg_str = format_kpi_value(col, avg_val)
        
        # Abbreviate name
        col_short = str(col)[:15] + ("..." if len(str(col)) > 15 else "")
        kpis.append((f"Total {col_short}", val_str, f"Average: {avg_str} / row"))
        used_num_cols.add(col)
        
    # --- Group 3: Ratio & Continuous Metrics (Average / MEAN) ---
    # Metrics where summing is nonsensical (e.g., Age, Ratings, Scores). We find the Average.
    remaining_nums = [c for c in numeric_cols if c not in used_num_cols]
    
    for col in remaining_nums[:3]: # Cap at 3 average metrics
        avg_val = df[col].mean()
        min_val, max_val = df[col].min(), df[col].max()
        
        val_str = format_kpi_value(col, avg_val)
        min_str = format_kpi_value(col, min_val)
        max_str = format_kpi_value(col, max_val)
        
        col_short = str(col)[:15] + ("..." if len(str(col)) > 15 else "")
        kpis.append((f"Average {col_short}", val_str, f"Range: {min_str} to {max_str}"))
        used_num_cols.add(col)

    # --- Group 4: Predictive Correlation ---
    correlations = data_analysis.find_correlations(df)
    if correlations:
        top_corr = correlations[0]
        col1_short = str(top_corr['col1'])[:12] + ("..." if len(str(top_corr['col1'])) > 12 else "")
        col2_short = str(top_corr['col2'])[:12] + ("..." if len(str(top_corr['col2'])) > 12 else "")
        kpis.append((f"Max Correlation", f"{top_corr['score']:.2f}", f"Between {col1_short} & {col2_short}"))

    # --- Group 5: Categorical Insights ---
    for col in cat_cols:
        if df[col].nunique() > 1:
            try:
                top_val = df[col].mode().iloc[0]
                top_count = (df[col] == top_val).sum()
                col_short = str(col)[:15] + ("..." if len(str(col)) > 15 else "")
                val_format = str(top_val)[:22] + ("..." if len(str(top_val)) > 22 else "")
                
                kpis.append((f"Top {col_short}", f"{utils.format_number(top_count)}", f"Value: '{val_format}'"))
                break # Highlight only the most prominent categorical column
            except Exception:
                pass

    # --- Group 6: Business-Aware Synthesis ---
    # Smart logic to combine metrics
    cols_l = [c.lower() for c in numeric_cols]
    if 'revenue' in cols_l and 'cost' in cols_l:
        r_col = numeric_cols[cols_l.index('revenue')]
        c_col = numeric_cols[cols_l.index('cost')]
        total_rev = df[r_col].sum()
        total_cost = df[c_col].sum()
        if total_rev > 0:
            margin = (total_rev - total_cost) / total_rev
            kpis.insert(1, ("Gross Margin %", f"{margin*100:.1f}%", "Calculated from Revenue & Cost"))

    if 'profit' in cols_l and 'revenue' in cols_l:
        p_col = numeric_cols[cols_l.index('profit')]
        r_col = numeric_cols[cols_l.index('revenue')]
        total_profit = df[p_col].sum()
        total_rev = df[r_col].sum()
        if total_rev > 0:
            p_margin = total_profit / total_rev
            kpis.insert(2, ("Profit Margin", f"{p_margin*100:.1f}%", "Overall profitability ratio"))

    # --- Group 6: Timeline Breadth ---
    if date_cols:
        d_col = date_cols[0]
        min_d, max_d = df[d_col].min(), df[d_col].max()
        if pd.notna(min_d) and pd.notna(max_d):
            days = (max_d - min_d).days
            col_short = str(d_col)[:10]
            kpis.append((f"Timeline ({col_short})", f"{days} Days", f"{min_d.strftime('%b %d, %Y')} to {max_d.strftime('%b %d, %Y')}"))
            
    # Pad to ensure grid integrity
    return kpis[:12]
