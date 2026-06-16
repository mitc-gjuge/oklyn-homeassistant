# Oklyn pour Home Assistant

[![CI](https://github.com/mitc-gjuge/oklyn-homeassistant/actions/workflows/ci.yml/badge.svg)](https://github.com/mitc-gjuge/oklyn-homeassistant/actions/workflows/ci.yml)

Intégration **custom component** (non officielle) pour les appareils de pilotage
de piscine **Oklyn**, via l'API publique `https://api.oklyn.fr/public/v1`.

Elle expose, pour chaque appareil :

| Entité | Type | Détail | Attributs |
|--------|------|--------|-----------|
| Température de l'eau | `sensor` | °C | `status`, `recorded` |
| Température de l'air | `sensor` | °C | `status`, `recorded` |
| pH | `sensor` | device class `ph` | `status`, `recorded` |
| RedOx (ORP) | `sensor` | mV | `status`, `recorded` |
| Salinité | `sensor` | g/L | `status`, `recorded` |
| Filtration active | `binary_sensor` | état **réel** de la pompe (device class `running`) | — |
| Filtration | `select` | mode `off` / `on` / `auto` | `running`, `changed_at` |
| Contact auxiliaire 1 & 2 | `switch` | marche / arrêt (2 contacts : `aux`, `aux2`) | `changed_at` |

> Sur les capteurs de mesure, l'attribut `status` reflète l'indicateur de plage
> renvoyé par Oklyn (`normal`, `null`, …) et `recorded` l'horodatage de la mesure.
> Le `select` (mode choisi) et le `binary_sensor` (pompe réellement en marche)
> sont **distincts** : en mode `auto`, la pompe peut être à l'arrêt ou en marche.

## Installation

### Via HACS (recommandé)

1. HACS → menu (⋮) → **Dépôts personnalisés**.
2. Ajoutez l'URL de ce dépôt GitHub, catégorie **Integration**.
3. Installez « Oklyn (piscine) », puis **redémarrez** Home Assistant.

### Manuellement

Copiez le dossier `custom_components/oklyn/` dans le dossier `config/custom_components/`
de votre installation, puis redémarrez Home Assistant.

## Configuration

Paramètres → **Appareils et services** → **Ajouter une intégration** → « Oklyn ».
Renseignez :

- **Identifiant de l'appareil** (`device_id`)
- **Clé API** (transmise dans l'en-tête `X-Api-Token`)

> La clé et l'identifiant se trouvent dans votre espace Oklyn. N'utilisez jamais
> la clé d'exemple présente dans la collection Postman publique : c'est un
> placeholder, pas une clé valide.

## Dépannage

En cas de souci (capteur `unknown`, état incohérent), activez les logs de debug
et inspectez le JSON renvoyé par l'API :

```yaml
logger:
  logs:
    custom_components.oklyn: debug
```

## Notes techniques

- Polling toutes les **120 s** par défaut (un seul `DataUpdateCoordinator`
  partagé, appels concurrents via `asyncio.gather`).
- État stocké via `entry.runtime_data` (pratique moderne, pas de `hass.data`).
- Le client HTTP est embarqué dans `api.py`. Pour une publication propre dans
  HACS par défaut (et a fortiori pour le cœur de HA), la bonne pratique est de
  l'externaliser dans un paquet PyPI listé dans `manifest.json` → `requirements`.

## Développement

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_test.txt ruff

pytest                       # tests unitaires du décodage (api.py)
ruff check . && ruff format --check .
```

La CI GitHub Actions (`.github/workflows/ci.yml`) rejoue le lint, les tests
(Python 3.12 et 3.13) et la validation Home Assistant (`hassfest`) à chaque
push / pull request. La validation HACS y est présente mais **informative** tant
que le dépôt est privé (elle s'appuie sur l'API GitHub) ; à repasser bloquante
lors du passage en public.

## Avertissement

Projet indépendant, sans lien avec Oklyn. Fourni « tel quel », à vos risques.
