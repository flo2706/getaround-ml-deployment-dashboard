<h1 align="center">MLflow Tracking Server</h1>

Ce service déploie un serveur MLflow utilisé pour le suivi des expériences d’entraînement des modèles (tracking des runs, métriques et artefacts).    
Ce serveur MLflow fait partie du projet Getaround et centralise le suivi des expériences d’entraînement des modèles.     
Il n’est pas requis pour faire tourner l’API de prédiction.

---

## Lancer le serveur MLflow (Docker)
```bash
docker build -t getaround-mlflow .
docker run --rm -p 7860:7860 getaround-mlflow
```
Puis ouvrir :
- MLflow UI : http://localhost:7860/

---
## Configuration (variables d’environnement)

Le serveur MLflow est configuré via des variables d’environnement.    
Sur Hugging Face Spaces, ces variables sont définies comme secrets et ne sont pas exposées publiquement.    

Variables utilisées :

- `PORT` : port d’exposition du serveur MLflow
- `BACKEND_STORE_URI` : backend de stockage des runs MLflow
- `ARTIFACT_STORE_URI` : emplacement de stockage des artefacts
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` : accès au stockage S3 des artefacts
- `AWS_DEFAULT_REGION` : région AWS utilisée

Ces variables sont fournies automatiquement par la plateforme en production.

### Exemple en local (sans dépendance à AWS)

```bash
docker run --rm -p 7860:7860 \
  -e BACKEND_STORE_URI=sqlite:////home/user/app/mlflow.db \
  -e ARTIFACT_STORE_URI=file:/home/user/app/mlruns \
  getaround-mlflow
```
