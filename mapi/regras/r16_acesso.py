"""R16: `write`/`destroy` sem `access.callers`.

Defeito que impede: capacidade que muda estado sem dizer QUEM pode chamá-la vira "quem tem o token
chama tudo" (medido na casa: o Factory MCP tem um token compartilhado e nenhum filtro por quem chama).
O contrato já dizia o que a capacidade faz, se tem volta e como provar; faltava quem.
"""
from __future__ import annotations

from . import achado, regra


@regra("R16")
def acesso_obrigatorio(contrato, todos):
    """`write`/`destroy` precisam de `access.callers` como lista não vazia. `read` pode omitir
    `access` (vale quem alcança o binding, como antes); se declarar, a R17 confere a forma.
    Seção de tipo errado (`None`, texto, lista) vira achado, nunca exceção."""
    if not isinstance(contrato, dict) or contrato.get("effect") not in ("write", "destroy"):
        return []
    acesso = contrato.get("access")
    if acesso is None:
        return [achado("R16", contrato, "$.access", "write/destroy sem access: diga quem pode chamar")]
    if not isinstance(acesso, dict):
        return [achado("R16", contrato, "$.access", "access deve ser um mapa")]
    callers = acesso.get("callers")
    if not isinstance(callers, list) or not callers:
        return [achado("R16", contrato, "$.access.callers", "access.callers deve ser uma lista não vazia")]
    return []
