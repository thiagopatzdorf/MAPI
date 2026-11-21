"""Nenhuma regra pode levantar exceção, qualquer que seja o tipo de uma seção do contrato.

Erro -> regra (2026-10-20): no piloto da horda, 2 de 3 regras (R2 e R5) dava `AttributeError` quando
uma seção vinha vazia (`proof:` em YAML é `None`) ou com tipo errado; a R4 devolvia um achado. Pior: o
`checar()` roda todas as regras, então a R5 derrubava a entrada que a R4 existe para reportar. Este teste
troca cada seção (até o 2º nível) dos 7 contratos reais por valores de tipo errado e roda todas as regras
registradas, as de hoje e as que vierem: regra nova não precisa lembrar de se proteger, o teste cobra.
"""
import copy
from pathlib import Path

import pytest

from mapi.modelo import carregar
from mapi.regras import checar

EXEMPLOS = sorted((Path(__file__).resolve().parents[1] / "examples").glob("*.mapi.yaml"))
CONTRATOS = [(c["capability"], c) for arq in EXEMPLOS for c in carregar(arq)]
TIPOS_ERRADOS = [None, "texto", 0, True, [], [1], {}]
EFEITOS = [None, "read", "write", "destroy", "talvez", 3]


def _caminhos(contrato):
    for k, v in contrato.items():
        yield (k,)
        if isinstance(v, dict):
            for k2 in v:
                yield (k, k2)


def _trocar(contrato, caminho, valor):
    c = copy.deepcopy(contrato)
    alvo = c
    for chave in caminho[:-1]:
        alvo = alvo[chave]
    alvo[caminho[-1]] = valor
    return c


@pytest.mark.parametrize("capability,contrato", CONTRATOS, ids=[c for c, _ in CONTRATOS])
def test_regra_nao_levanta_excecao_com_secao_de_tipo_errado(capability, contrato):
    todos = [c for _, c in CONTRATOS if c is not contrato]
    quebrou = []
    for caminho in _caminhos(contrato):
        for valor in TIPOS_ERRADOS:
            mutado = _trocar(contrato, caminho, valor)
            try:
                checar([mutado] + todos)
            except Exception as e:  # noqa: BLE001 - é exatamente o que se mede
                quebrou.append(f"{'.'.join(caminho)}={valor!r}: {type(e).__name__}: {str(e)[:60]}")
    assert quebrou == [], f"regra derrubada por contrato malformado ({len(quebrou)}): {quebrou[:5]}"


@pytest.mark.parametrize("capability,contrato", CONTRATOS, ids=[c for c, _ in CONTRATOS])
def test_regra_nao_levanta_excecao_com_effect_fora_do_dominio(capability, contrato):
    todos = [c for _, c in CONTRATOS if c is not contrato]
    for efeito in EFEITOS:
        checar([_trocar(contrato, ("effect",), efeito)] + todos)


def test_contrato_sem_nenhuma_chave_nao_derruba_regra_alguma():
    checar([{}])
    checar([{"capability": "a.b"}])
