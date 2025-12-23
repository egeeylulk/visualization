# BedFlow Diagnostic Dashboard — UI Redesign Specification

> **Version:** 2.0  
> **Date:** December 23, 2025  
> **Core Question:** _"Why did refusals increase for a given service during a specific week?"_

---

## Executive Summary

This redesign transforms BedFlow from a cramped single-page dashboard into a **two-stage diagnostic workflow** with clear progressive disclosure, selection-aware controls, and intelligent use of screen space.

**Key Changes:**

1. **Two-stage layout:** Locator Mode → Diagnostic Workspace Mode
2. **Context Panel** replaces static sidebar (selection-aware controls)
3. **Views 2–4 become diagnostically meaningful** with windowed data, visual markers, and narrative structure
4. **KPIs reflect filtered context** (not full dataset)
5. **Remove Comparison Mode** (replace with focus-based filtering)

---

## 1. Information Architecture

### Stage A: Locator Mode (No Selection)

| Zone                          | Component                                 | Purpose                                |
| ----------------------------- | ----------------------------------------- | -------------------------------------- |
| **Header Strip**              | Mini KPI bar (4 cards)                    | Global metrics for filtered week range |
| **Context Panel** (collapsed) | Week range slider, Diagnostic focus radio | Pre-filter before selection            |
| **Main Area**                 | Full-width heatmap (Service × Week)       | Identify problem cells to investigate  |
| **Footer Area**               | Instructional prompt                      | Guide user toward selection            |

**Visible Controls (Pre-Selection):**

- 🎚️ Week Range slider
- 🔘 Diagnostic Focus (Refusal Rate / Staffing Pressure / Bed Saturation)
- 📍 Selection Status: "No selection — Click a cell to begin"

---

### Stage B: Diagnostic Workspace Mode (Selection Exists)

| Zone                         | Component                                      | Purpose                              |
| ---------------------------- | ---------------------------------------------- | ------------------------------------ |
| **Sticky Header**            | Selection badge + navigation buttons           | Context + Back/Clear actions         |
| **Mini-Locator Strip**       | Collapsed heatmap (1 row for selected service) | Context + alternative week selection |
| **Main Workspace**           | 2×2 grid of diagnostic views                   | Investigate the selected case        |
| **Context Panel** (expanded) | Selection-aware controls + event toggles       | Refine diagnostic lens               |

**Visible Controls (Post-Selection):**

- 🔍 Active Selection badge (Service + Week)
- ✕ Clear Selection button
- ↑ Back to Locator button
- 👁️ Context Visibility checkboxes (Flu / Strike / Donation)
- 🎚️ Diagnostic Focus (carries over)
- 📊 View Options: "Show baseline comparison" toggle

---

## 2. Layout Grid Specification

### 2.1 Locator Mode Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]                   (4-column flex) │
├────────────────┬─────────────────────────────────────────────────────┤
│                │                                                     │
│  Context Panel │           PROBLEM LOCATOR HEATMAP                   │
│  (240px fixed) │              (Service × Week)                       │
│                │                                                     │
│  ┌──────────┐  │         [Click cell to investigate →]               │
│  │Week Range│  │                                                     │
│  │  [====]  │  │                                                     │
│  └──────────┘  │                                                     │
│  ┌──────────┐  │                                                     │
│  │Diagnostic│  │                                                     │
│  │  Focus   │  │                                                     │
│  │ ○ Refusal│  │                                                     │
│  │ ○ Staff  │  │                                                     │
│  │ ○ Beds   │  │                                                     │
│  └──────────┘  │                                                     │
│                │                                                     │
│  Selection:    │                                                     │
│  [None]        │                                                     │
│                │                                                     │
└────────────────┴─────────────────────────────────────────────────────┘
```

**CSS Grid:**

```css
.locator-mode {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: auto 1fr;
  gap: 16px;
  padding: 16px;
  min-height: 100vh;
}

.kpi-strip {
  grid-column: 1 / -1;
  display: flex;
  gap: 12px;
}
```

---

### 2.2 Workspace Mode Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ 📊 Diagnostic Workspace   ✅ Cardiology — Week 23    [↑ Back] [✕ Clear]│
├──────────────────────────────────────────────────────────────────────┤
│                    MINI-LOCATOR (selected service row only)          │
│    [w18][w19][w20][w21][w22][■W23■][w24][w25][w26][w27][w28]         │
├──────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │               VIEW 2: CAPACITY TIMELINE (±6 weeks)             │  │
│  │   Stacked bar: Admitted + Refused | Staff line | Event bands   │  │
│  │                      ▼ Selected Week marker                    │  │
│  └────────────────────────────────────────────────────────────────┘  │
├────────────────────────────────┬─────────────────────────────────────┤
│  ┌──────────────────────────┐  │  ┌───────────────────────────────┐  │
│  │  VIEW 3: IMPACT VALID.   │  │  │  VIEW 4: PRESSURE ANALYSIS    │  │
│  │  Morale + Satisfaction   │  │  │  Scatter: Staff vs Util       │  │
│  │      (±6 week window)    │  │  │      ★ Selected point         │  │
│  │   ▼ Selected Week line   │  │  │   — Avg lines + σ deviation   │  │
│  └──────────────────────────┘  │  └───────────────────────────────┘  │
├────────────────────────────────┴─────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │              VIEW 5: CASE EXPLANATION (Narrative)              │  │
│  │   Key metrics + bullet findings + contextual events            │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

**CSS Grid:**

```css
.workspace-mode {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto 1fr 1fr auto;
  gap: 16px;
  padding: 16px;
}

.sticky-header {
  grid-column: 1 / -1;
  position: sticky;
  top: 0;
  z-index: 100;
}
.mini-locator {
  grid-column: 1 / -1;
  height: 80px;
}
.timeline-view {
  grid-column: 1 / -1;
  height: 400px;
}
.impact-view {
  grid-column: 1 / 2;
}
.pressure-view {
  grid-column: 2 / 2;
}
.explanation-view {
  grid-column: 1 / -1;
}
```

---

### 2.3 Responsive Breakpoints

| Breakpoint     | Behavior                                                          |
| -------------- | ----------------------------------------------------------------- |
| **≥1200px**    | Full 2-column workspace grid                                      |
| **900–1199px** | Stack Views 3+4 vertically; Context Panel becomes drawer          |
| **<900px**     | Single-column stack; Mini-locator hidden; floating action buttons |

```css
@media (max-width: 1199px) {
  .workspace-mode {
    grid-template-columns: 1fr;
  }
  .impact-view,
  .pressure-view {
    grid-column: 1 / -1;
  }
}

@media (max-width: 899px) {
  .mini-locator {
    display: none;
  }
  .context-panel {
    position: fixed;
    bottom: 0;
    transform: translateY(calc(100% - 56px));
    transition: transform 0.3s ease;
  }
  .context-panel.expanded {
    transform: translateY(0);
  }
}
```

---

## 3. Context Panel Redesign

### 3.1 Pre-Selection State

```
┌─────────────────────────────┐
│ BedFlow Diagnostic Dashboard│
│ ─────────────────────────── │
│ "Why did refusals increase  │
│  for a given service during │
│  a specific week?"          │
├─────────────────────────────┤
│ 🔍 DIAGNOSTIC FOCUS         │
│   ○ Refusal Spikes          │
│   ○ Staffing Pressure       │
│   ○ Bed Saturation          │
│                             │
│ Tooltip: "Choose what       │
│ problem type to highlight   │
│ in the heatmap"             │
├─────────────────────────────┤
│ 📅 ANALYSIS PERIOD          │
│   Week 1 ──●────● Week 52   │
│            [12]  [36]       │
│                             │
│ Tooltip: "Narrow the time   │
│ window to focus your search"│
├─────────────────────────────┤
│ 📍 SELECTION STATUS         │
│ ┌─────────────────────────┐ │
│ │ ⚪ No selection         │ │
│ │                         │ │
│ │ Click a dark red cell   │ │
│ │ to begin diagnosis      │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

**Hidden Pre-Selection:**

- Event visibility toggles (not useful until viewing timeline)
- Service dropdown (selection replaces this)
- Comparison mode (removed entirely)

---

### 3.2 Post-Selection State

```
┌─────────────────────────────┐
│ 📍 ACTIVE INVESTIGATION     │
│ ┌─────────────────────────┐ │
│ │ ✅ Cardiology           │ │
│ │    Week 23              │ │
│ │                         │ │
│ │ Refusal Rate: 34%       │ │
│ │ vs. Baseline: +18pts    │ │
│ └─────────────────────────┘ │
│                             │
│ [✕ Clear Selection]         │
│ [↑ Back to Locator]         │
├─────────────────────────────┤
│ 👁️ CONTEXT VISIBILITY       │
│   ☑ 🟡 Flu Outbreaks       │
│   ☑ 🟠 Staff Strikes       │
│   ☑ 🟢 Donation Drives     │
│                             │
│ Tooltip: "Toggle event      │
│ overlays on timeline charts"│
├─────────────────────────────┤
│ 📊 VIEW OPTIONS             │
│   ☑ Show baseline comparison│
│   ☐ Highlight anomalies     │
│                             │
│ Tooltip: "Baseline = average│
│ of same service, all weeks" │
├─────────────────────────────┤
│ 🔍 DIAGNOSTIC FOCUS         │
│   ● Refusal Spikes (active) │
│   ○ Staffing Pressure       │
│   ○ Bed Saturation          │
└─────────────────────────────┘
```

---

## 4. Interaction Specification

### 4.1 Selection Mechanics

| Action                             | Behavior                                              |
| ---------------------------------- | ----------------------------------------------------- |
| **Click heatmap cell**             | Select (service, week) → transition to Workspace Mode |
| **Click same cell again**          | Deselect → return to Locator Mode                     |
| **Click different cell**           | Change selection → Workspace updates in place         |
| **Click "Clear Selection" button** | Deselect → return to Locator Mode                     |
| **Click "Back to Locator" button** | Smooth scroll to heatmap; keep selection active       |

**Justification for toggle-deselect:** Users exploring multiple cases benefit from quick A/B comparison without reaching for a button. The clear button remains for explicit intent.

---

### 4.2 Auto-Scroll Behavior

```javascript
// On selection change → smooth scroll to Workspace
function onSelectionChange(newSelection) {
  if (newSelection.service && newSelection.week) {
    const workspace = document.getElementById("workspace-mode");
    workspace.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }
}

// Respect reduced motion preference
const prefersReducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)"
).matches;
if (prefersReducedMotion) {
  workspace.scrollIntoView({ behavior: "auto", block: "start" });
}
```

---

### 4.3 Crosshair Linking (Views 2, 3, 4)

All time-based charts (Timeline, Impact) share a hover crosshair:

```python
# Dash callback for crosshair sync
@app.callback(
    Output('impact-timeline', 'figure'),
    Input('capacity-timeline', 'hoverData'),
    State('impact-timeline', 'figure')
)
def sync_crosshair(hover_data, current_fig):
    if hover_data:
        week = hover_data['points'][0]['x']
        # Add temporary vline at hovered week
        current_fig['layout']['shapes'] = [{
            'type': 'line',
            'x0': week, 'x1': week,
            'y0': 0, 'y1': 1,
            'yref': 'paper',
            'line': {'color': 'rgba(0,0,0,0.3)', 'width': 1, 'dash': 'dot'}
        }]
    return current_fig
```

---

### 4.4 Selected Week Highlighting

All time-based charts show a persistent red dashed vertical line at the selected week:

```python
fig.add_vline(
    x=selected_week,
    line_dash="dash",
    line_color="#e74c3c",
    line_width=2,
    annotation_text=f"Week {selected_week}",
    annotation_position="top",
    annotation_font=dict(color="#e74c3c", size=10, weight="bold")
)
```

---

## 5. View Redesign Specifications

### 5.1 View 2: Event-Aware Capacity Timeline

**Purpose:** Answer _"What happened operationally during this period?"_

| Attribute            | Specification                                                               |
| -------------------- | --------------------------------------------------------------------------- |
| **Time Window**      | Selected week ±6 weeks (13-week window)                                     |
| **Primary Marks**    | Stacked bar: Admitted (green) + Refused (red)                               |
| **Secondary Marks**  | Staff line (purple, scaled, right y-axis)                                   |
| **Event Bands**      | Vertical shaded regions for flu (yellow), strike (orange), donation (green) |
| **Selection Marker** | Red dashed vline at selected week                                           |
| **Title**            | "Capacity Timeline — {Service} (Week {W} ±6)"                               |

**Narrative Elements:**

- Annotation at selected week: "Selected: +{N} refusals vs prev week"
- Legend shows event types with counts in window

---

### 5.2 View 3: Impact Validation

**Purpose:** Answer _"What was the human cost of this problem?"_

| Attribute              | Specification                                                  |
| ---------------------- | -------------------------------------------------------------- |
| **Time Window**        | Selected week ±6 weeks                                         |
| **Primary Marks**      | Dual lines: Staff Morale (purple), Patient Satisfaction (blue) |
| **Baseline Reference** | Horizontal dashed line at service average                      |
| **Delta Annotation**   | At selected week: "Morale: {X} (−{Y} vs baseline)"             |
| **Selection Marker**   | Red dashed vline at selected week                              |
| **Title**              | "Impact Validation — {Service} (Week {W} ±6)"                  |

**Enhancements:**

- Fill area between line and baseline when below average (red tint)
- Marker enlargement at selected week point

---

### 5.3 View 4: Pressure Analysis

**Purpose:** Answer _"How severe was this case relative to normal operations?"_

| Attribute             | Specification                                                              |
| --------------------- | -------------------------------------------------------------------------- |
| **Axes**              | X: Patients per Staff, Y: Refusal Rate (or Bed Utilization based on focus) |
| **Background Points** | All service-weeks, faded (opacity 0.2), colored by service                 |
| **Selected Point**    | Red star marker, size 22, black outline                                    |
| **Reference Lines**   | Dashed gray lines at mean X and mean Y                                     |
| **Deviation Label**   | Text above star: "+2.1σ" or "−1.3σ" (max of x/y deviation)                 |
| **Title**             | "Pressure Analysis — {Service} (Week {W})"                                 |

**Quadrant Interpretation Guide:**

```
        High Refusal Rate
              │
    Understaffed │  Crisis Zone
    & Overwhelmed│  (investigate)
    ─────────────┼─────────────
    Efficient    │  Overstaffed?
    Operations   │  (review)
              │
        Low Refusal Rate
      Low Staff Load    High Staff Load
```

---

### 5.4 View 5: Case Explanation (Narrative)

**Purpose:** Answer _"How do I explain this case to someone else?"_

**New Structure:**

```
┌──────────────────────────────────────────────────────────────────────┐
│  📋 CASE SUMMARY: Cardiology — Week 23                               │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  KEY METRICS                          CONTEXTUAL FACTORS             │
│  ┌────────────────────────────┐      ┌─────────────────────────────┐│
│  │  Requests:     145 (+23%)  │      │  🟡 Flu outbreak active     ││
│  │  Admitted:      96         │      │  🟠 No strikes              ││
│  │  Refused:       49 (34%)   │      │  🟢 Donation drive (Wk 22)  ││
│  │  ─────────────────────     │      └─────────────────────────────┘│
│  │  Beds:          42         │                                      │
│  │  Staff:         12         │      DIAGNOSTIC FINDINGS             │
│  │  Utilization:   98%        │      ┌─────────────────────────────┐│
│  │  Pts/Staff:     8.1        │      │  • Refusal rate +18pts above││
│  └────────────────────────────┘      │    service baseline (16%)   ││
│                                      │  • Flu week correlation: 0.7 ││
│                                      │  • Staff morale dropped to  ││
│                                      │    lowest point in 12 weeks ││
│                                      │  • Bed util near capacity   ││
│                                      └─────────────────────────────┘│
│                                                                      │
│  ────────────────────────────────────────────────────────────────── │
│  💡 HYPOTHESIS: High demand from flu outbreak exceeded bed capacity  │
│     with inadequate staffing adjustment.                             │
└──────────────────────────────────────────────────────────────────────┘
```

**Implementation:** Replace horizontal bar chart with structured HTML layout containing:

- Left column: metric cards with delta indicators
- Right column: event badges + bullet findings
- Bottom: auto-generated hypothesis (template-based)

---

## 6. Empty State Policy

**Decision:** Views 2–4 show **"Awaiting Selection"** state, not aggregate data.

**Justification:**

1. **Progressive disclosure:** Showing aggregate data pre-selection creates confusion about what's being diagnosed
2. **Performance:** Avoids computing aggregate views that will be immediately discarded
3. **User intent:** Users who haven't selected aren't yet asking diagnostic questions

**Empty State Design:**

```
┌────────────────────────────────────────────────┐
│                                                │
│           🔍                                   │
│                                                │
│     Select a cell to investigate              │
│                                                │
│     This view will show {specific content}    │
│     for your selected service-week.           │
│                                                │
│     [↑ Go to Heatmap]                         │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 7. KPI Strip Specification

**Decision:** KPIs reflect **filtered context** (week range + service selection).

| KPI                 | Pre-Selection                    | Post-Selection                          |
| ------------------- | -------------------------------- | --------------------------------------- |
| **Total Requests**  | Sum for week range, all services | Sum for selected service, selected week |
| **Total Refusals**  | Sum for week range, all services | Sum for selected service, selected week |
| **Refusal Rate**    | Avg for week range               | Rate for selected cell                  |
| **Bed Utilization** | Avg for week range               | Utilization for selected cell           |

**Visual Treatment:**

- Delta indicators: "↑ +12% vs baseline" or "↓ −5% vs baseline"
- Color coding: Green (good), Red (bad), Gray (neutral)
- Baseline = service average (when service selected) or global average (no selection)

```python
# KPI with delta indicator
def make_kpi_card(label, value, baseline, is_lower_better=False):
    delta = value - baseline
    delta_pct = (delta / baseline * 100) if baseline else 0
    is_good = (delta < 0) if is_lower_better else (delta > 0)

    return html.Div([
        html.Span(label, className="kpi-label"),
        html.Span(f"{value:.0f}", className="kpi-value"),
        html.Span(
            f"{'↑' if delta > 0 else '↓'} {abs(delta_pct):.0f}%",
            className=f"kpi-delta {'good' if is_good else 'bad'}"
        )
    ], className="kpi-card")
```

---

## 8. Comparison Mode Decision

**Decision:** **Remove Comparison Mode entirely.**

**Rationale:**

1. Current implementation is incomplete and confusing
2. Small multiples comparison adds complexity without clear diagnostic benefit
3. The diagnostic question is about a _single_ case, not service comparison

**Alternative:**

- Use **Diagnostic Focus** to change which metric is highlighted across all views
- Users can click different heatmap cells to quickly compare cases
- Future enhancement: "Pin" a case and select a second for side-by-side (v2.1)

---

## 9. Performance Recommendation

**Decision:** Use **Dash `Patch()` incremental updates** for selection-driven changes.

**Rationale:**

- Dataset is small-to-medium (52 weeks × ~10 services × ~5 metrics)
- Selection changes only require updating markers/highlights, not full re-render
- `Patch()` reduces callback latency from ~300ms to ~50ms for highlight changes

**Implementation Pattern:**

```python
from dash import Patch

@app.callback(
    Output('capacity-timeline', 'figure'),
    Input('global-state', 'data'),
    State('capacity-timeline', 'figure')
)
def update_timeline_highlights(state, current_fig):
    selected_week = state.get('selected_week')

    # Use Patch for incremental update
    patched_fig = Patch()

    # Update only the vline shape
    patched_fig['layout']['shapes'] = [{
        'type': 'line',
        'x0': selected_week, 'x1': selected_week,
        'y0': 0, 'y1': 1, 'yref': 'paper',
        'line': {'color': '#e74c3c', 'width': 2, 'dash': 'dash'}
    }]

    return patched_fig
```

**Full Re-render Triggers:**

- Week range slider change
- Diagnostic focus change
- Initial load

---

## 10. Build Checklist for Developer

### Phase 1: Layout Restructure

- [ ] Create new CSS grid system for Locator Mode (`locator-mode` class)
- [ ] Create new CSS grid system for Workspace Mode (`workspace-mode` class)
- [ ] Implement Mini-Locator strip component (single-row heatmap)
- [ ] Add sticky header for Workspace Mode with selection badge
- [ ] Implement responsive breakpoints (1200px, 900px)
- [ ] Add mobile drawer for Context Panel

### Phase 2: Context Panel

- [ ] Restructure sidebar into Context Panel with grouped sections
- [ ] Add selection-aware visibility (show/hide controls based on state)
- [ ] Add "Clear Selection" and "Back to Locator" buttons
- [ ] Add tooltips to all control groups
- [ ] Display baseline comparison in selection badge

### Phase 3: View Updates

- [ ] **View 2:** Implement ±6 week windowing
- [ ] **View 2:** Add selected week vline with annotation
- [ ] **View 3:** Implement ±6 week windowing
- [ ] **View 3:** Add baseline reference lines and delta annotation
- [ ] **View 3:** Add fill area for below-baseline periods
- [ ] **View 4:** Ensure star marker with σ deviation label
- [ ] **View 4:** Add quadrant interpretation labels
- [ ] **View 5:** Replace bar chart with narrative HTML layout
- [ ] **View 5:** Implement auto-generated hypothesis template

### Phase 4: Interactions

- [ ] Implement toggle-deselect on heatmap cell click
- [ ] Implement crosshair hover sync between Views 2 and 3
- [ ] Refine auto-scroll with reduced motion support
- [ ] Add scroll-to-heatmap for "Back to Locator" button

### Phase 5: KPIs & Polish

- [ ] Update KPI strip to show filtered context
- [ ] Add delta indicators to KPI cards
- [ ] Remove Comparison Mode radio buttons
- [ ] Implement `Patch()` for selection highlight updates
- [ ] Add loading states for view transitions
- [ ] Test responsive behavior at all breakpoints

---

## 11. Microcopy Suggestions

### Empty States

| View                           | Empty State Text                                                       |
| ------------------------------ | ---------------------------------------------------------------------- |
| **Heatmap (no data)**          | "No data matches your filters. Try expanding the week range."          |
| **Timeline (no selection)**    | "Select a cell to see what happened operationally during that period." |
| **Impact (no selection)**      | "Select a cell to validate the human cost of the identified problem."  |
| **Pressure (no selection)**    | "Select a cell to assess severity relative to normal operations."      |
| **Explanation (no selection)** | "Select a cell to generate an explanatory summary for stakeholders."   |

### Tooltips

| Control                | Tooltip Text                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------- |
| **Diagnostic Focus**   | "Choose which metric to highlight. This changes heatmap colors and Y-axis on scatter plot." |
| **Week Range**         | "Narrow the analysis period. All views will filter to this range."                          |
| **Context Visibility** | "Show or hide event overlays (flu, strikes, donations) on timeline charts."                 |
| **Clear Selection**    | "Return to the problem locator view and reset all diagnostic charts."                       |
| **Back to Locator**    | "Scroll back to the heatmap while keeping your current selection active."                   |

### Selection Badge

```
Pre-selection:  "⚪ No selection — Click a heatmap cell"
Post-selection: "✅ Cardiology — Week 23 (Refusal Rate: 34%)"
```

### Hypothesis Templates (View 5)

```
Template 1 (Flu correlation):
"High demand from flu outbreak exceeded bed capacity with inadequate staffing adjustment."

Template 2 (Strike correlation):
"Staff strike reduced effective capacity while demand remained constant."

Template 3 (High utilization):
"Near-capacity bed utilization left no buffer for demand surge."

Template 4 (Generic):
"Elevated refusal rate during this period warrants further investigation into specific operational factors."
```

---

## 12. Visual Design Tokens

```css
:root {
  /* Colors */
  --color-primary: #3498db;
  --color-danger: #e74c3c;
  --color-success: #27ae60;
  --color-warning: #f39c12;
  --color-muted: #95a5a6;
  --color-background: #f9f9f9;
  --color-surface: #ffffff;
  --color-text: #2c3e50;
  --color-text-secondary: #7f8c8d;

  /* Event Colors */
  --event-flu: rgba(241, 196, 15, 0.3);
  --event-strike: rgba(230, 126, 34, 0.3);
  --event-donation: rgba(46, 204, 113, 0.2);

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 400ms ease;
}
```

---

## Appendix: State Machine

```
┌─────────────────┐
│  LOCATOR MODE   │◄──────────────────────────────┐
│  (no selection) │                               │
└────────┬────────┘                               │
         │                                        │
         │ click cell                             │ clear / toggle-deselect
         ▼                                        │
┌─────────────────┐                               │
│  WORKSPACE MODE │───────────────────────────────┘
│  (selection)    │
│                 │◄───┐
│  • Timeline     │    │
│  • Impact       │    │ click different cell
│  • Pressure     │    │
│  • Explanation  │────┘
└─────────────────┘
```

---

_End of specification_
