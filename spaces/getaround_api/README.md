<h1 align="center">Getaround API</h1>

API FastAPI de prédiction du prix journalier de location d’un véhicule.  
Le modèle est un bundle MLflow exporté et chargé localement au démarrage de l’API (pas de connexion à un serveur MLflow de tracking).

- Dashboard : https://flodussart-getaround-delay-pricing-dashboard.hf.space
---

## Lancer l'API
Pour un lancement fiable et reproductible (notamment sur Windows), l'utilisation de Docker est recommandée.

### Build & run
```bash
docker build -t getaround-api .
docker run --rm -p 7860:7860 getaround-api
```

puis ouvrir:
- Swagger UI : http://localhost:7860/docs
- Redoc : http://localhost:7860/redoc

---
## Endpoints
- GET / : métadonnées (features attendues, chemin modèle, liens utiles)
- GET /healthz : health check
- POST /predict : prédiction du prix journalier


### Exemple d'input /predict
Exemple de requête pour l’endpoint `POST /predict` (format recommandé `rows`) :
```json
{
  "rows": [
    {
      "mileage": 45000,
      "engine_power": 120,
      "model_key": "renault",
      "fuel_grouped": "diesel",
      "paint_color": "grey",
      "car_type": "sedan",
      "private_parking_available": true,
      "has_gps": true,
      "has_air_conditioning": true,
      "automatic_car": false,
      "has_getaround_connect": true,
      "has_speed_regulator": true,
      "winter_tires": false
    }
  ]
}
```

Réponse attendue :
```json
{
  "prediction": [42.7]
}
```
> Le format `input` (non montré ici) est conservé pour respecter les consignes du projet.    
> Le format `rows` est recommandé pour sa validation automatique.

