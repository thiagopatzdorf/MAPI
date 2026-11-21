"""Carrega contratos MAPI (YAML, vários documentos por arquivo)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def carregar_texto(texto: str) -> list[dict[str, Any]]:
    """Cada documento YAML não vazio vira um contrato. Documento que não é mapa é erro,
    porque um contrato que parece lista seria ignorado em silêncio pelas regras."""
    contratos = []
    for doc in yaml.safe_load_all(texto):
        if doc is None:
            continue
        if not isinstance(doc, dict):
            raise ValueError(f"contrato precisa ser um mapa, veio {type(doc).__name__}")
        contratos.append(doc)
    return contratos


def carregar(caminho: str | Path) -> list[dict[str, Any]]:
    return carregar_texto(Path(caminho).read_text(encoding="utf-8"))
