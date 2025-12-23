# jbi100_app/main.py
from dash import Dash, html, dcc, Input, Output
import pandas as pd

from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.panels import compute_kpis, make_timeline, make_heatmap
from jbi100_app.data import load_hospitalbeds


def create_app():
    app = Dash(__name__)
    app.title = "Hospital Beds Control Panel"

    # DATA (UPDATED: now returns 3 values)
    df, cols, extras = load_hospitalbeds("data")

    # service values as clean strings
    services = sorted(df[cols.service].dropna().astype(str).unique().tolist())

    def kpi_card(label, value):
        return html.Div(
            className="graph_card",
            children=[
                html.H6(label),
                html.Div(value, style={"fontSize": "26px", "fontWeight": "700"}),
            ],
        )

    def _fmt_int(x):
        if x is None:
            return "n/a"
        try:
            if pd.isna(x):
                return "n/a"
        except Exception:
            pass
        try:
            return str(int(x))
        except Exception:
            return "n/a"

    def _fmt_pct(x):
        if x is None:
            return "n/a"
        try:
            if pd.isna(x):
                return "n/a"
        except Exception:
            pass
        try:
            return f"{float(x):.1%}"
        except Exception:
            return "n/a"

    app.layout = html.Div(
        className="container",
        children=[
            html.Div(
                className="row",
                children=[
                    # LEFT MENU
                    html.Div(
                        className="four columns",
                        id="left-column",
                        children=make_menu_layout(services),
                    ),
                    # RIGHT CONTENT
                    html.Div(
                        className="eight columns",
                        id="right-column",
                        children=[
                            html.Div(
                                className="row",
                                id="kpi-row",
                                children=[
                                    html.Div(className="four columns", children=kpi_card("Total Requests", "—")),
                                    html.Div(className="four columns", children=kpi_card("Total Refusals", "—")),
                                    html.Div(className="four columns", children=kpi_card("Refusal Rate", "—")),
                                ],
                            ),
                            html.Div(
                                className="graph_card",
                                children=[html.H6("Weekly Timeline"), dcc.Graph(id="timeline")],
                            ),
                            html.Div(
                                className="graph_card",
                                children=[html.H6("Service × Week Heatmap"), dcc.Graph(id="heatmap")],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )

    def metric_series(dff: pd.DataFrame, metric: str) -> pd.Series:
        if metric == "requests" and getattr(cols, "requests", None):
            return dff[cols.requests]
        if metric == "admissions" and getattr(cols, "admissions", None):
            return dff[cols.admissions]
        if metric == "refusals" and getattr(cols, "refusals", None):
            return dff[cols.refusals]
        if metric == "beds" and getattr(cols, "beds", None):
            return dff[cols.beds]
        # NEW: staff availability derived from staff_schedule.csv -> available_staff
        if metric == "staff" and getattr(cols, "staff", None):
            return dff[cols.staff]
        if metric == "refusal_rate" and getattr(cols, "requests", None) and getattr(cols, "refusals", None):
            denom = dff[cols.requests].replace(0, pd.NA)
            return (dff[cols.refusals] / denom).fillna(0)
        return pd.Series([0] * len(dff))

    @app.callback(
        Output("kpi-row", "children"),
        Output("timeline", "figure"),
        Output("heatmap", "figure"),
        Input("service-select", "value"),
        Input("timeline-metric", "value"),
        Input("heatmap-metric", "value"),
    )
    def update(service, timeline_metric, heatmap_metric):
        # Safe filter
        if service == "__ALL__" or service is None:
            dff = df
            service_label = "All services"
        else:
            dff = df[df[cols.service].astype(str) == str(service)]
            service_label = str(service)

        k = compute_kpis(dff, cols.week, cols.requests, cols.admissions, cols.refusals)

        kpis = [
            html.Div(className="four columns", children=kpi_card("Total Requests", _fmt_int(k.get("total_requests")))),
            html.Div(className="four columns", children=kpi_card("Total Refusals", _fmt_int(k.get("total_refusals")))),
            html.Div(className="four columns", children=kpi_card("Refusal Rate", _fmt_pct(k.get("refusal_rate")))),
        ]

        tl_title = f"Weekly {timeline_metric} — {service_label}"
        hm_title = f"{heatmap_metric} by Service × Week"

        tl = make_timeline(dff, cols.week, metric_series(dff, timeline_metric), tl_title)
        hm = make_heatmap(dff, cols.week, cols.service, metric_series(dff, heatmap_metric), hm_title)

        return kpis, tl, hm

    return app
