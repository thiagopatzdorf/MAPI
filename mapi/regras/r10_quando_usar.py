"""R10: `when_to_use` vazio ou com mais de 300 caracteres.

Defeito que impede: descrição vaga ou muito longa para o construtor de GPT.
"""
from __future__ import annotations

from . import achado, regra


@regra("R10")
def when_to_use_valido(contrato, todos):
    """Para qualquer effect: passa se when_to_use é texto cujo strip() tem de 1 a 300 caracteres.
    Ausente, vazio, que não é texto ou maior: um achado em $.when_to_use."""
    # Para qualquer effect
    when_to_use = contrato.get("when_to_use")
    
    # Se for None (YAML vazio: secao:) ou ausente
    if when_to_use is None:
        return [achado("R10", contrato, "$.when_to_use", "when_to_use ausente")]
    
    # Se não for texto
    if not isinstance(when_to_use, str):
        return [achado("R10", contrato, "$.when_to_use", f"when_to_use deve ser texto, encontrado {type(when_to_use).__name__}")]
    
    # Verificar tamanho do texto após strip()
    stripped = when_to_use.strip()
    length = len(stripped)
    
    # Se estiver vazio após strip
    if length == 0:
        return [achado("R10", contrato, "$.when_to_use", "when_to_use vazio ou só com espaços")]
    
    # Se for maior que 300 caracteres
    if length > 300:
        return [achado("R10", contrato, "$.when_to_use", f"when_to_use com {length} caracteres, máximo é 300")]
    
    # Se chegou até aqui, está tudo certo
    return []