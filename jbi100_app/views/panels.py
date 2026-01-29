
from typing import Optional, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import textwrap


def wrap_title(text: str, width: int = 38) -> str:
    text = text.replace(" — ", " — ")
    lines = textwrap.wrap(
        text, width=width, break_long_words=False, break_on_hyphens=False
    )
    return "<br>".join(lines[:2])


def apply_title(fig, title: str, top_margin: int = 140, font_size: int = 16):
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor="center",
            y=0.92,
            yanchor="top",
            automargin=False,
            font=dict(size=font_size),
        ),
        margin=dict(t=top_margin),
    )
    return fig


def apply_standard_layout(
    fig,
    title: str,
    font_size: int = 16,
    top_margin: int = 110,
    legend_y: float = 1.08,
    legend_orientation: str = "h",
):
    apply_title(fig, title, top_margin=top_margin, font_size=font_size)
    fig.update_layout(
        margin=dict(l=20, r=20, t=top_margin, b=20),
        legend=dict(
            orientation=legend_orientation,
            yanchor="bottom",
            y=legend_y,
            xanchor="right",
            x=1,
        ),
    )
    return fig



def make_heatmap_locator(
    df: pd.DataFrame,
    week_col: str,
    service_col: str,
    values: pd.Series,
    title: str = "Refusal Rate by Service × Week",
    selected_week: Optional[int] = None,
    selected_service: Optional[str] = None,
    service_filter: Optional[str] = None,
):
    dff = df[[week_col, service_col]].copy()
    dff["value"] = values.values

    if service_filter and service_filter != "__ALL__":
        dff = dff[dff[service_col] == service_filter]

    pivot = dff.pivot_table(
        index=service_col,
        columns=week_col,
        values="value",
        aggfunc="mean",
        fill_value=0,
    )

    pivot = pivot.reindex(pivot.mean(axis=1).sort_values(ascending=False).index)

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="RdYlBu_r",
        labels=dict(x="Week", y="Service", color="Value"),
    )

    if selected_week is not None and selected_service is not None:
        services = list(pivot.index)
        weeks = list(pivot.columns)
        if selected_service in services and selected_week in weeks:
            y_idx = services.index(selected_service)
            x_idx = weeks.index(selected_week)
            fig.add_shape(
                type="rect",
                x0=x_idx - 0.5,
                x1=x_idx + 0.5,
                y0=y_idx - 0.5,
                y1=y_idx + 0.5,
                line=dict(color="#2c3e50", width=4),
            )
            fig.add_annotation(
                x=x_idx,
                y=y_idx,
                text="★",
                showarrow=False,
                font=dict(color="white", size=16),
            )

    apply_standard_layout(fig, title, font_size=16, top_margin=80, legend_y=1.05)
    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Service",
        showlegend=False,
        plot_bgcolor="white",
        coloraxis_colorbar=dict(
            title="Rate",
            tickformat=".0%",
        ),
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Week: %{x}<br>"
            "Value: %{z:.2%}<br>"
            "<extra>Click to investigate</extra>"
        )
    )

    return fig


def make_diagnostic_timeline(
    df: pd.DataFrame,
    week_col: str,
    service_col: str,
    requests_col: Optional[str] = None,
    admitted_col: Optional[str] = None,
    refused_col: Optional[str] = None,
    beds_col: Optional[str] = None,
    staff_col: Optional[str] = None,
    bed_utilization_col: Optional[str] = None,
    patients_per_staff_col: Optional[str] = None,
    event_col: Optional[str] = None,
    visible_events: Optional[List[str]] = None,
    selected_service: Optional[str] = None,
    selected_week: Optional[int] = None,
    diagnostic_focus: str = "refusal_rate",
    highlight_range: Optional[List[float]] = None,
):
    if visible_events is None:
        visible_events = ["flu", "strike", "donation"]

    if selected_service is None:
        fig = go.Figure()
        fig.add_annotation(
            text=(
                "<b>Select a service-week in the heatmap above</b><br><br>"
                "This view will show:<br>"
                "• Patient flow (requests, admitted, refused)<br>"
                "• Resource constraints (beds, staff)<br>"
                "• External events (flu, strikes, donations)"
            ),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#666"),
            align="center",
        )
        fig.update_layout(
            title="Diagnostic Decomposition — Awaiting Selection",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(248,249,250,0.8)",
            showlegend=False,
            height=900,
        )
        return fig

    dff = df.copy()

    if service_col in dff.columns and selected_service:
        dff = dff[dff[service_col] == selected_service]

    if selected_week is not None:
        week_min = max(1, selected_week - 6)
        week_max = selected_week + 6
        dff = dff[(dff[week_col] >= week_min) & (dff[week_col] <= week_max)]

    service_display = (
        selected_service.replace("_", " ").title()
        if selected_service
        else "All Services"
    )

    row_heights = [0.38, 0.18, 0.18, 0.14, 0.12]
    num_rows = 5

    subplot_titles = [
        (
            "<b>Patient Flow</b> — "
            "<span style='color:rgba(52,152,219,0.9)'>■</span> Requests  "
            "<span style='color:#2ecc71'>■</span> Admitted  "
            "<span style='color:#e74c3c'>■</span> Refused"
        ),
        (
            "<b>Bed Utilization</b> — "
            "<span style='color:#9b59b6'>━</span> Utilization  "
            "<span style='color:rgba(231,76,60,0.6)'>┄┄</span> 90% Capacity"
        ),
        "<b>Staff Availability</b> — <span style='color:#3498db'>━</span> Staff Count",
        "<b>Patients per Staff</b> — <span style='color:#e67e22'>━</span> Ratio",
        (
            "<b>Events</b> — "
            "<span style='color:#f1c40f'>●</span> Flu  "
            "<span style='color:#e67e22'>●</span> Strike  "
            "<span style='color:#27ae60'>●</span> Donation"
        ),
    ]

    fig = make_subplots(
        rows=num_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=row_heights,
        subplot_titles=subplot_titles,
    )

    agg_dict = {}
    if requests_col and requests_col in dff.columns:
        agg_dict[requests_col] = "sum"
    if admitted_col and admitted_col in dff.columns:
        agg_dict[admitted_col] = "sum"
    if refused_col and refused_col in dff.columns:
        agg_dict[refused_col] = "sum"
    if beds_col and beds_col in dff.columns:
        agg_dict[beds_col] = "mean"
    if staff_col and staff_col in dff.columns:
        agg_dict[staff_col] = "mean"
    if bed_utilization_col and bed_utilization_col in dff.columns:
        agg_dict[bed_utilization_col] = "mean"
    if patients_per_staff_col and patients_per_staff_col in dff.columns:
        agg_dict[patients_per_staff_col] = "mean"

    agg = dff.groupby(week_col, dropna=False).agg(agg_dict).reset_index()

    selected_indices = None
    if highlight_range:
        selected_indices = agg[
            (agg[week_col] >= highlight_range[0]) &
            (agg[week_col] <= highlight_range[1])
        ].index.tolist()



    if requests_col and requests_col in agg.columns:
        fig.add_trace(
            go.Bar(
                x=agg[week_col],
                y=agg[requests_col],
                name="Requests",
                marker_color="rgba(52, 152, 219, 0.6)",
                offsetgroup=0,
                hovertemplate="Week %{x}<br>Requests: %{y}<extra></extra>",
                showlegend=False,
            ),
            row=1,
            col=1,
        )

    if admitted_col and admitted_col in agg.columns:
        fig.add_trace(
            go.Bar(
                x=agg[week_col],
                y=agg[admitted_col],
                name="Admitted",
                marker_color="#2ecc71",
                offsetgroup=1,
                hovertemplate="Week %{x}<br>Admitted: %{y}<extra></extra>",
                showlegend=False,
            ),
            row=1,
            col=1,
        )

    if refused_col and refused_col in agg.columns:
        fig.add_trace(
            go.Bar(
                x=agg[week_col],
                y=agg[refused_col],
                name="Refused",
                marker_color="#e74c3c",
                offsetgroup=1,
                base=agg[admitted_col] if admitted_col in agg.columns else None,
                hovertemplate="Week %{x}<br>Refused: %{y}<extra></extra>",
                showlegend=False,
            ),
            row=1,
            col=1,
        )

    if bed_utilization_col and bed_utilization_col in agg.columns:
        line_width = 3 if diagnostic_focus == "bed_utilization" else 2
        line_color = "#e74c3c" if diagnostic_focus == "bed_utilization" else "#9b59b6"

        fig.add_trace(
            go.Scatter(
                x=agg[week_col],
                y=agg[bed_utilization_col],
                mode="lines+markers",
                name="Bed Utilization",
                line=dict(color=line_color, width=line_width),
                marker=dict(size=8),
                hovertemplate="Week %{x}<br>Utilization: %{y:.1%}<extra></extra>",
                showlegend=False,
            ),
            row=2,
            col=1,
        )
        if not agg.empty:
            last_week = agg[week_col].iloc[-1]
            last_val = agg[bed_utilization_col].iloc[-1]
            fig.add_annotation(
                x=last_week,
                y=last_val,
                xref="x2",
                yref="y2",
                text="<b>Utilization</b>",
                showarrow=False,
                xanchor="left",
                xshift=10,
                font=dict(size=11, color=line_color),
            )
        fig.add_hline(
            y=0.9,
            line_dash="dot",
            line_color="rgba(180, 80, 60, 0.4)",
            annotation_text="90%",
            annotation_position="right",
            annotation_font=dict(size=9, color="rgba(180, 80, 60, 0.7)"),
            row=2,
            col=1,
        )

    if staff_col and staff_col in agg.columns:
        line_width = 3 if diagnostic_focus == "patients_per_staff" else 2
        line_color = (
            "#e74c3c" if diagnostic_focus == "patients_per_staff" else "#3498db"
        )

        fig.add_trace(
            go.Scatter(
                x=agg[week_col],
                y=agg[staff_col],
                mode="lines+markers",
                name="Staff Available",
                line=dict(color=line_color, width=line_width),
                marker=dict(size=8),
                hovertemplate="Week %{x}<br>Staff: %{y:.0f}<extra></extra>",
                showlegend=False,
            ),
            row=3,
            col=1,
        )
        if not agg.empty:
            last_week = agg[week_col].iloc[-1]
            last_val = agg[staff_col].iloc[-1]
            fig.add_annotation(
                x=last_week,
                y=last_val,
                xref="x3",
                yref="y3",
                text="<b>Staff</b>",
                showarrow=False,
                xanchor="left",
                xshift=10,
                font=dict(size=11, color=line_color),
            )

    if patients_per_staff_col and patients_per_staff_col in agg.columns:
        line_width = 3 if diagnostic_focus == "patients_per_staff" else 2
        line_color = (
            "#e74c3c" if diagnostic_focus == "patients_per_staff" else "#e67e22"
        )

        fig.add_trace(
            go.Scatter(
                x=agg[week_col],
                y=agg[patients_per_staff_col],
                mode="lines+markers",
                name="Patients/Staff",
                line=dict(color=line_color, width=line_width),
                marker=dict(size=8),
                hovertemplate="Week %{x}<br>Pts/Staff: %{y:.1f}<extra></extra>",
                showlegend=False,
            ),
            row=4,
            col=1,
        )
        if not agg.empty:
            last_week = agg[week_col].iloc[-1]
            last_val = agg[patients_per_staff_col].iloc[-1]
            fig.add_annotation(
                x=last_week,
                y=last_val,
                xref="x4",
                yref="y4",
                text="<b>Pts/Staff</b>",
                showarrow=False,
                xanchor="left",
                xshift=10,
                font=dict(size=11, color=line_color),
            )

    event_config = {
        "flu": {"color": "#f1c40f", "y_base": 2, "label": "Flu"},
        "strike": {"color": "#e67e22", "y_base": 1, "label": "Strike"},
        "donation": {"color": "#27ae60", "y_base": 0, "label": "Donation"},
    }
    strip_height = 0.8 
    if event_col and event_col in dff.columns:
        event_weeks = dff.groupby([week_col, event_col]).size().reset_index()

        for event_type, config in event_config.items():
            if event_type not in visible_events:
                continue
            event_data = event_weeks[event_weeks[event_col] == event_type]
            if not event_data.empty:
                weeks_with_event = sorted(event_data[week_col].unique())

                i = 0
                while i < len(weeks_with_event):
                    start = weeks_with_event[i]
                    end = start
                    while (
                        i + 1 < len(weeks_with_event)
                        and weeks_with_event[i + 1] == weeks_with_event[i] + 1
                    ):
                        i += 1
                        end = weeks_with_event[i]

                    y_base = config["y_base"]
                    
                    shape_opacity = 0.85
                    if highlight_range:
                        if end < highlight_range[0] or start > highlight_range[1]:
                            shape_opacity = 0.2

                    fig.add_shape(
                        type="rect",
                        x0=start - 0.4,
                        x1=end + 0.4,
                        y0=y_base,
                        y1=y_base + strip_height,
                        fillcolor=config["color"],
                        line=dict(color=config["color"], width=1),
                        opacity=shape_opacity,
                        xref="x5",
                        yref="y5",
                        layer="above",
                    )
                    i += 1

    fig.update_yaxes(
        row=5,
        col=1,
        range=[-0.2, 3],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )

    if not agg.empty:
         fig.add_trace(
            go.Scatter(
                x=agg[week_col],
                y=[1.5] * len(agg), 
                mode="markers",
                marker=dict(opacity=0, size=0), 
                showlegend=False,
                hoverinfo="skip"
            ),
            row=5, col=1
        )

    if selected_week is not None:
        for row in range(1, num_rows + 1):
            fig.add_vline(
                x=selected_week,
                line_dash="dash",
                line_color="#2c3e50",
                line_width=2,
                row=row,
                col=1,
            )

        fig.add_annotation(
            x=selected_week,
            y=1.06,  
            xref="x", 
            yref="paper",
            text=f"<b>▼ Week {selected_week}</b>",
            showarrow=False,
            xanchor="center", 
            yanchor="bottom",  
            align="center",    
            font=dict(size=10, color="#2c3e50"),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#2c3e50",
            borderwidth=1,
            borderpad=3,
        )


    title_text = f"Diagnostic Decomposition — {service_display}"
    if selected_week:
        title_text += f" (Week {selected_week} ±6)"

    fig.update_layout(
        title=dict(text=title_text, x=0.5, font=dict(size=16)),
        height=630,  
        barmode="group",
        hovermode="x unified",
        showlegend=False,  
        margin=dict(l=60, r=70, t=120, b=40),
        plot_bgcolor="white",
    )

    fig.update_yaxes(title_text="Patients", row=1, col=1)
    fig.update_yaxes(title_text="Rate", tickformat=".0%", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=3, col=1)
    fig.update_yaxes(title_text="Ratio", row=4, col=1)
    
    fig.update_xaxes(title_text="Week", row=num_rows, col=1)
    

    
    if selected_indices is not None:
    
        if highlight_range and not agg.empty:
            x_min = agg[week_col].min()
            x_max = agg[week_col].max()
            
            if highlight_range[0] > x_min:
                fig.add_shape(
                    type="rect",
                    x0=x_min - 5, 
                    x1=highlight_range[0],
                    y0=0,
                    y1=1,
                    xref="x",
                    yref="paper",
                    fillcolor="white",
                    opacity=0.75,
                    layer="above", 
                    line_width=0,
                )
            
            if highlight_range[1] < x_max:
                fig.add_shape(
                    type="rect",
                    x0=highlight_range[1],
                    x1=x_max + 5,
                    y0=0,
                    y1=1,
                    xref="x",
                    yref="paper",
                    fillcolor="white",
                    opacity=0.75,
                    layer="above", 
                    line_width=0,
                )

        fig.update_traces(
            selectedpoints=selected_indices,
            unselected=dict(
                marker=dict(opacity=0.2)
            )
        )

    fig.update_layout(
        dragmode="select",
        uirevision=selected_service or "default"
    )

    return fig


def make_impact_validation(
    df: pd.DataFrame,
    week_col: str,
    service_col: str,
    morale_col: Optional[str] = None,
    satisfaction_col: Optional[str] = None,
    selected_service: Optional[str] = None,
    selected_week: Optional[int] = None,
    highlight_range: Optional[List[float]] = None,
):
    
    if selected_service is None:
        fig = go.Figure()
        fig.add_annotation(
            text=(
                "<b>Select a service-week in the heatmap</b><br><br>"
                "This view will show:<br>"
                "• Staff morale trends<br>"
                "• Patient satisfaction scores<br>"
                "• Impact of operational issues"
            ),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#666"),
            align="center",
        )
        fig.update_layout(
            title="Impact Validation — Awaiting Selection",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(248,249,250,0.8)",
            showlegend=False,
            height=300,
        )
        return fig

    dff = df.copy()

    if service_col in dff.columns and selected_service:
        dff = dff[dff[service_col] == selected_service]

    if selected_week is not None:
        week_min = max(1, selected_week - 6)
        week_max = selected_week + 6
        dff = dff[(dff[week_col] >= week_min) & (dff[week_col] <= week_max)]

    service_display = (
        selected_service.replace("_", " ").title()
        if selected_service
        else "All Services"
    )

    agg_dict = {}
    if morale_col and morale_col in dff.columns:
        agg_dict[morale_col] = "mean"
    if satisfaction_col and satisfaction_col in dff.columns:
        agg_dict[satisfaction_col] = "mean"

    if not agg_dict:
        fig = go.Figure()
        fig.add_annotation(
            text="No morale/satisfaction data available in dataset",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#888"),
        )
        fig.update_layout(
            title="Impact Validation — No Data",
            showlegend=False,
            height=300,
        )
        return fig

    agg = dff.groupby(week_col, dropna=False).agg(agg_dict).reset_index()

    selected_indices = None
    if highlight_range:
        selected_indices = agg[
            (agg[week_col] >= highlight_range[0]) &
            (agg[week_col] <= highlight_range[1])
        ].index.tolist()

    fig = go.Figure()

    if morale_col and morale_col in agg.columns:
        fig.add_trace(
            go.Scatter(
                x=agg[week_col],
                y=agg[morale_col],
                mode="lines+markers",
                name="Staff Morale",
                line=dict(color="#9b59b6", width=3),
                marker=dict(size=10, symbol="circle"),
                hovertemplate="Week %{x}<br>Morale: %{y:.1f}<extra></extra>",
            )
        )

    if satisfaction_col and satisfaction_col in agg.columns:
        fig.add_trace(
            go.Scatter(
                x=agg[week_col],
                y=agg[satisfaction_col],
                mode="lines+markers",
                name="Patient Satisfaction",
                line=dict(color="#3498db", width=3),
                marker=dict(size=10, symbol="diamond"),
                hovertemplate="Week %{x}<br>Satisfaction: %{y:.1f}<extra></extra>",
            )
        )

    all_values: List[float] = []
    if morale_col and morale_col in agg.columns:
        all_values.extend(agg[morale_col].dropna().tolist())
    if satisfaction_col and satisfaction_col in agg.columns:
        all_values.extend(agg[satisfaction_col].dropna().tolist())

    if all_values:
        y_min = min(all_values)
        y_max = max(all_values)
        pad = (y_max - y_min) * 0.15 if y_max > y_min else 5
        y_range = [max(0, y_min - pad), min(100, y_max + pad)]
    else:
        y_range = [0, 100]

    if selected_week is not None:
        fig.add_vline(
            x=selected_week,
            line_dash="dash",
            line_color="#2c3e50",
            line_width=2,
            annotation_text=f"Week {selected_week}",
            annotation_position="top",
            annotation_font=dict(size=10, color="#2c3e50"),
        )

        week_min = max(1, selected_week - 6)
        week_max = selected_week + 6
        if selected_week > week_min:
            fig.add_vrect(
                x0=week_min - 0.5,
                x1=selected_week - 0.5,
                fillcolor="rgba(46, 204, 113, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Before",
                annotation_position="top left",
                annotation_font=dict(size=9, color="#27ae60"),
            )
        if selected_week < week_max:
            fig.add_vrect(
                x0=selected_week + 0.5,
                x1=week_max + 0.5,
                fillcolor="rgba(231, 76, 60, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="After",
                annotation_position="top right",
                annotation_font=dict(size=9, color="#e74c3c"),
            )

    title_text = f"Impact Validation — {service_display}"
    if selected_week:
        title_text += f" (Week {selected_week} ±6)"

    fig.update_layout(
        title=dict(text=title_text, x=0.5, font=dict(size=16)),
        xaxis_title="Week",
        yaxis_title="Score (0-100)",
        yaxis=dict(range=y_range),
        height=320,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=60, r=20, t=80, b=50),
        plot_bgcolor="white",
    )

    if selected_indices is not None:
        if highlight_range and not agg.empty:
            x_min = agg[week_col].min()
            x_max = agg[week_col].max()
            
            if highlight_range[0] > x_min:
                fig.add_shape(
                    type="rect",
                    x0=x_min - 5, 
                    x1=highlight_range[0],
                    y0=0,
                    y1=1,
                    xref="x",
                    yref="paper",
                    fillcolor="white",
                    opacity=0.75,
                    layer="above", 
                    line_width=0,
                )
            
            if highlight_range[1] < x_max:
                fig.add_shape(
                    type="rect",
                    x0=highlight_range[1],
                    x1=x_max + 5,
                    y0=0,
                    y1=1,
                    xref="x",
                    yref="paper",
                    fillcolor="white",
                    opacity=0.75,
                    layer="above", 
                    line_width=0,
                )

        fig.update_traces(
            selectedpoints=selected_indices,
            unselected=dict(
                marker=dict(opacity=0.2)
            )
        )

    fig.update_layout(
        dragmode="select",
        uirevision=selected_service or "default"
    )

    return fig


def make_heatmap_interactive(
    df: pd.DataFrame,
    week_col: str,
    service_col: str,
    values: pd.Series,
    title: str,
    selected_week: Optional[int] = None,
    selected_service: Optional[str] = None,
):
    return make_heatmap_locator(
        df=df,
        week_col=week_col,
        service_col=service_col,
        values=values,
        title=title,
        selected_week=selected_week,
        selected_service=selected_service,
    )


def make_event_timeline(
    df: pd.DataFrame,
    week_col: str,
    admitted_col: str,
    refused_col: str,
    staff_col: Optional[str] = None,
    event_col: Optional[str] = None,
    title: str = "Diagnostic Timeline",
    visible_events: Optional[List[str]] = None,
    selected_service: Optional[str] = None,
    selected_week: Optional[int] = None,
    service_col: Optional[str] = None,
    **kwargs,
):
    return make_diagnostic_timeline(
        df=df,
        week_col=week_col,
        service_col=service_col or "",
        admitted_col=admitted_col,
        refused_col=refused_col,
        staff_col=staff_col,
        event_col=event_col,
        visible_events=visible_events,
        selected_service=selected_service,
        selected_week=selected_week,
        **kwargs,
    )


def make_human_cost_timeline(
    df: pd.DataFrame,
    week_col: str,
    morale_col: Optional[str] = None,
    satisfaction_col: Optional[str] = None,
    title: str = "Impact Validation",
    selected_service: Optional[str] = None,
    selected_week: Optional[int] = None,
    service_col: Optional[str] = None,
):
    return make_impact_validation(
        df=df,
        week_col=week_col,
        service_col=service_col or "",
        morale_col=morale_col,
        satisfaction_col=satisfaction_col,
        selected_service=selected_service,
        selected_week=selected_week,
    )
