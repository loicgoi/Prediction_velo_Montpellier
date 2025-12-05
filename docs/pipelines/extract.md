# Collecte de Données (Extract)

Le module backend.download contient les connecteurs vers les APIs externes.

## Stratégie de Pagination (Chunking)

L'API EcoCompteur de Montpellier impose une limite de taille par requête. Pour contourner cela, nous avons implémenté une stratégie de découpage temporel :

La période totale est divisée en sous-périodes (chunks) de 6 mois.

Si la période demandée est d'un seul jour (mise à jour quotidienne), un chunk unique est généré.

Les résultats sont agrégés dans une liste unique avant d'être retournés.

## API Trafic

::: download.trafic_history_api.EcoCounterTimeseriesLoader
handler: python
options:
members:
- fetch_data
- _generate_date_chunks
show_root_heading: true

## API Météo

Nous utilisons OpenMeteo pour l'historique et les prévisions.

::: download.daily_weather_api.OpenMeteoDailyAPIC
handler: python
options:
members:
- get_weather_json
show_root_heading: true