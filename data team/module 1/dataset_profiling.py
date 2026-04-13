import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_column_type(series):
    """Classify column as Numeric, Categorical, or Date."""
    if pd.api.types.is_numeric_dtype(series):
        return "Numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "Date"
    else:
        try:
            pd.to_datetime(series, infer_datetime_format=True)
            return "Date"
        except Exception:
            return "Categorical"


def generate_profiling_table(df):
    """Build a column-level profiling summary as a DataFrame."""
    rows = []
    for col in df.columns:
        series = df[col]
        col_type    = get_column_type(series)
        total       = len(series)
        missing     = series.isna().sum()
        missing_pct = round((missing / total) * 100, 2) if total > 0 else 0
        unique      = series.nunique()

        if col_type == "Numeric":
            min_val  = round(series.min(), 4)
            max_val  = round(series.max(), 4)
            mean_val = round(series.mean(), 4)
            std_val  = round(series.std(), 4)
        else:
            min_val = max_val = mean_val = std_val = "N/A"

        rows.append({
            "Column"        : col,
            "Data Type"     : col_type,
            "Missing Values": missing,
            "Missing %"     : f"{missing_pct}%",
            "Unique Values" : unique,
            "Min"           : min_val,
            "Max"           : max_val,
            "Mean"          : mean_val,
            "Std Dev"       : std_val,
        })
    return pd.DataFrame(rows)


def plot_missing_heatmap(df):
    """Return a matplotlib figure showing missing value heatmap."""
    fig, ax = plt.subplots(figsize=(max(10, len(df.columns) * 0.6), 5))
    missing_matrix = df.isnull().astype(int)
    sns.heatmap(
        missing_matrix,
        cmap="YlOrRd",
        cbar_kws={"label": "Missing (1) / Present (0)"},
        yticklabels=False,
        ax=ax,
        linewidths=0.1,
    )
    ax.set_title("Missing Value Heatmap", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Columns", fontsize=11)
    ax.set_ylabel("Rows", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.tight_layout()
    return fig


def plot_missing_bar(df):
    """Return a bar chart of missing value % per column (only columns with missing data)."""
    missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    missing_pct = missing_pct[missing_pct > 0]
    if missing_pct.empty:
        return None

    fig, ax = plt.subplots(figsize=(max(8, len(missing_pct) * 0.7), 4))
    colors = ["#d62728" if v > 30 else "#ff7f0e" if v > 10 else "#1f77b4"
              for v in missing_pct.values]
    bars = ax.bar(missing_pct.index, missing_pct.values, color=colors, edgecolor="white")
    ax.set_title("Missing Values (%) per Column", fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("Columns", fontsize=11)
    ax.set_ylabel("Missing %", fontsize=11)
    ax.set_ylim(0, 110)
    for bar, val in zip(bars, missing_pct.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=8)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.tight_layout()
    return fig


def plot_numeric_distributions(df):
    """Return a grid of histograms for numeric columns."""
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        return None

    n_cols = 3
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols,
                             figsize=(5 * n_cols, 3.5 * n_rows))
    axes = np.array(axes).flatten()

    for i, col in enumerate(numeric_cols):
        axes[i].hist(df[col].dropna(), bins=25, color="#4c72b0",
                     edgecolor="white", alpha=0.85)
        axes[i].set_title(col, fontsize=10, fontweight="bold")
        axes[i].set_xlabel("Value", fontsize=8)
        axes[i].set_ylabel("Frequency", fontsize=8)

    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("Numeric Column Distributions", fontsize=14,
                 fontweight="bold", y=1.01)
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────
#  MAIN PROFILING SECTION (called from app.py)
# ─────────────────────────────────────────────

def dataset_profiling_section(df):
    """
    Main function to render the Smart Dataset Profiling UI.
    Accepts a Pandas DataFrame from the file upload module.
    """
    st.title("📊 Smart Dataset Profiling")
    st.markdown(
        "Full structural and statistical profile of your uploaded dataset — "
        "including missing value analysis and visual insights."
    )
    st.divider()

    # ── Overview Metrics ─────────────────────
    st.subheader("📋 Dataset Overview")
    total_cells   = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    completeness  = round((1 - missing_cells / total_cells) * 100, 2) if total_cells else 0
    numeric_cols  = df.select_dtypes(include=np.number).columns.tolist()
    dup_rows      = df.duplicated().sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Rows",      f"{df.shape[0]:,}")
    col2.metric("Total Columns",   df.shape[1])
    col3.metric("Completeness",    f"{completeness}%")
    col4.metric("Duplicate Rows",  dup_rows)
    col5.metric("Numeric Columns", len(numeric_cols))

    st.divider()

    # ── Dataset Preview ──────────────────────
    with st.expander("🔍 Preview Dataset (first 10 rows)", expanded=True):
        st.dataframe(df.head(10), use_container_width=True)

    st.divider()

    # ── Profiling Table ──────────────────────
    st.subheader("📑 Column-Level Profiling Summary")
    profiling_df = generate_profiling_table(df)

    def highlight_missing(val):
        try:
            pct = float(str(val).replace("%", ""))
            if pct > 30:
                return "background-color: #ffcccc"
            elif pct > 10:
                return "background-color: #fff3cd"
            else:
                return ""
        except Exception:
            return ""

    styled = profiling_df.style.map(highlight_missing, subset=["Missing %"])
    st.dataframe(styled, use_container_width=True, height=350)
    st.caption("🟥 >30% missing  |  🟨 10–30% missing  |  ⬜ <10% missing")

    st.divider()

    # ── Missing Value Visualizations ─────────
    st.subheader("🕳️ Missing Value Analysis")
    tab1, tab2 = st.tabs(["Heatmap", "Bar Chart"])

    with tab1:
        st.markdown("Each cell shows whether a value is **missing (dark)** or **present (light)**.")
        st.pyplot(plot_missing_heatmap(df))

    with tab2:
        fig_bar = plot_missing_bar(df)
        if fig_bar:
            st.pyplot(fig_bar)
        else:
            st.success("🎉 No missing values found in this dataset!")

    st.divider()

    # ── Numeric Distributions ────────────────
    if numeric_cols:
        st.subheader("📈 Numeric Column Distributions")
        fig_dist = plot_numeric_distributions(df)
        if fig_dist:
            st.pyplot(fig_dist)
        st.divider()

    # ── Descriptive Statistics ───────────────
    st.subheader("🔢 Descriptive Statistics (Numeric Columns)")
    if numeric_cols:
        st.dataframe(df[numeric_cols].describe().T.round(4), use_container_width=True)
    else:
        st.info("No numeric columns found in this dataset.")

    st.divider()

    # ── Categorical Summary ──────────────────
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    if cat_cols:
        st.subheader("🏷️ Categorical Column Summary")
        cat_data = []
        for col in cat_cols:
            top_val   = df[col].value_counts().idxmax() if df[col].notna().any() else "N/A"
            top_count = df[col].value_counts().max()    if df[col].notna().any() else 0
            cat_data.append({
                "Column"       : col,
                "Unique Values": df[col].nunique(),
                "Top Value"    : top_val,
                "Top Count"    : top_count,
                "Missing %"    : f"{round(df[col].isna().mean() * 100, 2)}%",
            })
        st.dataframe(pd.DataFrame(cat_data), use_container_width=True)
        st.divider()

    # ── Download Report ──────────────────────
    st.subheader("⬇️ Download Profiling Report")
    csv_buffer = io.StringIO()
    profiling_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Profiling Summary (CSV)",
        data=csv_buffer.getvalue(),
        file_name="profiling_report.csv",
        mime="text/csv",
    )
