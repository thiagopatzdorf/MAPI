"""R17: `access.callers` com quem não se resolve para uma chave, ou `*` onde muda estado.

Defeito que impede: um nome livre ("admin", "time") não vira chave de ninguém, então a política
parece existir e não protege nada. Cada caller tem de ser uma forma que um binding resolve para
chaves públicas: `@usuario` (as chaves SSH que o GitHub publica, fixadas pelo binding, como o
`git selo add` faz), `group:<nome>` (grupo do registro de identidades do binding), `age1…` ou uma
linha `ssh-ed25519`/`ssh-rsa`. `*` (qualquer um) só vale em `read`.
"""
from __future__ import annotations

import re

from . import achado, regra

FORMAS = (
    re.compile(r"^@[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$"),  # usuário do GitHub
    re.compile(r"^group:[a-z][a-z0-9_-]*$"),
    re.compile(r"^age1[02-9ac-hj-np-z]{58}$"),  # bech32 de 32 bytes
    re.compile(r"^ssh-(ed25519|rsa) [A-Za-z0-9+/]+=*$"),
)
EM_REPOUSO = {"plain", "encrypted"}


@regra("R17")
def quem_se_resolve(contrato, todos):
    """Só olha quando `access` é mapa (ausência e tipo errado são da R16). Um achado por caller
    inválido, em `$.access.callers[i]`; `access.data.at_rest`, se presente, é `plain|encrypted`."""
    if not isinstance(contrato, dict) or not isinstance(contrato.get("access"), dict):
        return []
    acesso, achados = contrato["access"], []
    callers = acesso.get("callers")
    if isinstance(callers, list):
        for i, c in enumerate(callers):
            caminho = f"$.access.callers[{i}]"
            if c == "*":
                if contrato.get("effect") != "read":
                    achados.append(achado("R17", contrato, caminho, "'*' (qualquer um) só vale em read"))
            elif not isinstance(c, str) or not any(f.match(c) for f in FORMAS):
                achados.append(achado("R17", contrato, caminho, f"caller {c!r} não se resolve para chave: use @usuario, group:nome, age1… ou ssh-ed25519/ssh-rsa"))
    dados = acesso.get("data")
    if dados is not None and (not isinstance(dados, dict) or dados.get("at_rest", "plain") not in EM_REPOUSO):
        achados.append(achado("R17", contrato, "$.access.data.at_rest", "access.data.at_rest deve ser plain ou encrypted"))
    return achados
