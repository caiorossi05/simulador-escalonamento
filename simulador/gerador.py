"""Sorteio de conjuntos de tarefas e comparacao dos algoritmos em lote."""

import random

from .metricas import calcular
from .modelo import Tarefa
from .motor import simular
from .politicas import SIGLAS


def sortear(
    quantidade: int,
    ingresso_maximo: int = 8,
    duracao_maxima: int = 6,
    prioridade_maxima: int = 5,
    com_recurso: bool = False,
) -> list[Tarefa]:
    """Sorteia um conjunto de tarefas dentro das faixas informadas."""
    if quantidade <= 0:
        raise ValueError("a quantidade de tarefas deve ser positiva")

    tarefas = []
    for identificador in range(1, quantidade + 1):
        duracao = random.randint(1, duracao_maxima)
        uso_de_r = None
        if com_recurso and duracao >= 2 and random.random() < 0.5:
            inicio = random.randint(0, duracao - 2)
            fim = random.randint(inicio + 1, duracao)
            uso_de_r = (inicio, fim - inicio)
        tarefas.append(
            Tarefa(
                id=identificador,
                ingresso=random.randint(0, ingresso_maximo),
                tp=duracao,
                prioridade=random.randint(1, prioridade_maxima),
                uso_de_r=uso_de_r,
            )
        )
    return tarefas


def comparar_em_lote(
    cenarios: int = 50,
    tarefas_por_cenario: int = 5,
    quantum: int = 2,
    custo_troca: int = 0,
    ingresso_maximo: int = 8,
    duracao_maxima: int = 6,
    prioridade_maxima: int = 5,
) -> dict[str, dict[str, float]]:
    """Sorteia um lote de cenarios e devolve as medias de cada algoritmo.

    Os valores absolutos mudam a cada execucao. O que se mantem e a ordenacao:
    o SRTF apresenta o menor Tw e o Round-Robin o menor tempo medio ate a
    primeira execucao.
    """
    acumulado = {sigla: {"tt": 0.0, "tw": 0.0, "primeira": 0.0} for sigla in SIGLAS}

    for _ in range(cenarios):
        conjunto = sortear(
            tarefas_por_cenario, ingresso_maximo, duracao_maxima, prioridade_maxima
        )
        for sigla in SIGLAS:
            metricas = calcular(
                simular(conjunto, sigla, quantum=quantum, custo_troca=custo_troca)
            )
            acumulado[sigla]["tt"] += metricas.tt_medio
            acumulado[sigla]["tw"] += metricas.tw_medio
            acumulado[sigla]["primeira"] += metricas.primeira_media

    return {
        sigla: {chave: valor / cenarios for chave, valor in medidas.items()}
        for sigla, medidas in acumulado.items()
    }
