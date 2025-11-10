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
  - la fréquence des retards ;
  - leur impact sur les revenus ;
  - les scénarios possibles selon le délai entre locations.
- Développer un **modèle de prédiction du prix de location**, exposé via un endpoint `/predict`.
- Déployer l’ensemble sur le web :
  - API hébergée sur **Hugging Face Spaces** (FastAPI)
  - Dashboard déployé sur **Hugging Face** (Streamlit)
  - Suivi du modèle via **MLflow**
- Documenter l’API à l’URL `/docs`.


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

- d’explorer les retards selon les types de location (mobile, connectée),
- d’évaluer l’impact d’un délai minimal sur les revenus potentiels,
- d’afficher les indicateurs clés pour la prise de décision produit.

Accès au dashboard :  
[**Getaround Dashboard sur Hugging Face**](https://huggingface.co/spaces/flodussart/getaroundcertifter)


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

## Suivi du modèle (MLflow)

Le suivi du modèle (versions, métriques, paramètres) a été mis en place sur MLflow, déployé sur un espace Hugging Face dédié :  
[**Suivi du modèle**](https://huggingface.co/spaces/flodussart/getaround_mlflow)








