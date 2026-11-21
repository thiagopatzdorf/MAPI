from mapi.regras.r02_inversa import inversa_obrigatoria


def test_write_sem_reversible_e_recusado(escrita, todos):
    """Teste: write sem reversible é recusado"""
    del escrita["reversible"]
    achados = inversa_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R2"
    assert achados[0]["path"] == "$.reversible"


def test_irreversible_com_reason_vazio_e_recusado(escrita, todos):
    """Teste: irreversible com reason vazio é recusado"""
    escrita["reversible"] = {"irreversible": {"reason": ""}}
    achados = inversa_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R2"
    assert achados[0]["path"] == "$.reversible"


def test_irreversible_com_reason_preenchido_passa(escrita, todos):
    """Teste: irreversible com reason preenchido passa"""
    escrita["reversible"] = {"irreversible": {"reason": "Não tem volta"}}
    achados = inversa_obrigatoria(escrita, todos)
    assert achados == []


def test_inverse_preenchida_passa(escrita, todos):
    """Teste: inverse preenchida passa"""
    escrita["reversible"] = {"inverse": {"effect": "read"}}
    achados = inversa_obrigatoria(escrita, todos)
    assert achados == []


def test_leitura_nunca_recebe_r2(leitura, todos):
    """Teste: leitura nunca recebe R2"""
    # Mesmo que tenha reversible inválido, leitura não deve receber R2
    # Primeiro adicionamos uma chave reversible inválida para testar
    leitura["reversible"] = None
    achados = inversa_obrigatoria(leitura, todos)
    assert achados == []


def test_reversible_vazio_do_yaml_vira_achado_e_nao_excecao(escrita, todos):
    """Teste: reversible vazio do YAML vira achado e não exceção"""
    # Simular o que acontece quando tem "reversible:" vazio no YAML
    escrita["reversible"] = {}
    achados = inversa_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R2"
    assert achados[0]["path"] == "$.reversible"


def test_irreversible_vazio_do_yaml_vira_achado_e_nao_excecao(escrita, todos):
    """Teste: irreversible vazio do YAML vira achado e não exceção"""
    # Simular o que acontece quando tem "reversible: {irreversible:}" no YAML
    escrita["reversible"] = {"irreversible": {}}
    achados = inversa_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R2"
    assert achados[0]["path"] == "$.reversible"


def test_reversible_que_e_texto_vira_achado_e_nao_excecao(escrita, todos):
    """Teste: reversible que é texto vira achado e não exceção"""
    # Simular o que acontece quando tem "reversible: texto" no YAML
    escrita["reversible"] = "texto"
    achados = inversa_obrigatoria(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R2"
    assert achados[0]["path"] == "$.reversible"


def test_destruicao_sem_reversible_e_recusado(destruicao, todos):
    """Teste: destroy sem reversible é recusado"""
    del destruicao["reversible"]
    achados = inversa_obrigatoria(destruicao, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R2"
    assert achados[0]["path"] == "$.reversible"