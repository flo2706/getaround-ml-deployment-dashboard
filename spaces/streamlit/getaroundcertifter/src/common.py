# common.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

# Constants

# Column names (dataset schema)
COL_DELAY = "delay_at_checkout_in_minutes"
COL_GAP = "time_delta_with_previous_rental_in_minutes"
COL_CHECKIN = "checkin_type"
COL_RENTAL_ID = "rental_id"
COL_PREV_ID = "previous_ended_rental_id"
COL_STATE = "state"

# Clipping bounds (minutes) used across the app for delay visualizations
CLIP_MIN, CLIP_MAX = -500, 1000

# Order of checkout status labels used in charts 
ORDER_STATUS = ["En avance", "À l'heure", "En retard"]

# Brand/color palette (kept centralized for visual consistency)
BRAND_BLUE = "#2563eb"     # default series color
MOBILE_BLUE = "#3b82f6"    # mobile
CONNECT_AMBER = "#f59e0b"  # connect
SUCCESS_GREEN = "#10b981"  # on-time/early
DANGER_RED = "#ef4444"     # late
GREY_NEUTRAL = "#9ca3af"   # neutral
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
    "COL_DELAY",
    "COL_GAP",
    "COL_CHECKIN",
    "COL_RENTAL_ID",
    "COL_PREV_ID",
    "COL_STATE",
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
    """Return a minimal Plotly template aligned with the dashboard styles.

    Notes
    -----
    - Keep the theme small and predictable; charts can still override layout.
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
    """Place chart title identically across all figures."""
    fig.update_layout(
        title=dict(text=text, x=0.5, y=y, xanchor="center", yanchor="top"),
        margin=dict(t=70),
    ) 


def require_cols(df: pd.DataFrame, cols: set[str], label: str) -> bool:
    """Validate that required columns exist in a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe to validate.
    cols : set[str]
        Required column names.
    label : str
        Friendly dataframe label displayed in Streamlit warnings.

    Returns
    -------
    bool
        True if all columns are present, False otherwise (with a Streamlit warning).
    """
    missing = cols - set(df.columns)
    if missing:
        st.warning(f"Colonnes manquantes dans {label} : {sorted(missing)}")
        return False
    return True


def read_logo(name: str = "getaround_logo.svg") -> Optional[str]:
    """Read an SVG file colocated with this module and return its content.

    Parameters
    ----------
    name : str
        SVG filename to read (default: 'getaround_logo.svg').

    Returns
    -------
    Optional[str]
        SVG text content, or None if not found/readable.
    """
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
    """Apply a business scope filter to both delay and pricing datasets.

    Parameters
    ----------
    df_delay : pd.DataFrame
        Delay/ops dataframe (includes states, check-in type, etc.).
    pricing : pd.DataFrame
        Pricing dataframe (includes daily price, connect flag, etc.).
    scope : str
        One of {"Toutes les voitures", "Connect uniquement", "Mobile uniquement"}.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (filtered_delay_df, filtered_pricing_df)
    """
    df = df_delay.copy()
    pr = pricing.copy()

    # Normalize boolean for the connect flag if present
    if "has_getaround_connect" in pr.columns:
        pr["has_getaround_connect"] = (
            pr["has_getaround_connect"].astype("boolean").fillna(False)
        )

    if scope == "Connect uniquement":
        if "checkin_type" in df.columns:
            df = df[df["checkin_type"].eq("connect")].copy()
        if "has_getaround_connect" in pr.columns:
            pr = pr[pr["has_getaround_connect"]].copy()

    elif scope == "Mobile uniquement":
        if "checkin_type" in df.columns:
            df = df[df["checkin_type"].eq("mobile")].copy()
        # No safe "mobile-only" filter on the pricing dataset; keep as is.

    return df, pr


# Cached aggregations

@st.cache_data(show_spinner=False)
def state_pct(df_delay_scoped: pd.DataFrame) -> pd.DataFrame:
    """Compute the percentage breakdown of booking states.

    Returns
    -------
    pd.DataFrame
        Tidy dataframe with columns ['Statut de réservation', 'Pourcentage'].
    """
    return (
        df_delay_scoped["state"]
        .dropna()
        .value_counts(normalize=True)
        .mul(100)
        .rename_axis("Statut de réservation")
        .reset_index(name="Pourcentage")
    )


@st.cache_data(show_spinner=False)
def checkin_pct(df_delay_scoped: pd.DataFrame) -> pd.DataFrame:
    """Compute the percentage breakdown of check-in types.

    Returns
    -------
    pd.DataFrame
        Tidy dataframe with columns ['Type de check-in', 'Pourcentage'].
    """
    return (
        df_delay_scoped["checkin_type"]
        .dropna()
        .value_counts(normalize=True)
        .mul(100)
        .rename_axis("Type de check-in")
        .reset_index(name="Pourcentage")
    )


@st.cache_data(show_spinner=False)
def checkout_counts(df_delay_scoped: pd.DataFrame) -> pd.DataFrame:
    """Count checkout status (early/on-time/late) per check-in type.

    Notes
    -----
    - Returns an empty-but-typed dataframe if no valid rows exist to keep
      downstream Plotly code from breaking.

    Returns
    -------
    pd.DataFrame
        Columns: ['checkin_type', 'checkout_status', 'n', 'pct', 'total_type'].
    """
    cols = ["checkin_type", "delay_at_checkout_in_minutes"]
    df = df_delay_scoped.loc[
        df_delay_scoped["delay_at_checkout_in_minutes"].notna(), cols
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
        df["delay_at_checkout_in_minutes"],
        bins=[-1e9, -1e-9, 1e-9, 1e9],
        labels=ORDER_STATUS,
        include_lowest=True,
    )

    counts = (
        df.groupby(["checkin_type", "checkout_status"], observed=True)
        .size()
        .reset_index(name="n")
    )
    counts["total_type"] = counts.groupby("checkin_type")["n"].transform("sum")
    counts["pct"] = counts["n"] / counts["total_type"] * 100
    return counts


# Analytics helpers

def pick_value(df_long: pd.DataFrame, label: str, t: int) -> float:
    """Safely pick a single y-value in a long-format curve at threshold t.

    If t is not present in the index, perform a simple linear interpolation
    between the nearest lower and higher thresholds.

    Parameters
    ----------
    df_long : pd.DataFrame
        Long-format dataframe with columns ['Seuil (min)', 'variable', 'value'].
    label : str
        Variable name to filter (e.g., 'Masquées mobile (%)').
    t : int
        Threshold (in minutes).

    Returns
    -------
    float
        Interpolated value at t (or boundary value if extrapolated).
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
    """Precompute long-format curves for % masked and % solved vs threshold.

    Expected columns in df_gap:
    - 'delay_clipped' (float): clipped delay at checkout
    - 'gap' (float): minutes between rentals
    - 'checkin_type' in {'mobile', 'connect'}
    - 'was_conflict' (bool): historical conflict, i.e. delay_clipped > gap

    The function computes values for thresholds in [0, 180] with a 1-minute step.

    Returns
    -------
    (pd.DataFrame, pd.DataFrame)
        loss_curve, solved_curve
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
