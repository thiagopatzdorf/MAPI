"""R2: `write`/`destroy` sem `reversible.inverse` nem `reversible.irreversible.reason`.

Defeito que impede: sem inversa, ninguém limpa.
"""
from __future__ import annotations

from . import achado, regra


@regra("R2")
def inversa_obrigatoria(contrato, todos):
    """Para `effect` em `write` ou `destroy`: passa se `reversible.inverse` é um mapa não vazio
    **ou** `reversible.irreversible.reason` é texto não vazio (depois de `strip()`). Senão, um achado
    em `$.reversible`. `read` nunca recebe R2. Seção que não é mapa (`None`, texto, número, lista)
    nunca levanta exceção: use `isinstance(x, dict)` antes de `.get`; `reversible` vazio ou de tipo
    errado é "sem inversa", ou seja, um achado em `$.reversible`."""
    efeito = contrato.get("effect")

    # read nunca recebe R2
    if efeito == "read":
        return []

    # Apenas write e destroy precisam de inversa
    if efeito not in ("write", "destroy"):
        return []

    # Verificar se reversible existe e é um dict
    reversible = contrato.get("reversible")
    if not isinstance(reversible, dict):
        # reversible que não é dict é considerado "sem inversa"
        return [achado("R2", contrato, "$.reversible", "write/destroy sem reversible (deve ser um mapa)")]

    # Se reversible é um dict vazio, também é considerado "sem inversa"
    if not reversible:
        return [achado("R2", contrato, "$.reversible", "write/destroy com reversible vazio")]

    # Verificar se inverse existe e é um mapa não vazio
    inverse = reversible.get("inverse")
    if isinstance(inverse, dict) and inverse:
        # Tem inverse válida
        return []

    # Verificar se irreversible existe e tem reason preenchido
    irreversible = reversible.get("irreversible")
    if isinstance(irreversible, dict):
        reason = irreversible.get("reason")
        if isinstance(reason, str) and reason.strip():
            # Tem reason válido
            return []

    # Se chegou até aqui, não tem nem inverse nem reason válidos
    return [achado("R2", contrato, "$.reversible", "write/destroy sem reversible.inverse nem reversible.irreversible.reason")]