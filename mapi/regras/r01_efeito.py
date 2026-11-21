"""R1: ``effect`` ausente ou fora de read|write|destroy.

Defeito que impede: tool sem efeito vira ``destructiveHint: true`` por padrão no MCP, e o ruído
ensina o cliente a ignorar o hint.
"""
from __future__ import annotations

from . import achado, regra

EFEITOS = ("read", "write", "destroy")


@regra("R1")
def efeito_valido(contrato, todos):
    efeito = contrato.get("effect")
    if efeito in EFEITOS:
        return []
    return [achado("R1", contrato, "$.effect", f"effect ausente ou fora de {list(EFEITOS)}: {efeito!r}")]
