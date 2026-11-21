import copy

from mapi.regras.r08_leitura_pura import leitura_pura


def test_leitura_com_consent_e_recusada(leitura, todos):
    """Testa que leitura com consent é recusada por R8."""
    leitura_com_consent = copy.deepcopy(leitura)
    leitura_com_consent["consent"] = {"dry_run": "default"}
    
    achados = leitura_pura(leitura_com_consent, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R8"
    assert achados[0]["path"] == "$.consent"


def test_leitura_com_reversible_e_recusada(leitura, todos):
    """Testa que leitura com reversible é recusada por R8."""
    leitura_com_reversible = copy.deepcopy(leitura)
    leitura_com_reversible["reversible"] = {"inverse": {"capability": "some.capability"}}
    
    achados = leitura_pura(leitura_com_reversible, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R8"
    assert achados[0]["path"] == "$.reversible"


def test_leitura_com_as_duas_gera_dois_achados(leitura, todos):
    """Testa que leitura com ambas consent e reversible gera dois achados."""
    leitura_com_ambas = copy.deepcopy(leitura)
    leitura_com_ambas["consent"] = {"dry_run": "default"}
    leitura_com_ambas["reversible"] = {"inverse": {"capability": "some.capability"}}
    
    achados = leitura_pura(leitura_com_ambas, todos)
    assert len(achados) == 2
    paths = {achado["path"] for achado in achados}
    assert paths == {"$.consent", "$.reversible"}


def test_leitura_limpa_passa(leitura, todos):
    """Testa que leitura sem consent nem reversible passa."""
    # Remover se existirem (do exemplo cloudflare.rest.get)
    leitura_limpa = copy.deepcopy(leitura)
    leitura_limpa.pop("consent", None)
    leitura_limpa.pop("reversible", None)
    
    achados = leitura_pura(leitura_limpa, todos)
    assert achados == []


def test_escrita_nunca_recebe_r8(escrita, todos):
    """Testa que escrita nunca recebe R8, mesmo com consent/reversible."""
    escrita["consent"] = {"dry_run": "default"}
    escrita["reversible"] = {"inverse": {"capability": "some.capability"}}
    
    achados = leitura_pura(escrita, todos)
    assert achados == []


def test_consent_vazio_do_yaml_numa_leitura_e_recusado(leitura, todos):
    """Testa que consent vazio (None do YAML) em leitura é recusado."""
    leitura_com_consent_vazio = copy.deepcopy(leitura)
    # YAML vazio (secao:) vira None
    leitura_com_consent_vazio["consent"] = None
    
    achados = leitura_pura(leitura_com_consent_vazio, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R8"
    assert achados[0]["path"] == "$.consent"