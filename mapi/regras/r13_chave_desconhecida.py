"""R13: chave de topo desconhecida sem prefixo `x-`.

Defeito que impede: erro de digitação não vira campo ignorado em silêncio.
"""
from __future__ import annotations

from . import achado, regra

CHAVES_PERMITIDAS = {
    "mapi", "capability", "version", "title", "when_to_use", "when_not_to_use",
    "effect", "idempotent", "open_world", "input", "output", "consent",
    "reversible", "precondition", "proof", "budget", "bindings", "examples", "access"
}


@regra("R13")
def chave_desconhecida(contrato, todos):
    """Chaves de topo permitidas: mapi, capability, version, title, when_to_use, when_not_to_use,
    effect, idempotent, open_world, input, output, consent, reversible, precondition, proof,
    budget, bindings, examples, access, mais qualquer uma que comece com `x-`. Cada chave fora disso:
    um achado em `$.<chave>`. Chave que não é texto (o YAML aceita número) também conta como
    desconhecida, sem exceção. Seção que não é mapa (`None`, texto, número, lista) nunca levanta
    exceção: use isinstance(x, dict) antes de cada .get; o YAML vazio (`secao:`) vira `None`."""
    
    # Se contrato não é um dicionário, não há chaves para verificar
    if not isinstance(contrato, dict):
        return []
    
    achados = []
    
    # Verificar cada chave no contrato
    for chave, valor in contrato.items():
        # Se a chave não é uma string, é desconhecida
        if not isinstance(chave, str):
            achados.append(achado("R13", contrato, f"$.{chave!r}", f"chave não é texto: {chave!r}"))
            continue
            
        # Se a chave é permitida ou começa com x-, está ok
        if chave in CHAVES_PERMITIDAS or chave.startswith("x-"):
            continue
            
        # Chave desconhecida sem prefixo x-
        achados.append(achado("R13", contrato, f"$.{chave}", f"chave desconhecida: {chave!r}"))
    
    return achados