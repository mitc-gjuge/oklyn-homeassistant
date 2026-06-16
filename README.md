# Oklyn pour Home Assistant

Intégration **custom component** (non officielle) pour les appareils de pilotage
de piscine **Oklyn**, via l'API publique `https://api.oklyn.fr/public/v1`.

Elle expose, pour chaque appareil :

| Entité | Type | Détail |
|--------|------|--------|
| Température de l'eau | `sensor` | °C |
| Température de l'air | `sensor` | °C |
| pH | `sensor` | device class `ph` |
| RedOx (ORP) | `sensor` | mV |
| Filtration | `select` | `off` / `on` / `auto` |
| Contact auxiliaire | `switch` | marche / arrêt |

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

## Point à vérifier après le premier démarrage

La collection Postman fournie **ne documente pas la forme des réponses** des
endpoints de lecture (`GET .../data/ph`, `/pump`, `/aux`). Le décodage repose
donc sur des hypothèses raisonnables, toutes centralisées dans **un seul
endroit** : la fonction `_extract_scalar()` de `custom_components/oklyn/api.py`.

Si après installation un capteur reste vide (`unknown`) ou si la filtration ne
reflète pas le bon état :

1. Activez les logs de debug :
   ```yaml
   logger:
     logs:
       custom_components.oklyn: debug
   ```
2. Regardez la forme réelle du JSON renvoyé par l'API.
3. Ajustez `_extract_scalar()` (et éventuellement `PUMP_OPTIONS` / `AUX_ON` /
   `AUX_OFF` dans `const.py`) en conséquence. C'est la seule retouche nécessaire.

## Notes techniques

- Polling toutes les **120 s** par défaut (un seul `DataUpdateCoordinator`
  partagé, appels concurrents).
- État stocké via `entry.runtime_data` (pratique moderne, pas de `hass.data`).
- Le client HTTP est embarqué dans `api.py`. Pour une publication propre dans
  HACS par défaut (et a fortiori pour le cœur de HA), la bonne pratique est de
  l'externaliser dans un paquet PyPI listé dans `manifest.json` → `requirements`.

## Avertissement

Projet indépendant, sans lien avec Oklyn. Fourni « tel quel », à vos risques.
