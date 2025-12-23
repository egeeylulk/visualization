# jbi100_app/views/panels.py
from typing import Optional, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import textwrap


def wrap_title(text: str, width: int = 38) -> str:
    """
    Wrap for Plotly annotations using <br>.
    width is roughly character-based; adjust to taste.
    """
    # keep em dash chunks readable
    text = text.replace(" — ", " — ")
    lines = textwrap.wrap(
        text, width=width, break_long_words=False, break_on_hyphens=False
    )
    return "<br>".join(lines[:2])  # 2 lines max (prevents huge top area)


# ============================================================================
# Shared layout helper
# ============================================================================
def apply_title(fig, title: str, top_margin: int = 140, font_size: int = 16):
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor="center",
            y=0.92,  # was 0.98 -> puts title under the modebar
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
    """
    Opinionated default layout for this app: fixes common title clipping by:
    - applying apply_title()
    - moving horizontal legend slightly above the plotting area but within top margin
    - using consistent margins/hovermode defaults
    """
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


# ============================================================================
# KPI helpers
# ============================================================================
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


# ============================================================================
# Basic charts
# ============================================================================
def make_timeline(df: pd.DataFrame, week_col: str, value_series: pd.Series, title: str):
    dff = df[[week_col]].copy()
    dff["value"] = value_series.values
    agg = dff.groupby(week_col, dropna=False)["value"].sum().reset_index()

    fig = px.line(agg, x=week_col, y="value", markers=True, title=title)
    apply_standard_layout(fig, title, font_size=16, top_margin=100, legend_y=1.05)
    fig.update_layout(hovermode="x unified")
    return fig


def make_heatmap(
    df: pd.DataFrame, week_col: str, service_col: str, values: pd.Series, title: str
):
    dff = df[[week_col, service_col]].copy()
    dff["value"] = values.values

    pivot = dff.pivot_table(
        index=service_col, columns=week_col, values="value", aggfunc="sum", fill_value=0
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        title=title,
        color_continuous_scale="RdYlBu_r",
        labels=dict(x="Week", y="Service", color="Value"),
    )

    apply_standard_layout(fig, title, font_size=16, top_margin=100, legend_y=1.05)
    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Service",
        showlegend=False,  # heatmap legend is the colorbar, not Plotly legend
    )
    return fig


# ============================================================================
# VISUALIZATION 1: Parallel Categories Diagram
# ============================================================================
def make_parcats(
    df: pd.DataFrame,
    service_col: str,
    event_col: Optional[str],
    demand_level_col: Optional[str],
    refusal_level_col: Optional[str],
    color_col: Optional[str] = None,
    title: str = "Parallel Categories: Service Flow Analysis",
):
    """
    Creates a Parallel Categories diagram for categorical overview.
    Dimensions: service -> event -> demand_level -> refusal_level
    """
    dimensions: List[str] = []
    dff = df.copy()

    # Always include service
    dimensions.append(service_col)

    # Add event if available
    if event_col and event_col in dff.columns:
        dimensions.append(event_col)

    # Add demand_level if available
    if demand_level_col and demand_level_col in dff.columns:
        dff[demand_level_col] = dff[demand_level_col].astype(str)
        dimensions.append(demand_level_col)

    # Add refusal_level if available
    if refusal_level_col and refusal_level_col in dff.columns:
        dff[refusal_level_col] = dff[refusal_level_col].astype(str)
        dimensions.append(refusal_level_col)

    if len(dimensions) < 2:
        fig = px.bar(
            dff,
            x=service_col,
            title="Service Distribution (insufficient categorical data)",
        )
        apply_standard_layout(
            fig, "Service Distribution (insufficient categorical data)"
        )
        return fig

    color = None
    if color_col and color_col in dff.columns:
        color = dff[color_col]

    fig = px.parallel_categories(
        dff,
        dimensions=dimensions,
        color=color,
        color_continuous_scale=px.colors.sequential.Viridis,
        title=title,
    )
    apply_standard_layout(fig, title, font_size=16, top_margin=110, legend_y=1.05)
    return fig


# ============================================================================
# VISUALIZATION 3: Multi-Line Time Series
# ============================================================================
def make_multiline_timeline(
    df: pd.DataFrame,
    week_col: str,
    metrics: dict,  # {"Requests": series, "Admitted": series, ...}
    title: str = "Weekly Patient Flow",
):
    """
    Creates a multi-line time series chart.
    metrics: dict mapping label -> pd.Series of values
    """
    dff = df[[week_col]].copy()
    for label, series in metrics.items():
        dff[label] = series.values

    agg = dff.groupby(week_col, dropna=False).sum().reset_index()
    melted = agg.melt(id_vars=[week_col], var_name="Metric", value_name="Value")

    fig = px.line(
        melted,
        x=week_col,
        y="Value",
        color="Metric",
        markers=True,
        title=title,
    )

    apply_standard_layout(fig, title, font_size=16, top_margin=110, legend_y=1.08)
    fig.update_layout(hovermode="x unified")
    return fig


# ============================================================================
# VISUALIZATION 4: Scatter Plot (Bubble Chart)
# ============================================================================
def make_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    size_col: Optional[str] = None,
    week_col: Optional[str] = None,
    hover_data: Optional[List[str]] = None,
    title: str = "Pressure Analysis",
    selected_service: Optional[str] = None,
    selected_week: Optional[int] = None,
):
    # -------------------- helper: title as annotation (wrap-safe) --------------------
    def set_annotation_title(fig, text: str, top_margin: int = 30):
        # Remove plotly title (it clips, no wrap)
        fig.update_layout(title=None)

        # Put title inside the figure as an annotation (wraps in HTML <br>)
        # We'll also add a small top margin so it doesn't touch container edges.
        fig.update_layout(margin=dict(l=20, r=20, t=top_margin, b=20))
        wrapped = wrap_title(text, width=38)
        fig.add_annotation(
            text=f"<b>{wrapped}</b>",
            xref="paper",
            yref="paper",
            x=0.0,
            y=1.18,  # above plot area
            xanchor="left",
            yanchor="top",
            align="left",
            showarrow=False,
            font=dict(size=18, color="#2c3e50"),
        )
        return fig

    # -------------------- placeholder --------------------
    if selected_service is None:
        fig = go.Figure()
        fig.add_annotation(
            text="👆 Select a service-week in the heatmap<br>to analyze pressure context",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#666"),
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(248,249,250,0.5)",
            showlegend=False,
        )
        set_annotation_title(
            fig, "Pressure Analysis — Awaiting Selection", top_margin=40
        )
        return fig

    dff = df.copy()

    if hover_data is None:
        hover_data = []
    if week_col and week_col not in hover_data:
        hover_data = [week_col] + hover_data

    dff["_is_selected"] = False
    if selected_service and selected_week is not None and week_col:
        dff["_is_selected"] = (dff[color_col] == selected_service) & (
            dff[week_col] == selected_week
        )

    fig = go.Figure()

    # Background points
    faded = dff[~dff["_is_selected"]]
    for service in faded[color_col].dropna().unique():
        sd = faded[faded[color_col] == service]
        fig.add_trace(
            go.Scatter(
                x=sd[x_col],
                y=sd[y_col],
                mode="markers",
                name=str(service).replace("_", " ").title(),
                marker=dict(size=10, opacity=0.25),
                customdata=sd[[week_col]].values if week_col else None,
                hovertemplate=(
                    f"Service: {service}<br>"
                    f"Week: %{{customdata[0]}}<br>"
                    f"{x_col}: %{{x:.2f}}<br>"
                    f"{y_col}: %{{y:.2f}}<extra></extra>"
                ),
                showlegend=True,
            )
        )

    # Selected point
    sel = dff[dff["_is_selected"]]
    if not sel.empty:
        service_display = selected_service.replace("_", " ").title()

        x_mean, y_mean = dff[x_col].mean(), dff[y_col].mean()
        x_std, y_std = dff[x_col].std(), dff[y_col].std()
        sx, sy = sel[x_col].iloc[0], sel[y_col].iloc[0]
        x_sig = (sx - x_mean) / x_std if x_std and x_std > 0 else 0
        y_sig = (sy - y_mean) / y_std if y_std and y_std > 0 else 0
        sig = max(abs(x_sig), abs(y_sig))
        sign = "+" if (x_sig > 0 or y_sig > 0) else "-"

        fig.add_trace(
            go.Scatter(
                x=[sx],
                y=[sy],
                mode="markers+text",
                name=f"★ {service_display} (Week {selected_week})",
                marker=dict(
                    size=22,
                    color="#e74c3c",
                    symbol="star",
                    line=dict(color="black", width=2),
                ),
                text=[f"{sign}{sig:.1f}σ"],
                textposition="top center",
                textfont=dict(size=11, color="#e74c3c", family="Arial Black"),
                showlegend=True,
            )
        )

    # Reference lines
    fig.add_vline(
        x=dff[x_col].mean(),
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Avg: {dff[x_col].mean():.2f}",
    )
    fig.add_hline(
        y=dff[y_col].mean(),
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Avg: {dff[y_col].mean():.2f}",
    )

    # Layout (legend stays inside plot)
    fig.update_layout(
        xaxis_title=x_col.replace("_", " ").title(),
        yaxis_title=y_col.replace("_", " ").title(),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0,
        ),
        plot_bgcolor="white",
        hovermode="closest",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    final_title = f"Pressure Analysis — {selected_service.replace('_', ' ').title()} (Week {selected_week})"
    set_annotation_title(fig, final_title, top_margin=40)

    return fig


# ============================================================================
# VISUALIZATION 5: Event-Aware Capacity Timeline (Primary Diagnostic View)
# ============================================================================
def make_event_timeline(
    df: pd.DataFrame,
    week_col: str,
    admitted_col: str,
    refused_col: str,
    staff_col: Optional[str] = None,
    event_col: Optional[str] = None,
    title: str = "Event-Aware Capacity Timeline",
    visible_events: Optional[List[str]] = None,
    selected_service: Optional[str] = None,
    selected_week: Optional[int] = None,
    service_col: Optional[str] = None,
    comparison_mode: str = "single",
):
    from plotly.subplots import make_subplots

    if visible_events is None:
        visible_events = ["flu", "strike", "donation"]

    # Placeholder
    if selected_service is None:
        fig = go.Figure()
        fig.add_annotation(
            text="👆 Select a service-week in the heatmap<br>to diagnose capacity constraints",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#666"),
        )
        apply_standard_layout(
            fig, "Diagnostic Timeline — Awaiting Selection", font_size=16
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(248,249,250,0.5)",
            showlegend=False,
        )
        return fig

    dff = df.copy()

    # Window constraint: ±6 weeks from selected week
    if selected_week is not None and comparison_mode == "single":
        week_min = max(1, selected_week - 6)
        week_max = selected_week + 6
        dff = dff[(dff[week_col] >= week_min) & (dff[week_col] <= week_max)]

    # Compare services mode
    if comparison_mode == "services" and service_col and service_col in dff.columns:
        service_ranking = (
            dff.groupby(service_col, dropna=False)
            .agg({refused_col: "sum", admitted_col: "sum"})
            .reset_index()
        )
        denom = service_ranking[refused_col] + service_ranking[admitted_col]
        service_ranking["refusal_rate"] = service_ranking[refused_col] / denom.replace(
            0, pd.NA
        )
        service_ranking = service_ranking.sort_values("refusal_rate", ascending=False)

        top_services = service_ranking.head(5)[service_col].tolist()

        fig = make_subplots(
            rows=len(top_services),
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=[s.replace("_", " ").title() for s in top_services],
        )

        for idx, service in enumerate(top_services, start=1):
            service_data = dff[dff[service_col] == service].copy()
            agg = (
                service_data.groupby(week_col, dropna=False)
                .agg(
                    {
                        admitted_col: "sum",
                        refused_col: "sum",
                        **(
                            ({staff_col: "mean"})
                            if staff_col and staff_col in service_data.columns
                            else {}
                        ),
                    }
                )
                .reset_index()
            )

            fig.add_trace(
                go.Bar(
                    x=agg[week_col],
                    y=agg[admitted_col],
                    name="Admitted" if idx == 1 else None,
                    marker_color="#2ecc71",
                    showlegend=(idx == 1),
                    legendgroup="admitted",
                    hovertemplate="Week %{x}<br>Admitted: %{y}<extra></extra>",
                ),
                row=idx,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=agg[week_col],
                    y=agg[refused_col],
                    name="Refused" if idx == 1 else None,
                    marker_color="#e74c3c",
                    showlegend=(idx == 1),
                    legendgroup="refused",
                    hovertemplate="Week %{x}<br>Refused: %{y}<extra></extra>",
                ),
                row=idx,
                col=1,
            )

            if event_col and event_col in service_data.columns:
                event_colors = {
                    "flu": "rgba(241, 196, 15, 0.3)",
                    "strike": "rgba(230, 126, 34, 0.3)",
                    "donation": "rgba(46, 204, 113, 0.2)",
                }
                event_weeks = (
                    service_data.groupby([week_col, event_col]).size().reset_index()
                )
                for event_type, color in event_colors.items():
                    if event_type not in visible_events:
                        continue
                    event_data = event_weeks[event_weeks[event_col] == event_type]
                    if not event_data.empty:
                        for w in sorted(event_data[week_col].unique()):
                            fig.add_vrect(
                                x0=w - 0.5,
                                x1=w + 0.5,
                                fillcolor=color,
                                layer="below",
                                line_width=0,
                                row=idx,
                                col=1,
                            )

            if selected_week is not None:
                fig.add_vline(
                    x=selected_week,
                    line_dash="dash",
                    line_color="#e74c3c",
                    line_width=2,
                    row=idx,
                    col=1,
                )

        fig.update_xaxes(title_text="Week", row=len(top_services), col=1)
        fig.update_yaxes(title_text="Patients")

        compare_title = f"Compare Services — Top {len(top_services)} by Refusal Rate"
        apply_title(fig, compare_title, top_margin=120, font_size=16)
        fig.update_layout(
            barmode="stack",
            height=150 * len(top_services),
            margin=dict(l=20, r=20, t=120, b=20),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.06, xanchor="right", x=1
            ),
            hovermode="x unified",
        )
        return fig

    # Single service mode
    if service_col and service_col in dff.columns and selected_service:
        dff = dff[dff[service_col] == selected_service]
        service_display = selected_service.replace("_", " ").title()
        if selected_week is not None:
            title = f"Capacity Timeline — {service_display} (Week {selected_week} ±6)"
        else:
            title = f"Capacity Timeline — {service_display}"

    agg = (
        dff.groupby(week_col, dropna=False)
        .agg(
            {
                admitted_col: "sum",
                refused_col: "sum",
                **(
                    ({staff_col: "mean"})
                    if staff_col and staff_col in dff.columns
                    else {}
                ),
            }
        )
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=agg[week_col],
            y=agg[admitted_col],
            name="Admitted",
            marker_color="#2ecc71",
            hovertemplate="Week %{x}<br>Admitted: %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=agg[week_col],
            y=agg[refused_col],
            name="Refused",
            marker_color="#e74c3c",
            hovertemplate="Week %{x}<br>Refused: %{y}<extra></extra>",
        )
    )

    # Event background bands
    if event_col and event_col in dff.columns:
        event_colors = {
            "flu": ("rgba(241, 196, 15, 0.3)", "🟡 FLU"),
            "strike": ("rgba(230, 126, 34, 0.3)", "🟠 STRIKE"),
            "donation": ("rgba(46, 204, 113, 0.2)", "🟢 DONATION"),
        }
        event_weeks = dff.groupby([week_col, event_col]).size().reset_index()
        for event_type, (color, label) in event_colors.items():
            if event_type not in visible_events:
                continue
            event_data = event_weeks[event_weeks[event_col] == event_type]
            if not event_data.empty:
                weeks = sorted(event_data[week_col].unique())
                i = 0
                while i < len(weeks):
                    start = weeks[i]
                    end = start
                    while i + 1 < len(weeks) and weeks[i + 1] == weeks[i] + 1:
                        i += 1
                        end = weeks[i]
                    fig.add_vrect(
                        x0=start - 0.5,
                        x1=end + 0.5,
                        fillcolor=color,
                        layer="below",
                        line_width=0,
                        annotation_text=label if start == end else "",
                        annotation_position="top left",
                        annotation_font_size=9,
                    )
                    i += 1

    # Staff line overlay
    if staff_col and staff_col in agg.columns:
        max_patients = (agg[admitted_col] + agg[refused_col]).max()
        max_staff = agg[staff_col].max()
        scale_factor = max_patients / max_staff if max_staff and max_staff > 0 else 1

        fig.add_trace(
            go.Scatter(
                x=agg[week_col],
                y=agg[staff_col] * scale_factor,
                mode="lines+markers",
                name="Staff (scaled)",
                line=dict(dash="dot", color="#9b59b6", width=2),
                marker=dict(size=6),
                yaxis="y2",
                hovertemplate="Week %{x}<br>Staff: %{customdata:.0f}<extra></extra>",
                customdata=agg[staff_col],
            )
        )

    apply_standard_layout(fig, title, font_size=16, top_margin=120, legend_y=1.08)

    fig.update_layout(
        barmode="stack",
        xaxis_title="Week",
        yaxis_title="Patients",
        yaxis2=dict(title="Staff", overlaying="y", side="right", showgrid=False),
        margin=dict(l=20, r=60, t=120, b=20),
        hovermode="x unified",
        plot_bgcolor="white",
    )

    # Event legend annotation
    if event_col and event_col in dff.columns:
        fig.add_annotation(
            text="🟡 Flu | 🟠 Strike | 🟢 Donation",
            xref="paper",
            yref="paper",
            x=0,
            y=-0.12,
            showarrow=False,
            font=dict(size=10),
        )

    # Selected week marker
    if selected_week is not None:
        fig.add_vline(
            x=selected_week,
            line_dash="dash",
            line_color="#e74c3c",
            line_width=2,
            annotation_text="Selected Week",
            annotation_position="top",
            annotation_font_color="#e74c3c",
            annotation_font_size=10,
            annotation_font_weight="bold",
        )

    return fig


# ============================================================================
# VISUALIZATION 6: Human Cost Timeline (Linked Contextual View)
# ============================================================================
def make_human_cost_timeline(
    df: pd.DataFrame,
    week_col: str,
    morale_col: Optional[str] = None,
    satisfaction_col: Optional[str] = None,
    title: str = "Human Impact Over Time",
    selected_service: Optional[str] = None,
    selected_week: Optional[int] = None,
    service_col: Optional[str] = None,
):
    """
    Dual-line chart:
    - Staff morale
    - Patient satisfaction
    """
    # Placeholder
    if selected_service is None:
        fig = go.Figure()
        fig.add_annotation(
            text="👆 Select a service-week in the heatmap<br>to validate human impact",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#666"),
        )
        apply_standard_layout(
            fig, "Impact Validation — Awaiting Selection", font_size=14
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="rgba(248,249,250,0.5)",
            showlegend=False,
        )
        return fig

    dff = df.copy()

    # Window constraint: ±6 weeks
    if selected_week is not None:
        week_min = max(1, selected_week - 6)
        week_max = selected_week + 6
        dff = dff[(dff[week_col] >= week_min) & (dff[week_col] <= week_max)]

    # Filter to service
    if service_col and service_col in dff.columns and selected_service:
        dff = dff[dff[service_col] == selected_service]
        service_display = selected_service.replace("_", " ").title()
        if selected_week is not None:
            title = f"Impact Validation — {service_display} (Week {selected_week} ±6)"
        else:
            title = f"Impact Validation — {service_display}"

    # Aggregate by week
    agg_dict = {}
    if morale_col and morale_col in dff.columns:
        agg_dict[morale_col] = "mean"
    if satisfaction_col and satisfaction_col in dff.columns:
        agg_dict[satisfaction_col] = "mean"

    if not agg_dict:
        fig = go.Figure()
        fig.add_annotation(
            text="No morale/satisfaction data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        apply_standard_layout(fig, title, font_size=14)
        fig.update_layout(showlegend=False)
        return fig

    agg = dff.groupby(week_col, dropna=False).agg(agg_dict).reset_index()

    fig = go.Figure()

    if morale_col and morale_col in agg.columns:
        fig.add_trace(
            go.Scatter(
                x=agg[week_col],
                y=agg[morale_col],
                mode="lines+markers",
                name="Staff Morale",
                line=dict(color="#9b59b6", width=2),
                marker=dict(size=8),
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
                line=dict(color="#3498db", width=2),
                marker=dict(size=8),
                hovertemplate="Week %{x}<br>Satisfaction: %{y:.1f}<extra></extra>",
            )
        )

    # y-axis padding
    all_values: List[float] = []
    if morale_col and morale_col in agg.columns:
        all_values.extend(agg[morale_col].dropna().tolist())
    if satisfaction_col and satisfaction_col in agg.columns:
        all_values.extend(agg[satisfaction_col].dropna().tolist())

    if all_values:
        y_min = min(all_values)
        y_max = max(all_values)
        pad = (y_max - y_min) * 0.1 if y_max > y_min else 0.5
        y_range = [max(0, y_min - pad), y_max + pad]
    else:
        y_range = [0, 10]

    apply_standard_layout(fig, title, font_size=14, top_margin=120, legend_y=1.08)

    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Score",
        margin=dict(l=20, r=20, t=120, b=30),
        hovermode="x unified",
        yaxis=dict(range=y_range, autorange=False),
        plot_bgcolor="white",
    )

    if selected_week is not None:
        fig.add_vline(
            x=selected_week,
            line_dash="dash",
            line_color="#e74c3c",
            line_width=2,
            annotation_text="Selected Week",
            annotation_position="top",
            annotation_font_color="#e74c3c",
            annotation_font_size=10,
            annotation_font_weight="bold",
        )

    return fig


# ============================================================================
# VISUALIZATION 7: Service Capacity Breakdown (Detail View)
# ============================================================================
def make_capacity_breakdown(
    df: pd.DataFrame,
    week: int,
    service: str,
    week_col: str,
    service_col: str,
    beds_col: Optional[str] = None,
    admitted_col: Optional[str] = None,
    refused_col: Optional[str] = None,
    staff_col: Optional[str] = None,
    utilization_col: Optional[str] = None,
    patients_per_staff_col: Optional[str] = None,
    title: str = "Service Capacity Breakdown",
):
    dff = df[(df[week_col] == week) & (df[service_col] == service)]

    if dff.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data for {service} in Week {week}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14),
        )
        apply_standard_layout(fig, title, font_size=14)
        fig.update_layout(showlegend=False)
        return fig

    values = {}
    labels: List[str] = []
    colors: List[str] = []

    if beds_col and beds_col in dff.columns:
        values["Beds"] = float(dff[beds_col].sum())
        labels.append("Beds")
        colors.append("#3498db")

    if admitted_col and admitted_col in dff.columns:
        values["Admitted"] = float(dff[admitted_col].sum())
        labels.append("Admitted")
        colors.append("#2ecc71")

    if refused_col and refused_col in dff.columns:
        values["Refused"] = float(dff[refused_col].sum())
        labels.append("Refused")
        colors.append("#e74c3c")

    if staff_col and staff_col in dff.columns:
        values["Staff"] = float(dff[staff_col].sum())
        labels.append("Staff")
        colors.append("#9b59b6")

    fig = go.Figure(
        data=[
            go.Bar(
                y=labels,
                x=[values[label] for label in labels],
                orientation="h",
                marker_color=colors,
                text=[f"{values[label]:.0f}" for label in labels],
                textposition="outside",
                textfont=dict(size=14, color="#333"),
            )
        ]
    )

    ratio_parts: List[str] = []
    if utilization_col and utilization_col in dff.columns:
        util = float(dff[utilization_col].mean())
        ratio_parts.append(f"Utilization: {util:.0%}")
    if patients_per_staff_col and patients_per_staff_col in dff.columns:
        pps = float(dff[patients_per_staff_col].mean())
        ratio_parts.append(f"Pts/Staff: {pps:.1f}")

    service_display = service.replace("_", " ").title()
    subtitle = (
        f"<br><span style='font-size:12px;color:#666'>{' · '.join(ratio_parts)}</span>"
        if ratio_parts
        else ""
    )

    apply_title(
        fig, f"{service_display} — Week {week}{subtitle}", top_margin=110, font_size=14
    )
    fig.update_layout(
        xaxis_title="Count",
        yaxis_title="",
        margin=dict(l=80, r=40, t=110, b=40),
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
        yaxis=dict(tickfont=dict(size=12)),
    )
    return fig


# ============================================================================
# ENHANCED HEATMAP: With click selection support
# ============================================================================
def make_heatmap_interactive(
    df: pd.DataFrame,
    week_col: str,
    service_col: str,
    values: pd.Series,
    title: str,
    selected_week: Optional[int] = None,
    selected_service: Optional[str] = None,
):
    dff = df[[week_col, service_col]].copy()
    dff["value"] = values.values
    pivot = dff.pivot_table(
        index=service_col, columns=week_col, values="value", aggfunc="sum", fill_value=0
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        title=title,
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
                line=dict(color="black", width=3),
            )

    apply_standard_layout(fig, title, font_size=16, top_margin=100, legend_y=1.05)
    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Service",
        showlegend=False,
    )

    fig.update_traces(
        hovertemplate="Service: %{y}<br>Week: %{x}<br>Value: %{z:.2f}<extra></extra>"
    )

    return fig
