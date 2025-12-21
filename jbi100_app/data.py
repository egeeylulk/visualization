# jbi100_app/data.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class HBCols:
    week: str
    service: str
    requests: str | None
    admissions: str | None
    refusals: str | None
    beds: str | None
    staff: str | None


def _pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    # fuzzy contains
    for cand in candidates:
        for c in df.columns:
            if cand.lower() in c.lower():
                return c
    return None


def load_hospitalbeds(data_dir: str = "data") -> tuple[pd.DataFrame, HBCols]:
    """
    Expected a weekly table that contains at least:
      - week column
      - service column
      - (optionally) requests/admissions/refusals/beds/staff columns
    """
    data_path = Path(data_dir)

    # Most common file in that Kaggle set for weekly/service metrics
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

    df = pd.read_csv(weekly_file)

    # Column detection (robust)
    week = _pick_col(df, ["week", "week_start", "week_number", "week_index"])
    service = _pick_col(df, ["service", "department", "unit", "ward"])

    if week is None or service is None:
        raise ValueError(
            f"Couldn't detect 'week' and/or 'service' columns in {weekly_file.name}. "
            f"Columns found: {list(df.columns)}"
        )

    requests = _pick_col(df, ["requests", "patient_requests", "demand", "requested"])
    admissions = _pick_col(df, ["admissions", "accepted", "admit", "acceptances"])
    refusals = _pick_col(df, ["refusals", "rejections", "refused", "reject", "denied"])
    beds = _pick_col(df, ["beds", "bed_available", "available_beds", "capacity_beds"])
    staff = _pick_col(df, ["staff", "nurses", "doctors", "staff_available", "capacity_staff"])

    cols = HBCols(
        week=week,
        service=service,
        requests=requests,
        admissions=admissions,
        refusals=refusals,
        beds=beds,
        staff=staff,
    )

    # Normalize week for sorting if possible
    # If it's numeric or date-like, let pandas parse; otherwise keep as string
    try:
        df[cols.week] = pd.to_datetime(df[cols.week])
    except Exception:
        pass

    return df, cols
