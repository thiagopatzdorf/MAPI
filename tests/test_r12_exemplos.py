from mapi.regras.r12_exemplos import exemplos_obrigatorios


def test_examples_ausente_e_recusado(escrita, todos):
    """Teste: contrato sem examples deve ser recusado"""
    del escrita["examples"]
    achados = exemplos_obrigatorios(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R12"
    assert achados[0]["path"] == "$.examples"
    assert "examples ausente, vazio ou não é uma lista" in achados[0]["message"]


def test_examples_vazio_e_recusado(escrita, todos):
    """Teste: examples vazio deve ser recusado"""
    escrita["examples"] = []
    achados = exemplos_obrigatorios(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R12"
    assert achados[0]["path"] == "$.examples"
    assert "examples ausente, vazio ou não é uma lista" in achados[0]["message"]


def test_examples_que_nao_e_lista_e_recusado(escrita, todos):
    """Teste: examples que não é lista deve ser recusado"""
    escrita["examples"] = "texto"
    achados = exemplos_obrigatorios(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R12"
    assert achados[0]["path"] == "$.examples"
    assert "examples ausente, vazio ou não é uma lista" in achados[0]["message"]


def test_examples_com_um_item_passa(escrita, leitura, destruicao, todos):
    """Teste: examples com pelo menos um item não deve gerar achado"""
    for c in (escrita, leitura, destruicao):
        # Garantir que tem pelo menos um exemplo
        if "examples" not in c or len(c["examples"]) == 0:
            c["examples"] = [{"name": "teste", "input": {}}]
        achados = exemplos_obrigatorios(c, todos)
        assert achados == []