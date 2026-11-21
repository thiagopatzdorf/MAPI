"""R9: `budget.max_output_bytes` ausente.

Defeito que impede: saída sem teto estoura a janela do modelo (medido: worker lendo arquivo inteiro).
"""
from __future__ import annotations

from . import achado, regra


@regra("R9")
def saida_com_teto(contrato, todos):
    """Para qualquer `effect`: passa se `budget.max_output_bytes` é inteiro maior que zero
    (`bool` não conta como inteiro). Senão, um achado em `$.budget.max_output_bytes`.
    
    Seção que não é mapa (`None`, texto, número, lista) nunca levanta exceção: use `isinstance(x, dict)`
    antes de cada `.get`; o YAML vazio (`secao:`) vira `None`.
    """
    # Verificar se budget existe e é um dicionário
    budget = contrato.get("budget")
    if budget is None:
        return [achado("R9", contrato, "$.budget.max_output_bytes", "budget ausente")]
    
    if not isinstance(budget, dict):
        # Se budget não é um dicionário, não podemos acessar max_output_bytes
        return [achado("R9", contrato, "$.budget.max_output_bytes", "budget.max_output_bytes ausente")]
    
    # Verificar se max_output_bytes existe
    max_output_bytes = budget.get("max_output_bytes")
    if max_output_bytes is None:
        return [achado("R9", contrato, "$.budget.max_output_bytes", "budget.max_output_bytes ausente")]
    
    # Verificar se max_output_bytes é inteiro maior que zero (bool não conta como inteiro)
    if not isinstance(max_output_bytes, int) or isinstance(max_output_bytes, bool) or max_output_bytes <= 0:
        return [achado("R9", contrato, "$.budget.max_output_bytes", "budget.max_output_bytes deve ser inteiro maior que zero")]
    
    # Se chegou até aqui, está tudo certo
    return []