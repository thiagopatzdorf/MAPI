import pytest

from mapi.regras.r16_acesso import acesso_obrigatorio
from mapi.regras.r17_quem import quem_se_resolve

AGE = "age1" + "q" * 58


def test_escrita_sem_access_e_recusada_porque_ninguem_sabe_quem_pode_chamar(escrita, todos):
    del escrita["access"]
    a = acesso_obrigatorio(escrita, todos)
    assert [(x["rule"], x["path"]) for x in a] == [("R16", "$.access")]


def test_destruicao_com_callers_vazio_e_recusada(destruicao, todos):
    destruicao["access"] = {"callers": []}
    assert [x["path"] for x in acesso_obrigatorio(destruicao, todos)] == ["$.access.callers"]


@pytest.mark.parametrize("valor", [None, "todos", ["@a"], 3])
def test_access_de_tipo_errado_vira_achado_e_nao_excecao(escrita, todos, valor):
    escrita["access"] = valor
    assert acesso_obrigatorio(escrita, todos)[0]["rule"] == "R16"
    assert quem_se_resolve(escrita, todos) == []  # tipo errado é da R16, sem achado duplo


def test_leitura_pode_omitir_access(leitura, todos):
    leitura.pop("access", None)
    assert acesso_obrigatorio(leitura, todos) == [] and quem_se_resolve(leitura, todos) == []


def test_as_quatro_formas_que_viram_chave_passam(escrita, todos):
    escrita["access"] = {"callers": ["@thiagopatzdorf", "group:socios", AGE, "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGkv"]}
    assert quem_se_resolve(escrita, todos) == []


@pytest.mark.parametrize("caller", ["admin", "time", "@", "@-x", "group:", "age1curto", "ecdsa-sha2-nistp256 AAAA", 42, None])
def test_nome_que_nao_vira_chave_e_recusado(escrita, todos, caller):
    escrita["access"] = {"callers": ["@ok", caller]}
    a = quem_se_resolve(escrita, todos)
    assert [(x["rule"], x["path"]) for x in a] == [("R17", "$.access.callers[1]")]


def test_qualquer_um_so_vale_em_leitura(escrita, leitura, todos):
    escrita["access"] = {"callers": ["*"]}
    assert quem_se_resolve(escrita, todos)[0]["message"].startswith("'*'")
    leitura["access"] = {"callers": ["*"]}
    assert quem_se_resolve(leitura, todos) == []


@pytest.mark.parametrize("dados", [{"at_rest": "secreto"}, "encrypted", []])
def test_at_rest_fora_de_plain_ou_encrypted_e_recusado(escrita, todos, dados):
    escrita["access"]["data"] = dados
    assert [x["path"] for x in quem_se_resolve(escrita, todos)] == ["$.access.data.at_rest"]


def test_dados_cifrados_em_repouso_passam(escrita, todos):
    escrita["access"]["data"] = {"at_rest": "encrypted"}
    assert quem_se_resolve(escrita, todos) == []
