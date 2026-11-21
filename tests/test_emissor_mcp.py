"""O emissor MCP é cobrado por invariantes que não dependem dele, não por um gabarito que ele reproduz.

Erro -> regra (2026-10-20): os alvos `examples/*.mcp.json` foram escritos à mão e não saem do contrato (têm
frases como "ou cloudflare_apagar se a chamada criou o recurso" e `destructiveHint: false` numa leitura).
Igualdade byte a byte forçaria o emissor a inventar texto ou o gabarito a ser editado para caber no código.
Aqui o que se mede é: schema válido, todo `$ref` resolve, annotations batem com o efeito, `confirm` existe
se e somente se há consentimento, nome válido e único, e os exemplos do contrato conformam com o schema.
"""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

from mapi.emissores.mcp import (NOME_VALIDO, anotacoes, descricao, emitir, emitir_todos, nome_da_tool,
                                parametro_de_consentimento, schema_do_resultado)
from mapi.modelo import carregar, carregar_texto

EXEMPLOS = sorted((Path(__file__).resolve().parents[1] / "examples").glob("*.mapi.yaml"))
CONTRATOS = [c for arq in EXEMPLOS for c in carregar(arq)]
TODOS = {c["capability"]: c for c in CONTRATOS}
IDS = [c["capability"] for c in CONTRATOS]


def _refs(no):
    if isinstance(no, dict):
        for k, v in no.items():
            if k == "$ref":
                yield v
            else:
                yield from _refs(v)
    elif isinstance(no, list):
        for x in no:
            yield from _refs(x)


@pytest.mark.parametrize("contrato", CONTRATOS, ids=IDS)
def test_schemas_emitidos_sao_json_schema_2020_12_valido(contrato):
    tool = emitir(contrato, TODOS)
    jsonschema.Draft202012Validator.check_schema(tool["inputSchema"])
    jsonschema.Draft202012Validator.check_schema(tool["outputSchema"])


@pytest.mark.parametrize("contrato", CONTRATOS, ids=IDS)
def test_todo_ref_dos_schemas_emitidos_resolve_para_um_defs_existente(contrato):
    tool = emitir(contrato, TODOS)
    for chave in ("inputSchema", "outputSchema"):
        raiz = tool[chave]
        for ref in _refs(raiz):
            assert ref.startswith("#/$defs/"), f"{chave}: ref fora de $defs: {ref}"
            assert ref.split("/")[-1] in raiz.get("$defs", {}), f"{chave}: {ref} sem definição"
        assert "#/x-mapi-defs/" not in json.dumps(raiz), f"{chave}: sobrou ref do contrato"


@pytest.mark.parametrize("contrato", CONTRATOS, ids=IDS)
def test_annotations_batem_com_o_efeito_do_contrato(contrato):
    a = emitir(contrato, TODOS)["annotations"]
    efeito = contrato["effect"]
    assert a["readOnlyHint"] is (efeito == "read")
    if efeito == "read":
        assert "destructiveHint" not in a and a["idempotentHint"] is True
    else:
        assert a["destructiveHint"] is (efeito == "destroy")
    assert a["openWorldHint"] is bool(contrato.get("open_world", False))
    assert a["title"] == contrato["title"]


@pytest.mark.parametrize("contrato", CONTRATOS, ids=IDS)
def test_confirm_so_existe_no_input_quando_o_contrato_tem_consentimento(contrato):
    entrada = emitir(contrato, TODOS)["inputSchema"]
    param = parametro_de_consentimento(contrato)
    if contrato["effect"] == "read":
        assert param is None and "confirm" not in entrada.get("properties", {})
    else:
        assert param in entrada["properties"] and param not in entrada.get("required", [])
        assert entrada["properties"][param]["default"] is False


def test_nomes_de_tool_dos_exemplos_sao_validos_e_unicos():
    tools = emitir_todos(CONTRATOS)
    nomes = [t["name"] for t in tools]
    assert len(nomes) == len(set(nomes)) == 7 and all(NOME_VALIDO.match(n) for n in nomes)
    assert nomes == [nome_da_tool(c) for c in sorted(CONTRATOS, key=lambda c: c["capability"])]


def test_saida_e_deterministica_para_o_tools_list_ser_cacheavel():
    a = json.dumps(emitir_todos(copy.deepcopy(CONTRATOS)), sort_keys=True)
    b = json.dumps(emitir_todos(copy.deepcopy(CONTRATOS)), sort_keys=True)
    assert a == b


def test_emitir_nao_muda_o_contrato_de_entrada():
    antes = copy.deepcopy(CONTRATOS)
    emitir_todos(CONTRATOS)
    assert CONTRATOS == antes


# ---------------------------------------------------------------- os exemplos conformam com o schema emitido
def _casos_de_exemplo():
    for c in CONTRATOS:
        for ex in c.get("examples") or []:
            yield pytest.param(c, ex, id=f"{c['capability']}::{ex['name']}")


def _sem_required(no):
    """`output_expected` é expectativa PARCIAL (subconjunto): vale tipo e const, não a lista de obrigatórios."""
    if isinstance(no, dict):
        return {k: _sem_required(v) for k, v in no.items() if k != "required"}
    if isinstance(no, list):
        return [_sem_required(x) for x in no]
    return no


@pytest.mark.parametrize("contrato,exemplo", list(_casos_de_exemplo()))
def test_resultado_esperado_do_exemplo_valida_contra_o_output_do_contrato(contrato, exemplo):
    esperado = exemplo.get("output_expected")
    if esperado is None:
        pytest.skip("exemplo sem output_expected")
    if contrato["effect"] == "read":
        # leitura: output_expected é o próprio resultado
        jsonschema.validate(esperado, schema_do_resultado(contrato), cls=jsonschema.Draft202012Validator)
        return
    # escrita: output_expected é o envelope executado, afirmado só em parte; cada campo tem de existir e ter o tipo certo
    defs = emitir(contrato, TODOS)["outputSchema"]["$defs"]
    props = defs["mapi_executed"]["properties"]
    for campo, valor in esperado.items():
        assert campo in props, f"{contrato['capability']}::{exemplo['name']}: campo {campo!r} não existe no envelope executado"
        jsonschema.validate(valor, _sem_required({**props[campo], "$defs": defs}), cls=jsonschema.Draft202012Validator)


@pytest.mark.parametrize("contrato,exemplo", list(_casos_de_exemplo()))
def test_seco_e_recusa_do_exemplo_validam_contra_o_outputschema_emitido(contrato, exemplo):
    tool = emitir(contrato, TODOS)
    validador = jsonschema.Draft202012Validator(tool["outputSchema"])
    param = parametro_de_consentimento(contrato)
    if "dry_run_expected" in exemplo:
        instancia = {"ok": True, "dry_run": True, "refused": None, "to_execute": f"repeat with {param}=true",
                     **exemplo["dry_run_expected"]}
        validador.validate(instancia)
    elif "refused_expected" in exemplo:
        validador.validate({"ok": False, "refused": {"id": exemplo["refused_expected"], "reason": "x"}})
    else:
        pytest.skip("exemplo sem seco nem recusa")


# ---------------------------------------------------------------- casos de borda do emissor
BASE = """
mapi: "0.1"
capability: a.escrever
version: 1
title: Escrever
when_to_use: "Escreve algo."
effect: write
idempotent: false
input: {type: object, properties: {x: {type: string}}}
output: {type: object}
consent: {dry_run: default}
reversible: {irreversible: {reason: "e-mail enviado não volta"}}
proof: {read: {capability: a.ler}, expect: [{condition: "$.ok", type: simple}]}
budget: {cost: {amount: 0, unit: USD}, max_output_bytes: 1024}
bindings: {mcp: {tool: a_escrever}}
examples: [{name: e, input: {x: "1"}}]
"""


def test_irreversivel_aparece_na_descricao_como_sem_volta_e_nao_inventa_inversa():
    c = carregar_texto(BASE)[0]
    d = descricao(c, {})
    assert "SEM VOLTA: e-mail enviado não volta." in d and "Inverse:" not in d
    assert "inverse" not in json.dumps(emitir(c, {})["outputSchema"]["$defs"]["mapi_executed"]["properties"])


def test_campo_do_input_com_o_nome_do_parametro_de_consentimento_e_recusado_em_vez_de_sobrescrito():
    c = carregar_texto(BASE)[0]
    c["input"]["properties"]["confirm"] = {"type": "string"}
    with pytest.raises(ValueError, match="colide"):
        emitir(c, {})


def test_nome_de_tool_invalido_e_recusado():
    c = carregar_texto(BASE)[0]
    c["bindings"]["mcp"]["tool"] = "tem espaço"
    with pytest.raises(ValueError, match="inválido"):
        emitir(c, {})


def test_duas_capacidades_com_a_mesma_tool_sao_recusadas():
    a = carregar_texto(BASE)[0]
    b = copy.deepcopy(a)
    b["capability"] = "b.escrever"
    with pytest.raises(ValueError, match="repetido"):
        emitir_todos([a, b])


def test_parametro_de_consentimento_customizado_vai_para_o_input_e_para_a_descricao():
    c = carregar_texto(BASE)[0]
    c["consent"]["confirm"] = {"parameter": "sim"}
    tool = emitir(c, {})
    assert "sim" in tool["inputSchema"]["properties"] and "pass sim=true" in tool["description"]
    assert tool["outputSchema"]["$defs"]["mapi_dry_run"]["properties"]["to_execute"] == {"const": "repeat with sim=true"}


def test_idempotente_de_escrita_sai_nas_annotations_e_leitura_e_sempre_idempotente():
    c = carregar_texto(BASE)[0]
    assert anotacoes(c)["idempotentHint"] is False
    c["idempotent"] = True
    assert anotacoes(c)["idempotentHint"] is True
