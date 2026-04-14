import streamlit as st
import pandas as pd

def apply_genesis_theme(fig_to_style):
    """Centralized theme applicator for Plotly charts in Genesis AI."""
    fig_to_style.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="white", size=12),
        title_font=dict(size=16, color="white", family="Inter"),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,0.1)", tickfont=dict(size=10, color="rgba(255,255,255,0.5)")),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False, linecolor="rgba(0,0,0,0)", tickfont=dict(size=10, color="rgba(255,255,255,0.5)")),
        showlegend=True,
        legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)")
    )
    return fig_to_style

def format_number(num):
    """Format large numbers to a readable string (e.g. 1M, 5K)."""
    try:
        num = float(num)
        if abs(num) >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif abs(num) >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif abs(num) >= 1_000:
            return f"{num / 1_000:.2f}K"
        elif num.is_integer():
            return str(int(num))
        else:
            return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(num)
