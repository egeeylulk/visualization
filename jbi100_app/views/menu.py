from dash import dcc, html


def generate_description_card():
    return html.Div(
        id="description-card",
        children=[
            html.H5("BedFlow Dashboard"),
            html.Div(
                id="intro",
            ),
        ],
    )


def generate_control_card(services: list[str], events: list[str], max_week: int):
    return html.Div(
        id="control-card",
        children=[
            html.Details(
                className="accordion-section",
                open=True,
                children=[
                    html.Summary(
                        className="accordion-header",
                        children=[
                            html.H6(
                                "🔍 Diagnostic Focus",
                                style={"margin": "0", "color": "#2c3e50"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="accordion-content",
                        children=[
                            dcc.RadioItems(
                                id="diagnostic-focus",
                                options=[
                                    {
                                        "label": " Refusal Spikes (default)",
                                        "value": "refusal_rate",
                                    },
                                    {
                                        "label": " Staffing Pressure",
                                        "value": "patients_per_staff",
                                    },
                                    {
                                        "label": " Bed Saturation",
                                        "value": "bed_utilization",
                                    },
                                ],
                                value="refusal_rate",
                                labelStyle={
                                    "display": "block",
                                    "marginBottom": "4px",
                                    "fontSize": "12px",
                                },
                            ),
                        ],
                    ),
                ],
            ),
            html.Details(
                className="accordion-section",
                open=True,
                children=[
                    html.Summary(
                        className="accordion-header",
                        children=[
                            html.H6(
                                "📊 Context Visibility",
                                style={"margin": "0", "color": "#2c3e50"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="accordion-content",
                        children=[
                            dcc.Checklist(
                                id="event-visibility",
                                options=[
                                    {"label": " 🟡 Flu Outbreaks", "value": "flu"},
                                    {"label": " 🟠 Staff Strikes", "value": "strike"},
                                    {
                                        "label": " 🟢 Donation Drives",
                                        "value": "donation",
                                    },
                                ],
                                value=["flu", "strike", "donation"],
                                labelStyle={
                                    "display": "block",
                                    "marginBottom": "4px",
                                    "fontSize": "12px",
                                },
                            ),
                        ],
                    ),
                ],
            ),
            dcc.RadioItems(
                id="comparison-mode",
                options=[{"label": "Single Service", "value": "single"}],
                value="single",
                style={"display": "none"},
            ),
            html.Details(
                className="accordion-section",
                open=True,
                children=[
                    html.Summary(
                        className="accordion-header",
                        children=[
                            html.H6(
                                "🔧 Filters", style={"margin": "0", "color": "#2c3e50"}
                            ),
                        ],
                    ),
                    html.Div(
                        className="accordion-content",
                        children=[
                            html.Label(
                                "🏥 Service / Department",
                                style={
                                    "fontSize": "11px",
                                    "fontWeight": "600",
                                    "marginBottom": "4px",
                                    "display": "block",
                                },
                            ),
                            dcc.Dropdown(
                                id="service-select",
                                options=[{"label": "All Services", "value": "__ALL__"}]
                                + [
                                    {"label": s.replace("_", " ").title(), "value": s}
                                    for s in services
                                ],
                                value="__ALL__",
                                clearable=False,
                                style={"fontSize": "12px", "marginBottom": "12px"},
                            ),
                            
                            html.Label(
                                "📅 Week Range",
                                style={
                                    "fontSize": "11px",
                                    "fontWeight": "600",
                                    "marginBottom": "4px",
                                    "display": "block",
                                },
                            ),
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
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),
                        ],
                    ),
                ],
            ),

            html.Div(
                id="selection-info",
                children=[
                    html.Div(
                        id="selection-display",
                        children=[
                            html.Span("No selection", style={"color": "#e74c3c"}),
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
