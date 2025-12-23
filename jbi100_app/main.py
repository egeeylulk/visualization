# jbi100_app/main.py
from dash import Dash, html, dcc, Input, Output, State
import pandas as pd

from .views.menu import make_menu_layout
from .views.panels import (
    make_heatmap_interactive,
    make_event_timeline,
    make_human_cost_timeline,
    make_scatter,
    make_capacity_breakdown,
)
from .data import load_hospitalbeds


def create_app():
    app = Dash(__name__)
    app.title = "BedFlow Diagnostic Dashboard"

    # DATA (UPDATED: now returns 3 values)
    df, cols, extras = load_hospitalbeds("data")

    # service values as clean strings
    services = sorted(df[cols.service].dropna().astype(str).unique().tolist())

    # event values
    events = []
    if cols.event and cols.event in df.columns:
        events = sorted(df[cols.event].dropna().astype(str).unique().tolist())

    # max week for slider
    max_week = int(df[cols.week].max()) if cols.week else 52

    app.layout = html.Div(
        className="container",
        children=[
            # Global state store for all interactive state
            dcc.Store(
                id="global-state",
                data={
                    "selected_service": None,
                    "selected_week": None,
                    "diagnostic_focus": "refusal_rate",
                    "visible_events": ["flu", "strike", "donation"],
                    "comparison_mode": "single",
                },
            ),
            # ========== SCREEN 1: PROBLEM LOCATOR (Always Visible) ==========
            html.Div(
                id="screen-1",
                className="screen-1",
                children=[
                    html.Div(
                        className="screen-1-layout",
                        children=[
                            # LEFT SIDEBAR
                            html.Div(
                                className="sidebar",
                                id="left-column",
                                children=[
                                    # Mobile drawer toggle (hidden on desktop)
                                    html.Button(
                                        "☰ Controls",
                                        id="sidebar-toggle",
                                        className="sidebar-toggle",
                                    ),
                                    html.Div(
                                        id="sidebar-content",
                                        className="sidebar-content",
                                        children=make_menu_layout(
                                            services, events, max_week
                                        ),
                                    ),
                                ],
                            ),
                            # MAIN HEATMAP AREA
                            html.Div(
                                className="main-content",
                                id="right-column",
                                children=[
                                    html.Div(
                                        className="graph_card heatmap-card",
                                        children=[
                                            html.H6(
                                                "🔍 Problem Locator — Service × Week",
                                                style={"color": "#2c3e50"},
                                            ),
                                            html.P(
                                                "Click a cell to begin diagnosis →",
                                                style={
                                                    "fontSize": "12px",
                                                    "color": "#888",
                                                    "marginBottom": "8px",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="heatmap",
                                                style={"height": "350px"},
                                                config={"displayModeBar": True},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # ========== PLACEHOLDER: Instructional message (shown when no selection) ==========
            html.Div(
                id="screen-2-placeholder",
                className="screen-2-placeholder",
                children=[
                    html.Div(
                        className="placeholder-content",
                        children=[
                            html.Div(
                                className="placeholder-icon-pulse",
                                children=[html.Span("🔍", style={"fontSize": "48px"})],
                            ),
                            html.H5(
                                "Select a high-value cell to investigate",
                                style={
                                    "color": "#2c3e50",
                                    "marginTop": "16px",
                                    "fontWeight": "600",
                                },
                            ),
                            html.P(
                                "Click a dark red cell in the heatmap above — these indicate potential problem areas requiring diagnosis.",
                                style={
                                    "color": "#666",
                                    "fontSize": "14px",
                                    "maxWidth": "400px",
                                    "margin": "8px auto",
                                },
                            ),
                            html.Div(
                                className="placeholder-workflow-preview",
                                style={
                                    "marginTop": "24px",
                                    "padding": "16px",
                                    "backgroundColor": "#fff",
                                    "borderRadius": "8px",
                                    "boxShadow": "0 2px 8px rgba(0,0,0,0.1)",
                                },
                                children=[
                                    html.P(
                                        "What you'll discover:",
                                        style={
                                            "fontWeight": "bold",
                                            "fontSize": "13px",
                                            "color": "#2c3e50",
                                            "marginBottom": "12px",
                                        },
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "center",
                                            "gap": "20px",
                                            "flexWrap": "wrap",
                                        },
                                        children=[
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "📊", style={"fontSize": "24px"}
                                                    ),
                                                    html.P(
                                                        "Timeline",
                                                        style={
                                                            "fontSize": "11px",
                                                            "color": "#666",
                                                            "margin": "4px 0 0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "What happened?",
                                                        style={
                                                            "fontSize": "10px",
                                                            "color": "#999",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                ],
                                                style={"textAlign": "center"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "💔", style={"fontSize": "24px"}
                                                    ),
                                                    html.P(
                                                        "Impact",
                                                        style={
                                                            "fontSize": "11px",
                                                            "color": "#666",
                                                            "margin": "4px 0 0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "What was the cost?",
                                                        style={
                                                            "fontSize": "10px",
                                                            "color": "#999",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                ],
                                                style={"textAlign": "center"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "⚠️", style={"fontSize": "24px"}
                                                    ),
                                                    html.P(
                                                        "Pressure",
                                                        style={
                                                            "fontSize": "11px",
                                                            "color": "#666",
                                                            "margin": "4px 0 0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "How severe?",
                                                        style={
                                                            "fontSize": "10px",
                                                            "color": "#999",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                ],
                                                style={"textAlign": "center"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "📋", style={"fontSize": "24px"}
                                                    ),
                                                    html.P(
                                                        "Explanation",
                                                        style={
                                                            "fontSize": "11px",
                                                            "color": "#666",
                                                            "margin": "4px 0 0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Summary",
                                                        style={
                                                            "fontSize": "10px",
                                                            "color": "#999",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                ],
                                                style={"textAlign": "center"},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # ========== SCREEN 2: DIAGNOSTIC WORKSPACE (Hidden until selection) ==========
            html.Div(
                id="screen-2",
                className="screen-2",
                style={"display": "none"},
                children=[
                    # STICKY MINI-HEADER with navigation
                    html.Div(
                        id="screen-2-header",
                        className="screen-2-header",
                        children=[
                            html.Div(
                                className="header-left",
                                children=[
                                    html.Div(
                                        className="header-title-row",
                                        children=[
                                            html.Span(
                                                "📊 Diagnostic Workspace",
                                                style={
                                                    "fontWeight": "bold",
                                                    "fontSize": "16px",
                                                },
                                            ),
                                            html.Span(
                                                id="header-selection-display",
                                                style={
                                                    "marginLeft": "16px",
                                                    "color": "#27ae60",
                                                },
                                            ),
                                        ],
                                    ),
                                    # Workflow step indicator
                                    html.Div(
                                        className="workflow-indicator",
                                        children=[
                                            html.Span(
                                                "✓ Locate",
                                                className="workflow-step completed",
                                            ),
                                            html.Span("→", className="workflow-arrow"),
                                            html.Span(
                                                "Timeline",
                                                className="workflow-step active",
                                                id="step-timeline",
                                            ),
                                            html.Span("→", className="workflow-arrow"),
                                            html.Span(
                                                "Impact",
                                                className="workflow-step",
                                                id="step-impact",
                                            ),
                                            html.Span("→", className="workflow-arrow"),
                                            html.Span(
                                                "Explain",
                                                className="workflow-step",
                                                id="step-explain",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="header-right",
                                children=[
                                    html.Button(
                                        "↑ Back to Locator",
                                        id="back-to-locator-btn",
                                        className="nav-button",
                                    ),
                                    html.Button(
                                        "✕ Clear Selection",
                                        id="header-clear-btn",
                                        className="nav-button clear-button",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # ========== SECTION 2A: Diagnostic Timeline (FULL WIDTH) ==========
                    html.Div(
                        className="section-2a",
                        children=[
                            html.Div(
                                className="graph_card",
                                id="diagnostic-timeline-card",
                                children=[
                                    html.H6(
                                        "2A️⃣ Diagnostic Timeline — Events & Constraints",
                                        style={"color": "#2c3e50"},
                                    ),
                                    html.P(
                                        "What happened operationally, and when?",
                                        style={
                                            "fontSize": "12px",
                                            "color": "#888",
                                            "margin": "0 7px 8px",
                                        },
                                    ),
                                    dcc.Graph(
                                        id="event-timeline",
                                        style={"height": "500px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # ========== SECTION 2B: Impact & Context (SPLIT VIEW) ==========
                    html.Div(
                        className="section-2b",
                        children=[
                            html.Div(
                                className="split-view-container",
                                children=[
                                    # LEFT: Impact Validation (60%)
                                    html.Div(
                                        className="impact-panel",
                                        children=[
                                            html.Div(
                                                className="graph_card",
                                                id="impact-validation-card",
                                                children=[
                                                    html.H6(
                                                        "2B-L️⃣ Impact Validation — Morale & Satisfaction",
                                                        style={"color": "#2c3e50"},
                                                    ),
                                                    html.P(
                                                        "Validate consequences of the problem",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#888",
                                                            "margin": "0 7px 8px",
                                                        },
                                                    ),
                                                    dcc.Graph(
                                                        id="human-cost-timeline",
                                                        style={"height": "350px"},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    # RIGHT: Pressure Analysis (40%)
                                    html.Div(
                                        className="pressure-panel",
                                        children=[
                                            html.Div(
                                                className="graph_card",
                                                id="pressure-analysis-card",
                                                children=[
                                                    html.H6(
                                                        "2B-R️⃣ Pressure Analysis — Staffing vs Utilization",
                                                        style={"color": "#2c3e50"},
                                                    ),
                                                    html.P(
                                                        "Assess severity relative to baseline",
                                                        style={
                                                            "fontSize": "12px",
                                                            "color": "#888",
                                                            "margin": "0 7px 8px",
                                                        },
                                                    ),
                                                    dcc.Graph(
                                                        id="scatter",
                                                        style={"height": "350px"},
                                                        config={
                                                            "displayModeBar": "hover",
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
                    # ========== SECTION 2C: Case Explanation (FULL WIDTH) ==========
                    html.Div(
                        className="section-2c",
                        children=[
                            html.Div(
                                className="graph_card",
                                id="case-explanation-card",
                                children=[
                                    html.H6(
                                        "2C️⃣ Case Explanation — Selected Service-Week",
                                        style={"color": "#2c3e50"},
                                    ),
                                    html.P(
                                        "How do I explain this case to someone else?",
                                        style={
                                            "fontSize": "12px",
                                            "color": "#888",
                                            "margin": "0 7px 8px",
                                        },
                                    ),
                                    dcc.Graph(
                                        id="capacity-breakdown",
                                        style={"height": "300px"},
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
        if metric == "requests" and getattr(cols, "requests", None):
            return dff[cols.requests]
        if metric == "admissions" and getattr(cols, "admissions", None):
            return dff[cols.admissions]
        if metric == "refusals" and getattr(cols, "refusals", None):
            return dff[cols.refusals]
        if metric == "beds" and getattr(cols, "beds", None):
            return dff[cols.beds]
        if metric == "staff" and getattr(cols, "staff", None):
            return dff[cols.staff]
        if metric == "refusal_rate" and getattr(cols, "refusal_rate", None):
            return dff[cols.refusal_rate]
        if metric == "bed_utilization" and getattr(cols, "bed_utilization", None):
            return dff[cols.bed_utilization]
        if metric == "patients_per_staff" and getattr(cols, "patients_per_staff", None):
            return dff[cols.patients_per_staff]
        if (
            metric == "refusal_rate"
            and getattr(cols, "requests", None)
            and getattr(cols, "refusals", None)
        ):
            denom = dff[cols.requests].replace(0, pd.NA)
            return (dff[cols.refusals] / denom).fillna(0)
        return pd.Series([0] * len(dff))

    # ========== CALLBACK: Handle heatmap click to update selection (with deselection support) ==========
    @app.callback(
        Output("global-state", "data"),
        Input("heatmap", "clickData"),
        Input("clear-selection-btn", "n_clicks"),
        Input("header-clear-btn", "n_clicks"),
        State("global-state", "data"),
        prevent_initial_call=True,
    )
    def update_selection(click_data, clear_clicks, header_clear_clicks, current_state):
        from dash import callback_context

        if not callback_context.triggered:
            return current_state

        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        # Handle clear buttons (both sidebar and header)
        if triggered_id in ["clear-selection-btn", "header-clear-btn"]:
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

    # ========== CALLBACK: Update menu controls from global state ==========
    @app.callback(
        Output("diagnostic-focus", "value"),
        Output("event-visibility", "value"),
        Output("comparison-mode", "value"),
        Input("global-state", "data"),
    )
    def sync_controls_from_state(state):
        return (
            state.get("diagnostic_focus", "refusal_rate"),
            state.get("visible_events", ["flu", "strike", "donation"]),
            state.get("comparison_mode", "single"),
        )

    # ========== CALLBACK: Update global state from menu controls ==========
    @app.callback(
        Output("global-state", "data", allow_duplicate=True),
        Input("diagnostic-focus", "value"),
        Input("event-visibility", "value"),
        Input("comparison-mode", "value"),
        State("global-state", "data"),
        prevent_initial_call=True,
    )
    def update_state_from_controls(
        diagnostic_focus, visible_events, comparison_mode, state
    ):
        state["diagnostic_focus"] = diagnostic_focus
        state["visible_events"] = visible_events or []
        state["comparison_mode"] = comparison_mode
        return state

    # ========== CALLBACK: Update selection display ==========
    @app.callback(
        Output("selection-display", "children"),
        Input("global-state", "data"),
    )
    def update_selection_display(state):
        service = state.get("selected_service")
        week = state.get("selected_week")

        if service and week:
            service_display = service.replace("_", " ").title()
            return [
                html.Span(
                    f"✅ {service_display}",
                    style={"color": "#27ae60", "fontWeight": "bold"},
                ),
                html.Br(),
                html.Span(f"Week {week}", style={"fontSize": "14px"}),
            ]
        else:
            return [
                html.Span("No selection", style={"color": "#e74c3c"}),
                html.Br(),
                html.Span(
                    "Click a heatmap cell to begin diagnosis",
                    style={"fontSize": "10px", "color": "#888"},
                ),
            ]

    # ========== CALLBACK: Layer visibility based on selection ==========
    @app.callback(
        Output("screen-2", "style"),
        Output("screen-2-placeholder", "style"),
        Input("global-state", "data"),
    )
    def update_screen_visibility(state):
        has_selection = state.get("selected_service") and state.get("selected_week")

        if has_selection:
            # Show SCREEN 2, hide placeholder
            return {"display": "block"}, {"display": "none"}
        else:
            # Hide SCREEN 2, show placeholder
            return {"display": "none"}, {"display": "block"}

    # ========== CALLBACK: Update header selection display ==========
    @app.callback(
        Output("header-selection-display", "children"),
        Input("global-state", "data"),
    )
    def update_header_selection(state):
        service = state.get("selected_service")
        week = state.get("selected_week")

        if service and week:
            service_display = service.replace("_", " ").title()
            return f"✅ {service_display} — Week {week}"
        return ""

    # ========== CLIENTSIDE CALLBACK: Auto-scroll to SCREEN 2 on selection ==========
    app.clientside_callback(
        """
        function(state) {
            if (state && state.selected_service && state.selected_week) {
                // Small delay to allow DOM to update
                setTimeout(function() {
                    var screen2 = document.getElementById('screen-2');
                    if (screen2) {
                        // Check for reduced motion preference
                        var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
                        screen2.scrollIntoView({
                            behavior: prefersReducedMotion ? 'auto' : 'smooth',
                            block: 'start'
                        });
                    }
                }, 100);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("screen-2", "data-scroll-trigger"),
        Input("global-state", "data"),
    )

    # ========== CLIENTSIDE CALLBACK: Back to Locator button ==========
    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks) {
                var screen1 = document.getElementById('screen-1');
                if (screen1) {
                    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
                    screen1.scrollIntoView({
                        behavior: prefersReducedMotion ? 'auto' : 'smooth',
                        block: 'start'
                    });
                }
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("screen-1", "data-scroll-trigger"),
        Input("back-to-locator-btn", "n_clicks"),
    )

    # ========== CLIENTSIDE CALLBACK: Sidebar toggle for mobile ==========
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

    # ========== MODULAR CALLBACKS: Update visualizations independently ==========

    # ========== CALLBACK 1: Update Heatmap ==========
    @app.callback(
        Output("heatmap", "figure"),
        Input("global-state", "data"),
        Input("week-range", "value"),
    )
    def update_heatmap(state, week_range):
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

        # Use diagnostic focus to determine heatmap metric
        focus_labels = {
            "refusal_rate": "Refusal Rate",
            "patients_per_staff": "Staffing Pressure",
            "bed_utilization": "Bed Saturation",
        }
        hm_title = f"{focus_labels.get(diagnostic_focus, 'Metric')} by Service × Week"

        return make_heatmap_interactive(
            dff_heatmap,
            cols.week,
            cols.service,
            metric_series(dff_heatmap, diagnostic_focus),
            hm_title,
            selected_week=selected_week,
            selected_service=selected_service,
        )

    # ========== CALLBACK 2: Update Event Timeline ==========
    @app.callback(
        Output("event-timeline", "figure"),
        Input("global-state", "data"),
        Input("week-range", "value"),
    )
    def update_timeline(state, week_range):
        selected_service = state.get("selected_service")
        selected_week = state.get("selected_week")
        visible_events = state.get("visible_events", [])
        comparison_mode = state.get("comparison_mode", "single")

        # Filter by week range
        dff_timeline = df.copy()
        if week_range:
            dff_timeline = dff_timeline[
                (dff_timeline[cols.week] >= week_range[0])
                & (dff_timeline[cols.week] <= week_range[1])
            ]

        return make_event_timeline(
            dff_timeline,
            week_col=cols.week,
            admitted_col=cols.admissions,
            refused_col=cols.refusals,
            staff_col=cols.staff,
            event_col=cols.event,
            title="Capacity Timeline",
            visible_events=visible_events,
            selected_service=selected_service,
            selected_week=selected_week,
            service_col=cols.service,
            comparison_mode=comparison_mode,
        )

    # ========== CALLBACK 3: Update Human Impact Timeline ==========
    @app.callback(
        Output("human-cost-timeline", "figure"),
        Input("global-state", "data"),
        Input("week-range", "value"),
    )
    def update_human_impact(state, week_range):
        selected_service = state.get("selected_service")
        selected_week = state.get("selected_week")

        # Find morale and satisfaction columns
        morale_col = None
        satisfaction_col = None
        for col in df.columns:
            if "morale" in col.lower():
                morale_col = col
            if "satisfaction" in col.lower():
                satisfaction_col = col

        # Filter by week range
        dff_human = df.copy()
        if week_range:
            dff_human = dff_human[
                (dff_human[cols.week] >= week_range[0])
                & (dff_human[cols.week] <= week_range[1])
            ]

        return make_human_cost_timeline(
            dff_human,
            week_col=cols.week,
            morale_col=morale_col,
            satisfaction_col=satisfaction_col,
            title="Human Impact",
            selected_service=selected_service,
            selected_week=selected_week,
            service_col=cols.service,
        )

    # ========== CALLBACK 4: Update Scatter Plot ==========
    @app.callback(
        Output("scatter", "figure"),
        Input("global-state", "data"),
        Input("week-range", "value"),
    )
    def update_scatter(state, week_range):
        diagnostic_focus = state.get("diagnostic_focus", "refusal_rate")
        selected_service = state.get("selected_service")
        selected_week = state.get("selected_week")

        x_col = cols.patients_per_staff if cols.patients_per_staff else cols.requests

        # Y-axis based on diagnostic focus
        if diagnostic_focus == "bed_utilization":
            y_col_scatter = cols.bed_utilization
        else:
            y_col_scatter = cols.refusal_rate

        if not y_col_scatter:
            y_col_scatter = cols.refusal_rate or cols.refusals

        # Filter by week range
        dff_scatter = df.copy()
        if week_range:
            dff_scatter = dff_scatter[
                (dff_scatter[cols.week] >= week_range[0])
                & (dff_scatter[cols.week] <= week_range[1])
            ]

        return make_scatter(
            dff_scatter,
            x_col=x_col or cols.requests,
            y_col=y_col_scatter or cols.refusals,
            color_col=cols.service,
            size_col=cols.refusal_rate,
            week_col=cols.week,
            hover_data=[cols.event] if cols.event else None,
            title="Staffing vs. Utilization",
            selected_service=selected_service,
            selected_week=selected_week,
        )

    # ========== CALLBACK 5: Update Capacity Breakdown ==========
    @app.callback(
        Output("capacity-breakdown", "figure"),
        Input("global-state", "data"),
    )
    def update_capacity(state):
        selected_week = state.get("selected_week")
        selected_service = state.get("selected_service")

        if selected_week and selected_service:
            return make_capacity_breakdown(
                df,
                week=selected_week,
                service=selected_service,
                week_col=cols.week,
                service_col=cols.service,
                beds_col=cols.beds,
                admitted_col=cols.admissions,
                refused_col=cols.refusals,
                staff_col=cols.staff,
                utilization_col=cols.bed_utilization,
                patients_per_staff_col=cols.patients_per_staff,
                title="Capacity Breakdown",
            )
        else:
            import plotly.graph_objects as go

            breakdown_fig = go.Figure()
            breakdown_fig.add_annotation(
                text="👆 Select a cell in the heatmap above<br>to see detailed case explanation",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="#666"),
            )
            breakdown_fig.update_layout(
                title="Case Explanation — Awaiting Selection",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                margin=dict(l=20, r=20, t=60, b=20),
                plot_bgcolor="rgba(248,249,250,0.5)",
            )
            return breakdown_fig

    return app
