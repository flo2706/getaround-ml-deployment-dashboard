<h1 align="center">Getaround API</h1>

API FastAPI de prédiction du prix journalier de location d’un véhicule.  
Le modèle est un bundle MLflow exporté et chargé localement au démarrage de l’API (pas de connexion à un serveur MLflow de tracking).

---

## Lancer l'API
Pour un lancement fiable et reproductible, l'utilisation de Docker est recommandée.

### Build & Run
```bash
docker build -t getaround-api .
docker run --rm -p 7860:7860 getaround-api

puis ouvrir:
- Swagger UI : http://localhost:7860/docs
- Redoc : http://localhost:7860/redoc

---

## Endpoints
- GET / : métadonnées (features attendues, chemin modèle, liens utiles)
- GET /healthz : health check
- POST /predict : prédiction du prix journalier

