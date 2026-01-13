# EDA — Analyse des retards Getaround

## Sommaire

1. Imports & chargement des données  
2. Documentation des variables  
3. Analyse exploratoire (EDA)
   - Statistiques descriptives  
   - Distribution des variables catégorielles  
     - Types de check-in  
     - Statuts de location  
     - Répartition des statuts de location selon le type de check-in  
   - Distribution des variables numériques  
     - Répartition du nombre de locations par véhicule  
     - Répartition des restitutions  
     - Analyse des valeurs manquantes (retards non renseignés)  
     - Répartition des retours selon le type de check-in  
     - Analyse des retours anticipés et tardifs  
       - IQR  
       - Retours anticipés  
       - Retards  
       - Valeurs extrêmes (avance / retard)  
     - Analyse des délais entre deux locations  
4. Analyse des conflits entre locations successives
   - Calcul du délai entre deux locations successives  
   - Impact des temps tampons sur les locations  
   - Impact d’un buffer minimal sur les locations à risque  
   - Impact du retard précédent sur l’annulation (locations enchaînées < 12h)
