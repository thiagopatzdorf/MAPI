from mapi.regras.r09_saida_com_teto import saida_com_teto


def test_budget_ausente_e_recusado(escrita, todos):
    """Testa quando budget está ausente."""
    del escrita["budget"]
    achados = saida_com_teto(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R9"
    assert achados[0]["path"] == "$.budget.max_output_bytes"
    assert "ausente" in achados[0]["message"]


def test_max_output_bytes_ausente_e_recusado(escrita, todos):
    """Testa quando max_output_bytes está ausente."""
    del escrita["budget"]["max_output_bytes"]
    achados = saida_com_teto(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R9"
    assert achados[0]["path"] == "$.budget.max_output_bytes"
    assert "ausente" in achados[0]["message"]


def test_max_output_bytes_zero_e_recusado(escrita, todos):
    """Testa quando max_output_bytes é zero."""
    escrita["budget"]["max_output_bytes"] = 0
    achados = saida_com_teto(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R9"
    assert achados[0]["path"] == "$.budget.max_output_bytes"
    assert "inteiro maior que zero" in achados[0]["message"]


def test_max_output_bytes_booleano_e_recusado(escrita, todos):
    """Testa quando max_output_bytes é booleano."""
    escrita["budget"]["max_output_bytes"] = True
    achados = saida_com_teto(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R9"
    assert achados[0]["path"] == "$.budget.max_output_bytes"
    assert "inteiro maior que zero" in achados[0]["message"]


def test_max_output_bytes_positivo_passa(escrita, leitura, destruicao, todos):
    """Testa quando max_output_bytes é positivo."""
    for contrato in (escrita, leitura, destruicao):
        contrato["budget"]["max_output_bytes"] = 1024
        achados = saida_com_teto(contrato, todos)
        assert achados == []


def test_budget_vazio_do_yaml_vira_achado_e_nao_excecao(escrita, todos):
    """Testa quando budget é vazio (None)."""
    escrita["budget"] = None
    achados = saida_com_teto(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R9"
    assert achados[0]["path"] == "$.budget.max_output_bytes"
    assert "ausente" in achados[0]["message"]