import requests
import time
from typing import Optional
from utils.logging_config import logger

# URL de l'API Nominatim (OpenStreetMap)
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/reverse"


def get_street_name_from_coords(lat: float, lon: float) -> Optional[str]:
    """
    Récupère un nom de rue ou de lieu lisible à partir de coordonnées GPS
    via l'API OpenStreetMap Nominatim.

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        Optional[str]: Le nom de la rue (ex: "Rue de la Loge") ou None en cas d'échec.
    """
    if not lat or not lon:
        return None

    # Paramètres pour le géocodage inverse
    # zoom=18 correspond au niveau "rue/détail"
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 18, "addressdetails": 1}

    # IMPORTANT : Nominatim exige un User-Agent valide identifiant l'application.
    # Si on ne le met pas, la requête sera bloquée (403 Forbidden).
    headers = {"User-Agent": "PredictionVeloMontpellier/1.0 (contact@ton-domaine.com)"}

    try:
        # Pause de politesse pour éviter le Rate Limiting (max 1 req/sec recommandé)
        time.sleep(1.1)

        response = requests.get(
            NOMINATIM_API_URL, params=params, headers=headers, timeout=5
        )
        response.raise_for_status()

        data = response.json()
        address = data.get("address", {})

        # Liste de priorité pour trouver un nom pertinent
        # On cherche d'abord une rue, puis une zone piétonne, une place, un parc, etc.
        priority_keys = [
            "road",  # Route standard
            "pedestrian",  # Zone piétonne
            "footway",  # Passage piéton
            "cycleway",  # Piste cyclable
            "square",  # Place
            "park",  # Parc
            "construction",  # Zone en travaux (parfois retourné)
            "hamlet",  # Hameau (pour les zones moins denses)
            "suburb",  # Quartier
            "city_district",  # Arrondissement
        ]

        # 1. On cherche la clé la plus précise
        for key in priority_keys:
            if key in address:
                # Parfois le nom contient déjà "Montpellier", on le garde propre
                return address[key]

        # 2. Si aucune clé précise, on essaie le nom d'affichage générique (souvent long)
        if "display_name" in data:
            # On prend juste le premier segment du display_name (avant la première virgule)
            return data["display_name"].split(",")[0]

        # 3. Fallback ultime
        return f"Point ({lat:.3f}, {lon:.3f})"

    except requests.exceptions.HTTPError as e:
        logger.error(f"Erreur HTTP Nominatim pour ({lat}, {lon}) : {e}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Erreur de connexion à Nominatim. Vérifiez votre internet.")
        return None
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout Nominatim pour ({lat}, {lon})")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors du géocodage : {e}")
        return None


if __name__ == "__main__":
    # Test rapide si on lance le fichier directement
    test_lat, test_lon = 43.6112, 3.8767  # Près du Peyrou à Montpellier
    print(f"Test pour {test_lat}, {test_lon}...")
    name = get_street_name_from_coords(test_lat, test_lon)
    print(f"Résultat : {name}")
