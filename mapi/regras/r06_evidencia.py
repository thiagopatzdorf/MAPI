"""R6: `destroy` sem `precondition.evidence`.

Defeito que impede: sem evidência, não se sabe como reconstruir após destruir.
"""
from __future__ import annotations

from . import achado, regra


@regra("R6")
def evidencia_obrigatoria(contrato, todos):
    """Para `destroy`: passa se `precondition.evidence` é lista não vazia.
    Senão, um achado em `$.precondition.evidence`. `write` e `read` nunca recebem R6.
    
    Seção que não é mapa (None, texto, número, lista) nunca levanta exceção:
    use isinstance(x, dict) antes de cada .get; o YAML vazio (secao:) vira None.
    """
    efeito = contrato.get("effect")

    # write e read nunca recebem R6
    if efeito != "destroy":
        return []

    # Verificar se precondition existe e é um mapa
    precondition = contrato.get("precondition")
    if precondition is None or not isinstance(precondition, dict):
        return [achado("R6", contrato, "$.precondition.evidence", "destroy sem precondition.evidence")]

    # Verificar se evidence existe e é uma lista não vazia
    evidence = precondition.get("evidence")
    if evidence is None:
        return [achado("R6", contrato, "$.precondition.evidence", "destroy sem precondition.evidence")]
    
    if not isinstance(evidence, list) or len(evidence) == 0:
        return [achado("R6", contrato, "$.precondition.evidence", "precondition.evidence deve ser uma lista não vazia")]

    # Se chegou até aqui, está tudo certo
    return []