"""R3: `inverse.capability` inexistente no conjunto compilado, ou com `effect: read`, ou igual à própria sem `idempotent: true` **e** sem `inverse.captures_state_before: true`.

Defeito que impede: inversa que não escreve não desfaz nada; a própria capacidade só serve de
inversa se repetir converge (idempotente) ou se restaura um estado absoluto capturado antes.
"""
from __future__ import annotations

from . import achado, regra


@regra("R3")
def inversa_valida(contrato, todos):
    """Para `write`/`destroy` com `reversible.inverse` mapa e `inverse.capability` texto;
    procure em `todos`. Um achado em `$.reversible.inverse.capability` se: (a) não existe;
    (b) tem `effect == read`; (c) é a própria `capability` do contrato e o contrato não tem
    `idempotent: true` nem `inverse.captures_state_before: true`. Senão, sem achado.
    `reversible` ausente ou que não é mapa: sem achado (a R2 cuida)."""
    efeito = contrato.get("effect")

    # Apenas write e destroy podem ter R3
    if efeito not in ("write", "destroy"):
        return []

    # Verificar se reversible existe e é um dict
    reversible = contrato.get("reversible")
    if not isinstance(reversible, dict):
        # reversible que não é dict não gera R3 (R2 cuida disso)
        return []

    # Verificar se inverse existe e é um dict
    inverse = reversible.get("inverse")
    if not isinstance(inverse, dict):
        # inverse que não é dict não gera R3 (R2 cuida disso)
        return []

    # Verificar se capability existe e é string
    capability = inverse.get("capability")
    if not isinstance(capability, str):
        # capability que não é string não gera R3 (R2 cuida disso)
        return []

    # Procurar a capacidade inversa em todos
    inversa = todos.get(capability)
    
    # (a) capability não existe em todos
    if inversa is None:
        return [achado("R3", contrato, "$.reversible.inverse.capability", f"capability '{capability}' não existe no conjunto compilado")]

    # (b) capability tem effect == read
    if inversa.get("effect") == "read":
        return [achado("R3", contrato, "$.reversible.inverse.capability", f"capability '{capability}' tem effect=read, não pode ser inversa de write/destroy")]

    # (c) é a própria capability do contrato e o contrato não tem idempotent: true nem inverse.captures_state_before: true
    if capability == contrato.get("capability"):
        idempotent = contrato.get("idempotent") is True
        captures_state_before = inverse.get("captures_state_before") is True
        
        if not idempotent and not captures_state_before:
            return [achado("R3", contrato, "$.reversible.inverse.capability", f"capability '{capability}' é a própria e contrato não tem idempotent: true nem inverse.captures_state_before: true")]

    # Se chegou até aqui, está tudo certo
    return []