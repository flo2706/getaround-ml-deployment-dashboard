# EDA — Analyse des retards Getaround 🚗⏱️

## Sommaire

1. 📌 Imports & Chargement des données  
2. 📄 Documentation des variables  
3. 📊 Analyse exploratoire (EDA)
   3.1 Statistiques descriptives  
   3.2 Distribution des variables catégorielles  
       - Types de check-in  
       - Statuts de location  
       - Répartition des statuts selon le type de check-in  
   3.3 Distribution des variables numériques  
       - Répartition des retards de restitution  
       - Analyse des valeurs manquantes  
       - Répartition des retours selon le type de check-in  
       - Analyse des retours anticipés et tardifs  
         * retours anticipés  
         * retards  
         * valeurs extrêmes (avance/retard)  
4. 🔍 Analyse des conflits entre locations successives
   - Calcul du délai entre deux locations successives  
   - Impact des temps tampons sur les locations  
   - Impact d’un buffer minimal sur les locations à risque  
   - Impact du retard précédent sur l’annulation (locations enchaînées < 12h)  
5. ✅ Synthèse & Insights clés  
6. 🎯 Recommandation produit  
7. 📦 Impacts pour le dashboard & l’API


---

## ✅ Synthèse des enseignements clés

### 📌 Fréquence et ampleur des retards
- **44 %** des locations se terminent en retard
- Mais la grande majorité sont **des retards courts**
  - **68 %** des retards < **100 min**
  - Les retards extrêmes existent mais restent **marginaux**

➡ Les retards sont fréquents mais **pas forcément critiques**

---

### 🔍 Locations enchaînées = situation à risque
- Seulement **8,6 %** des locations sont enchaînées (< 12h)
- Parmi elles, **18 %** mènent à un **conflit** réel
  (retard qui impacte la location suivante)

➡ Le **risque est concentré sur une minorité de cas**, faciles à cibler

---

### 📲 Différence entre types de check-in
- Les voitures **Connect** sont **plus exposées** aux frictions
  - Moins de marge opérationnelle (accès sans propriétaire)
  - Légère différence d’annulation observée

➡ Ciblage pertinent : **prioriser les voitures Connect**

---

### 🔁 Effet de cascade
Plus le retard initial est important, plus **le risque d’annulation** augmente :

| Retard précédent | Taux d’annulation |
|----------------|------------------|
| < 100 min | 10–12 % |
| 500–1000 min | **27 %** 🚨 |

➡ Une mauvaise restitution peut **perturber toute la chaîne**

---

### ⏱️ Tampon : un compromis revenu / expérience
- **30 min** → ~15 % de locations masquées
- **180 min** → ~50 % masquées

➡ Un buffer trop large → **perte de revenu significative**  
➡ Un buffer trop faible → **peu efficace**

---

## 🎯 Recommandation Produit

> ✅ Implémenter un buffer **de 60 minutes**  
> ✅ **d’abord** sur les voitures **Connect**  
> 🎯 Réduit **~70 % des conflits**  
> 💰 Impact **< 5 %** sur la disponibilité

Ce choix apporte le **meilleur compromis** entre :
✔ Amélioration de l’expérience client  
✔ Maintien du revenu / taux de conversion  
✔ Facilité de mise en œuvre

---

### 📦 Impact pour la suite du projet
- Les résultats alimentent le **dashboard interactif**
- Le seuil et la portée seront **ajustables** par l’équipe Produit
- Possibilité de déployer la fonctionnalité via un **A/B test**

---

