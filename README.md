<h1 align="center">Jedha's ML Engineer Certificate</h1>
<h2 align="center">Bloc 5 : Déploiement</h2>

<p align="center"><strong>Étude de cas sur le déploiement d'un dashboard web :</strong></p>

<p align="center">
  Projet Getaround — <em>Analyse des retards et optimisation des prix</em><br>
</p>


---
## Contexte du projet

Getaround est une plateforme de location de véhicules entre particuliers.  
L’entreprise souhaite fiabiliser et automatiser la gestion de ses locations autour de deux problématiques clés :

1. **Retards de restitution** — qui perturbent la rotation des véhicules et entraînent une perte de revenus.  
2. **Optimisation des prix** — pour ajuster la tarification en fonction des caractéristiques du véhicule et du marché.

L’objectif est de concevoir et déployer une solution de **Machine Learning opérationnelle**, combinant :
- un **dashboard analytique** pour explorer les retards,  
- et un **modèle de prédiction de prix**, accessible via une **API déployée en production**.
---

## Objectifs principaux  

Le projet s’inscrit dans une démarche **MLOps complète**, de l’analyse exploratoire au déploiement :

- **Dashboard Streamlit**
  - Visualisation des retards et de leurs impacts sur les revenus  
  - Simulation de scénarios selon le délai minimal entre locations  
  - Intégration d’une interface de **prédiction en ligne** connectée à l’API  

- **API FastAPI**
  - Endpoint `/predict` exposant le modèle LightGBM  
  - Hébergement sur **Hugging Face Spaces**

- **Suivi du modèle**
  - Gestion des expérimentations et métriques via **MLflow**  
  - Stockage des artefacts sur **Amazon S3** et suivi des runs dans **Neon DB (PostgreSQL)**  

- **Documentation et reproductibilité**
  - Documentation automatique à l’URL `/docs`  
  - Jeux de données versionnés sur **Hugging Face Datasets**

---
## Sélection du modèle final

Plusieurs modèles ont été comparés dans MLflow : **Linear Regression**, **XGBoost** et **LightGBM**.  
Les modèles **XGBoost** présentaient un léger surapprentissage, tandis que **LightGBM** offrait un **meilleur compromis biais/variance**.  

Le modèle retenu, **`lgbm_search_catset_5`**, a été choisi pour :
- ses **performances équilibrées** entre train et test,  
- sa **stabilité en validation croisée**,  
- et son **intégration fluide** avec le pipeline MLflow.  

Ce modèle est celui **déployé dans l’API `/predict`** sur Hugging Face.

---
## Suivi et déploiement du modèle 

L’ensemble du pipeline de suivi et de déploiement repose sur **MLflow**, qui assure :  
- le **tracking des expérimentations et métriques**,  
- le **versioning des modèles et configurations**,  
- et la **centralisation des artefacts** sur S3 et Neon DB.

**Suivi du modèle :**  
[Suivi MLflow sur Hugging Face](https://huggingface.co/spaces/flodussart/getaround_mlflow)

Les artefacts (modèles entraînés, métriques, configurations) sont versionnés et sauvegardés automatiquement via :

- MLflow Tracking (expérimentations et métriques) :  
[**Suivi du modèle**](https://huggingface.co/spaces/flodussart/getaround_mlflow)

- Amazon S3 (stockage des artefacts du modèle)  
- Neon DB (PostgreSQL) pour le suivi des runs et la persistance des métadonnées

---
##  API de prédiction

L’API permet de générer des **prédictions de prix optimaux** à partir des caractéristiques d’un véhicule et d’une location.

- **Endpoint :** `/predict`  
- **Méthode :** `POST`  
- **Exemple d’entrée :**

```json
{
  "input": [[7.0, 0.27, 0.36, 20.7, 0.045, 45.0, 170.0, 1.001, 3.0, 0.45, 8.8]]
}
```
Documentation interactive :  
[**Documentation de l'API sur Hugging Face**](https://flodussart-getaroundapicertif.hf.space/doc)

Espace Hugging Face :  
[**Espace Hugging Face**](https://huggingface.co/spaces/flodussart/getaroundapicertif)

---
## Données utilisées

Deux jeux de données hébergés sur Hugging Face Datasets assurent la traçabilité et la reproductibilité du projet :


| Dataset                  | Description                                                     | Lien                                                                                                                                                  |
| ------------------------ | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **delay_analysis**       | Analyse des retards lors de la restitution des véhicules        | [get_around_delay_analysis.xlsx](https://huggingface.co/datasets/flodussart/getaround_xls_certif/resolve/main/get_around_delay_analysis.xlsx)      |
| **pricing_optimization** | Données d'entraînement pour la tarification prédictive| [ get_around_pricing_project.csv](https://huggingface.co/datasets/flodussart/getaround_pricing_project/resolve/main/get_around_pricing_project.csv) |

--- 
## Infrastructure du projet

| Composant                 | Rôle                                                 |
| ------------------------- | ---------------------------------------------------- |
| **FastAPI**               | API REST de prédiction                               |
| **Streamlit**             | Dashboard d’analyse et de visualisation              |
| **MLflow**                | Suivi des expérimentations et versioning des modèles |
| **Hugging Face Spaces**   | Hébergement de l’API et du dashboard                 |
| **Hugging Face Datasets** | Gestion publique et versionnée des jeux de données   |
| **Docker**                | Conteneurisation pour un déploiement reproductible   |

---
## Accès au dashboard :  
[**Getaround Dashboard sur Hugging Face**](https://huggingface.co/spaces/flodussart/getaroundcertifter)
