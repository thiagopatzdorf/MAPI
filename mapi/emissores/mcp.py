"""Emissor MCP: contrato MAPI -> objeto Tool do `tools/list` (SPEC §8).

Entrada já passou por `checar()`: o emissor não revalida, e um contrato malformado pode levantar
exceção aqui. Saída é determinística (mesma entrada, mesmo JSON) para o `tools/list` ser cacheável.

Decisões de desenho (2026-10-20), cada uma com o defeito que impede:
- `annotations` saem da tabela do efeito (`read` sem `destructiveHint`; `write` com `destructiveHint: false`
  explícito): o padrão do protocolo é `destructiveHint: true` e `openWorldHint: true`, que mentem para infra.
- O parâmetro de consentimento (`confirm`) é injetado no `inputSchema`; colidir com um campo do contrato
  é erro, porque o campo do contrato seria sobrescrito em silêncio.
- A descrição é montada só do que o contrato diz (uso, consentimento, recusas, volta, prova, "Not for").
  Nada é inventado: texto que não sai do contrato não pode aparecer na descrição que o modelo lê.
- `x-mapi-defs` vira `$defs` e os `$ref` são reescritos; os do envelope levam prefixo `mapi_` para não
  colidir com as definições do contrato.
"""
from __future__ import annotations

import copy
import re
from typing import Any

NOME_VALIDO = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
PREFIXO_REF_CONTRATO = "#/x-mapi-defs/"
PREFIXO_REF_EMITIDO = "#/$defs/"
PARAMETRO_PADRAO = "confirm"

ORCAMENTO_SCHEMA = {
    "type": "object",
    "properties": {
        "cost": {"type": "object", "properties": {"amount": {"type": "number"}, "unit": {"type": "string"}}},
        "output_bytes": {"type": "integer"},
        "truncated": {"type": "boolean"},
    },
}


def nome_da_tool(contrato: dict[str, Any]) -> str:
    mcp = (contrato.get("bindings") or {}).get("mcp") or {}
    return mcp.get("tool") or contrato["capability"].replace(".", "_")


def _nome_de(capability: str, todos: dict[str, dict[str, Any]]) -> str:
    return nome_da_tool(todos[capability]) if capability in todos else capability.replace(".", "_")


def parametro_de_consentimento(contrato: dict[str, Any]) -> str | None:
    consent = contrato.get("consent")
    if not consent:
        return None
    return (consent.get("confirm") or {}).get("parameter") or PARAMETRO_PADRAO


def _reescrever_refs(no: Any) -> Any:
    if isinstance(no, dict):
        saida = {}
        for k, v in no.items():
            if k == "$ref" and isinstance(v, str) and v.startswith(PREFIXO_REF_CONTRATO):
                saida[k] = PREFIXO_REF_EMITIDO + v[len(PREFIXO_REF_CONTRATO):]
            else:
                saida[k] = _reescrever_refs(v)
        return saida
    if isinstance(no, list):
        return [_reescrever_refs(x) for x in no]
    return no


def _usa_defs(no: Any) -> bool:
    if isinstance(no, dict):
        return any((k == "$ref" and isinstance(v, str) and v.startswith(PREFIXO_REF_EMITIDO)) or _usa_defs(v)
                   for k, v in no.items())
    if isinstance(no, list):
        return any(_usa_defs(x) for x in no)
    return False


def _defs_do_contrato(contrato: dict[str, Any]) -> dict[str, Any]:
    return _reescrever_refs(copy.deepcopy(contrato.get("x-mapi-defs") or {}))


def schema_do_resultado(contrato: dict[str, Any]) -> dict[str, Any]:
    """O `output` do contrato, autossuficiente (com `$defs` se usar `$ref`). É o `result` do envelope."""
    saida = _reescrever_refs(copy.deepcopy(contrato["output"]))
    if _usa_defs(saida):
        saida["$defs"] = _defs_do_contrato(contrato)
    return saida


def anotacoes(contrato: dict[str, Any]) -> dict[str, Any]:
    efeito = contrato["effect"]
    a: dict[str, Any] = {"title": contrato["title"], "readOnlyHint": efeito == "read"}
    if efeito != "read":
        a["destructiveHint"] = efeito == "destroy"
    a["idempotentHint"] = True if efeito == "read" else bool(contrato.get("idempotent"))
    a["openWorldHint"] = bool(contrato.get("open_world", False))
    return a


def _frase(texto: str) -> str:
    return " ".join(str(texto).split())


def descricao(contrato: dict[str, Any], todos: dict[str, dict[str, Any]]) -> str:
    partes = [_frase(contrato["when_to_use"])]
    param = parametro_de_consentimento(contrato)
    if param:
        partes.append(f"Dry run by default: pass {param}=true to execute.")
    recusas = (contrato.get("consent") or {}).get("refuses") or []
    if recusas:
        partes.append("Refuses: " + "; ".join(_frase(r["reason"]) for r in recusas) + ".")
    rev = contrato.get("reversible") or {}
    if rev.get("inverse"):
        partes.append(f"Inverse: {_nome_de(rev['inverse']['capability'], todos)}.")
    elif rev.get("irreversible"):
        partes.append(f"SEM VOLTA: {_frase(rev['irreversible']['reason'])}.")
    prova = contrato.get("proof")
    if prova:
        janela = f" within {prova['within_s']} s" if prova.get("within_s") else ""
        partes.append(f"Proof: re-read via {_nome_de(prova['read']['capability'], todos)}{janela}.")
    if contrato.get("when_not_to_use"):
        partes.append("Not for: " + _frase(contrato["when_not_to_use"]))
    return " ".join(p if p.endswith((".", "!", "?")) else p + "." for p in partes)


def schema_de_entrada(contrato: dict[str, Any]) -> dict[str, Any]:
    entrada = _reescrever_refs(copy.deepcopy(contrato["input"]))
    param = parametro_de_consentimento(contrato)
    if param:
        props = entrada.setdefault("properties", {})
        if param in props:
            raise ValueError(f"{contrato['capability']}: o campo {param!r} do input colide com o parâmetro de consentimento")
        props[param] = {
            "type": "boolean", "default": False,
            "description": "false (padrão) = dry run: devolve would_do e a volta sem executar. true = executa e prova pela releitura.",
        }
    if _usa_defs(entrada):
        entrada["$defs"] = _defs_do_contrato(contrato)
    return entrada


def schema_de_saida(contrato: dict[str, Any]) -> dict[str, Any]:
    resultado = _reescrever_refs(copy.deepcopy(contrato["output"]))
    defs = _defs_do_contrato(contrato)
    if contrato["effect"] == "read":
        schema: dict[str, Any] = {
            "type": "object",
            "required": ["ok", "dry_run", "result", "budget"],
            "properties": {
                "ok": {"type": "boolean"},
                "dry_run": {"type": "boolean", "const": False},
                "result": resultado,
                "budget": copy.deepcopy(ORCAMENTO_SCHEMA),
            },
        }
        if defs:
            schema["$defs"] = defs
        return schema
    param = parametro_de_consentimento(contrato)
    rev = contrato.get("reversible") or {}
    volta = bool(rev.get("inverse"))
    guarda_estado = bool((rev.get("inverse") or {}).get("captures_state_before"))
    defs["mapi_inverse"] = {
        "type": "object", "required": ["capability", "args"],
        "properties": {"capability": {"type": "string"}, "args": {"type": "object"}},
    }
    seco_props: dict[str, Any] = {
        "ok": {"const": True}, "dry_run": {"const": True}, "would_do": {"type": "string"},
        "refused": {"type": "null"}, "precondition": {"type": "object"},
        "to_execute": {"const": f"repeat with {param}=true"},
    }
    if volta:
        seco_props["inverse"] = {"$ref": PREFIXO_REF_EMITIDO + "mapi_inverse"}
    defs["mapi_dry_run"] = {"type": "object", "required": ["ok", "dry_run", "would_do", "to_execute"], "properties": seco_props}
    defs["mapi_refused"] = {
        "type": "object", "required": ["ok", "refused"],
        "properties": {
            "ok": {"const": False},
            "refused": {"type": "object", "required": ["id", "reason"],
                        "properties": {"id": {"type": "string"}, "reason": {"type": "string"}}},
        },
    }
    exec_props: dict[str, Any] = {
        "ok": {"type": "boolean"}, "dry_run": {"const": False}, "result": resultado,
        "proof": {"type": "object", "required": ["checked", "passed"],
                  "properties": {"checked": {"type": "boolean"}, "passed": {"type": "boolean"},
                                 "read_at": {"type": "string"}, "attempts": {"type": "integer"}}},
        "budget": copy.deepcopy(ORCAMENTO_SCHEMA), "error": {"type": "string"},
    }
    exigidos = ["ok", "dry_run", "proof"]
    if guarda_estado:
        exec_props["state_before"] = {}
        exigidos.append("state_before")
    if volta:
        exec_props["inverse"] = {"$ref": PREFIXO_REF_EMITIDO + "mapi_inverse"}
    defs["mapi_executed"] = {"type": "object", "required": exigidos, "properties": exec_props}
    return {"oneOf": [{"$ref": PREFIXO_REF_EMITIDO + n} for n in ("mapi_dry_run", "mapi_refused", "mapi_executed")],
            "$defs": defs}


def _meta(contrato: dict[str, Any]) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "io.mapi/version": "0.1",
        "io.mapi/capability": f"{contrato['capability']}@{contrato['version']}",
        "io.mapi/effect": contrato["effect"],
        "io.mapi/budget": copy.deepcopy(contrato["budget"]),
    }
    param = parametro_de_consentimento(contrato)
    if param:
        meta["io.mapi/consent"] = {"dry_run": "default", "confirm": param}
    rev = contrato.get("reversible") or {}
    if rev.get("inverse"):
        meta["io.mapi/inverse"] = rev["inverse"]["capability"]
    if rev.get("irreversible"):
        meta["io.mapi/irreversible"] = _frase(rev["irreversible"]["reason"])
    if contrato.get("proof"):
        meta["io.mapi/proof"] = contrato["proof"]["read"]["capability"]
    return meta


def emitir(contrato: dict[str, Any], todos: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    todos = todos or {}
    nome = nome_da_tool(contrato)
    if not NOME_VALIDO.match(nome):
        raise ValueError(f"{contrato['capability']}: nome de tool inválido {nome!r} (1 a 128 de A-Z a-z 0-9 _ - .)")
    anot = anotacoes(contrato)
    return {
        "name": nome, "title": contrato["title"], "description": descricao(contrato, todos),
        "inputSchema": schema_de_entrada(contrato), "outputSchema": schema_de_saida(contrato),
        "annotations": anot, "_meta": _meta(contrato),
    }


def emitir_todos(contratos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordem alfabética pelo id da capacidade (SPEC §8: `tools/list` determinístico e cacheável)."""
    todos = {c["capability"]: c for c in contratos}
    tools = [emitir(c, todos) for c in sorted(contratos, key=lambda c: c["capability"])]
    nomes = [t["name"] for t in tools]
    repetidos = sorted({n for n in nomes if nomes.count(n) > 1})
    if repetidos:
        raise ValueError(f"nome de tool repetido entre capacidades: {repetidos}")
    return tools
