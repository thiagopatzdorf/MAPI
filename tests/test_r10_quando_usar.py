from mapi.regras.r10_quando_usar import when_to_use_valido


def test_when_to_use_ausente_e_recusado(escrita, todos):
    """Teste: when_to_use ausente deve ser recusado"""
    del escrita["when_to_use"]
    achados = when_to_use_valido(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R10"
    assert achados[0]["path"] == "$.when_to_use"
    assert "when_to_use ausente" in achados[0]["message"]


def test_when_to_use_so_com_espacos_e_recusado(escrita, todos):
    """Teste: when_to_use só com espaços deve ser recusado"""
    escrita["when_to_use"] = "   "
    achados = when_to_use_valido(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R10"
    assert achados[0]["path"] == "$.when_to_use"
    assert "when_to_use vazio ou só com espaços" in achados[0]["message"]


def test_when_to_use_com_301_caracteres_e_recusado(escrita, todos):
    """Teste: when_to_use com 301 caracteres deve ser recusado"""
    escrita["when_to_use"] = "a" * 301
    achados = when_to_use_valido(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R10"
    assert achados[0]["path"] == "$.when_to_use"
    assert "when_to_use com 301 caracteres, máximo é 300" in achados[0]["message"]


def test_when_to_use_com_300_caracteres_passa(escrita, todos):
    """Teste: when_to_use com 300 caracteres deve passar"""
    escrita["when_to_use"] = "a" * 300
    achados = when_to_use_valido(escrita, todos)
    assert len(achados) == 0


def test_when_to_use_numero_e_recusado(escrita, todos):
    """Teste: when_to_use com número deve ser recusado"""
    escrita["when_to_use"] = 123
    achados = when_to_use_valido(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R10"
    assert achados[0]["path"] == "$.when_to_use"
    assert "when_to_use deve ser texto, encontrado int" in achados[0]["message"]


def test_when_to_use_valido_passa(escrita, leitura, destruicao, todos):
    """Teste: when_to_use válido deve passar em todos os efeitos"""
    for contrato in (escrita, leitura, destruicao):
        achados = when_to_use_valido(contrato, todos)
        assert len(achados) == 0