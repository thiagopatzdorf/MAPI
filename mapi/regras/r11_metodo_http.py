"""R11: `bindings.http.method` incompatível com `effect`.

Defeito que impede: método HTTP mentindo sobre o efeito (ex.: `read` com POST sem override).
"""
from __future__ import annotations

from . import achado, regra


@regra("R11")
def metodo_http_compativel(contrato, todos):
    """Verifica se `bindings.http.method` é compatível com `effect`.
    
    Regra: Só se `bindings.http.method` existir e for texto (compare em maiúsculas).
    `read`: GET, HEAD ou QUERY; POST só se `bindings.http["x-mapi-method-override"]` for `true`.
    `write`: POST, PUT ou PATCH.
    `destroy`: DELETE ou POST.
    Fora disso, um achado em `$.bindings.http.method`.
    Sem binding http, sem achado.
    """
    # Verificar se há bindings.http
    bindings = contrato.get("bindings")
    if not isinstance(bindings, dict):
        return []
    
    http = bindings.get("http")
    if not isinstance(http, dict):
        return []
    
    method = http.get("method")
    if not isinstance(method, str):
        return []
    
    # Converter para maiúsculas para comparação
    method_upper = method.upper()
    effect = contrato.get("effect")
    
    # Verificar compatibilidade com base no efeito
    if effect == "read":
        # read: GET, HEAD ou QUERY; POST só se x-mapi-method-override for true
        if method_upper in ("GET", "HEAD", "QUERY"):
            return []
        elif method_upper == "POST":
            # Verificar se x-mapi-method-override é true
            x_mapi_override = http.get("x-mapi-method-override")
            if x_mapi_override is True:
                return []
            else:
                return [achado("R11", contrato, "$.bindings.http.method", 
                              "read com POST sem x-mapi-method-override=true")]
        else:
            return [achado("R11", contrato, "$.bindings.http.method", 
                          f"read com método HTTP incompatível: {method}")]
    
    elif effect == "write":
        # write: POST, PUT ou PATCH
        if method_upper in ("POST", "PUT", "PATCH"):
            return []
        else:
            return [achado("R11", contrato, "$.bindings.http.method", 
                          f"write com método HTTP incompatível: {method}")]
    
    elif effect == "destroy":
        # destroy: DELETE ou POST
        if method_upper in ("DELETE", "POST"):
            return []
        else:
            return [achado("R11", contrato, "$.bindings.http.method", 
                          f"destroy com método HTTP incompatível: {method}")]
    
    # Se não for nenhum dos efeitos conhecidos, não aplicar a regra
    return []