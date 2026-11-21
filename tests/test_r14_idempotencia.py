from mapi.regras.r14_idempotencia import idempotencia_garantida


def test_idempotente_sem_garantia_e_recusado(escrita, todos):
    """Teste: write com idempotent: true sem nenhuma garantia deve ser recusado."""
    escrita["idempotent"] = True
    # Remover possíveis garantias
    if "bindings" in escrita:
        del escrita["bindings"]
    if "x-mapi-natural-key" in escrita:
        del escrita["x-mapi-natural-key"]
    # Remover token de idempotência do input se existir
    if "input" in escrita and isinstance(escrita["input"], dict):
        if "properties" in escrita["input"] and isinstance(escrita["input"]["properties"], dict):
            for prop in escrita["input"]["properties"].values():
                if isinstance(prop, dict) and "x-mapi-idempotency-token" in prop:
                    del prop["x-mapi-idempotency-token"]
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R14"
    assert achados[0]["path"] == "$.idempotent"


def test_idempotente_com_token_passa(escrita, todos):
    """Teste: write com idempotent: true e token de idempotência deve passar."""
    escrita["idempotent"] = True
    # Adicionar token de idempotência
    if "input" in escrita and isinstance(escrita["input"], dict):
        if "properties" in escrita["input"] and isinstance(escrita["input"]["properties"], dict):
            # Adicionar uma propriedade com token de idempotência
            escrita["input"]["properties"]["token"] = {"type": "string", "x-mapi-idempotency-token": True}
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 0


def test_idempotente_por_put_passa(escrita, todos):
    """Teste: write com idempotent: true e método HTTP PUT deve passar."""
    escrita["idempotent"] = True
    # Adicionar binding HTTP com método PUT
    escrita["bindings"] = {"http": {"method": "PUT"}}
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 0


def test_idempotente_por_delete_passa(escrita, todos):
    """Teste: write com idempotent: true e método HTTP DELETE deve passar."""
    escrita["idempotent"] = True
    # Adicionar binding HTTP com método DELETE
    escrita["bindings"] = {"http": {"method": "DELETE"}}
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 0


def test_idempotente_por_post_sem_garantia_e_recusado(escrita, todos):
    """Teste: write com idempotent: true e método HTTP POST sem garantia deve ser recusado."""
    escrita["idempotent"] = True
    # Adicionar binding HTTP com método POST (não idempotente por padrão)
    escrita["bindings"] = {"http": {"method": "POST"}}
    # Remover outras possíveis garantias
    if "x-mapi-natural-key" in escrita:
        del escrita["x-mapi-natural-key"]
    # Remover token de idempotência do input se existir
    if "input" in escrita and isinstance(escrita["input"], dict):
        if "properties" in escrita["input"] and isinstance(escrita["input"]["properties"], dict):
            for prop in escrita["input"]["properties"].values():
                if isinstance(prop, dict) and "x-mapi-idempotency-token" in prop:
                    del prop["x-mapi-idempotency-token"]
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R14"


def test_idempotente_com_chave_natural_valida_passa(escrita, todos):
    """Teste: write com idempotent: true e chave natural válida deve passar."""
    escrita["idempotent"] = True
    # Adicionar chave natural
    escrita["x-mapi-natural-key"] = ["name"]
    # Garantir que a chave natural existe no input
    if "input" in escrita and isinstance(escrita["input"], dict):
        if "properties" not in escrita["input"]:
            escrita["input"]["properties"] = {}
        if isinstance(escrita["input"]["properties"], dict):
            escrita["input"]["properties"]["name"] = {"type": "string"}
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 0


def test_chave_natural_com_campo_inexistente_e_recusada(escrita, todos):
    """Teste: write com idempotent: true e chave natural inexistente deve ser recusado."""
    escrita["idempotent"] = True
    # Adicionar chave natural que não existe no input
    escrita["x-mapi-natural-key"] = ["nonexistent_field"]
    # Garantir que o campo não existe no input
    if "input" in escrita and isinstance(escrita["input"], dict):
        if "properties" in escrita["input"] and isinstance(escrita["input"]["properties"], dict):
            # Remover o campo se existir
            if "nonexistent_field" in escrita["input"]["properties"]:
                del escrita["input"]["properties"]["nonexistent_field"]
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R14"


def test_idempotent_falso_nao_gera_r14(escrita, todos):
    """Teste: write com idempotent: false não deve gerar R14."""
    escrita["idempotent"] = False
    # Remover possíveis garantias
    if "bindings" in escrita:
        del escrita["bindings"]
    if "x-mapi-natural-key" in escrita:
        del escrita["x-mapi-natural-key"]
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 0


def test_leitura_nunca_recebe_r14(leitura, todos):
    """Teste: read nunca deve receber R14, mesmo com idempotent: true."""
    leitura["idempotent"] = True
    # Remover possíveis garantias
    if "bindings" in leitura:
        del leitura["bindings"]
    if "x-mapi-natural-key" in leitura:
        del leitura["x-mapi-natural-key"]
    
    achados = idempotencia_garantida(leitura, todos)
    assert len(achados) == 0


def test_input_vazio_do_yaml_nao_derruba_a_regra(escrita, todos):
    """Teste: input sendo None (vindo de YAML vazio) não deve derrubar a regra."""
    escrita["idempotent"] = True
    # Simular input vazio do YAML (secao: sem conteúdo vira None)
    escrita["input"] = None
    # Adicionar uma garantia alternativa
    escrita["bindings"] = {"http": {"method": "PUT"}}
    
    achados = idempotencia_garantida(escrita, todos)
    assert len(achados) == 0