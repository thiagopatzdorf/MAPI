"""R4: `write`/`destroy` sem `proof`.

Defeito que impede: sem prova, o cliente não sabe como verificar se a operação funcionou.
"""
from __future__ import annotations

from . import achado, regra


@regra("R4")
def prova_obrigatoria(contrato, todos):
    """Para `write`/`destroy`: passa se `proof` é mapa com `read.capability` (texto não vazio) 
    e `expect` (lista não vazia). Senão, um achado em `$.proof`. `read` nunca recebe R4."""
    efeito = contrato.get("effect")
    
    # read nunca recebe R4
    if efeito == "read":
        return []
    
    # Apenas write e destroy precisam de prova
    if efeito not in ("write", "destroy"):
        return []
    
    # Verificar se proof existe
    proof = contrato.get("proof")
    if proof is None:
        return [achado("R4", contrato, "$.proof", "write/destroy sem proof")]
    
    # Verificar se proof é um mapa
    if not isinstance(proof, dict):
        return [achado("R4", contrato, "$.proof", "proof deve ser um mapa")]
    
    # Verificar se read.capability existe e não está vazio
    read_proof = proof.get("read")
    if read_proof is None:
        return [achado("R4", contrato, "$.proof.read", "proof.read ausente")]
    
    if not isinstance(read_proof, dict):
        return [achado("R4", contrato, "$.proof.read", "proof.read deve ser um mapa")]
    
    capability = read_proof.get("capability")
    if not capability or not isinstance(capability, str) or not capability.strip():
        return [achado("R4", contrato, "$.proof.read.capability", "proof.read.capability ausente ou vazio")]
    
    # Verificar se expect existe e é uma lista não vazia
    expect = proof.get("expect")
    if expect is None:
        return [achado("R4", contrato, "$.proof.expect", "proof.expect ausente")]
    
    if not isinstance(expect, list) or len(expect) == 0:
        return [achado("R4", contrato, "$.proof.expect", "proof.expect deve ser uma lista não vazia")]
    
    # Se chegou até aqui, está tudo certo
    return []