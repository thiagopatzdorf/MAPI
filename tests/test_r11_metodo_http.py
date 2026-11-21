from mapi.regras.r11_metodo_http import metodo_http_compativel


def test_leitura_por_delete_e_recusada(leitura, todos):
    """Testa que read com DELETE é recusado."""
    leitura["bindings"]["http"]["method"] = "DELETE"
    achados = metodo_http_compativel(leitura, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R11"
    assert achados[0]["path"] == "$.bindings.http.method"


def test_leitura_por_post_sem_override_e_recusada(leitura, todos):
    """Testa que read com POST sem x-mapi-method-override é recusado."""
    leitura["bindings"]["http"]["method"] = "POST"
    # Garantir que não há x-mapi-method-override ou que é diferente de True
    if "x-mapi-method-override" in leitura["bindings"]["http"]:
        del leitura["bindings"]["http"]["x-mapi-method-override"]
    
    achados = metodo_http_compativel(leitura, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R11"
    assert achados[0]["path"] == "$.bindings.http.method"


def test_leitura_por_post_com_override_passa(leitura, todos):
    """Testa que read com POST e x-mapi-method-override=True passa."""
    leitura["bindings"]["http"]["method"] = "POST"
    leitura["bindings"]["http"]["x-mapi-method-override"] = True
    
    achados = metodo_http_compativel(leitura, todos)
    assert len(achados) == 0


def test_escrita_por_get_e_recusada(escrita, todos):
    """Testa que write com GET é recusado."""
    escrita["bindings"]["http"]["method"] = "GET"
    achados = metodo_http_compativel(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R11"
    assert achados[0]["path"] == "$.bindings.http.method"


def test_destroy_por_get_e_recusado(destruicao, todos):
    """Testa que destroy com GET é recusado."""
    destruicao["bindings"]["http"]["method"] = "GET"
    achados = metodo_http_compativel(destruicao, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R11"
    assert achados[0]["path"] == "$.bindings.http.method"


def test_contrato_sem_binding_http_nao_gera_r11(escrita, todos):
    """Testa que contrato sem binding HTTP não gera achado R11."""
    if "bindings" in escrita:
        del escrita["bindings"]
    
    achados = metodo_http_compativel(escrita, todos)
    assert len(achados) == 0


def test_bindings_vazio_do_yaml_nao_derruba_a_regra(escrita, todos):
    """Testa que bindings vazio (None do YAML) não derruba a regra."""
    escrita["bindings"] = None  # Simula secao: vazio no YAML
    
    achados = metodo_http_compativel(escrita, todos)
    assert len(achados) == 0


def test_leitura_por_get_passa(leitura, todos):
    """Testa que read com GET passa (caso válido)."""
    leitura["bindings"]["http"]["method"] = "GET"
    
    achados = metodo_http_compativel(leitura, todos)
    assert len(achados) == 0


def test_escrita_por_post_passa(escrita, todos):
    """Testa que write com POST passa (caso válido)."""
    escrita["bindings"]["http"]["method"] = "POST"
    
    achados = metodo_http_compativel(escrita, todos)
    assert len(achados) == 0


def test_destroy_por_delete_passa(destruicao, todos):
    """Testa que destroy com DELETE passa (caso válido)."""
    destruicao["bindings"]["http"]["method"] = "DELETE"
    
    achados = metodo_http_compativel(destruicao, todos)
    assert len(achados) == 0