"""O corpus de conformidade: os contratos de `examples/` não podem ser recusados por nenhuma regra.

Cada regra nova que entra roda aqui contra os sete contratos reais; regra que recusa um exemplo
válido está errada (ou o exemplo está), e este teste é onde isso aparece.
"""
from mapi.modelo import carregar
from mapi.regras import checar

import pytest
from pathlib import Path

ARQUIVOS = sorted((Path(__file__).resolve().parents[1] / "examples").glob("*.mapi.yaml"))


@pytest.mark.parametrize("arquivo", ARQUIVOS, ids=[a.name for a in ARQUIVOS])
def test_exemplo_valido_nao_e_recusado_por_nenhuma_regra(arquivo):
    assert checar(carregar(arquivo)) == []


def test_corpus_tem_os_sete_contratos_da_spec():
    assert sum(len(carregar(a)) for a in ARQUIVOS) == 7
