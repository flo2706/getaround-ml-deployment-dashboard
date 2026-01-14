# EDA

## I. Analyse des retards (`delay_analysis`)

### Sommaire

1. Imports & chargement des données
2. Page de documentation
3. Analyse exploratoire (EDA)
   - Statistiques descriptives
   - Distribution des variables catégorielles
     - Types de check-in
     - Statuts de location
     - Répartition des statuts de location selon le type de check-in
   - Distribution des variables numériques
     - Répartition du nombre de locations par véhicule
     - Répartition des restitutions - Interprétation et choix méthodologiques
     - Analyse des valeurs manquantes (retards non renseignés)
     - Répartition des retours selon le type de check-in
     - Analyse des retours anticipés et tardifs
       - IQR
       - Retours anticipés
       - Retards
       - Valeurs extrêmes (avance / retard)
     - Analyse des délais entre deux locations successives
4. Analyse des conflits entre locations successives
   - Impact des buffers sur les locations
   - Impact d’un buffer minimal sur les locations à risque
   - Impact du retard précédent sur le taux d'annulation (locations enchaînées < 12h)

## II. Analyse des prix (`pricing_analysis`)

### Sommaire

1. Imports & chargement des données
2. EDA

- Statistiques descriptives
- Distribution des prix de location
- Analyse bivariée
