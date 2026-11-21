import copy

from mapi.regras.r13_chave_desconhecida import chave_desconhecida


def test_chave_digitada_errada_e_recusada(escrita, todos):
    """Testa que uma chave digitada errada é recusada."""
    contrato = copy.deepcopy(escrita)
    contrato["titel"] = "Título digitado errado"  # Deveria ser "title"
    achados = chave_desconhecida(contrato, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R13"
    assert achados[0]["path"] == "$.titel"


def test_duas_chaves_desconhecidas_geram_dois_achados(escrita, todos):
    """Testa que duas chaves desconhecidas geram dois achados."""
    contrato = copy.deepcopy(escrita)
    contrato["titel"] = "Título digitado errado"  # Deveria ser "title"
    contrato["efect"] = "write"  # Deveria ser "effect"
    achados = chave_desconhecida(contrato, todos)
    assert len(achados) == 2
    regras = {achado["rule"] for achado in achados}
    caminhos = {achado["path"] for achado in achados}
    assert regras == {"R13"}
    assert caminhos == {"$.titel", "$.efect"}


def test_chave_com_prefixo_x_passa(escrita, todos):
    """Testa que chave com prefixo x- passa."""
    contrato = copy.deepcopy(escrita)
    contrato["x-mapi-custom-field"] = "valor customizado"
    achados = chave_desconhecida(contrato, todos)
    assert len(achados) == 0


def test_contrato_so_com_chaves_do_modelo_passa(escrita, todos):
    """Testa que contrato só com chaves do modelo passa."""
    contrato = copy.deepcopy(escrita)
    # Remover campos que possam ter sido adicionados e não sejam do modelo
    chaves_para_remover = [k for k in contrato.keys() if k not in [
        "mapi", "capability", "version", "title", "when_to_use", "when_not_to_use",
        "effect", "idempotent", "open_world", "input", "output", "consent",
        "reversible", "precondition", "proof", "budget", "bindings", "examples"
    ]]
    for chave in chaves_para_remover:
        del contrato[chave]
    
    achados = chave_desconhecida(contrato, todos)
    assert len(achados) == 0


def test_chave_numerica_nao_derruba_a_regra(escrita, todos):
    """Testa que chave numérica não derruba a regra."""
    contrato = copy.deepcopy(escrita)
    contrato[123] = "valor com chave numérica"
    achados = chave_desconhecida(contrato, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R13"
    assert achados[0]["path"] == "$.123"