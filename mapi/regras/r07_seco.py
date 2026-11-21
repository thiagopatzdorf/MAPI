"""R7: `write`/`destroy` com `consent.dry_run != default`.

Defeito que impede: seco por padrão é a regra, não opção.
"""
from __future__ import annotations

from . import achado, regra


@regra("R7")
def seco_por_padrao(contrato, todos):
    """Para `write`/`destroy`: passa se `consent.dry_run == "default"`. Ausente, `supported`, 
    `none` ou qualquer outro valor: um achado em `$.consent.dry_run`. `read` nunca recebe R7.
    
    Seção que não é mapa (`None`, texto, número, lista) nunca levanta exceção: use 
    `isinstance(x, dict)` antes de cada `.get`; o YAML vazio (`secao:`) vira `None`."""
    efeito = contrato.get("effect")

    # read nunca recebe R7
    if efeito == "read":
        return []

    # Apenas write e destroy precisam ser secos por padrão
    if efeito not in ("write", "destroy"):
        return []

    # Verificar se consent existe e é um mapa
    consent = contrato.get("consent")
    if consent is None:
        return [achado("R7", contrato, "$.consent", "write/destroy sem consent")]
    
    if not isinstance(consent, dict):
        return [achado("R7", contrato, "$.consent", "consent deve ser um mapa")]

    # Verificar dry_run
    dry_run = consent.get("dry_run")
    
    # Se dry_run é "default", está tudo certo
    if dry_run == "default":
        return []

    # Qualquer outro valor (ausente, supported, none, etc) gera um achado
    return [achado("R7", contrato, "$.consent.dry_run", f"dry_run deve ser 'default', não {dry_run!r}")]