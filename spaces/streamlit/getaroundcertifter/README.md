<h1 align="center">Getaround Pricing Dashboard</h1>

Dashboard **Streamlit** permettant de visualiser et tester les résultats du projet Getaround.

Il permet notamment :
- d’explorer les analyses réalisées sur les retards et les locations,
- de visualiser les impacts business,
- d’interagir avec l’API de prédiction du prix journalier.

---

## Accès au dashboard

Le dashboard est déployé sur Hugging Face Spaces :

- https://flodussart-getaround-delay-pricing-dashboard.hf.space

---

## Lancer le dashboard en local (recommandé : Docker)

```bash
docker build -t getaround-dashboard .
docker run --rm -p 8501:8501 getaround-dashboard
.
