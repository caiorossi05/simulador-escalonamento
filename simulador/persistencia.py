"""Gravacao e recarga de conjuntos de tarefas em JSON.

Um cenario sorteado se perde ao fim da execucao. Gravar o conjunto em uso
permite reexaminar depois qualquer cenario, digitado ou sorteado.
"""

import json
from pathlib import Path

from .modelo import Tarefa, validar


def gravar(tarefas: list[Tarefa], caminho: str | Path) -> None:
    """Grava o conjunto de tarefas no arquivo indicado."""
    conteudo = {
        "versao": 1,
        "tarefas": [tarefa.para_dicionario() for tarefa in tarefas],
    }
    Path(caminho).write_text(
        json.dumps(conteudo, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def carregar(caminho: str | Path) -> list[Tarefa]:
    """Le um conjunto de tarefas gravado. Recusa arquivo invalido."""
    try:
        conteudo = json.loads(Path(caminho).read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ValueError(f"o arquivo nao e um cenario valido: {erro}") from erro

    if not isinstance(conteudo, dict) or "tarefas" not in conteudo:
        raise ValueError("o arquivo nao contem um conjunto de tarefas")

    tarefas = [Tarefa.de_dicionario(dados) for dados in conteudo["tarefas"]]
    if not tarefas:
        raise ValueError("o arquivo nao contem nenhuma tarefa")
    for tarefa in tarefas:
        validar(tarefa)
    return tarefas
