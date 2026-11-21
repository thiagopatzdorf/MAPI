from mapi.regras.r06_evidencia import evidencia_obrigatoria


def test_destroy_sem_precondition_e_recusado(destruicao, todos):
    """Teste para contrato destroy sem precondition - deve ser recusado"""
    del destruicao["precondition"]
    achados = evidencia_obrigatoria(destruicao, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R6"
    assert achados[0]["path"] == "$.precondition.evidence"


def test_destroy_com_evidence_vazia_e_recusado(destruicao, todos):
    """Teste para contrato destroy com evidence vazia - deve ser recusado"""
    destruicao["precondition"]["evidence"] = []
    achados = evidencia_obrigatoria(destruicao, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R6"
    assert achados[0]["path"] == "$.precondition.evidence"


def test_destroy_com_evidence_passa(destruicao, todos):
    """Teste para contrato destroy com evidence válida - deve passar"""
    # O contrato destruicao já vem com evidence válida do fixture
    achados = evidencia_obrigatoria(destruicao, todos)
    assert len(achados) == 0


def test_write_nunca_recebe_r6(escrita, todos):
    """Teste para contrato write - nunca deve receber R6"""
    achados = evidencia_obrigatoria(escrita, todos)
    assert len(achados) == 0


def test_precondition_vazio_do_yaml_vira_achado_e_nao_excecao(destruicao, todos):
    """Teste para precondition vazio (None) - deve gerar achado e não exceção"""
    # Simular YAML vazio (secao:) que vira None
    destruicao["precondition"] = None
    achados = evidencia_obrigatoria(destruicao, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R6"
    assert achados[0]["path"] == "$.precondition.evidence"