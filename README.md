<h1 align="center">Jedha's ML Engineer Certificate</h1>
<h2 align="center">Bloc 5 : Déploiement</h2>

<p align="center"><strong>Une étude de cas sur le déploiement d'un dashboard web :</strong></p>

<p align="center">
  Projet Getaround — <em>Analyse des retards et optimisation des prix</em><br>
</p>


---
## Contexte du projet

Getaround est une plateforme de location de voitures entre particuliers.  
Lors de la restitution d’un véhicule, certains conducteurs sont en retard, ce qui génère des frustrations pour le conducteur suivant et un risque de perte de revenus.

L’objectif de ce projet est double :

1. **Analyser** les retards de restitution pour proposer une durée minimale entre deux locations.  
2. **Optimiser les prix** grâce à un modèle de Machine Learning accessible via une API en ligne.
---

## Objectifs principaux  
- Construire un **tableau de bord interactif** permettant de visualiser :
  - la fréquence des retards 
  - leur impact sur les revenus 
  - les scénarios possibles selon le délai entre locations
- Développer un **modèle de prédiction du prix de location**, exposé via un endpoint `/predict`, **et intégré directement dans le dashboard Streamlit pour la prédiction en ligne.**  
- Déployer l’ensemble sur le web :
  - API hébergée sur **Hugging Face Spaces** (FastAPI)
  - Dashboard déployé sur **Hugging Face** (Streamlit)
  - Suivi du modèle via **MLflow**
- Documenter l’API à l’URL `/docs`


---

## Stack technique  

| Catégorie | Technologies |
|------------|--------------|
| **Langage principal** | Python 3 |
| **Data Science** | Pandas, NumPy, Scikit-learn |
| **Visualisation** | Plotly, Streamlit |
| **API & Backend** | FastAPI |
| **Suivi de modèle** | MLflow |
| **Conteneurisation** | Docker |
| **Hébergement** | Hugging Face Spaces |
| **Suivi du code** | Git & GitHub |
| **Normes** | PEP8 (via flake8 / black) |

---

## Résultats & visualisations  
Le tableau de bord permet :

- d’explorer les retards selon les types de location (mobile, connectée)
- d’évaluer l’impact d’un délai minimal sur les revenus potentiels
- d’afficher les indicateurs clés pour la prise de décision produit
- et de tester directement le modèle de prédiction via une page dédiée qui interagit avec l’API FastAPI  

Accès au dashboard :  
[**Getaround Dashboard sur Hugging Face**](https://huggingface.co/spaces/flodussart/getaroundcertifter)

---
## Sélection du modèle final

## Sélection du modèle final

Plusieurs modèles ont été entraînés et comparés pour l’optimisation des prix :
**Linear Regression**, **XGBoost** et **LightGBM**.

Les expérimentations, suivies avec **MLflow**, ont montré que :
- Les modèles **XGBoost** offraient de très bonnes performances mais tendaient à **sur-apprendre** les données d’entraînement.  
- Le modèle **LightGBM** (run `lgbm_search_catset_5`) présentait le **meilleur compromis entre biais et variance**, avec d’excellents résultats de généralisation sur le jeu de test.

Ce modèle a donc été retenu pour :
- sa stabilité en validation croisée et ses performances équilibrées
- et son intégration fluide avec **MLflow** pour le suivi et le déploiement

Le modèle final **`lgbm_search_catset_5`** est celui **déployé dans l’API `/predict`** sur Hugging Face.


## Suivi du modèle (MLflow)
Les artefacts (modèles entraînés, métriques, configurations) sont versionnés et sauvegardés automatiquement via :

- MLflow Tracking (expérimentations et métriques) :  
[**Suivi du modèle**](https://huggingface.co/spaces/flodussart/getaround_mlflow)

- Amazon S3 (stockage des artefacts du modèle)  
- Neon DB (PostgreSQL) pour le suivi des runs et la persistance des métadonnées

---
##  API de prédiction

Une API a été développée pour fournir des **prédictions de prix optimaux** selon les caractéristiques d’un véhicule et de la location.

- **Endpoint principal :** `/predict`  
- **Méthode :** `POST`  
- **Exemple d’entrée :**

```json
{
  "input": [[7.0, 0.27, 0.36, 20.7, 0.045, 45.0, 170.0, 1.001, 3.0, 0.45, 8.8]]
}
```
Documentation de l'API :  
[**Documentation de l'API sur Hugging Face**](https://flodussart-getaroundapicertif.hf.space/doc)

Espace Hugging Face :  
[**Espace Hugging Face**](https://huggingface.co/spaces/flodussart/getaroundapicertif)

---
## Données utilisées

Deux datasets distincts ont été exploités et stockés sur Hugging Face Datasets pour garantir la traçabilité et la réplicabilité du projet.


| Dataset                  | Description                                                     | Lien                                                                                                                                                  |
| ------------------------ | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **delay_analysis**       | Analyse des retards lors de la restitution des véhicules        | [📄 get_around_delay_analysis.xlsx](https://huggingface.co/datasets/flodussart/getaround_xls_certif/resolve/main/get_around_delay_analysis.xlsx)      |
| **pricing_optimization** | Données pour l’apprentissage automatique d’optimisation de prix | [📊 get_around_pricing_project.csv](https://huggingface.co/datasets/flodussart/getaround_pricing_project/resolve/main/get_around_pricing_project.csv) |

--- 
## Infrastructure du projet

L’infrastructure repose sur une architecture modulaire et reproductible :
- **FastAPI** : API REST pour la prédiction en ligne.
- **Streamlit** : interface web interactive pour l’analyse des retards.
- **MLflow + Neon DB + S3** : suivi, stockage et persistance du modèle.
- **Hugging Face Datasets** : gestion centralisée des jeux de données.
- **Docker** : conteneurisation et déploiement multi-environnements.




