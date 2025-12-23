# jbi100_app/menu.py
from dash import dcc, html


def generate_description_card():
    return html.Div(
        id="description-card",
        children=[
            html.H5("BedFlow Diagnostic Dashboard"),
            html.Div(
                id="intro",
                children=(
                    "A visual analytics system for diagnosing capacity–demand mismatches "
                    "in hospital operations."
                ),
            ),
            html.Hr(),
            html.P(
                "Core Question: Why did refusals increase for a given service during a specific week?",
                style={"fontStyle": "italic", "fontSize": "12px", "color": "#666"},
            ),
            html.Hr(),
            html.Div(
                children=[
                    html.P(
                        "Diagnostic Workflow:",
                        style={
                            "fontWeight": "bold",
                            "fontSize": "11px",
                            "marginBottom": "4px",
                        },
                    ),
                    html.P(
                        "① Locate → ② Diagnose → ③ Validate → ④ Test → ⑤ Explain",
                        style={
                            "fontSize": "10px",
                            "color": "#888",
                            "marginBottom": "2px",
                        },
                    ),
                    html.P(
                        "Click a cell in the heatmap to begin diagnosis.",
                        style={"fontSize": "10px", "color": "#888"},
                    ),
                ],
            ),
        ],
    )


def generate_control_card(services: list[str], events: list[str], max_week: int):
    return html.Div(
        id="control-card",
        children=[
            # ========== DIAGNOSTIC FOCUS ==========
            html.H6(
                "🔍 Diagnostic Focus", style={"marginTop": "10px", "color": "#2c3e50"}
            ),
            dcc.RadioItems(
                id="diagnostic-focus",
                options=[
                    {"label": " Refusal Spikes", "value": "refusal_rate"},
                    {"label": " Staffing Pressure", "value": "patients_per_staff"},
                    {"label": " Bed Saturation", "value": "bed_utilization"},
                ],
                value="refusal_rate",
                labelStyle={
                    "display": "block",
                    "marginBottom": "4px",
                    "fontSize": "12px",
                },
            ),
            html.Br(),
            # ========== CONTEXT VISIBILITY ==========
            html.H6(
                "📊 Context Visibility", style={"marginTop": "5px", "color": "#2c3e50"}
            ),
            dcc.Checklist(
                id="event-visibility",
                options=[
                    {"label": " 🟡 Flu Outbreaks", "value": "flu"},
                    {"label": " 🟠 Staff Strikes", "value": "strike"},
                    {"label": " 🟢 Donation Drives", "value": "donation"},
                ],
                value=["flu", "strike", "donation"],
                labelStyle={
                    "display": "block",
                    "marginBottom": "4px",
                    "fontSize": "12px",
                },
            ),
            html.Br(),
            # Hidden comparison mode (single service only - comparison modes deferred)
            dcc.RadioItems(
                id="comparison-mode",
                options=[{"label": "Single Service", "value": "single"}],
                value="single",
                style={"display": "none"},
            ),
            # ========== SERVICE FILTER (for single mode) ==========
            html.Div(
                id="service-filter-container",
                children=[
                    html.Label("Service / Department", style={"fontSize": "12px"}),
                    dcc.Dropdown(
                        id="service-select",
                        options=[{"label": "All services", "value": "__ALL__"}]
                        + [
                            {"label": s.replace("_", " ").title(), "value": s}
                            for s in services
                        ],
                        value="__ALL__",
                        clearable=False,
                        style={"fontSize": "12px"},
                    ),
                ],
            ),
            html.Br(),
            # ========== WEEK RANGE ==========
            html.Label("Week Range", style={"fontSize": "12px"}),
            dcc.RangeSlider(
                id="week-range",
                min=1,
                max=max_week,
                step=1,
                value=[1, max_week],
                marks={
                    1: "1",
                    max_week // 2: str(max_week // 2),
                    max_week: str(max_week),
                },
                tooltip={"placement": "bottom", "always_visible": False},
            ),
            html.Br(),
            html.Hr(),
            # ========== SELECTION STATUS ==========
            html.Div(
                id="selection-info",
                children=[
                    html.H6(
                        "📍 Active Selection",
                        style={"marginTop": "10px", "color": "#2c3e50"},
                    ),
                    html.Div(
                        id="selection-display",
                        children=[
                            html.Span("No selection", style={"color": "#e74c3c"}),
                            html.Br(),
                            html.Span(
                                "Click a heatmap cell to begin diagnosis",
                                style={"fontSize": "10px", "color": "#888"},
                            ),
                        ],
                        style={
                            "fontSize": "12px",
                            "padding": "8px",
                            "backgroundColor": "#f8f9fa",
                            "borderRadius": "4px",
                            "marginBottom": "8px",
                        },
                    ),
                    html.Button(
                        "Clear Selection",
                        id="clear-selection-btn",
                        n_clicks=0,
                        style={
                            "width": "100%",
                            "padding": "6px 12px",
                            "fontSize": "11px",
                            "backgroundColor": "#e74c3c",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                        },
                    ),
                ],
            ),
        ],
        style={"textAlign": "left"},
    )


def make_menu_layout(services: list[str], events: list[str] = None, max_week: int = 52):
    if events is None:
        events = ["none", "flu", "donation", "strike"]
    return [
        generate_description_card(),
        generate_control_card(services, events, max_week),
    ]
