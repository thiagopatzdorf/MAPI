"""R14: `write`/`destroy` com `idempotent: true` sem nenhuma garantia declarada.

Defeito que impede: idempotência declarada e não implementada.
"""
from __future__ import annotations

from . import achado, regra


@regra("R14")
def idempotencia_garantida(contrato, todos):
    """Para `write`/`destroy` com `idempotent: true`: passa se há ao menos uma garantia.
    
    Garantias aceitas:
    (a) alguma propriedade de `input.properties` tem `x-mapi-idempotency-token: true`
    (b) `bindings.http.method` é texto e, em maiúsculas, é PUT ou DELETE
    (c) `x-mapi-natural-key` é lista não vazia de textos e cada um é chave de `input.properties`
    
    Senão, um achado em `$.idempotent`. `read` nunca recebe R14; `idempotent` falso ou ausente: sem achado.
    """
    efeito = contrato.get("effect")
    
    # read nunca recebe R14
    if efeito == "read":
        return []
    
    # Apenas write e destroy podem ter idempotência
    if efeito not in ("write", "destroy"):
        return []
    
    # Verificar se idempotent é true
    idempotent = contrato.get("idempotent")
    if idempotent is not True:  # Se for False, None ou ausente, não aplica a regra
        return []
    
    # Verificar garantia (a): token de idempotência no input
    input_secao = contrato.get("input")
    if isinstance(input_secao, dict):
        properties = input_secao.get("properties")
        if isinstance(properties, dict):
            for prop_value in properties.values():
                if isinstance(prop_value, dict) and prop_value.get("x-mapi-idempotency-token") is True:
                    return []  # Achou token, passa
    
    # Verificar garantia (b): método HTTP PUT ou DELETE
    bindings = contrato.get("bindings")
    if isinstance(bindings, dict):
        http_binding = bindings.get("http")
        if isinstance(http_binding, dict):
            method = http_binding.get("method")
            if isinstance(method, str) and method.upper() in ("PUT", "DELETE"):
                return []  # Achou método idempotente, passa
    
    # Verificar garantia (c): chave natural
    natural_key = contrato.get("x-mapi-natural-key")
    if (isinstance(natural_key, list) and 
        len(natural_key) > 0 and 
        all(isinstance(k, str) for k in natural_key)):
        # Verificar se todas as chaves naturais estão em input.properties
        if isinstance(input_secao, dict):
            properties = input_secao.get("properties")
            if isinstance(properties, dict):
                if all(key in properties for key in natural_key):
                    return []  # Todas as chaves naturais existem, passa
    
    # Se chegou até aqui, não tem garantia
    return [achado("R14", contrato, "$.idempotent", "idempotent: true sem garantia declarada")]