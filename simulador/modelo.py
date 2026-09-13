"""Estrutura de uma tarefa e do seu estado durante a simulacao."""

from dataclasses import dataclass, field


@dataclass
class Tarefa:
    """Descreve uma tarefa e guarda o seu estado ao longo da simulacao.

    Campos de definicao (informados por quem executa o simulador):
        id          identificador da tarefa
        ingresso    instante em que a tarefa surge
        tp          tempo de processamento demandado
        prioridade  valor base; maior valor significa prioridade mais alta
        uso_de_r    (inicio, duracao) da secao critica, medida no tempo de
                    execucao propria da tarefa, ou None se ela nao usa R

    Campos de estado (mantidos pelo motor):
        executado       unidades uteis ja processadas
        conclusao       instante em que a tarefa terminou
        primeira_exec   instante do primeiro despacho efetivo
        suspensa        True enquanto espera o recurso R
        detem_r         True enquanto mantem o recurso R
        liberou_r       True depois de devolver R (nao o pede outra vez)
        ultimo_despacho instante do ultimo despacho, base do envelhecimento
        prioridade_efetiva  prioridade apos envelhecimento, heranca ou teto
    """

    id: int
    ingresso: int
    tp: int
    prioridade: int
    uso_de_r: tuple | None = None

    executado: int = field(default=0, compare=False)
    conclusao: int | None = field(default=None, compare=False)
    primeira_exec: int | None = field(default=None, compare=False)
    suspensa: bool = field(default=False, compare=False)
    detem_r: bool = field(default=False, compare=False)
    liberou_r: bool = field(default=False, compare=False)
    ultimo_despacho: int | None = field(default=None, compare=False)
    prioridade_efetiva: int = field(default=0, compare=False)

    def reiniciar(self) -> None:
        """Devolve a tarefa ao estado anterior a qualquer simulacao."""
        self.executado = 0
        self.conclusao = None
        self.primeira_exec = None
        self.suspensa = False
        self.detem_r = False
        self.liberou_r = False
        self.ultimo_despacho = None
        self.prioridade_efetiva = self.prioridade

    @property
    def restante(self) -> int:
        """Tempo de processamento ainda nao executado."""
        return self.tp - self.executado

    @property
    def concluida(self) -> bool:
        return self.conclusao is not None

    @property
    def inicio_secao_critica(self) -> int | None:
        return self.uso_de_r[0] if self.uso_de_r else None

    @property
    def fim_secao_critica(self) -> int | None:
        return self.uso_de_r[0] + self.uso_de_r[1] if self.uso_de_r else None

    def copia_limpa(self) -> "Tarefa":
        """Nova tarefa com os mesmos dados de definicao e estado zerado."""
        return Tarefa(
            id=self.id,
            ingresso=self.ingresso,
            tp=self.tp,
            prioridade=self.prioridade,
            uso_de_r=tuple(self.uso_de_r) if self.uso_de_r else None,
        )

    def para_dicionario(self) -> dict:
        return {
            "id": self.id,
            "ingresso": self.ingresso,
            "tp": self.tp,
            "prioridade": self.prioridade,
            "uso_de_r": list(self.uso_de_r) if self.uso_de_r else None,
        }

    @staticmethod
    def de_dicionario(dados: dict) -> "Tarefa":
        uso = dados.get("uso_de_r")
        return Tarefa(
            id=int(dados["id"]),
            ingresso=int(dados["ingresso"]),
            tp=int(dados["tp"]),
            prioridade=int(dados["prioridade"]),
            uso_de_r=(int(uso[0]), int(uso[1])) if uso else None,
        )


def validar(tarefa: Tarefa) -> None:
    """Recusa uma tarefa fora das faixas validas, com mensagem clara."""
    if tarefa.ingresso < 0:
        raise ValueError(f"tarefa {tarefa.id}: o ingresso nao pode ser negativo")
    if tarefa.tp <= 0:
        raise ValueError(f"tarefa {tarefa.id}: o tempo de processamento deve ser positivo")
    if tarefa.uso_de_r is not None:
        inicio, duracao = tarefa.uso_de_r
        if inicio < 0:
            raise ValueError(f"tarefa {tarefa.id}: o inicio da secao critica nao pode ser negativo")
        if duracao <= 0:
            raise ValueError(f"tarefa {tarefa.id}: a duracao da secao critica deve ser positiva")
        if inicio + duracao > tarefa.tp:
            raise ValueError(
                f"tarefa {tarefa.id}: a secao critica deve caber na duracao da tarefa"
            )
