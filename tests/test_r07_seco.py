from mapi.regras import checar
from mapi.regras.r07_seco import seco_por_padrao


def test_write_sem_consent_e_recusado(escrita, todos):
    del escrita["consent"]
    a = seco_por_padrao(escrita, todos)
    assert [x["rule"] for x in a] == ["R7"] and a[0]["path"] == "$.consent"


def test_dry_run_supported_e_recusado(escrita, todos):
    escrita["consent"]["dry_run"] = "supported"
    a = seco_por_padrao(escrita, todos)
    assert [x["rule"] for x in a] == ["R7"] and a[0]["path"] == "$.consent.dry_run"


def test_dry_run_none_e_recusado(escrita, todos):
    escrita["consent"]["dry_run"] = "none"
    a = seco_por_padrao(escrita, todos)
    assert [x["rule"] for x in a] == ["R7"] and a[0]["path"] == "$.consent.dry_run"


def test_dry_run_default_passa(escrita, leitura, destruicao, todos):
    for c in (escrita, leitura, destruicao):
        if c.get("effect") in ("write", "destroy"):
            c["consent"]["dry_run"] = "default"
        assert seco_por_padrao(c, todos) == []


def test_leitura_nunca_recebe_r7(escrita, leitura, destruicao, todos):
    # read nunca recebe R7, mesmo se tiver consent com valor inválido
    if "consent" not in leitura:
        leitura["consent"] = {}
    leitura["consent"]["dry_run"] = "supported"  # mesmo valor inválido
    assert seco_por_padrao(leitura, todos) == []  # mas não recebe R7


def test_consent_vazio_do_yaml_vira_achado_e_nao_excecao(escrita, todos):
    escrita["consent"] = None  # YAML `consent:` vira None
    a = seco_por_padrao(escrita, todos)
    assert [x["rule"] for x in a] == ["R7"] and a[0]["path"] == "$.consent"


def test_checar_acha_a_r7_sozinho_sem_registro_manual(escrita):
    del escrita["consent"]
    assert "R7" in {x["rule"] for x in checar([escrita])}