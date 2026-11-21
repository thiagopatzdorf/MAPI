from mapi.regras import checar
from mapi.regras.r05_prova_le import prova_le


def test_prova_que_aponta_para_escrita_e_recusada(escrita, todos):
    """Teste para verificar que prova apontando para capacidade de escrita é recusada."""
    # Modificar a escrita para apontar para outra capacidade de escrita
    escrita["proof"]["read"]["capability"] = "cloudflare.rest.write"  # Outra capacidade de escrita
    achados = prova_le(escrita, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R5"
    assert achados[0]["path"] == "$.proof.read.capability"


def test_prova_que_aponta_para_destroy_e_recusada(destruicao, todos):
    """Teste para verificar que prova apontando para capacidade de destruição é recusada."""
    # Modificar a destruição para apontar para uma capacidade de destruição
    destruicao["proof"]["read"]["capability"] = "gcp.disk.delete"  # Outra capacidade de destruição
    achados = prova_le(destruicao, todos)
    assert len(achados) == 1
    assert achados[0]["rule"] == "R5"
    assert achados[0]["path"] == "$.proof.read.capability"


def test_prova_que_aponta_para_leitura_passa(escrita, leitura, todos):
    """Teste para verificar que prova apontando para capacidade de leitura passa."""
    # Modificar a escrita para apontar para uma capacidade de leitura
    escrita["proof"]["read"]["capability"] = "cloudflare.rest.get"  # Capacidade de leitura
    achados = prova_le(escrita, todos)
    assert achados == []


def test_prova_que_aponta_para_capacidade_desconhecida_nao_gera_r5(escrita, todos):
    """Teste para verificar que prova apontando para capacidade desconhecida não gera R5."""
    # Modificar a escrita para apontar para uma capacidade desconhecida
    escrita["proof"]["read"]["capability"] = "capacidade.desconhecida"
    achados = prova_le(escrita, todos)
    assert achados == []


def test_leitura_nunca_recebe_r5(leitura, todos):
    """Teste para verificar que leitura nunca recebe R5."""
    # Mesmo que tenha uma prova apontando para algo errado, leitura não deve receber R5
    leitura["proof"] = {"read": {"capability": "cloudflare.rest.write"}}
    achados = prova_le(leitura, todos)
    assert achados == []


def test_proof_vazio_do_yaml_nao_derruba_a_regra(escrita, todos):
    """Teste para verificar que proof vazio (None) não derruba a regra."""
    # Em YAML, `proof:` vazio é None
    escrita["proof"] = None
    achados = prova_le(escrita, todos)
    assert achados == []


def test_proof_read_vazio_do_yaml_nao_derruba_a_regra(escrita, todos):
    """Teste para verificar que proof.read vazio não derruba a regra."""
    # Em YAML, `proof.read:` vazio é None
    escrita["proof"]["read"] = None
    achados = prova_le(escrita, todos)
    assert achados == []


def test_capability_que_nao_e_texto_nao_derruba_a_regra(escrita, todos):
    """Teste para verificar que capability que não é texto não derruba a regra."""
    # capability como número
    escrita["proof"]["read"]["capability"] = 123
    achados = prova_le(escrita, todos)
    assert achados == []

    # capability como lista
    escrita["proof"]["read"]["capability"] = ["cloudflare.rest.get"]
    achados = prova_le(escrita, todos)
    assert achados == []


def test_checar_acha_a_r5_sozinho_sem_registro_manual(escrita, todos):
    """Teste para verificar que checar() acha a R5 sozinho."""
    # Modificar a escrita para apontar para outra capacidade de escrita
    escrita["proof"]["read"]["capability"] = "cloudflare.rest.write"
    achados = checar([escrita])
    assert "R5" in {x["rule"] for x in achados}