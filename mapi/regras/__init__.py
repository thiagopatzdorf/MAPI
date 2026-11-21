"""Regras de recusa da SPEC §3. Uma regra por módulo ``rNN_*.py``, descoberto sozinho.

Uma regra é ``(contrato, todos) -> list[achado]`` registrada com ``@regra("Rn")``. ``todos`` mapeia
``capability`` para o contrato (as regras que olham outras capacidades, como R3 e R5, usam).
Achado: ``{rule, capability, path, message}`` -- o JSON que o ``exit 2`` imprime.
"""
from __future__ import annotations

import importlib
import pkgutil
from typing import Any, Callable

Achado = dict[str, Any]
Regra = Callable[[dict[str, Any], dict[str, dict[str, Any]]], list[Achado]]

REGRAS: dict[str, Regra] = {}


def regra(id_: str) -> Callable[[Regra], Regra]:
    def registrar(fn: Regra) -> Regra:
        if id_ in REGRAS:
            raise ValueError(f"regra {id_} registrada duas vezes ({REGRAS[id_].__module__} e {fn.__module__})")
        REGRAS[id_] = fn
        return fn

    return registrar


def achado(id_: str, contrato: dict[str, Any], caminho: str, mensagem: str) -> Achado:
    return {"rule": id_, "capability": contrato.get("capability"), "path": caminho, "message": mensagem}


def _descobrir() -> None:
    for m in pkgutil.iter_modules(__path__):
        if m.name[:1] == "r" and m.name[1:3].isdigit():
            importlib.import_module(f"{__name__}.{m.name}")


def checar(contratos: list[Achado]) -> list[Achado]:
    _descobrir()
    # `capability` que não é texto (lista, mapa) não é chave de dicionário: não indexa, e a R-de-formato a recusa.
    todos = {c["capability"]: c for c in contratos if isinstance(c.get("capability"), str)}
    achados: list[Achado] = []
    for c in contratos:
        for id_ in sorted(REGRAS, key=lambda r: int(r[1:])):
            achados += REGRAS[id_](c, todos)
    return achados
