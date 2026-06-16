"""Configuration des tests.

`api.py` importe `aiohttp` au niveau module, mais les fonctions testées
(`_extract_scalar`, `_parse_measure` et leurs helpers) sont de la logique pure
sans dépendance réseau. On charge donc le module par chemin de fichier — ce qui
évite aussi la collision entre `oklyn/select.py` et le module `select` de la
stdlib que provoquerait l'ajout du dossier au `sys.path` — après avoir stubé
`aiohttp` s'il n'est pas installé.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

if "aiohttp" not in sys.modules:
    try:  # pragma: no cover - dépend de l'environnement
        import aiohttp  # noqa: F401
    except ModuleNotFoundError:
        _stub = types.ModuleType("aiohttp")
        _stub.ClientSession = object
        _stub.ClientError = Exception
        sys.modules["aiohttp"] = _stub

_API_PATH = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "oklyn"
    / "api.py"
)


@pytest.fixture(scope="session")
def api():
    """Charge `custom_components/oklyn/api.py` comme module isolé."""
    spec = importlib.util.spec_from_file_location("oklyn_api", _API_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
