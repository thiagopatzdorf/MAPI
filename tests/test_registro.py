import pytest

from mapi.modelo import carregar_texto
from mapi.regras import REGRAS, regra


def test_documento_yaml_que_nao_e_mapa_e_erro_em_vez_de_sumir():
    with pytest.raises(ValueError):
        carregar_texto("- a\n- b\n")


def test_regra_registrada_duas_vezes_e_erro():
    @regra("R9999")
    def a(c, t):
        return []

    with pytest.raises(ValueError):
        regra("R9999")(a)
    del REGRAS["R9999"]


def test_exemplo_nao_usa_chave_de_topo_fora_do_modelo_sem_prefixo_x():
    """Erro -> regra (2026-10-20): `audit` no exemplo da receita_apagar não existe no modelo da SPEC §2;
    a R13 vai recusá-lo. Extensão é `x-audit`. Este teste vale antes da R13 existir."""
    from pathlib import Path

    from mapi.modelo import carregar
    from mapi.regras.r13_chave_desconhecida import (
        CHAVES_PERMITIDAS as permitidas,  # uma cópia só: a da R13
    )
    for arq in sorted((Path(__file__).resolve().parents[1] / "examples").glob("*.mapi.yaml")):
        for c in carregar(arq):
            fora = [k for k in c if k not in permitidas and not k.startswith("x-")]
            assert fora == [], f"{arq.name}/{c['capability']}: chave de topo fora do modelo: {fora}"


def test_natural_key_do_exemplo_aponta_para_campos_que_existem_no_input():
    """Guarda da garantia (c) da R14 (SPEC §2.1) antes de a R14 existir: chave natural inventada não garante nada."""
    from pathlib import Path

    from mapi.modelo import carregar

    for arq in sorted((Path(__file__).resolve().parents[1] / "examples").glob("*.mapi.yaml")):
        for c in carregar(arq):
            chave = c.get("x-mapi-natural-key")
            if chave is None:
                continue
            props = (c.get("input") or {}).get("properties") or {}
            assert isinstance(chave, list) and chave and all(k in props for k in chave), f"{c['capability']}: {chave}"
