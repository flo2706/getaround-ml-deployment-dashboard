import os
import json
from pathlib import Path
from typing import Optional, Any

import pandas as pd
import mlflow.pyfunc
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from unidecode import unidecode


# Configuration
PORT = int(os.getenv("PORT", 7860))
LOCAL_MODEL_PATH = os.getenv("MODEL_PATH", "model_bundle/model")


# Helper functions
def load_features_from_artifacts(model_dir: str) -> list[str]:
    """
    Attempt to load `features_used.json` generated during training.

    Fallback
    --------
    If the file is missing, return a known grouped feature layout that
    stays aligned with the API contract.
    """
    fp = Path(model_dir) / "artifacts" / "features_used.json"
    if fp.exists():
        data = json.loads(fp.read_text())
        return (
            list(data.get("numeric", []))
            + list(data.get("categorical", []))
            + list(data.get("boolean", []))
        )

    # Fallback set aligned with API contract
    return [
        "mileage",
        "engine_power",
        "model_key",
        "fuel_grouped",
        "paint_color",
        "car_type",
        "private_parking_available",
        "has_gps",
        "has_air_conditioning",
        "automatic_car",
        "has_getaround_connect",
        "has_speed_regulator",
        "winter_tires",
    ]


# FastAPI initialization
app = FastAPI(
    title="🚗 Getaround Pricing API",
    description=(
        "Prédiction du prix journalier de location.\n\n"
        "• Dashboard : https://flodussart-getaroundcertifter.hf.space\n\n"
        "• Endpoint ML : `POST /predict`\n\n"
        ' - Format recommandé : {"input": [[...], ...]} (ordre strict des features)\n\n '
        ' - Format enrichi (optionnel) : {"rows": [...] }.\n'
    ),
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Authorized origins — Streamlit app and local dev
origins = [
    "https://flodussart-getaroundcertifter.hf.space",  # Streamlit dashboard on Hugging Face
    "http://localhost:8501",  # local Streamlit testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load MLflow model bundle locally
try:
    model = mlflow.pyfunc.load_model(LOCAL_MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Unable to load local MLflow model '{LOCAL_MODEL_PATH}': {e}")

FEATURES: list[str] = load_features_from_artifacts(LOCAL_MODEL_PATH)


# Pydantic schemas
ALLOWED_FUEL = {"diesel", "petrol", "other"}
ALLOWED_PAINT = {
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
    "other",
}
ALLOWED_CARTYPE = {
    "estate",
    "sedan",
    "suv",
    "hatchback",
    "subcompact",
    "coupe",
    "convertible",
    "van",
    "other",
}

KNOWN_MODELS = {
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
    "yamaha",
    "other",
}

# If True: reject unseen categories instead of mapping them to "other"
STRICT = True


def _norm(x: Any) -> str:
    """Normalize input values (ASCII fold + strip + lowercase)."""
    return unidecode(str(x)).strip().lower()


class PredictRow(BaseModel):
    """
    Input schema aligned with grouped features used during training.
    """

    mileage: float
    engine_power: float
    model_key: str
    fuel_grouped: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

    # Normalize before validation
    @field_validator(
        "model_key",
        "fuel_grouped",
        "paint_color",
        "car_type",
        mode="before",
    )
    @classmethod
    def _normalize(cls, v: Any) -> str:
        return _norm(v)

    # Domain validations
    @field_validator("fuel_grouped")
    @classmethod
    def _fuel(cls, v: str) -> str:
        if v in ALLOWED_FUEL:
            return v
        if STRICT:
            raise ValueError(f"fuel_grouped must be in {sorted(ALLOWED_FUEL)}")
        return "other"

    @field_validator("paint_color")
    @classmethod
    def _paint(cls, v: str) -> str:
        if v in ALLOWED_PAINT:
            return v
        if STRICT:
            raise ValueError(f"paint_color must be in {sorted(ALLOWED_PAINT)}")
        return "other"

    @field_validator("car_type")
    @classmethod
    def _ctype(cls, v: str) -> str:
        if v in ALLOWED_CARTYPE:
            return v
        if STRICT:
            raise ValueError(f"car_type must be in {sorted(ALLOWED_CARTYPE)}")
        return "other"

    @field_validator("model_key")
    @classmethod
    def _model(cls, v: str) -> str:
        if v in KNOWN_MODELS:
            return v
        if STRICT:
            raise ValueError("unknown model_key")
        return "other"


class PredictPayload(BaseModel):
    """
    Accept row-wise (recommended) or legacy matrix-style input.

    Notes
    -----
    - 'rows' is validated/normalized by Pydantic.
    - 'input' requires strict column ordering as in `FEATURES`.
    """

    rows: Optional[list[PredictRow]] = Field(default=None)
    input: Optional[list[list[Any]]] = Field(
        default=None,
        description=(
            "Format legacy: matrix. Each row must follow ordering: {}".format(FEATURES)
        ),
    )


# Routes
@app.get("/")
def root() -> dict[str, Any]:
    """Root endpoint with basic metadata."""
    return {
        "status": "running",
        "message": "Bienvenue sur l’API Getaround 🚗 — utilisez POST /predict",
        "docs": "/docs",
        "dashboard": "https://flodussart-getaroundcertifter.hf.space",
        "model_path": LOCAL_MODEL_PATH,
        "features": FEATURES,
    }


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    """Lightweight health check endpoint."""
    return {"status": "ok", "features": FEATURES}


def build_df_from_payload(payload: PredictPayload) -> pd.DataFrame:
    """
    Build a feature-aligned DataFrame from either input format.

    - rows  → typed, normalized, validated objects (preferred)
    - input → raw matrix, strict `FEATURES` column ordering required
    """
    if payload.rows:
        df = pd.DataFrame([r.model_dump() for r in payload.rows])
        missing = [c for c in FEATURES if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Colonnes manquantes: {missing}. Attendu: {FEATURES}",
            )
        # Enforce training-time column order
        return df[FEATURES]

    if payload.input:
        n_cols = len(FEATURES)
        bad_rows = [i for i, row in enumerate(payload.input) if len(row) != n_cols]
        if bad_rows:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Lignes {bad_rows} n'ont pas {n_cols} valeurs. "
                    f"Ordre attendu: {FEATURES}"
                ),
            )
        return pd.DataFrame(payload.input, columns=FEATURES)

    raise HTTPException(
        status_code=400,
        detail="Fournis soit 'rows': [...] soit 'input': [[...]].",
    )


@app.post("/predict")
def predict(payload: PredictPayload) -> dict[str, list[float]]:
    """
    Perform model inference and return predictions as plain Python floats.
    """
    try:
        df = build_df_from_payload(payload)
        y_hat = model.predict(df)
        preds = [
            float(x) for x in (y_hat.tolist() if hasattr(y_hat, "tolist") else y_hat)
        ]
        return {"prediction": preds}
    except HTTPException:
        # Re-raise HTTP 4xx errors as-is
        raise
    except Exception as e:
        # Convert unexpected errors into a 500 for the client
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {e}",
        ) from e


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=PORT)
