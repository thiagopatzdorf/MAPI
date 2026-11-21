"""``python -m mapi check <arquivo.yaml>``: exit 0 limpo, exit 2 com a lista de achados em JSON.

``python -m mapi build --mcp <arquivo.yaml>``: confere e imprime o ``tools/list`` em JSON (exit 2 se recusado).
"""
from __future__ import annotations

import json
import sys

from .modelo import carregar
from .regras import checar


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "check":
        achados = checar(carregar(argv[1]))
        if achados:
            print(json.dumps(achados, ensure_ascii=False, indent=2))
            return 2
        return 0
    if len(argv) == 3 and argv[0] == "build" and argv[1] == "--mcp":
        from .emissores.mcp import emitir_todos

        contratos = carregar(argv[2])
        achados = checar(contratos)
        if achados:
            print(json.dumps(achados, ensure_ascii=False, indent=2))
            return 2
        print(json.dumps({"tools": emitir_todos(contratos)}, ensure_ascii=False, indent=2))
        return 0
    print("uso: python -m mapi check <arquivo.yaml> | python -m mapi build --mcp <arquivo.yaml>", file=sys.stderr)
    return 64


def _cli() -> None:
    """Ponto de entrada do comando `mapi` instalado pelo pip (pyproject.toml)."""
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    _cli()
