from mapi.regras.r04_prova import prova_obrigatoria


def test_write_sem_proof_e_recusado(escrita, todos):
    """Teste: write sem proof deve ser recusado"""
    del escrita["proof"]
    achados = prova_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R4"
    assert achados[0]["path"] == "$.proof"
    assert "write/destroy sem proof" in achados[0]["message"]


def test_proof_sem_read_e_recusado(escrita, todos):
    """Teste: proof sem read.capability deve ser recusado"""
    escrita["proof"] = {"expect": [{"context": "$.response", "condition": "$.status == 200"}]}
    achados = prova_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R4"
    assert achados[0]["path"] == "$.proof.read"
    assert "proof.read ausente" in achados[0]["message"]


def test_proof_com_expect_vazio_e_recusado(escrita, todos):
    """Teste: proof com expect vazio deve ser recusado"""
    escrita["proof"]["expect"] = []
    achados = prova_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R4"
    assert achados[0]["path"] == "$.proof.expect"
    assert "proof.expect deve ser uma lista não vazia" in achados[0]["message"]


def test_proof_completo_passa(escrita, destruicao, todos):
    """Teste: proof completo deve passar"""
    # Testar escrita com proof completo
    achados_escrita = prova_obrigatoria(escrita, todos)
    assert len(achados_escrita) == 0
    
    # Testar destruição com proof completo
    achados_destruicao = prova_obrigatoria(destruicao, todos)
    assert len(achados_destruicao) == 0


def test_leitura_nunca_recebe_r4(leitura, todos):
    """Teste: leitura nunca deve receber R4"""
    achados = prova_obrigatoria(leitura, todos)
    assert len(achados) == 0


def test_proof_read_nao_eh_dicionario(escrita, todos):
    """Teste: proof.read deve ser um dicionário"""
    escrita["proof"]["read"] = "invalid"
    achados = prova_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R4"
    assert achados[0]["path"] == "$.proof.read"
    assert "proof.read deve ser um mapa" in achados[0]["message"]


def test_proof_read_capability_vazio(escrita, todos):
    """Teste: proof.read.capability não pode ser vazio"""
    escrita["proof"]["read"]["capability"] = ""
    achados = prova_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R4"
    assert achados[0]["path"] == "$.proof.read.capability"
    assert "proof.read.capability ausente ou vazio" in achados[0]["message"]


def test_proof_nao_eh_dicionario(escrita, todos):
    """Teste: proof deve ser um dicionário"""
    escrita["proof"] = "invalid"
    achados = prova_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R4"
    assert achados[0]["path"] == "$.proof"
    assert "proof deve ser um mapa" in achados[0]["message"]


def test_proof_expect_nao_e_lista(escrita, todos):
    """Teste: proof.expect deve ser uma lista"""
    escrita["proof"]["expect"] = "invalid"
    achados = prova_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R4"
    assert achados[0]["path"] == "$.proof.expect"
    assert "proof.expect deve ser uma lista não vazia" in achados[0]["message"]