"""Motor de simulacao: o mecanismo comum a todos os algoritmos.

O motor avanca o relogio, monta o conjunto de tarefas prontas, cobra a troca de
contexto, controla o recurso de uso exclusivo e aplica os protocolos de correcao
de prioridade. A escolha de qual tarefa recebe o processador cabe a politica,
em politicas.py.

Convencoes adotadas (secao 3 do enunciado):
  C1  o tempo e discreto e avanca de uma em uma unidade;
  C2  valor maior de prioridade significa prioridade mais alta;
  C3  desempate por menor ingresso e depois por menor identificador;
  C4  ha troca de contexto sempre que a tarefa despachada difere da ultima que
      ocupou o processador, inclusive no primeiro despacho;
  C5  o custo da troca e descontado da fatia concedida, nunca somado a ela;
  C6  a tarefa que esgota o quantum volta a cauda da fila depois das que
      ingressaram naquele mesmo instante;
  C7  a secao critica e medida no tempo de execucao propria da tarefa;
  C8  tw = tt - tp;
  C9  o teto e calculado sobre as tarefas que declaram secao critica; heranca e
      teto sao alternativos e nao se combinam;
  C10 o envelhecimento conta desde o ultimo despacho, ou desde o ingresso caso a
      tarefa ainda nao tenha executado.
"""

from dataclasses import dataclass, field

from .modelo import Tarefa
from .politicas import ALGORITMOS, Algoritmo

OCIOSO = "ocioso"
TROCA = "troca"

PROTOCOLOS = ("nenhum", "heranca", "teto")


@dataclass
class Resultado:
    """O que uma simulacao produz."""

    tarefas: list[Tarefa]
    linha_do_tempo: list[tuple[int, str | int]] = field(default_factory=list)
    suspensas_por_instante: dict[int, set[int]] = field(default_factory=dict)
    trocas: int = 0
    sigla: str = ""
    quantum: int | None = None
    custo_troca: int = 0

    @property
    def duracao(self) -> int:
        return max((t.conclusao for t in self.tarefas if t.concluida), default=0)

    @property
    def eficiencia(self) -> float | None:
        """E = tq / (tq + ttc). So existe sob Round-Robin."""
        if self.sigla != "RR" or self.quantum is None:
            return None
        return self.quantum / (self.quantum + self.custo_troca)


class Motor:
    """Executa um conjunto de tarefas sob uma politica e uma configuracao."""

    LIMITE_DE_PASSOS = 1_000_000

    def __init__(
        self,
        tarefas: list[Tarefa],
        sigla: str,
        quantum: int | None = None,
        custo_troca: int = 0,
        protocolo: str = "nenhum",
        alfa: int = 0,
    ):
        if sigla not in ALGORITMOS:
            raise ValueError(f"algoritmo desconhecido: {sigla}")
        if protocolo not in PROTOCOLOS:
            raise ValueError(f"protocolo desconhecido: {protocolo}")
        if custo_troca < 0:
            raise ValueError("o custo da troca de contexto nao pode ser negativo")

        self.algoritmo: Algoritmo = ALGORITMOS[sigla]
        if self.algoritmo.usa_quantum:
            if quantum is None:
                raise ValueError("o Round-Robin exige um quantum")
            if quantum <= custo_troca:
                raise ValueError(
                    "o quantum precisa ser maior que o custo da troca de contexto: "
                    f"com quantum {quantum} e custo {custo_troca} nenhum trabalho util seria feito"
                )

        self.tarefas = [t.copia_limpa() for t in tarefas]
        for tarefa in self.tarefas:
            tarefa.reiniciar()
        self.quantum = quantum
        self.custo_troca = custo_troca
        self.protocolo = protocolo
        self.alfa = alfa

        # C9: o teto vale a maior prioridade entre as tarefas que declaram R.
        candidatas = [t.prioridade for t in self.tarefas if t.uso_de_r]
        self.teto = max(candidatas) if candidatas else 0

        self._fila: list[Tarefa] = []
        self._linha: list[tuple[int, str | int]] = []
        self._suspensas: dict[int, set[int]] = {}
        self._trocas = 0

    # ------------------------------------------------------------------ estado

    def _detentor(self) -> Tarefa | None:
        for tarefa in self.tarefas:
            if tarefa.detem_r:
                return tarefa
        return None

    def _prontas(self, t: int) -> list[Tarefa]:
        """Tarefas que ja ingressaram, nao concluiram e nao estao suspensas."""
        return [
            tarefa
            for tarefa in self.tarefas
            if tarefa.ingresso <= t and not tarefa.concluida and not tarefa.suspensa
        ]

    def _atualizar_fila(self, t: int, exceto: Tarefa | None = None) -> None:
        """Insere na fila circular as tarefas que ja podem concorrer.

        A insercao respeita a ordem de ingresso e, dentro do mesmo instante, a
        ordem de identificador. Chamar este metodo antes de devolver a tarefa
        preemptada a cauda realiza a convencao C6: ela entra depois das que
        ingressaram naquele mesmo instante. O parametro exceto mantem a tarefa
        que esta sendo devolvida fora desta insercao, para que ela nao entre
        duas vezes.
        """
        novas = [
            tarefa
            for tarefa in self.tarefas
            if tarefa.ingresso <= t
            and not tarefa.concluida
            and not tarefa.suspensa
            and tarefa is not exceto
            and tarefa not in self._fila
        ]
        novas.sort(key=lambda tarefa: (tarefa.ingresso, tarefa.id))
        self._fila.extend(novas)

    def _atualizar_prioridades(self, t: int, prontas: list[Tarefa]) -> None:
        """Recalcula a prioridade efetiva sob envelhecimento, heranca e teto."""
        for tarefa in self.tarefas:
            efetiva = tarefa.prioridade
            if self.alfa > 0 and tarefa in prontas:
                # C10: conta desde o ultimo despacho, ou desde o ingresso.
                referencia = (
                    tarefa.ultimo_despacho
                    if tarefa.ultimo_despacho is not None
                    else tarefa.ingresso
                )
                efetiva += self.alfa * (t - referencia)
            tarefa.prioridade_efetiva = efetiva

        detentor = self._detentor()
        if detentor is None or self.protocolo == "nenhum":
            return

        if self.protocolo == "teto":
            # Age na obtencao do recurso, independentemente de haver conflito.
            detentor.prioridade_efetiva = max(detentor.prioridade_efetiva, self.teto)
        elif self.protocolo == "heranca":
            # Age apenas quando a disputa aparece.
            bloqueadas = [t_ for t_ in self.tarefas if t_.suspensa]
            if bloqueadas:
                detentor.prioridade_efetiva = max(
                    [detentor.prioridade_efetiva]
                    + [b.prioridade_efetiva for b in bloqueadas]
                )

    def _registrar_suspensas(self, instante: int) -> None:
        """Guarda quais tarefas estao suspensas a espera de R neste instante.

        O diagrama de tempo usa este registro para distinguir a tarefa que
        apenas aguarda na fila de prontas daquela que esta bloqueada no recurso.
        """
        bloqueadas = {t.id for t in self.tarefas if t.suspensa}
        if bloqueadas:
            self._suspensas[instante] = bloqueadas

    def _liberar_recurso(self, tarefa: Tarefa) -> None:
        tarefa.detem_r = False
        tarefa.liberou_r = True
        for outra in self.tarefas:
            if outra.suspensa:
                outra.suspensa = False

    # ---------------------------------------------------------------- simulacao

    def simular(self) -> Resultado:
        t = 0
        ultima_despachada: Tarefa | None = None
        passos = 0

        while any(not tarefa.concluida for tarefa in self.tarefas):
            passos += 1
            if passos > self.LIMITE_DE_PASSOS:
                raise RuntimeError("a simulacao nao termina: verifique o conjunto de tarefas")

            self._atualizar_fila(t)
            prontas = self._prontas(t)

            if not prontas:
                # Relogio ocioso: salta para o proximo instante de ingresso.
                futuros = [
                    tarefa.ingresso
                    for tarefa in self.tarefas
                    if not tarefa.concluida and tarefa.ingresso > t
                ]
                if not futuros:
                    raise RuntimeError("todas as tarefas restantes estao suspensas")
                proximo = min(futuros)
                for instante in range(t, proximo):
                    self._linha.append((instante, OCIOSO))
                t = proximo
                continue

            self._atualizar_prioridades(t, prontas)
            escolhida = self.algoritmo.escolher(prontas, self._fila)

            # C4: ha troca sempre que a tarefa difere da ultima, inclusive na primeira.
            houve_troca = escolhida is not ultima_despachada
            if houve_troca:
                self._trocas += 1
                for instante in range(t, t + self.custo_troca):
                    self._registrar_suspensas(instante)
                    self._linha.append((instante, TROCA))
                t += self.custo_troca

            ultima_despachada = escolhida
            escolhida.ultimo_despacho = t
            if escolhida.primeira_exec is None:
                escolhida.primeira_exec = t

            # C5: o custo saiu de dentro da fatia, nao foi somado a ela.
            if self.algoritmo.usa_quantum:
                orcamento = self.quantum - (self.custo_troca if houve_troca else 0)
            else:
                orcamento = None

            t, ultima_despachada = self._despachar(t, escolhida, orcamento, ultima_despachada)

        return Resultado(
            tarefas=self.tarefas,
            linha_do_tempo=self._linha,
            suspensas_por_instante=self._suspensas,
            trocas=self._trocas,
            sigla=self.algoritmo.sigla,
            quantum=self.quantum,
            custo_troca=self.custo_troca,
        )

    def _despachar(
        self,
        t: int,
        escolhida: Tarefa,
        orcamento: int | None,
        ultima_despachada: Tarefa,
    ) -> tuple[int, Tarefa | None]:
        """Executa a tarefa escolhida ate que ela perca o processador.

        A tarefa perde o processador ao concluir, ao esgotar o quantum, ao ficar
        suspensa a espera do recurso, ou ao ser preemptada por outra de melhor
        criterio nos algoritmos preemptivos sem quantum.
        """
        util = 0

        while True:
            # Aquisicao do recurso, verificada antes de executar a proxima unidade.
            if (
                escolhida.uso_de_r
                and not escolhida.detem_r
                and not escolhida.liberou_r
                and escolhida.executado == escolhida.inicio_secao_critica
            ):
                detentor = self._detentor()
                if detentor is None:
                    escolhida.detem_r = True
                else:
                    # Sai do conjunto de prontas e da fila circular.
                    escolhida.suspensa = True
                    if escolhida in self._fila:
                        self._fila.remove(escolhida)
                    return t, ultima_despachada

            if orcamento is not None and util >= orcamento:
                # Esgotou o quantum: volta a cauda depois dos que ingressaram agora.
                if escolhida in self._fila:
                    self._fila.remove(escolhida)
                self._atualizar_fila(t, exceto=escolhida)
                self._fila.append(escolhida)
                return t, ultima_despachada

            self._registrar_suspensas(t)
            self._linha.append((t, escolhida.id))
            t += 1
            util += 1
            escolhida.executado += 1

            if escolhida.detem_r and escolhida.executado == escolhida.fim_secao_critica:
                self._liberar_recurso(escolhida)

            if escolhida.executado == escolhida.tp:
                escolhida.conclusao = t
                if escolhida.detem_r:
                    self._liberar_recurso(escolhida)
                if escolhida in self._fila:
                    self._fila.remove(escolhida)
                return t, ultima_despachada

            if self.algoritmo.preemptivo and not self.algoritmo.usa_quantum:
                self._atualizar_fila(t)
                prontas = self._prontas(t)
                self._atualizar_prioridades(t, prontas)
                melhor = self.algoritmo.escolher(prontas, self._fila)
                if melhor is not escolhida:
                    return t, ultima_despachada


def simular(
    tarefas: list[Tarefa],
    sigla: str,
    quantum: int | None = None,
    custo_troca: int = 0,
    protocolo: str = "nenhum",
    alfa: int = 0,
) -> Resultado:
    """Atalho para uma simulacao unica."""
    return Motor(tarefas, sigla, quantum, custo_troca, protocolo, alfa).simular()
