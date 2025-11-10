# loaders.py
from __future__ import annotations

import os
from typing import Optional, Any

import pandas as pd
import requests
import streamlit as st


XLSX_URL: str = os.getenv(
    "GETAROUND_DELAY_XLSX_URL",
    "https://huggingface.co/datasets/flodussart/getaround_xls_certif/resolve/main/get_around_delay_analysis.xlsx",
)

CSV_URL: str = os.getenv(
    "GETAROUND_PRICING_CSV_URL",
    "https://huggingface.co/datasets/flodussart/getaround_pricing_project/resolve/main/get_around_pricing_project.csv",
)

API_URL: str = os.getenv(
    "GETAROUND_API_URL",
    "https://flodussart-getaroundapicertif.hf.space",
)


# Data loading (cached)
@st.cache_data(show_spinner=False)
def load_pricing() -> pd.DataFrame:
    """Load the pricing CSV from Hugging Face.

    Notes
    -----
    - Direct URL reading via pandas is sufficient for public HF datasets.
    - Minimal parsing so column types are inferred naturally.
    """
    return pd.read_csv(CSV_URL)


@st.cache_data(show_spinner=False)
def load_delay() -> pd.DataFrame:
    """Load the delay Excel from Hugging Face.

    Notes
    -----
    - Direct URL reading via pandas is sufficient for public HF datasets.
    - Requires an Excel engine in the environment (e.g., openpyxl).
    """
    return pd.read_excel(XLSX_URL)


# API helpers
def _api_url(path: str) -> str:
    """Join API_URL and a path like '/predict' without duplicating slashes."""
    base = API_URL.rstrip("/")
    suffix = path if path.startswith("/") else f"/{path}"
    return f"{base}{suffix}"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_api_info() -> dict[str, Optional[Any]]:
    """Fetch model metadata from the API root.

    Returns
    -------
    dict
        A normalized dict with keys 'features' and 'model_path'.
        On failure, returns {'features': None, 'model_path': None} so the UI
        can remain usable without hard failing.
    """
    url = _api_url("/")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json() or {}
        return {
            "features": data.get("features"),
            "model_path": data.get("model_path"),
        }
    except Exception:
        # Non-blocking for the UI: return a minimal fallback.
        return {"features": None, "model_path": None}


def predict_rows(rows: list[dict[str, Any]]) -> list[float]:
    """Call POST /predict using the preferred 'rows' schema with legacy fallback.

    This function first tries the modern payload: {"rows": [...]}. If the API
    rejects it with a 422 (validation error), it falls back to the legacy
    matrix payload: {"input": [[...], ...]}.

    Parameters
    ----------
    rows : list of dict
        Each dict must match the API schema (feature: value).

    Returns
    -------
    list of float
        Model predictions as floats.

    Raises
    ------
    requests.HTTPError
        If the HTTP request fails with a non-2xx (other than the handled 422).
    ValueError
        If the API response format is unexpected (missing predictions list).
    """
    url = _api_url("/predict")
    headers = {"Content-Type": "application/json"}

    # Preferred modern schema
    try:
        resp = requests.post(url, json={"rows": rows}, headers=headers, timeout=20)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json() or {}
        preds = data.get("prediction") or data.get("predictions")
        if not isinstance(preds, list):
            raise ValueError("Unexpected API response: missing 'prediction' list.")
        return [float(x) for x in preds]

    except requests.HTTPError as exc:
        # Fallback if API rejects 'rows' with a validation error (commonly 422)
        if exc.response is not None and exc.response.status_code == 422:
            matrix = [list(r.values()) for r in rows]
            resp = requests.post(
                url, json={"input": matrix}, headers=headers, timeout=20
            )
            resp.raise_for_status()
            data = resp.json() or {}
            preds = data.get("prediction") or data.get("predictions")
            if not isinstance(preds, list):
                raise ValueError("Unexpected API response in fallback mode.")
            return [float(x) for x in preds]
        raise


__all__ = [
    "XLSX_URL",
    "CSV_URL",
    "API_URL",
    "load_pricing",
    "load_delay",
    "fetch_api_info",
    "predict_rows",
]
