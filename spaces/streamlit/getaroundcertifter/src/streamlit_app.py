# streamlit_app.py
from __future__ import annotations

# import importlib
# from typing import NoReturn

import streamlit as st

from loaders import load_pricing, load_delay
from home_page import main_page
from analysis_page import page_analyse_retards
from prediction_page import page_prediction

# Page config (must be called once, and before any Streamlit UI command)
st.set_page_config(page_title="GetAround Project", page_icon="🚗", layout="wide")


def router() -> None:
    """
    Main router for the dashboard.

    Notes
    -----
    - Datasets are loaded once via loaders (which can use @st.cache_data).
    - We keep loader calls outside of try/except so errors are visible.
    - Each page is responsible for its own data guards and warnings.
    """
    # Load datasets (errors bubble up to Streamlit error box if any)
    dataset_pricing = load_pricing()
    df_delay = load_delay()

    # Sidebar navigation
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choisissez une page",
        options=("Accueil", "Analyse des retards", "Prédiction des prix"),
        index=0,
    )

    # Route
    if page == "Accueil":
        main_page(dataset_pricing, df_delay)

    elif page == "Analyse des retards":
        page_analyse_retards(df_delay, dataset_pricing)

    elif page == "Prédiction des prix":
        try:
            page_prediction()  
        except Exception as exc:  # pragma: no cover — shown in Streamlit
            st.error("Impossible de charger la page de prédiction.")
            st.exception(exc)
            st.info(
                "Vérifie que 'prediction_page.py' existe, que la fonction 'page_prediction()' "
                "est bien définie, et que ses imports ne lèvent pas d'erreur."
            )

    else:
        st.warning("Page inconnue.")


def main() -> None:
    """Small indirection to support `python streamlit_app.py` if needed."""
    router()


if __name__ == "__main__":
    main()
