"""As seis politicas de escalonamento.

Uma politica recebe o conjunto de tarefas prontas e devolve a tarefa escolhida.
Ela nao conhece o relogio, o custo da troca de contexto nem o recurso: essas
sao responsabilidades do motor. O desempate segue a convencao C3, menor
instante de ingresso e depois menor identificador.
"""

from dataclasses import dataclass
from typing import Callable

from .modelo import Tarefa


def _desempate(tarefa: Tarefa) -> tuple:
    return (tarefa.ingresso, tarefa.id)


def fcfs(prontas: list[Tarefa], fila: list[Tarefa]) -> Tarefa:
    """Menor instante de ingresso."""
    return min(prontas, key=lambda t: (t.ingresso, t.id))


def sjf(prontas: list[Tarefa], fila: list[Tarefa]) -> Tarefa:
    """Menor tempo de processamento total."""
    return min(prontas, key=lambda t: (t.tp,) + _desempate(t))


def srtf(prontas: list[Tarefa], fila: list[Tarefa]) -> Tarefa:
    """Menor tempo de processamento restante."""
    return min(prontas, key=lambda t: (t.restante,) + _desempate(t))


def round_robin(prontas: list[Tarefa], fila: list[Tarefa]) -> Tarefa:
    """Primeiro da fila circular mantida pelo motor."""
    for tarefa in fila:
        if tarefa in prontas:
            return tarefa
    return min(prontas, key=_desempate)


def prioridade(prontas: list[Tarefa], fila: list[Tarefa]) -> Tarefa:
    """Maior prioridade efetiva."""
    return min(prontas, key=lambda t: (-t.prioridade_efetiva,) + _desempate(t))


@dataclass(frozen=True)
class Algoritmo:
    """Descreve uma politica e as propriedades que o motor precisa conhecer."""

    sigla: str
    nome: str
    escolher: Callable[[list[Tarefa], list[Tarefa]], Tarefa]
    preemptivo: bool
    usa_quantum: bool
    usa_prioridade: bool


ALGORITMOS: dict[str, Algoritmo] = {
    "FCFS": Algoritmo("FCFS", "First-Come, First-Served", fcfs, False, False, False),
    "SJF": Algoritmo("SJF", "Shortest Job First", sjf, False, False, False),
    "SRTF": Algoritmo("SRTF", "Shortest Remaining Time First", srtf, True, False, False),
    "RR": Algoritmo("RR", "Round-Robin", round_robin, True, True, False),
    "PRIOc": Algoritmo("PRIOc", "Prioridade cooperativa", prioridade, False, False, True),
    "PRIOp": Algoritmo("PRIOp", "Prioridade preemptiva", prioridade, True, False, True),
}

SIGLAS = list(ALGORITMOS.keys())
