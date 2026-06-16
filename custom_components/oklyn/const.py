"""Constantes pour l'intégration Oklyn."""

from __future__ import annotations

DOMAIN = "oklyn"

# Clés de configuration (CONF_API_KEY est repris de homeassistant.const)
CONF_DEVICE_ID = "device_id"
CONF_SCAN_INTERVAL_S = "scan_interval"

# Intervalle de rafraîchissement par défaut (en secondes)
DEFAULT_SCAN_INTERVAL = 120

MANUFACTURER = "Oklyn"

# Modes de filtration possibles (PUT pump). Les trois sont confirmés en live
# (2026-06-16) : un PUT {"pump": <mode>} renvoie 200 et le GET reflète le mode.
PUMP_OPTIONS = ["off", "on", "auto"]

AUX_ON = "on"
AUX_OFF = "off"
