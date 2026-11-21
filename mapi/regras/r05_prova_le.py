"""R5: `proof.read.capability` com `effect != read`.

Defeito que impede: prova que escreve contamina o estado que mede.
"""
from __future__ import annotations

from . import achado, regra


@regra("R5")
def prova_le(contrato, todos):
    """Para `write`/`destroy` com `proof.read.capability` presente: procure em `todos`.
    Se existe e seu `effect` não é `read`, um achado em `$.proof.read.capability`.
    Capacidade que não está em `todos`: sem achado (referência desconhecida é outra regra).
    Seção que não é mapa (`None`, texto, número, lista) nunca levanta exceção: use
    isinstance(x, dict) em `proof` e em `proof.read`; `capability` que não é texto
    também não indexa `todos`. Nesses casos, sem achado de R5 (a R4 é quem reclama
    de prova malformada)."""
    efeito = contrato.get("effect")

    # read nunca recebe R5
    if efeito == "read":
        return []

    # Apenas write e destroy podem ter problemas com R5
    if efeito not in ("write", "destroy"):
        return []

    # Verificar se proof existe e é um dicionário
    proof = contrato.get("proof")
    if not isinstance(proof, dict):
        # Se proof não é um dicionário, não levantamos exceção (R4 cuida disso)
        return []

    # Verificar se proof.read existe e é um dicionário
    read_proof = proof.get("read")
    if not isinstance(read_proof, dict):
        # Se proof.read não é um dicionário, não levantamos exceção (R4 cuida disso)
        return []

    # Verificar se capability existe e é uma string
    capability = read_proof.get("capability")
    if not isinstance(capability, str):
        # Se capability não é uma string, não levantamos exceção (R4 cuida disso)
        return []

    # Se a capability não está em todos, não geramos achado (referência desconhecida é outra regra)
    if capability not in todos:
        return []

    # Verificar se a capacidade referenciada tem effect diferente de read
    capacidade_referenciada = todos[capability]
    efeito_referenciado = capacidade_referenciada.get("effect")
    
    if efeito_referenciado != "read":
        return [achado("R5", contrato, "$.proof.read.capability", 
                      f"capability {capability!r} tem effect {efeito_referenciado!r}, não 'read'")]

    # Se chegou até aqui, está tudo certo
    return []