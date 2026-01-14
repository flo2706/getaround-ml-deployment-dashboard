# common.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

# Constants

# Column names 
COL_DELAY_AT_CHECKOUT = "delay_at_checkout_in_minutes"
COL_GAP = "time_delta_with_previous_rental_in_minutes"
COL_CHECKIN = "checkin_type"
COL_RENTAL_ID = "rental_id"
COL_PREV_ID = "previous_ended_rental_id"
COL_STATE = "state"
COL_HAS_CONNECT = "has_getaround_connect"
COL_CAR_ID = "car_id"
COL_PRICE_PER_DAY = 'rental_price_per_day'
COL_CAR_TYPE = 'car_type'

# Clipping bounds (minutes) used across the app for delay visualizations
CLIP_MIN, CLIP_MAX = -500, 1000

# Order of checkout status labels used in charts
ORDER_STATUS = ["En avance", "À l'heure", "En retard"]

# Brand/color palette (kept centralized for visual consistency)
BRAND_BLUE = "#2563eb"  # default series color
MOBILE_BLUE = "#3b82f6"  
CONNECT_AMBER = "#f59e0b"  
SUCCESS_GREEN = "#10b981"  # on-time/early
DANGER_RED = "#ef4444"  # late
GREY_NEUTRAL = "#9ca3af"  # neutral
TEXT_DARK = "#374151"
GRID_GREY = "#e5e7eb"
BG_LIGHT = "#f8fafc"

# Reservation status colors (stacked bars, etc.)
RESA_COLORS = {
    "ended": SUCCESS_GREEN,
    "canceled": GREY_NEUTRAL,
}

# Check-in type colors
COLOR_CI = {"mobile": MOBILE_BLUE, "connect": CONNECT_AMBER}

# Checkout status colors
STATUS_COLORS = {
    "En avance": "#60a5fa",
    "À l'heure": SUCCESS_GREEN,
    "En retard": DANGER_RED,
    "Non renseigné": GREY_NEUTRAL,
}

__all__ = [
    # columns
    "COL_DELAY_AT_CHECKOUT",
    "COL_GAP",
    "COL_CHECKIN",
    "COL_RENTAL_ID",
    "COL_PREV_ID",
    "COL_STATE",
    "COL_HAS_CONNECT",
    "COL_CAR_ID",
    "COL_PRICE_PER_DAY",
    "COL_CAR_TYPE",
    # constants
    "CLIP_MIN",
    "CLIP_MAX",
    "ORDER_STATUS",
    "COLOR_CI",
    "BRAND_BLUE",
    "STATUS_COLORS",
    "RESA_COLORS",
    # utils
    "get_plotly_theme",
    "place_title",
    "require_cols",
    "read_logo",
    "apply_scope",
    "state_pct",
    "checkin_pct",
    "checkout_counts",
    "pick_value",
    "build_curves_masked_solved",
]


def get_plotly_theme() -> dict:
    """Minimal Plotly theme shared across the dashboard.

    Goal: ensure visual consistency (fonts, colors, grids) while keeping
    charts free to override layout details when needed.
    """
    return {
        "layout": {
            "font": {"family": "Inter, Segoe UI, sans-serif", "color": TEXT_DARK},
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
            "xaxis": {"gridcolor": GRID_GREY},
            "yaxis": {"gridcolor": GRID_GREY},
            "hoverlabel": {"bgcolor": "white", "font": {"color": TEXT_DARK}},
            "colorway": [BRAND_BLUE],
        }
    }


# Utility helpers
def place_title(fig, text: str, *, y: float = 0.95) -> None:
    """Standardize title positioning for visual consistency across charts."""
    fig.update_layout(
        title=dict(text=text, x=0.5, y=y, xanchor="center", yanchor="top"),
        margin=dict(t=70),
    )


def require_cols(df: pd.DataFrame, cols: set[str], label: str) -> bool:
    """Fail fast if required columns are missing and surface a Streamlit warning."""
    missing = cols - set(df.columns)
    if missing:
        st.warning(f"Colonnes manquantes dans {label} : {sorted(missing)}")
        return False
    return True


def read_logo(name: str = "getaround_logo.svg") -> Optional[str]:
    """Safely load a local SVG asset bundled with the app (returns None if unavailable)."""
    try:
        path = Path(__file__).resolve().parent / name
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def apply_scope(
    df_delay: pd.DataFrame,
    pricing: pd.DataFrame,
    scope: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the selected scope consistently to both delay and pricing datasets."""
    df = df_delay.copy()
    pr = pricing.copy()

    # Normalize boolean for the connect flag if present
    if COL_HAS_CONNECT in pr.columns:
        pr[COL_HAS_CONNECT] = (
            pr[COL_HAS_CONNECT].astype("boolean").fillna(False)
        )

    if scope == "Connect uniquement":
        if COL_CHECKIN in df.columns:
            df = df[df[COL_CHECKIN].eq("connect")].copy()
        if COL_HAS_CONNECT in pr.columns:
            pr = pr[pr[COL_HAS_CONNECT]].copy()

    elif scope == "Mobile uniquement":
        if COL_CHECKIN in df.columns:
            df = df[df[COL_CHECKIN].eq("mobile")].copy()
        # No safe "mobile-only" filter on the pricing dataset; keep as is.

    return df, pr


# Cached aggregations
@st.cache_data(show_spinner=False)
def state_pct(df_delay_scoped: pd.DataFrame) -> pd.DataFrame:
    """Compute the percentage breakdown of booking states."""
    return (
        df_delay_scoped[COL_STATE]
        .dropna()
        .value_counts(normalize=True)
        .mul(100)
        .rename_axis("Statut de réservation")
        .reset_index(name="Pourcentage")
    )


@st.cache_data(show_spinner=False)
def checkin_pct(df_delay_scoped: pd.DataFrame) -> pd.DataFrame:
    """Compute the percentage breakdown of check-in types."""
    return (
        df_delay_scoped[COL_CHECKIN]
        .dropna()
        .value_counts(normalize=True)
        .mul(100)
        .rename_axis("Type de check-in")
        .reset_index(name="Pourcentage")
    )


@st.cache_data(show_spinner=False)
def checkout_counts(df_delay_scoped: pd.DataFrame) -> pd.DataFrame:
    """Aggregate checkout outcomes (early/on-time/late) by check-in type for KPI charts."""
    cols = [COL_CHECKIN, COL_DELAY_AT_CHECKOUT]
    df = df_delay_scoped.loc[
        df_delay_scoped[COL_DELAY_AT_CHECKOUT].notna(), cols
    ].copy()

    if df.empty:
        return pd.DataFrame(
            {
                "checkin_type": pd.Series(dtype="object"),
                "checkout_status": pd.Series(dtype="object"),
                "n": pd.Series(dtype="int"),
                "pct": pd.Series(dtype="float"),
                "total_type": pd.Series(dtype="int"),
            }
        )

    df["checkout_status"] = pd.cut(
        df[COL_DELAY_AT_CHECKOUT],
        bins=[-1e9, -1e-9, 1e-9, 1e9],
        labels=ORDER_STATUS,
        include_lowest=True,
    )

    counts = (
        df.groupby([COL_CHECKIN, "checkout_status"], observed=True)
        .size()
        .reset_index(name="n")
    )
    counts["total_type"] = counts.groupby(COL_CHECKIN)["n"].transform("sum")
    counts["pct"] = counts["n"] / counts["total_type"] * 100
    return counts


# Analytics helpers
def pick_value(df_long: pd.DataFrame, label: str, t: int) -> float:
    """Safely extract a metric value from a long-format curve at a given threshold.

    If the exact threshold is missing, the value is linearly interpolated
    between the nearest lower and higher available thresholds.
    """
    sub = df_long[df_long["variable"] == label].sort_values("Seuil (min)")
    if sub.empty:
        return 0.0
    if t in set(sub["Seuil (min)"]):
        return float(sub.loc[sub["Seuil (min)"] == t, "value"].iloc[0])

    # Linear interpolation on the nearest neighbors
    lo = sub[sub["Seuil (min)"] <= t].tail(1)
    hi = sub[sub["Seuil (min)"] >= t].head(1)
    if lo.empty:
        return float(hi["value"].iloc[0])
    if hi.empty:
        return float(lo["value"].iloc[0])

    x0, y0 = int(lo["Seuil (min)"].iloc[0]), float(lo["value"].iloc[0])
    x1, y1 = int(hi["Seuil (min)"].iloc[0]), float(hi["value"].iloc[0])
    w = (t - x0) / (x1 - x0) if x1 != x0 else 0.0
    return y0 + w * (y1 - y0)


@st.cache_data(show_spinner=False)
def build_curves_masked_solved(
    df_gap: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Precompute long-format curves for the gap policy.

    Returns two long DataFrames (% masked, % avoided conflicts) across thresholds 0..180 minutes.
    - Masked: gap < t  (base: all rows per check-in type)
    - Avoided: was_conflict & (gap < t)  (base: conflicts per check-in type)

    Expected columns in df_gap: ['gap', 'was_conflict', COL_CHECKIN].
    """
    thresholds = np.arange(0, 181, 1, dtype=int)
    rows_loss: list[dict] = []
    rows_solved: list[dict] = []

    for t in thresholds:
        for ci in ("mobile", "connect"):
            sub = df_gap[df_gap[COL_CHECKIN] == ci]
            denom_loss = len(sub)
            denom_solved = int(sub["was_conflict"].sum())

            masked = int((sub["gap"] < t).sum())  # masked if gap < t
            solved = int(((sub["gap"] < t) & sub["was_conflict"]).sum())

            rows_loss.append(
                {
                    "Seuil (min)": t,
                    "variable": f"Masquées {ci} (%)",
                    "value": (masked / denom_loss * 100) if denom_loss else 0.0,
                }
            )
            rows_solved.append(
                {
                    "Seuil (min)": t,
                    "variable": f"Évités {ci} (%)",
                    "value": (solved / denom_solved * 100) if denom_solved else 0.0,
                }
            )

    loss_curve = pd.DataFrame(rows_loss)
    solved_curve = pd.DataFrame(rows_solved)
    return loss_curve, solved_curve
