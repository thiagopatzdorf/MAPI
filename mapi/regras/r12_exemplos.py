"""R12: `examples` vazio.

Defeito que impede: sem exemplo, não há caso de conformidade; sem caso, "MAPI" é só um rótulo.
"""
from __future__ import annotations

from . import achado, regra


@regra("R12")
def exemplos_obrigatorios(contrato, todos):
    """Para qualquer `effect`: passa se `examples` é lista não vazia. Ausente, vazio ou que não é lista:
    um achado em `$.examples`. Seção que não é mapa (`None`, texto, número, lista) nunca levanta exceção:
    use `isinstance(x, dict)` antes de cada `.get`; o YAML vazio (`secao:`) vira `None`."""
    
    # Para qualquer effect, examples é obrigatório
    examples = contrato.get("examples")
    
    # Se examples está ausente, é uma lista vazia ou não é uma lista, recusar
    if examples is None or not isinstance(examples, list) or len(examples) == 0:
        return [achado("R12", contrato, "$.examples", "examples ausente, vazio ou não é uma lista")]
    
    # Se chegou até aqui, está tudo certo
    return []