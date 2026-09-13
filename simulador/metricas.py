"""Calculo das metricas, por tarefa e em media.

  tt  tempo de execucao      = conclusao - ingresso
  tp  tempo de processamento = dado de entrada
  tw  tempo de espera        = tt - tp                        (convencao C8)
  t1  tempo ate a primeira execucao = primeira_exec - ingresso
"""

from dataclasses import dataclass

from .motor import Resultado


@dataclass
class LinhaDeMetricas:
    id: int
    ingresso: int
    tp: int
    prioridade: int
    conclusao: int
    tt: int
    tw: int
    primeira: int


@dataclass
class Metricas:
    linhas: list[LinhaDeMetricas]
    tt_medio: float
    tw_medio: float
    primeira_media: float
    trocas: int
    eficiencia: float | None

    def resumo(self) -> str:
        eficiencia = (
            f"{self.eficiencia:.3f}" if self.eficiencia is not None else "nao definida"
        )
        return (
            f"Tt={self.tt_medio:.2f}  Tw={self.tw_medio:.2f}  "
            f"1a exec={self.primeira_media:.2f}  trocas={self.trocas}  E={eficiencia}"
        )


def calcular(resultado: Resultado) -> Metricas:
    linhas = []
    for tarefa in sorted(resultado.tarefas, key=lambda t: t.id):
        tt = tarefa.conclusao - tarefa.ingresso
        tw = tt - tarefa.tp
        primeira = tarefa.primeira_exec - tarefa.ingresso
        linhas.append(
            LinhaDeMetricas(
                id=tarefa.id,
                ingresso=tarefa.ingresso,
                tp=tarefa.tp,
                prioridade=tarefa.prioridade,
                conclusao=tarefa.conclusao,
                tt=tt,
                tw=tw,
                primeira=primeira,
            )
        )

    quantidade = len(linhas) or 1
    return Metricas(
        linhas=linhas,
        tt_medio=sum(l.tt for l in linhas) / quantidade,
        tw_medio=sum(l.tw for l in linhas) / quantidade,
        primeira_media=sum(l.primeira for l in linhas) / quantidade,
        trocas=resultado.trocas,
        eficiencia=resultado.eficiencia,
    )


def sequencia_de_execucao(resultado: Resultado) -> str:
    """Devolve a sequencia no formato t1[0,5) t4[5,8) ..., ignorando trocas."""
    blocos: list[tuple[int, int, int]] = []
    for instante, rotulo in resultado.linha_do_tempo:
        if not isinstance(rotulo, int):
            continue
        if blocos and blocos[-1][2] == rotulo and blocos[-1][1] == instante:
            inicio, _, ident = blocos[-1]
            blocos[-1] = (inicio, instante + 1, ident)
        else:
            blocos.append((instante, instante + 1, rotulo))
    return " ".join(f"t{ident}[{inicio},{fim})" for inicio, fim, ident in blocos)
