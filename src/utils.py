"""
SummitBridge Analytics - Utilities
Helper functions for formatting, visualization, and common operations.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


# Color palettes
COLOR_SEQ = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
COLOR_MAP = {
    'Avoidable': '#d62728',
    'Potentially Avoidable': '#ff7f0e',
    'Non-Avoidable': '#2ca02c',
    'Commercial': '#1f77b4',
    'Marketplace': '#ff7f0e',
    'Medicare Advantage': '#2ca02c',
    'In-Network': '#2ca02c',
    'Out-of-Network': '#d62728',
}


def format_currency(value: float, decimals: int = 0) -> str:
    """Format number as currency string."""
    if pd.isna(value):
        return "N/A"
    if abs(value) >= 1e9:
        return f"${value/1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.{decimals}f}K"
    else:
        return f"${value:,.{decimals}f}"


def format_pct(value: float, decimals: int = 1) -> str:
    """Format number as percentage string."""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_number(value: float, decimals: int = 0) -> str:
    """Format number with commas."""
    if pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def create_kpi_gauge(value: float, target: float, title: str, 
                     higher_is_better: bool = False,
                     suffix: str = "") -> go.Figure:
    """Create a gauge chart for KPI tracking."""
    # Determine gauge color based on performance
    if higher_is_better:
        if value >= target:
            color = "green"
        elif value >= target * 0.8:
            color = "yellow"
        else:
            color = "red"
    else:
        if value <= target:
            color = "green"
        elif value <= target * 1.2:
            color = "yellow"
        else:
            color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        delta={'reference': target, 'relative': True, 'valueformat': '.1%'},
        gauge={
            'axis': {'range': [None, max(value, target) * 1.5]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, target * 0.5], 'color': "lightgray"},
                {'range': [target * 0.5, target], 'color': "gray"},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        },
        number={'suffix': suffix, 'font': {'size': 24}}
    ))
    
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def create_trend_chart(df: pd.DataFrame, x: str, y: str, color: str = None,
                       title: str = "", y_title: str = "", 
                       target_line: float = None) -> go.Figure:
    """Create a trend line chart with optional target line."""
    fig = px.line(df, x=x, y=y, color=color, title=title, markers=True,
                  color_discrete_sequence=COLOR_SEQ)
    
    if target_line is not None:
        fig.add_hline(y=target_line, line_dash="dash", line_color="red",
                      annotation_text=f"Target: {target_line}", 
                      annotation_position="bottom right")
    
    fig.update_layout(
        height=400,
        xaxis_title=x.replace('_', ' ').title(),
        yaxis_title=y_title or y.replace('_', ' ').title(),
        hovermode='x unified',
        legend_title_text=color.replace('_', ' ').title() if color else None
    )
    
    return fig


def create_bar_chart(df: pd.DataFrame, x: str, y: str, color: str = None,
                     title: str = "", y_title: str = "",
                     text_auto: str = '.2s', horizontal: bool = False) -> go.Figure:
    """Create a bar chart with consistent styling."""
    if horizontal:
        fig = px.bar(df, x=y, y=x, color=color, title=title, orientation='h',
                     color_discrete_sequence=COLOR_SEQ, text_auto=text_auto)
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    else:
        fig = px.bar(df, x=x, y=y, color=color, title=title,
                     color_discrete_sequence=COLOR_SEQ, text_auto=text_auto)
    
    fig.update_layout(
        height=400,
        xaxis_title=x.replace('_', ' ').title() if not horizontal else y_title,
        yaxis_title=y_title or y.replace('_', ' ').title() if not horizontal else x.replace('_', ' ').title(),
        showlegend=color is not None,
        hovermode='x unified' if not horizontal else 'y unified'
    )
    
    return fig


def create_pie_chart(df: pd.DataFrame, values: str, names: str, 
                     title: str = "", hole: float = 0) -> go.Figure:
    """Create a pie/donut chart."""
    fig = px.pie(df, values=values, names=names, title=title, hole=hole,
                 color_discrete_sequence=COLOR_SEQ)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig


def create_waterfall_chart(categories: List[str], values: List[float], 
                           title: str = "") -> go.Figure:
    """Create a waterfall chart for savings scenarios."""
    fig = go.Figure(go.Waterfall(
        name="Savings",
        orientation="v",
        measure=["relative"] * len(categories),
        x=categories,
        textposition="outside",
        text=[format_currency(v) for v in values],
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(title=title, height=500, showlegend=False)
    return fig


def create_heatmap(df: pd.DataFrame, title: str = "", 
                   colorscale: str = "RdYlGn_r") -> go.Figure:
    """Create a heatmap from a pivot table."""
    fig = px.imshow(df, title=title, color_continuous_scale=colorscale,
                    text_auto='.1f', aspect="auto")
    fig.update_layout(height=400)
    return fig


def save_figure(fig: go.Figure, path: str, format: str = "html") -> None:
    """Save plotly figure to file."""
    if format == "html":
        fig.write_html(path)
    elif format == "png":
        fig.write_image(path)
    elif format == "pdf":
        fig.write_image(path)
    logger.info(f"Saved figure to {path}")


def print_section(title: str, char: str = "=") -> None:
    """Print a formatted section header."""
    print(f"\n{char * 60}")
    print(title)
    print(char * 60)


def print_kpi_table(kpi_df: pd.DataFrame) -> None:
    """Pretty print KPI DataFrame."""
    for _, row in kpi_df.iterrows():
        current = row.get('current', 'N/A')
        target = row.get('target', 'N/A')
        print(f"  {row['kpi']}: {current} (Target: {target})")


def calculate_pmpm(allowed_amount: float, member_months: float) -> float:
    """Calculate PMPM safely."""
    if member_months == 0:
        return 0
    return allowed_amount / member_months


def calculate_rate(numerator: int, denominator: float, per: int = 1000) -> float:
    """Calculate rate per N (e.g., per 1000)."""
    if denominator == 0:
        return 0
    return numerator / denominator * per


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """Safe division with default."""
    if denominator == 0:
        return default
    return numerator / denominator


def get_top_n(df: pd.DataFrame, value_col: str, n: int = 10, 
              group_col: str = None) -> pd.DataFrame:
    """Get top N rows by value column, optionally within groups."""
    if group_col:
        return df.groupby(group_col).apply(
            lambda x: x.nlargest(n, value_col)
        ).reset_index(drop=True)
    return df.nlargest(n, value_col)


def pivot_kpi_by_dimension(kpi_df: pd.DataFrame, dimension: str, 
                           value_col: str = 'value') -> pd.DataFrame:
    """Pivot KPI results by a dimension for heatmap."""
    return kpi_df.pivot_table(index='kpi', columns=dimension, values=value_col, aggfunc='first')