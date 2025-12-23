# jbi100_app/menu.py
from dash import dcc, html


def generate_description_card():
    return html.Div(
        id="description-card",
        children=[
            html.H5("Hospital Beds Control Panel"),
            html.Div(
                id="intro",
                children=(
                    "A control panel built on the JBI100 Dash template for exploring "
                    "weekly demand, admissions, and refusal dynamics."
                ),
            ),
        ],
    )



def generate_control_card(services: list[str], default_service: str):
    return html.Div(
        id="control-card",
        children=[
            html.Label("Service / Department"),
            dcc.Dropdown(
                id="service-select",
                options=[{"label": "All services", "value": "__ALL__"}]
                + [{"label": s, "value": s} for s in services],
                value="__ALL__",
                clearable=False,
            ),
            html.Br(),

            html.Label("Timeline metric"),
            dcc.Dropdown(
                id="timeline-metric",
                options=[
                    {"label": "Requests", "value": "requests"},
                    {"label": "Admissions", "value": "admissions"},
                    {"label": "Refusals", "value": "refusals"},
                    {"label": "Refusal rate", "value": "refusal_rate"},
                    {"label": "Beds (capacity)", "value": "beds"},
                    {"label": "Staff (capacity)", "value": "staff"},
                ],
                value="refusals",
                clearable=False,
            ),
            html.Br(),

            html.Label("Heatmap metric"),
            dcc.Dropdown(
                id="heatmap-metric",
                options=[
                    {"label": "Refusals", "value": "refusals"},
                    {"label": "Refusal rate", "value": "refusal_rate"},
                    {"label": "Requests", "value": "requests"},
                    {"label": "Admissions", "value": "admissions"},
                ],
                value="refusal_rate",
                clearable=False,
            ),
        ],
        style={"textAlign": "left"},
    )


def make_menu_layout(services: list[str]):
    default_service = services[0] if services else "__ALL__"
    return [generate_description_card(), generate_control_card(services, default_service)]
