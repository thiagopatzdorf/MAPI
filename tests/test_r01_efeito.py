from mapi.regras import checar
from mapi.regras.r01_efeito import efeito_valido


def test_contrato_sem_effect_e_recusado_por_r1(escrita, todos):
    del escrita["effect"]
    a = efeito_valido(escrita, todos)
    assert [x["rule"] for x in a] == ["R1"] and a[0]["path"] == "$.effect"


def test_effect_com_grafia_fora_da_lista_e_recusado_por_r1(escrita, todos):
    escrita["effect"] = "delete"
    assert efeito_valido(escrita, todos)


def test_effect_valido_nao_gera_achado_de_r1(escrita, leitura, destruicao, todos):
    for c in (escrita, leitura, destruicao):
        assert efeito_valido(c, todos) == []


def test_checar_acha_a_r1_sozinho_sem_registro_manual(escrita):
    del escrita["effect"]
    assert "R1" in {x["rule"] for x in checar([escrita])}
