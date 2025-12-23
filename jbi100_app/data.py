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
    staff: Optional[str]   # derived staff count column name (we will add it)


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


def load_hospitalbeds(data_dir: str = "data") -> Tuple[pd.DataFrame, HBCols, Dict[str, pd.DataFrame]]:
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
    for name in ["services_weekly.csv", "service_weekly.csv", "weekly_services.csv", "hospital_beds.csv"]:
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

    requests = _pick_col(weekly, ["patients_request", "patient_requests", "requests", "demand"])
    admissions = _pick_col(weekly, ["patients_admitted", "admitted", "admissions", "accepted"])
    refusals = _pick_col(weekly, ["patients_refused", "refused", "refusals", "rejections"])
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

    cols = HBCols(
        week=week,
        service=service,
        requests=requests,
        admissions=admissions,
        refusals=refusals,
        beds=beds,
        staff=staff_col_name,  # None if we couldn't derive
    )

    return weekly, cols, extras
