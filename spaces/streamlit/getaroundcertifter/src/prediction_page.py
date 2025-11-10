# prediction_page.py
from __future__ import annotations

import json
import time
from typing import Any

import plotly.io as pio
import streamlit as st
from common import read_logo, get_plotly_theme
from loaders import fetch_api_info, predict_rows

# Plotly theme configuration
pio.templates["getaround"] = get_plotly_theme()
pio.templates.default = "getaround"

# Allowed values (must match API-side validation)
MODEL_KEYS: list[str] = [
    "citroen",
    "renault",
    "bmw",
    "peugeot",
    "audi",
    "nissan",
    "mitsubishi",
    "mercedes",
    "volkswagen",
    "toyota",
    "seat",
    "subaru",
    "pgo",
    "opel",
    "ferrari",
    "maserati",
    "suzuki",
    "ford",
    "porsche",
    "alfa romeo",
    "kia motors",
    "fiat",
    "lamborghini",
    "lexus",
    "honda",
    "mazda",
    "mini",
    "yamaha",
]

FUEL: list[str] = ["diesel", "petrol", "other"]

PAINT: list[str] = [
    "black",
    "grey",
    "blue",
    "white",
    "brown",
    "silver",
    "red",
    "beige",
    "green",
    "orange",
]

CAR_TYPES: list[str] = [
    "estate",
    "sedan",
    "suv",
    "hatchback",
    "subcompact",
    "coupe",
    "convertible",
    "van",
]

MODEL_KEY_LABELS = {
    "alfa romeo": "Alfa Romeo",
    "audi": "Audi",
    "bmw": "BMW",
    "citroen": "Citroën",
    "ferrari": "Ferrari",
    "fiat": "Fiat",
    "ford": "Ford",
    "honda": "Honda",
    "kia motors": "Kia Motors",
    "lamborghini": "Lamborghini",
    "lexus": "Lexus",
    "maserati": "Maserati",
    "mazda": "Mazda",
    "mercedes": "Mercedes",
    "mini": "Mini",
    "mitsubishi": "Mitsubishi",
    "nissan": "Nissan",
    "opel": "Opel",
    "peugeot": "Peugeot",
    "pgo": "PGO",
    "porsche": "Porsche",
    "renault": "Renault",
    "seat": "SEAT",
    "subaru": "Subaru",
    "suzuki": "Suzuki",
    "toyota": "Toyota",
    "volkswagen": "Volkswagen",
    "yamaha": "Yamaha",
}

FUEL_LABELS = {
    "diesel": "Diesel",
    "petrol": "Essence",
    "other": "Autre / inconnu",
}

PAINT_LABELS = {
    "beige": "Beige",
    "black": "Noir",
    "blue": "Bleu",
    "brown": "Marron",
    "green": "Vert",
    "grey": "Gris",
    "orange": "Orange",
    "other": "Autre couleur",
    "red": "Rouge",
    "silver": "Argent",
    "white": "Blanc",
}

CAR_TYPE_LABELS = {
    "convertible": "Cabriolet",
    "coupe": "Coupé",
    "estate": "Break",
    "hatchback": "Compacte / Hatchback",
    "other": "Autre type",
    "sedan": "Berline",
    "subcompact": "Citadine",
    "suv": "SUV",
    "van": "Van / Monospace",
}


# Helper functions
@st.cache_data(show_spinner=False)
def _safe_fetch_api_info() -> dict[str, Any]:
    """Safely fetch model metadata from API with caching and error handling."""
    try:
        return fetch_api_info() or {}
    except Exception as exc:  # pragma: no cover
        st.warning("Impossible de récupérer les métadonnées de l’API.")
        st.exception(exc)
        return {}


def _usd(val: float) -> str:
    """Format a float as a USD string (e.g., 1234.5 → '$1,234.50')."""
    return f"${val:,.2f}"


# Main page
def page_prediction() -> None:
    """Render the single prediction page (uses the /predict API endpoint)."""

    # Header / branding
    svg = read_logo("getaround_logo.svg")
    if svg:
        st.markdown(
            f"<div style='text-align:center'>{svg}</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<h2 style='text-align:center;'>"
        "Prédiction du prix journalier de location — 2017 USA (API)"
        "</h2>",
        unsafe_allow_html=True,
    )

    # API metadata
    info: dict[str, Any] = _safe_fetch_api_info()
    features = info.get("features") or []
    st.caption(f"Modèle : `{info.get('model_path', 'N/A')}`")
    st.caption(f"Features attendues : {features if features else 'N/A'}")

    ok = bool(info) and (
        info.get("features") is not None or info.get("model_path") is not None
    )
    st.caption(f"Statut API : {'🟢 Connectée' if ok else '🔴 Indisponible'}")

    st.link_button(
        "📘 Ouvrir la documentation API",
        "https://flodussart-getaroundapicertif.hf.space/docs",
    )
    st.divider()

    # Prepare sorted choices for UI
    sorted_model_keys = sorted(
        MODEL_KEYS,
        key=lambda x: MODEL_KEY_LABELS.get(x, x).lower(),
    )
    sorted_fuel = sorted(
        FUEL,
        key=lambda x: FUEL_LABELS.get(x, x).lower(),
    )
    sorted_paint = sorted(
        PAINT,
        key=lambda x: PAINT_LABELS.get(x, x).lower(),
    )
    sorted_car_types = sorted(
        CAR_TYPES,
        key=lambda x: CAR_TYPE_LABELS.get(x, x).lower(),
    )

    # Single prediction form
    st.subheader("Prédiction unitaire")

    with st.form("single_form"):
        c1, c2, c3 = st.columns(3)

        mileage: int = c1.number_input(
            "Kilométrage (miles)",
            min_value=0,
            max_value=400_000,
            step=1_000,
            value=120_000,
        )
        engine_power: int = c2.number_input(
            "Puissance moteur (hp)",
            min_value=50,
            max_value=400,
            step=1,
            value=120,
        )
        model_key: str = c3.selectbox(
            "Marque du véhicule",
            sorted_model_keys,
            index=sorted_model_keys.index("renault"),
            format_func=lambda x: MODEL_KEY_LABELS.get(x, x.title()),
        )

        fuel_grouped: str = c1.selectbox(
            "Carburant",
            sorted_fuel,
            index=sorted_fuel.index("diesel"),
            format_func=lambda x: FUEL_LABELS.get(x, x),
        )
        paint_color: str = c2.selectbox(
            "Couleur de la carrosserie",
            sorted_paint,
            index=sorted_paint.index("black"),
            format_func=lambda x: PAINT_LABELS.get(x, x),
        )
        car_type: str = c3.selectbox(
            "Type de véhicule",
            sorted_car_types,
            index=sorted_car_types.index("hatchback"),
            format_func=lambda x: CAR_TYPE_LABELS.get(x, x),
        )

        # Additional options
        st.markdown("**Options**")
        cc1, cc2, cc3, cc4 = st.columns(4)
        private_parking_available = cc1.checkbox(
            "Parking privé disponible",
            value=False,
        )
        has_gps = cc2.checkbox("GPS", value=True)
        has_air_conditioning = cc3.checkbox("Climatisation", value=True)
        automatic_car = cc4.checkbox("Boîte automatique", value=False)

        cc5, cc6, cc7 = st.columns(3)
        has_getaround_connect = cc5.checkbox("Getaround Connect", value=False)
        has_speed_regulator = cc6.checkbox("Régulateur de vitesse", value=True)
        winter_tires = cc7.checkbox("Pneus hiver", value=False)

        submitted = st.form_submit_button("Calculer le prix")

    # Prediction logic
    if submitted:
        # Construct the API payload
        row: dict[str, Any] = {
            "mileage": mileage,
            "engine_power": engine_power,
            "model_key": model_key,
            "fuel_grouped": fuel_grouped,
            "paint_color": paint_color,
            "car_type": car_type,
            "private_parking_available": private_parking_available,
            "has_gps": has_gps,
            "has_air_conditioning": has_air_conditioning,
            "automatic_car": automatic_car,
            "has_getaround_connect": has_getaround_connect,
            "has_speed_regulator": has_speed_regulator,
            "winter_tires": winter_tires,
        }

        # Perform API call
        try:
            t0 = time.perf_counter()
            pred = predict_rows([row])[0]
            latency_ms = (time.perf_counter() - t0) * 1000

            m1, m2 = st.columns(2)
            m1.metric("Prix journalier prédit (USD)", _usd(pred))
            m2.metric("Latence API (ms)", f"{latency_ms:.0f}")

            st.success(f"Prix prédit : {_usd(pred)}")
        except Exception as exc:  # pragma: no cover
            st.error("Erreur d’appel API.")
            st.exception(exc)

        # Display payloads for transparency
        payload_rows = {"rows": [row]}
        with st.expander(
            "Payload JSON envoyé (format rows — utilisé par le dashboard)",
        ):
            st.code(json.dumps(payload_rows, indent=2), language="json")

        with st.expander("Exemple curl (format rows)"):
            st.code(
                "curl -s -H 'Content-Type: application/json' "
                "-X POST https://flodussart-getaroundapicertif.hf.space/predict "
                f"-d '{json.dumps(payload_rows)}'",
                language="bash",
            )

        # Alternative payload ("input" format)
        feature_order = list(row.keys())
        ordered_values = [row[name] for name in feature_order]
        payload_input = {"input": [ordered_values]}

        with st.expander("Payload alternatif (format input : [[...]])"):
            st.code(json.dumps(payload_input, indent=2), language="json")

        with st.expander("Exemple curl (format input)"):
            st.code(
                "curl -s -H 'Content-Type: application/json' "
                "-X POST https://flodussart-getaroundapicertif.hf.space/predict "
                f"-d '{json.dumps(payload_input)}'",
                language="bash",
            )
