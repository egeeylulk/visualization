# jbi100_app/views/panels.py
from typing import Optional
import pandas as pd
import plotly.express as px


def compute_kpis(
    df: pd.DataFrame,
    week_col: str,
    req: Optional[str],
    adm: Optional[str],
    ref: Optional[str],
):

    total_requests = float(df[req].sum()) if req else None
    total_adm = float(df[adm].sum()) if adm else None
    total_ref = float(df[ref].sum()) if ref else None
    rate = None
    if req and ref and df[req].sum() != 0:
        rate = float(df[ref].sum() / df[req].sum())
    latest_week = None
    try:
        latest_week = df[week_col].max()
    except Exception:
        pass
    return {
        "total_requests": total_requests,
        "total_admissions": total_adm,
        "total_refusals": total_ref,
        "refusal_rate": rate,
        "latest_week": latest_week,
    }


def make_timeline(df: pd.DataFrame, week_col: str, value_series: pd.Series, title: str):
    dff = df[[week_col]].copy()
    dff["value"] = value_series.values
    agg = dff.groupby(week_col, dropna=False)["value"].sum().reset_index()
    fig = px.line(agg, x=week_col, y="value", markers=True, title=title)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def make_heatmap(df: pd.DataFrame, week_col: str, service_col: str, values: pd.Series, title: str):
    dff = df[[week_col, service_col]].copy()
    dff["value"] = values.values
    pivot = dff.pivot_table(index=service_col, columns=week_col, values="value", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, aspect="auto", title=title)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig
