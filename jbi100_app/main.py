from dash import Dash, html, dcc, Input, Output, State
import pandas as pd

from .views.menu import make_menu_layout
from .views.panels import (
    make_heatmap_locator,
    make_diagnostic_timeline,
    make_impact_validation,
)
from .data import load_hospitalbeds


def create_app():
    app = Dash(__name__)
    app.title = "BedFlow Diagnostic Dashboard"

    df, cols, extras = load_hospitalbeds("data")

    services = sorted(df[cols.service].dropna().astype(str).unique().tolist())
    events = []
    if cols.event and cols.event in df.columns:
        events = sorted(df[cols.event].dropna().astype(str).unique().tolist())
    max_week = int(df[cols.week].max()) if cols.week else 52

    morale_col = None
    satisfaction_col = None
    for col in df.columns:
        if "morale" in col.lower():
            morale_col = col
        if "satisfaction" in col.lower():
            satisfaction_col = col

    app.layout = html.Div(
        className="container",
        children=[
            dcc.Store(
                id="global-state",
                data={
                    "selected_service": None,
                    "selected_week": None,
                    "diagnostic_focus": "refusal_rate",
                    "visible_events": ["flu", "strike", "donation"],
                    "service_filter": "__ALL__",
                    "brush_range": None,
                    "brush_source": None,
                },
            ),
            html.Div(
                className="dashboard-layout",
                children=[
                    html.Div(
                        className="sidebar",
                        id="left-column",
                        children=[
                            html.Button(
                                "☰ Controls",
                                id="sidebar-toggle",
                                className="sidebar-toggle",
                            ),
                            html.Div(
                                id="sidebar-content",
                                className="sidebar-content",
                                children=make_menu_layout(services, events, max_week),
                            ),
                        ],
                    ),
                    html.Div(
                        className="main-content",
                        id="right-column",
                        children=[
                            html.Div(
                                className="view-section view-1",
                                id="view-1-section",
                                children=[
                                    html.Div(
                                        className="graph_card",
                                        children=[
                                            html.Div(
                                                className="view-header",
                                                children=[
                                                    html.H5(
                                                        "Problem Locator",
                                                        style={
                                                            "color": "#2c3e50",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Where and when do abnormal refusal rates occur?",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#666",
                                                            "margin": "4px 0 0 0",
                                                        },
                                                    ),
                                                ],
                                            ),
                                            html.P(
                                                "Click a cell to select service-week for diagnosis →",
                                                style={
                                                    "fontSize": "11px",
                                                    "color": "#888",
                                                    "marginBottom": "8px",
                                                    "fontStyle": "italic",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="heatmap",
                                                style={"height": "320px"},
                                                config={
                                                    "displayModeBar": True,
                                                    "displaylogo": False,
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                id="placeholder-section",
                                className="placeholder-section",
                                children=[
                                    html.Div(
                                        className="placeholder-content",
                                        children=[
                                            html.Div(
                                                className="placeholder-icon",
                                                children=[
                                                    html.Span(
                                                        "🔍", style={"fontSize": "48px"}
                                                    ),
                                                ],
                                            ),
                                            html.H5(
                                                "Select a cell to investigate",
                                                style={
                                                    "color": "#2c3e50",
                                                    "marginTop": "16px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.P(
                                                "Click a dark red cell in the heatmap above — "
                                                "these indicate potential problem areas requiring diagnosis.",
                                                style={
                                                    "color": "#666",
                                                    "fontSize": "13px",
                                                    "maxWidth": "400px",
                                                    "margin": "8px auto",
                                                },
                                            ),
                                            html.Div(
                                                className="preview-cards",
                                                style={
                                                    "display": "flex",
                                                    "gap": "20px",
                                                    "justifyContent": "center",
                                                    "marginTop": "24px",
                                                    "flexWrap": "wrap",
                                                },
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.P(
                                                                "Diagnose",
                                                                style={
                                                                    "fontSize": "12px",
                                                                    "color": "#666",
                                                                    "margin": "4px 0 0",
                                                                },
                                                            ),
                                                            html.P(
                                                                "Why did this happen?",
                                                                style={
                                                                    "fontSize": "10px",
                                                                    "color": "#999",
                                                                    "margin": "0",
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "textAlign": "center",
                                                            "padding": "12px",
                                                        },
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.P(
                                                                "Validate",
                                                                style={
                                                                    "fontSize": "12px",
                                                                    "color": "#666",
                                                                    "margin": "4px 0 0",
                                                                },
                                                            ),
                                                            html.P(
                                                                "What was the impact?",
                                                                style={
                                                                    "fontSize": "10px",
                                                                    "color": "#999",
                                                                    "margin": "0",
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "textAlign": "center",
                                                            "padding": "12px",
                                                        },
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="view-section view-2",
                                id="view-2-section",
                                style={"display": "none"},
                                children=[
                                    html.Div(
                                        className="graph_card",
                                        children=[
                                            html.Div(
                                                className="view-header",
                                                children=[
                                                    html.H5(
                                                        "Diagnostic Decomposition",
                                                        style={
                                                            "color": "#2c3e50",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Why did refusals increase here? (Multi-factor causal analysis)",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#666",
                                                            "margin": "4px 0 0 0",
                                                        },
                                                    ),
                                                ],
                                            ),
                                            dcc.Graph(
                                                id="diagnostic-timeline",
                                                style={"height": "650px"},
                                                config={
                                                    "displayModeBar": True,
                                                    "displaylogo": False,
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="view-section view-3",
                                id="view-3-section",
                                style={"display": "none"},
                                children=[
                                    html.Div(
                                        className="graph_card",
                                        children=[
                                            html.Div(
                                                className="view-header",
                                                children=[
                                                    html.H5(
                                                        "Impact Validation",
                                                        style={
                                                            "color": "#2c3e50",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Did this operational failure have consequences?",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#666",
                                                            "margin": "4px 0 0 0",
                                                        },
                                                    ),
                                                ],
                                            ),
                                            dcc.Graph(
                                                id="impact-validation",
                                                style={"height": "320px"},
                                                config={
                                                    "displayModeBar": True,
                                                    "displaylogo": False,
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    def metric_series(dff: pd.DataFrame, metric: str) -> pd.Series:
       
        if metric == "refusal_rate" and cols.refusal_rate:
            return dff[cols.refusal_rate]
        if metric == "bed_utilization" and cols.bed_utilization:
            return dff[cols.bed_utilization]
        if metric == "patients_per_staff" and cols.patients_per_staff:
            return dff[cols.patients_per_staff]
        if cols.refusal_rate:
            return dff[cols.refusal_rate]
        if cols.requests and cols.refusals:
            denom = dff[cols.requests].replace(0, pd.NA)
            return (dff[cols.refusals] / denom).fillna(0)
        return pd.Series([0] * len(dff))

    @app.callback(
        Output("global-state", "data"),
        Input("heatmap", "clickData"),
        Input("clear-selection-btn", "n_clicks"),
        Input("service-select", "value"),
        State("global-state", "data"),
        prevent_initial_call=True,
    )
    def update_selection(
        click_data, clear_clicks, service_filter, current_state
    ):
        from dash import callback_context

        if not callback_context.triggered:
            return current_state

        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "clear-selection-btn":
            current_state["selected_service"] = None
            current_state["selected_week"] = None
            current_state["brush_range"] = None
            current_state["brush_source"] = None
            return current_state

        if triggered_id == "service-select":
            current_state["service_filter"] = service_filter
            selected_service = current_state.get("selected_service")

            if selected_service is not None:
                if service_filter != "__ALL__" and service_filter != selected_service:
                    current_state["selected_service"] = None
                    current_state["selected_week"] = None
            return current_state

        if triggered_id == "heatmap" and click_data:
            try:
                point = click_data["points"][0]
                service = point["y"]
                week = int(point["x"])

                if (
                    current_state.get("selected_service") == service
                    and current_state.get("selected_week") == week
                ):
                    current_state["selected_service"] = None
                    current_state["selected_week"] = None
                else:
                    current_state["selected_service"] = service
                    current_state["selected_week"] = week

                current_state["brush_range"] = None  
                current_state["brush_source"] = None

                return current_state
            except (KeyError, IndexError, TypeError):
                return current_state

        return current_state

    @app.callback(
        Output("diagnostic-focus", "value"),
        Output("event-visibility", "value"),
        Input("global-state", "data"),
    )
    def sync_controls_from_state(state):
        return (
            state.get("diagnostic_focus", "refusal_rate"),
            state.get("visible_events", ["flu", "strike", "donation"]),
        )

    @app.callback(
        Output("global-state", "data", allow_duplicate=True),
        Input("diagnostic-focus", "value"),
        Input("event-visibility", "value"),
        State("global-state", "data"),
        prevent_initial_call=True,
    )
    def update_state_from_controls(diagnostic_focus, visible_events, state):
        state["diagnostic_focus"] = diagnostic_focus
        state["visible_events"] = visible_events or []
        return state

    @app.callback(
        Output("selection-display", "children"),
        Input("global-state", "data"),
    )
    def update_selection_display(state):
        service = state.get("selected_service")
        week = state.get("selected_week")

        if service and week:
            service_display = service.replace("_", " ").title()
            return []
        else:
            return []

    @app.callback(
        Output("view-2-section", "style"),
        Output("view-3-section", "style"),
        Output("placeholder-section", "style"),
        Input("global-state", "data"),
    )
    def update_view_visibility(state):
        has_selection = state.get("selected_service") and state.get("selected_week")

        if has_selection:
            return (
                {"display": "block"},  
                {"display": "block"},  
                {"display": "none"},  
            )
        else:
            return (
                {"display": "none"},  
                {"display": "none"},  
                {"display": "block"},  
            )

    @app.callback(
        Output("heatmap", "figure"),
        Input("global-state", "data"),
        Input("week-range", "value"),
    )
    def update_heatmap(state, week_range):
        service_filter = state.get("service_filter", "__ALL__")
        diagnostic_focus = state.get("diagnostic_focus", "refusal_rate")
        selected_week = state.get("selected_week")
        selected_service = state.get("selected_service")

        dff_heatmap = df.copy()
        if week_range:
            dff_heatmap = dff_heatmap[
                (dff_heatmap[cols.week] >= week_range[0])
                & (dff_heatmap[cols.week] <= week_range[1])
            ]

        focus_labels = {
            "refusal_rate": "Refusal Rate",
            "patients_per_staff": "Staffing Pressure",
            "bed_utilization": "Bed Saturation",
        }
        hm_title = f"{focus_labels.get(diagnostic_focus, 'Metric')} by Service × Week"

        return make_heatmap_locator(
            dff_heatmap,
            cols.week,
            cols.service,
            metric_series(dff_heatmap, diagnostic_focus),
            hm_title,
            selected_week=selected_week,
            selected_service=selected_service,
            service_filter=service_filter,
        )

    @app.callback(
        Output("global-state", "data", allow_duplicate=True),
        Input("diagnostic-timeline", "selectedData"),
        Input("impact-validation", "selectedData"),
        State("global-state", "data"),
        prevent_initial_call=True
    )
    def update_brush_selection(sel_diag, sel_impact, state):
        from dash import callback_context, no_update

        if not callback_context.triggered:
            return no_update

        triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        selected_data = sel_diag if triggered_id == "diagnostic-timeline" else sel_impact

        range_val = None
        if selected_data and "range" in selected_data and "x" in selected_data["range"]:
             range_val = selected_data["range"]["x"]

        if range_val is None:
            return no_update

        if state.get("brush_range") == range_val:
            return no_update

        state["brush_range"] = range_val
        state["brush_source"] = None 
        return state

    @app.callback(
        Output("diagnostic-timeline", "figure"),
        Input("global-state", "data"),
        Input("week-range", "value"),
    )
    def update_diagnostic_timeline(state, week_range):
        selected_service = state.get("selected_service")
        selected_week = state.get("selected_week")
        visible_events = state.get("visible_events", [])
        diagnostic_focus = state.get("diagnostic_focus", "refusal_rate")
        service_filter = state.get("service_filter", "__ALL__")
        brush_range = state.get("brush_range")

        dff = df.copy()
        if week_range:
            dff = dff[
                (dff[cols.week] >= week_range[0]) & (dff[cols.week] <= week_range[1])
            ]

        if service_filter and service_filter != "__ALL__":
            dff = dff[dff[cols.service] == service_filter]

        return make_diagnostic_timeline(
            dff,
            week_col=cols.week,
            service_col=cols.service,
            requests_col=cols.requests,
            admitted_col=cols.admissions,
            refused_col=cols.refusals,
            beds_col=cols.beds,
            staff_col=cols.staff,
            bed_utilization_col=cols.bed_utilization,
            patients_per_staff_col=cols.patients_per_staff,
            event_col=cols.event,
            visible_events=visible_events,
            selected_service=selected_service,
            selected_week=selected_week,
            diagnostic_focus=diagnostic_focus,
            highlight_range=brush_range,
        )

    @app.callback(
        Output("impact-validation", "figure"),
        Input("global-state", "data"),
        Input("week-range", "value"),
    )
    def update_impact_validation(state, week_range):
        selected_service = state.get("selected_service")
        selected_week = state.get("selected_week")
        service_filter = state.get("service_filter", "__ALL__")
        brush_range = state.get("brush_range")

        dff = df.copy()
        if week_range:
            dff = dff[
                (dff[cols.week] >= week_range[0]) & (dff[cols.week] <= week_range[1])
            ]

        if service_filter and service_filter != "__ALL__":
            dff = dff[dff[cols.service] == service_filter]

        return make_impact_validation(
            dff,
            week_col=cols.week,
            service_col=cols.service,
            morale_col=morale_col,
            satisfaction_col=satisfaction_col,
            selected_service=selected_service,
            selected_week=selected_week,
            highlight_range=brush_range,
        )

    app.clientside_callback(
        """
        function(state) {
            if (state && state.selected_service && state.selected_week) {
                setTimeout(function() {
                    var view2 = document.getElementById('view-2-section');
                    if (view2) {
                        var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
                        view2.scrollIntoView({
                            behavior: prefersReducedMotion ? 'auto' : 'smooth',
                            block: 'start'
                        });
                    }
                }, 150);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("view-2-section", "data-scroll-trigger"),
        Input("global-state", "data"),
    )

    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks) {
                var sidebar = document.getElementById('sidebar-content');
                if (sidebar) {
                    sidebar.classList.toggle('sidebar-expanded');
                }
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("sidebar-content", "data-toggle-trigger"),
        Input("sidebar-toggle", "n_clicks"),
    )

    return app
