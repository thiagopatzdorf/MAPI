from mapi.regras.r03_inversa_valida import inversa_valida


def test_inversa_para_capacidade_inexistente_e_recusada(escrita, todos):
    """Teste: inversa para capacidade inexistente é recusada"""
    escrita["reversible"]["inverse"]["capability"] = "capacidade.inexistente"
    achados = inversa_valida(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R3"
    assert achados[0]["path"] == "$.reversible.inverse.capability"


def test_inversa_para_leitura_e_recusada(escrita, todos):
    """Teste: inversa para leitura é recusada"""
    # Usar uma capacidade conhecida que é de leitura
    for cap in todos.values():
        if cap.get("effect") == "read":
            escrita["reversible"]["inverse"]["capability"] = cap["capability"]
            break
    
    achados = inversa_valida(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R3"
    assert achados[0]["path"] == "$.reversible.inverse.capability"


def test_inversa_propria_sem_idempotencia_nem_estado_capturado_e_recusada(escrita, todos):
    """Teste: inversa própria sem idempotência nem estado capturado é recusada"""
    # Remover idempotent e captures_state_before se existirem
    if "idempotent" in escrita:
        del escrita["idempotent"]
    
    inverse = escrita["reversible"]["inverse"]
    if "captures_state_before" in inverse:
        del inverse["captures_state_before"]
    
    achados = inversa_valida(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R3"
    assert achados[0]["path"] == "$.reversible.inverse.capability"


def test_inversa_propria_com_idempotent_true_passa(escrita, todos):
    """Teste: inversa própria com idempotent=true passa"""
    # Garantir que idempotent é True
    escrita["idempotent"] = True
    
    # Remover captures_state_before se existir
    inverse = escrita["reversible"]["inverse"]
    if "captures_state_before" in inverse:
        del inverse["captures_state_before"]
    
    achados = inversa_valida(escrita, todos)
    assert achados == []


def test_inversa_propria_com_captures_state_before_passa(escrita, todos):
    """Teste: inversa própria com captures_state_before passa"""
    # Remover idempotent se existir
    if "idempotent" in escrita:
        del escrita["idempotent"]
    
    # Garantir que captures_state_before é True
    escrita["reversible"]["inverse"]["captures_state_before"] = True
    
    achados = inversa_valida(escrita, todos)
    assert achados == []


def test_inversa_para_outra_escrita_passa(escrita, todos):
    """Teste: inversa para outra escrita passa"""
    # Procurar outra capacidade de escrita diferente
    for cap in todos.values():
        if cap.get("effect") == "write" and cap["capability"] != escrita["capability"]:
            escrita["reversible"]["inverse"]["capability"] = cap["capability"]
            break
    
    achados = inversa_valida(escrita, todos)
    assert achados == []


def test_leitura_nunca_recebe_r3(leitura, todos):
    """Teste: leitura nunca recebe R3"""
    # Mesmo que tenha reversible.inverse inválido, leitura não deve receber R3
    leitura["reversible"] = {"inverse": {"capability": "qualquer.coisa"}}
    achados = inversa_valida(leitura, todos)
    assert achados == []


def test_reversible_vazio_do_yaml_nao_derruba_a_regra(escrita, todos):
    """Teste: reversible vazio do YAML não derruba a regra"""
    # Simular o que acontece quando tem "reversible:" vazio no YAML
    escrita["reversible"] = {}
    achados = inversa_valida(escrita, todos)
    assert achados == []  # Não deve gerar R3 (R2 cuida disso)


def test_inverse_nao_mapa_nao_derruba_a_regra(escrita, todos):
    """Teste: inverse que não é mapa não derruba a regra"""
    # Tornar inverse uma string
    escrita["reversible"]["inverse"] = "nao.e.mapa"
    achados = inversa_valida(escrita, todos)
    assert achados == []  # Não deve gerar R3 (R2 cuida disso)


def test_capability_nao_string_nao_derruba_a_regra(escrita, todos):
    """Teste: capability que não é string não derruba a regra"""
    # Tornar capability um número
    escrita["reversible"]["inverse"]["capability"] = 123
    achados = inversa_valida(escrita, todos)
    assert achados == []  # Não deve gerar R3 (R2 cuida disso)