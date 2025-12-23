# jbi100_app/data.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import pandas as pd


@dataclass
class HBCols:
    week: str
    service: str
    requests: Optional[str]
    admissions: Optional[str]
    refusals: Optional[str]
    beds: Optional[str]
    staff: Optional[str]  # derived staff count column name (we will add it)
    event: Optional[str] = None  # event column (flu, strike, etc.)
    # Computed columns
    refusal_rate: Optional[str] = None
    bed_utilization: Optional[str] = None
    patients_per_staff: Optional[str] = None
    demand_level: Optional[str] = None
    refusal_level: Optional[str] = None


def _pick_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    cols = {c.lower(): c for c in df.columns}

    for cand in candidates:
        key = cand.lower()
        if key in cols:
            return cols[key]

    for cand in candidates:
        cand_l = cand.lower()
        for c in df.columns:
            if cand_l in c.lower():
                return c

    return None


def _read_csv_if_exists(path: Path) -> Optional[pd.DataFrame]:
    if path.exists():
        return pd.read_csv(path)
    return None


def load_hospitalbeds(
    data_dir: str = "data",
) -> Tuple[pd.DataFrame, HBCols, Dict[str, pd.DataFrame]]:
    """
    Loads:
      - services_weekly.csv (required)
      - staff_schedule.csv (optional)
      - staff.csv (optional)
      - patients.csv (optional)

    Returns:
      weekly_df, cols, extras(dict of other dfs)
    """
    data_path = Path(data_dir)

    # ---- 1) Weekly dataset (required)
    weekly_file = None
    for name in [
        "services_weekly.csv",
        "service_weekly.csv",
        "weekly_services.csv",
        "hospital_beds.csv",
    ]:
        p = data_path / name
        if p.exists():
            weekly_file = p
            break

    if weekly_file is None:
        raise FileNotFoundError(
            f"Could not find weekly dataset in '{data_path.resolve()}'. "
            "Put your CSVs under ./data/ (e.g., services_weekly.csv)."
        )

    weekly = pd.read_csv(weekly_file)

    # Detect core columns
    week = _pick_col(weekly, ["week", "week_number", "week_index"])
    service = _pick_col(weekly, ["service", "department", "unit", "ward"])

    if week is None or service is None:
        raise ValueError(
            f"Couldn't detect 'week' and/or 'service' columns in {weekly_file.name}. "
            f"Columns found: {list(weekly.columns)}"
        )

    requests = _pick_col(
        weekly, ["patients_request", "patient_requests", "requests", "demand"]
    )
    admissions = _pick_col(
        weekly, ["patients_admitted", "admitted", "admissions", "accepted"]
    )
    refusals = _pick_col(
        weekly, ["patients_refused", "refused", "refusals", "rejections"]
    )
    beds = _pick_col(weekly, ["available_beds", "beds", "bed_available"])

    # Ensure week is sortable (your week is numeric)
    try:
        weekly[week] = pd.to_numeric(weekly[week])
    except Exception:
        pass

    # ---- 2) Optional datasets
    staff_schedule = _read_csv_if_exists(data_path / "staff_schedule.csv")
    staff_master = _read_csv_if_exists(data_path / "staff.csv")
    patients = _read_csv_if_exists(data_path / "patients.csv")

    extras: Dict[str, pd.DataFrame] = {}
    if staff_schedule is not None:
        extras["staff_schedule"] = staff_schedule
    if staff_master is not None:
        extras["staff"] = staff_master
    if patients is not None:
        extras["patients"] = patients

    # ---- 3) Derive staff availability per (week, service) from staff_schedule
    # Add a new column into weekly: "available_staff" (count of present staff)
    staff_col_name = None
    if staff_schedule is not None:
        wcol = _pick_col(staff_schedule, ["week"])
        scol = _pick_col(staff_schedule, ["service"])
        present = _pick_col(staff_schedule, ["present"])

        if wcol and scol and present:
            # Make week numeric if possible
            try:
                staff_schedule[wcol] = pd.to_numeric(staff_schedule[wcol])
            except Exception:
                pass

            # Count present staff per week/service
            sched = staff_schedule.copy()
            sched[present] = pd.to_numeric(sched[present], errors="coerce").fillna(0)

            staff_counts = (
                sched[sched[present] == 1]
                .groupby([wcol, scol])
                .size()
                .reset_index(name="available_staff")
            )

            # Merge into weekly
            weekly = weekly.merge(
                staff_counts,
                how="left",
                left_on=[week, service],
                right_on=[wcol, scol],
            )

            # Clean up duplicate join columns if names differ
            if wcol != week and wcol in weekly.columns:
                weekly.drop(columns=[wcol], inplace=True)
            if scol != service and scol in weekly.columns:
                weekly.drop(columns=[scol], inplace=True)

            weekly["available_staff"] = weekly["available_staff"].fillna(0).astype(int)
            staff_col_name = "available_staff"

    # ---- 4) Detect event column
    event_col = _pick_col(weekly, ["event", "events", "special_event"])

    # ---- 5) Compute derived metrics for visualizations
    # Refusal rate
    refusal_rate_col = None
    if requests and refusals:
        denom = weekly[requests].replace(0, float("nan"))
        weekly["refusal_rate"] = (weekly[refusals] / denom).fillna(0.0)
        refusal_rate_col = "refusal_rate"

    # Bed utilization
    bed_util_col = None
    if admissions and beds:
        denom = weekly[beds].replace(0, float("nan"))
        weekly["bed_utilization"] = (weekly[admissions] / denom).fillna(0.0)
        bed_util_col = "bed_utilization"

    # Patients per staff
    patients_per_staff_col = None
    if admissions and staff_col_name:
        denom = weekly[staff_col_name].replace(0, float("nan"))
        weekly["patients_per_staff"] = (weekly[admissions] / denom).fillna(0.0)
        patients_per_staff_col = "patients_per_staff"

    # Demand level (binned from requests)
    demand_level_col = None
    if requests:
        req_median = weekly[requests].median()
        req_q75 = weekly[requests].quantile(0.75)
        weekly["demand_level"] = pd.cut(
            weekly[requests],
            bins=[-1, req_median * 0.5, req_median, req_q75, float("inf")],
            labels=["Low", "Medium", "High", "Very High"],
        )
        demand_level_col = "demand_level"

    # Refusal level (binned from refusal_rate)
    refusal_level_col = None
    if refusal_rate_col:
        weekly["refusal_level"] = pd.cut(
            weekly["refusal_rate"],
            bins=[-0.01, 0.05, 0.15, 0.30, 1.01],
            labels=["Low", "Medium", "High", "Critical"],
        )
        refusal_level_col = "refusal_level"

    cols = HBCols(
        week=week,
        service=service,
        requests=requests,
        admissions=admissions,
        refusals=refusals,
        beds=beds,
        staff=staff_col_name,  # None if we couldn't derive
        event=event_col,
        refusal_rate=refusal_rate_col,
        bed_utilization=bed_util_col,
        patients_per_staff=patients_per_staff_col,
        demand_level=demand_level_col,
        refusal_level=refusal_level_col,
    )

    return weekly, cols, extras
