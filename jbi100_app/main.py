# jbi100_app/main.py
"""
BedFlow Diagnostic Dashboard - Main Application
================================================
Implements the three-view diagnostic architecture:
1. VIEW 1 - Problem Locator (Heatmap) - Always visible
2. VIEW 2 - Diagnostic Decomposition (Multi-factor Timeline)
3. VIEW 3 - Impact Validation (Morale & Satisfaction)

Layout follows the specification:
- Left Control Panel (sidebar)
- Main content area with three coordinated views

Workflow: Locate → Diagnose → Validate → Explain
"""

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
    """Create and configure the Dash application."""
    app = Dash(__name__)
    app.title = "BedFlow Diagnostic Dashboard"

    # ========== DATA LOADING ==========
    df, cols, extras = load_hospitalbeds("data")

    # Extract metadata
    services = sorted(df[cols.service].dropna().astype(str).unique().tolist())
    events = []
    if cols.event and cols.event in df.columns:
        events = sorted(df[cols.event].dropna().astype(str).unique().tolist())
    max_week = int(df[cols.week].max()) if cols.week else 52

    # Detect morale and satisfaction columns
    morale_col = None
    satisfaction_col = None
    for col in df.columns:
        if "morale" in col.lower():
            morale_col = col
        if "satisfaction" in col.lower():
            satisfaction_col = col

    # ========== LAYOUT ==========
    app.layout = html.Div(
        className="container",
        children=[
            # ========== GLOBAL STATE STORE ==========
            dcc.Store(
                id="global-state",
                data={
                    "selected_service": None,
                    "selected_week": None,
                    "diagnostic_focus": "refusal_rate",
                    "visible_events": ["flu", "strike", "donation"],
                    "service_filter": "__ALL__",
                },
            ),
            # ========== MAIN LAYOUT ==========
            html.Div(
                className="dashboard-layout",
                children=[
                    # ========== LEFT SIDEBAR (Control Panel) ==========
                    html.Div(
                        className="sidebar",
                        id="left-column",
                        children=[
                            # Mobile toggle button
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
                    # ========== MAIN CONTENT AREA ==========
                    html.Div(
                        className="main-content",
                        id="right-column",
                        children=[
                            # ========== VIEW 1: Problem Locator (Heatmap) ==========
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
                            # ========== PLACEHOLDER (shown when no selection) ==========
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
                            # ========== VIEW 2: Diagnostic Decomposition ==========
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
                            # ========== VIEW 3: Impact Validation ==========
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

    # ========== HELPER FUNCTIONS ==========
    def metric_series(dff: pd.DataFrame, metric: str) -> pd.Series:
        """Get the appropriate metric series based on diagnostic focus."""
        if metric == "refusal_rate" and cols.refusal_rate:
            return dff[cols.refusal_rate]
        if metric == "bed_utilization" and cols.bed_utilization:
            return dff[cols.bed_utilization]
        if metric == "patients_per_staff" and cols.patients_per_staff:
            return dff[cols.patients_per_staff]
        # Fallback to refusal_rate
        if cols.refusal_rate:
            return dff[cols.refusal_rate]
        # Ultimate fallback
        if cols.requests and cols.refusals:
            denom = dff[cols.requests].replace(0, pd.NA)
            return (dff[cols.refusals] / denom).fillna(0)
        return pd.Series([0] * len(dff))

    # ========== CALLBACKS ==========

    # Callback 1: Handle heatmap click, clear buttons, and service filter changes
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

        # Handle clear button
        if triggered_id == "clear-selection-btn":
            current_state["selected_service"] = None
            current_state["selected_week"] = None
            return current_state

        # Handle service filter change (Rule A2: keep selection only if consistent)
        if triggered_id == "service-select":
            current_state["service_filter"] = service_filter
            selected_service = current_state.get("selected_service")

            # If a service is selected and the filter doesn't match, clear selection
            if selected_service is not None:
                if service_filter != "__ALL__" and service_filter != selected_service:
                    # Clear selection because filter doesn't match
                    current_state["selected_service"] = None
                    current_state["selected_week"] = None
            return current_state

        # Handle heatmap click
        if triggered_id == "heatmap" and click_data:
            try:
                point = click_data["points"][0]
                service = point["y"]
                week = int(point["x"])

                # Toggle deselection if same cell clicked
                if (
                    current_state.get("selected_service") == service
                    and current_state.get("selected_week") == week
                ):
                    current_state["selected_service"] = None
                    current_state["selected_week"] = None
                else:
                    current_state["selected_service"] = service
                    current_state["selected_week"] = week

                return current_state
            except (KeyError, IndexError, TypeError):
                return current_state

        return current_state

    # Callback 2: Sync controls with global state
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

    # Callback 3: Update global state from menu controls
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

    # Callback 4: Update selection display in sidebar
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

    # Callback 5: Toggle visibility of diagnostic views
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
                {"display": "block"},  # Show View 2
                {"display": "block"},  # Show View 3
                {"display": "none"},  # Hide placeholder
            )
        else:
            return (
                {"display": "none"},  # Hide View 2
                {"display": "none"},  # Hide View 3
                {"display": "block"},  # Show placeholder
            )

    # Callback 6: Update VIEW 1 - Heatmap
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

        # Filter by week range
        dff_heatmap = df.copy()
        if week_range:
            dff_heatmap = dff_heatmap[
                (dff_heatmap[cols.week] >= week_range[0])
                & (dff_heatmap[cols.week] <= week_range[1])
            ]

        # Determine title based on diagnostic focus
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

    # Callback 8: Update VIEW 2 - Diagnostic Timeline
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

        # Filter by week range
        dff = df.copy()
        if week_range:
            dff = dff[
                (dff[cols.week] >= week_range[0]) & (dff[cols.week] <= week_range[1])
            ]

        # Apply global service filter to View 2
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
        )

    # Callback 9: Update VIEW 3 - Impact Validation
    @app.callback(
        Output("impact-validation", "figure"),
        Input("global-state", "data"),
        Input("week-range", "value"),
    )
    def update_impact_validation(state, week_range):
        selected_service = state.get("selected_service")
        selected_week = state.get("selected_week")
        service_filter = state.get("service_filter", "__ALL__")

        # Filter by week range
        dff = df.copy()
        if week_range:
            dff = dff[
                (dff[cols.week] >= week_range[0]) & (dff[cols.week] <= week_range[1])
            ]

        # Apply global service filter to View 3
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
        )

    # Clientside callback: Auto-scroll to diagnostic views on selection
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

    # Clientside callback: Sidebar toggle for mobile
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
