"""R8: `read` com `consent` ou `reversible`.

Defeito que impede: contrato mente sobre o efeito (ou o efeito está errado).
"""
from __future__ import annotations

from . import achado, regra


@regra("R8")
def leitura_pura(contrato, todos):
    """Para `read`: um achado em `$.consent` se a chave existe e outro em `$.reversible` 
    se existe (qualquer valor, até vazio ou `None`). Sem as chaves, sem achado. 
    `write`/`destroy` nunca recebem R8."""
    efeito = contrato.get("effect")

    # write/destroy nunca recebem R8
    if efeito in ("write", "destroy"):
        return []

    # Apenas read pode receber R8
    if efeito != "read":
        return []

    achados = []

    # Verificar se consent existe (qualquer valor)
    if "consent" in contrato:
        achados.append(achado("R8", contrato, "$.consent", "read com consent"))

    # Verificar se reversible existe (qualquer valor)
    if "reversible" in contrato:
        achados.append(achado("R8", contrato, "$.reversible", "read com reversible"))

    return achados