# Documentation de l'Interface Utilisateur (Frontend)

Cette page décrit l'architecture, les fonctionnalités et la logique de l'interface utilisateur (frontend) du projet, développée avec le framework **NiceGUI**.

## 1. Vue d'ensemble

L'interface utilisateur a pour but de fournir une visualisation interactive et en temps réel des données de comptage de vélos à Montpellier. Elle permet aux utilisateurs de :
- Consulter les prédictions de trafic pour le jour même.
- Analyser les performances des prédictions passées.
- Explorer les tendances historiques et les profils d'utilisation de chaque compteur.

## 2. Architecture et Structure des Fichiers

Le frontend est organisé en modules clairs, chacun ayant une responsabilité unique, ce qui facilite la maintenance et l'évolution de l'application.

-   `app.py`: **Point d'entrée principal.** Il initialise l'application, définit la structure de la page (header, layout) et gère l'état global comme la sélection du compteur.

-   `components.py`: **Cœur de l'affichage dynamique.** Contient la logique pour afficher les KPIs, les cartes et les graphiques pour un compteur donné. Ce composant est "rafraîchissable" pour des mises à jour fluides.

-   `data.py`: **Couche d'accès aux données.** Centralise toute la communication avec les APIs externes (le backend du projet et l'API météo). Il est conçu pour être robuste et configurable.

-   `plots.py`: **Module de visualisation.** Regroupe toutes les fonctions qui génèrent les graphiques avec Matplotlib, assurant une séparation nette entre la logique de données et la présentation visuelle.

## 3. Fonctionnalités Détaillées

### Layout Principal et Gestion de l'État (`app.py`)

L'application est construite autour d'une page unique avec une mise en page réactive.

-   **Header Persistant** : Un en-tête contient le titre de l'application et un sélecteur (`ui.select`) permettant de choisir une station de comptage.
-   **Gestion de l'État Client** : L'application utilise `app.storage.client` pour mémoriser la station sélectionnée par l'utilisateur. Cela garantit que si l'utilisateur rafraîchit la page, sa dernière sélection est conservée, améliorant l'expérience utilisateur.
-   **Rafraîchissement Dynamique** : Lorsque l'utilisateur change de station, l'événement `on_change` du sélecteur appelle la méthode `.refresh()` du composant `render_counter_content`. Cela met à jour uniquement la partie centrale de la page, sans rechargement complet.

### Affichage du Contenu (`components.py`)

La fonction `@ui.refreshable render_counter_content` est le moteur de l'interface.

-   **Gestion des Données Obsolètes ou Manquantes** : Une des fonctionnalités clés est la capacité à informer l'utilisateur de l'état des données.
    -   Si la prédiction affichée ne date pas du jour même, un bandeau d'avertissement **orange** est affiché.
    -   Si aucune prédiction n'est disponible pour un compteur, un bandeau d'erreur **rouge** l'indique clairement.
    Cela rend l'application transparente sur la fraîcheur des informations qu'elle présente.

-   **Navigation par Onglets** : Le contenu est organisé en deux onglets pour une meilleure clarté :
    1.  **Tableau de Bord** : Affiche les informations essentielles en un coup d'œil (KPIs, carte, météo).
    2.  **Analyses & Stats** : Regroupe les graphiques d'analyse historique.

### Couche de Données Robuste (`data.py`)

Ce module est conçu pour être à la fois flexible et résilient.

-   **Configuration Intelligente de l'URL de l'API** : La fonction `_get_api_url` détecte automatiquement l'environnement d'exécution (variable d'environnement pour la production, présence de `/.dockerenv` pour Docker, ou `localhost` pour le développement local). Cela permet de déployer l'application dans différents contextes sans aucune modification du code.

-   **Mise en Cache Efficace** : La liste des compteurs est récupérée une seule fois et stockée dans `_COUNTERS_CACHE`. Cela évite des appels réseau inutiles et accélère les chargements ultérieurs de la page.

-   **Gestion des Erreurs d'API** : La fonction `get_dashboard_data` est encapsulée dans un bloc `try...except`. En cas d'échec de la connexion à l'API (timeout, erreur 500, etc.), elle ne fait pas planter l'application. Au lieu de cela, elle retourne une structure de données "vide" mais valide. Cela permet à l'interface de rester fonctionnelle et d'afficher un état dégradé propre au lieu d'une page d'erreur.

### Visualisations Claires (`plots.py`)

Ce module isole complètement la logique de création des graphiques.

-   **Modularité** : Chaque graphique (tendance 30 jours, fiabilité 7 jours, etc.) est généré par sa propre fonction.
-   **Style Cohérent** : Une fonction `apply_dashboard_style` est utilisée pour appliquer un style visuel commun à tous les graphiques, garantissant une apparence professionnelle et homogène.
-   **Gestion des Données Vides** : Chaque fonction de plot vérifie si les données d'entrée sont valides et fournit des valeurs par défaut si nécessaire, ce qui contribue à la robustesse générale de l'affichage.

## 4. Lancement de l'Application

L'application est lancée via la commande `ui.run()` à la fin du fichier `app.py`.

```python
ui.run(host="0.0.0.0", port=8080, title="Vélo Montpellier IA", favicon="🚴")
```

-   `host="0.0.0.0"` rend l'application accessible sur le réseau (essentiel pour Docker).
-   `port=8080` est le port d'écoute par défaut.
