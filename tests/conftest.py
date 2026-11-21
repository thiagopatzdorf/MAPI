import copy
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from mapi.modelo import carregar  # noqa: E402


def _por_capacidade(arquivo: str) -> dict:
    return {c["capability"]: c for c in carregar(RAIZ / "examples" / arquivo)}


@pytest.fixture
def escrita():
    """Contrato `write` completo e válido (cloudflare.rest.write). Cópia: o teste pode mutar."""
    return copy.deepcopy(_por_capacidade("cloudflare_rest.mapi.yaml")["cloudflare.rest.write"])


@pytest.fixture
def leitura():
    """Contrato `read` completo e válido (cloudflare.rest.get)."""
    return copy.deepcopy(_por_capacidade("cloudflare_rest.mapi.yaml")["cloudflare.rest.get"])


@pytest.fixture
def destruicao():
    """Contrato `destroy` completo e válido (gcp.disk.delete)."""
    return copy.deepcopy(_por_capacidade("receita_apagar.mapi.yaml")["gcp.disk.delete"])


@pytest.fixture
def todos():
    """Todas as capacidades dos exemplos, por id (para regras que olham outras capacidades)."""
    r = {}
    for arq in sorted((RAIZ / "examples").glob("*.mapi.yaml")):
        r.update({c["capability"]: c for c in carregar(arq)})
    return copy.deepcopy(r)
