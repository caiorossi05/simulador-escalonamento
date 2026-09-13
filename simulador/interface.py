"""Janela do simulador, em tkinter.

Toda a interacao acontece dentro do programa depois de aberto: quantidade de
tarefas, dados ou sorteio, quantum, custo da troca de contexto, algoritmo e
protocolo de correcao. Nada exige a edicao do codigo-fonte.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .gerador import comparar_em_lote, sortear
from .metricas import calcular, sequencia_de_execucao
from .modelo import Tarefa, validar
from .motor import OCIOSO, TROCA, simular
from .persistencia import carregar, gravar
from .politicas import ALGORITMOS, SIGLAS

COR_EXECUCAO = "#2f6fb5"
COR_TROCA = "#c8553d"
COR_AGUARDANDO = "#d9d2c5"
COR_SUSPENSA = "#8a6f4e"
COR_RECURSO = "#1f7a4d"

PROTOCOLOS_VISIVEIS = {
    "nenhum": "Nenhum",
    "heranca": "Heranca de prioridade",
    "teto": "Teto de prioridade",
}


class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Escalonamento de Tarefas")
        self.geometry("1180x780")
        self.minsize(980, 640)

        self.linhas_de_entrada: list[dict] = []
        self.ultimo_resultado = None

        self._montar_parametros()
        self._montar_tarefas()
        self._montar_resultados()
        self._montar_diagrama()
        self._aplicar_quantidade(inicial=True)

    # ------------------------------------------------------------- construcao

    def _montar_parametros(self):
        caixa = ttk.LabelFrame(self, text="Parametros", padding=8)
        caixa.pack(fill="x", padx=10, pady=(10, 4))

        ttk.Label(caixa, text="Numero de tarefas:").grid(row=0, column=0, sticky="w")
        self.var_quantidade = tk.StringVar(value="5")
        ttk.Entry(caixa, textvariable=self.var_quantidade, width=5).grid(row=0, column=1, padx=(4, 4))
        ttk.Button(caixa, text="Aplicar", command=self._aplicar_quantidade).grid(row=0, column=2)
        ttk.Button(caixa, text="Sortear tarefas", command=self._sortear).grid(row=0, column=3, padx=(12, 0))

        ttk.Label(caixa, text="Quantum tq:").grid(row=0, column=4, sticky="e", padx=(20, 0))
        self.var_quantum = tk.StringVar(value="2")
        ttk.Entry(caixa, textvariable=self.var_quantum, width=5).grid(row=0, column=5, padx=4)

        ttk.Label(caixa, text="Custo da troca ttc:").grid(row=0, column=6, sticky="e", padx=(12, 0))
        self.var_custo = tk.StringVar(value="0")
        ttk.Entry(caixa, textvariable=self.var_custo, width=5).grid(row=0, column=7, padx=4)

        ttk.Label(caixa, text="Algoritmo:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.var_algoritmo = tk.StringVar(value="FCFS")
        seletor = ttk.Combobox(
            caixa, textvariable=self.var_algoritmo, values=SIGLAS, state="readonly", width=8
        )
        seletor.grid(row=1, column=1, columnspan=2, sticky="w", padx=4, pady=(8, 0))

        ttk.Label(caixa, text="Protocolo:").grid(row=1, column=3, sticky="e", pady=(8, 0))
        self.var_protocolo = tk.StringVar(value="Nenhum")
        ttk.Combobox(
            caixa,
            textvariable=self.var_protocolo,
            values=list(PROTOCOLOS_VISIVEIS.values()),
            state="readonly",
            width=22,
        ).grid(row=1, column=4, columnspan=2, sticky="w", padx=4, pady=(8, 0))

        ttk.Label(caixa, text="Envelhecimento alfa:").grid(row=1, column=6, sticky="e", pady=(8, 0))
        self.var_alfa = tk.StringVar(value="0")
        ttk.Entry(caixa, textvariable=self.var_alfa, width=5).grid(row=1, column=7, padx=4, pady=(8, 0))

        acoes = ttk.Frame(caixa)
        acoes.grid(row=2, column=0, columnspan=9, sticky="w", pady=(10, 0))
        ttk.Button(acoes, text="Simular", command=self._simular).pack(side="left")
        ttk.Button(acoes, text="Comparar heranca x teto", command=self._comparar_protocolos).pack(
            side="left", padx=6
        )
        ttk.Button(acoes, text="Comparar algoritmos (lote)", command=self._comparar_lote).pack(
            side="left", padx=6
        )
        ttk.Button(acoes, text="Gravar cenario", command=self._gravar).pack(side="left", padx=(20, 6))
        ttk.Button(acoes, text="Carregar cenario", command=self._carregar).pack(side="left")

    def _montar_tarefas(self):
        caixa = ttk.LabelFrame(self, text="Tarefas", padding=8)
        caixa.pack(fill="x", padx=10, pady=4)

        cabecalhos = ["Tarefa", "Ingresso", "tp", "Prioridade", "Usa R", "Inicio da SC", "Duracao da SC"]
        for coluna, texto in enumerate(cabecalhos):
            ttk.Label(caixa, text=texto, font=("TkDefaultFont", 9, "bold")).grid(
                row=0, column=coluna, padx=6, pady=(0, 4)
            )

        self.area_tarefas = caixa
        ttk.Label(
            caixa,
            text="A secao critica e medida no tempo de execucao propria da tarefa: "
            "inicio 1 e duracao 4 significa que a tarefa obtem R apos executar 1 unidade "
            "util e o mantem ate ter executado 5.",
            foreground="#555555",
            wraplength=1100,
            justify="left",
        ).grid(row=99, column=0, columnspan=7, sticky="w", pady=(8, 0))

    def _montar_resultados(self):
        caixa = ttk.LabelFrame(self, text="Metricas", padding=8)
        caixa.pack(fill="both", expand=True, padx=10, pady=4)

        colunas = ("id", "ingresso", "tp", "prioridade", "conclusao", "tt", "tw", "primeira")
        titulos = {
            "id": "Tarefa",
            "ingresso": "Ingresso",
            "tp": "tp",
            "prioridade": "Prioridade",
            "conclusao": "Conclusao",
            "tt": "tt",
            "tw": "tw",
            "primeira": "1a execucao",
        }
        self.tabela = ttk.Treeview(caixa, columns=colunas, show="headings", height=7)
        for coluna in colunas:
            self.tabela.heading(coluna, text=titulos[coluna])
            self.tabela.column(coluna, width=100, anchor="center")
        self.tabela.pack(fill="both", expand=True)

        self.var_resumo = tk.StringVar(value="Defina as tarefas e clique em Simular.")
        ttk.Label(caixa, textvariable=self.var_resumo, font=("TkDefaultFont", 10, "bold")).pack(
            anchor="w", pady=(6, 0)
        )
        self.var_sequencia = tk.StringVar(value="")
        ttk.Label(caixa, textvariable=self.var_sequencia, foreground="#333333").pack(anchor="w")

    def _montar_diagrama(self):
        caixa = ttk.LabelFrame(self, text="Diagrama de tempo", padding=8)
        caixa.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        moldura = ttk.Frame(caixa)
        moldura.pack(fill="both", expand=True)
        self.tela = tk.Canvas(moldura, height=200, background="white", highlightthickness=1)
        vertical = ttk.Scrollbar(moldura, orient="vertical", command=self.tela.yview)
        horizontal = ttk.Scrollbar(caixa, orient="horizontal", command=self.tela.xview)
        self.tela.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        vertical.pack(side="right", fill="y")
        self.tela.pack(side="left", fill="both", expand=True)
        horizontal.pack(fill="x")

        legenda = ttk.Frame(caixa)
        legenda.pack(anchor="w", pady=(4, 0))
        for cor, texto in (
            (COR_EXECUCAO, "execucao"),
            (COR_TROCA, "troca de contexto"),
            (COR_AGUARDANDO, "pronta, aguardando na fila"),
            (COR_SUSPENSA, "suspensa a espera de R"),
            (COR_RECURSO, "detem R"),
        ):
            marca = tk.Canvas(legenda, width=14, height=14, highlightthickness=0)
            marca.create_rectangle(0, 0, 14, 14, fill=cor, outline=cor)
            marca.pack(side="left", padx=(8, 3))
            ttk.Label(legenda, text=texto).pack(side="left")

    # ------------------------------------------------------------------ tabela

    def _aplicar_quantidade(self, inicial: bool = False):
        try:
            quantidade = int(self.var_quantidade.get())
            if quantidade < 1 or quantidade > 20:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Valor invalido",
                "O numero de tarefas deve ser um inteiro entre 1 e 20.",
            )
            return

        for linha in self.linhas_de_entrada:
            for widget in linha["widgets"]:
                widget.destroy()
        self.linhas_de_entrada.clear()

        for indice in range(quantidade):
            self._criar_linha(indice + 1)

        if inicial:
            self._preencher(
                [
                    Tarefa(1, 0, 5, 2),
                    Tarefa(2, 0, 2, 3),
                    Tarefa(3, 1, 4, 1),
                    Tarefa(4, 3, 1, 4),
                    Tarefa(5, 5, 2, 5),
                ]
            )

    def _criar_linha(self, identificador: int):
        linha = identificador
        rotulo = ttk.Label(self.area_tarefas, text=f"t{identificador}")
        rotulo.grid(row=linha, column=0, padx=6, pady=2)

        variaveis = {}
        widgets = [rotulo]
        for coluna, chave in enumerate(("ingresso", "tp", "prioridade"), start=1):
            variaveis[chave] = tk.StringVar(value="0" if chave == "ingresso" else "1")
            campo = ttk.Entry(self.area_tarefas, textvariable=variaveis[chave], width=10, justify="center")
            campo.grid(row=linha, column=coluna, padx=6, pady=2)
            widgets.append(campo)

        variaveis["usa_r"] = tk.BooleanVar(value=False)
        marca = ttk.Checkbutton(self.area_tarefas, variable=variaveis["usa_r"])
        marca.grid(row=linha, column=4, padx=6, pady=2)
        widgets.append(marca)

        for coluna, chave in enumerate(("sc_inicio", "sc_duracao"), start=5):
            variaveis[chave] = tk.StringVar(value="")
            campo = ttk.Entry(self.area_tarefas, textvariable=variaveis[chave], width=12, justify="center")
            campo.grid(row=linha, column=coluna, padx=6, pady=2)
            widgets.append(campo)

        self.linhas_de_entrada.append(
            {"id": identificador, "variaveis": variaveis, "widgets": widgets}
        )

    def _preencher(self, tarefas: list[Tarefa]):
        self.var_quantidade.set(str(len(tarefas)))
        if len(self.linhas_de_entrada) != len(tarefas):
            self._aplicar_quantidade()
        for linha, tarefa in zip(self.linhas_de_entrada, tarefas):
            variaveis = linha["variaveis"]
            variaveis["ingresso"].set(str(tarefa.ingresso))
            variaveis["tp"].set(str(tarefa.tp))
            variaveis["prioridade"].set(str(tarefa.prioridade))
            variaveis["usa_r"].set(tarefa.uso_de_r is not None)
            variaveis["sc_inicio"].set(str(tarefa.uso_de_r[0]) if tarefa.uso_de_r else "")
            variaveis["sc_duracao"].set(str(tarefa.uso_de_r[1]) if tarefa.uso_de_r else "")

    def _ler_tarefas(self) -> list[Tarefa]:
        """Le a tabela. Recusa valores invalidos com mensagem clara."""
        tarefas = []
        for linha in self.linhas_de_entrada:
            identificador = linha["id"]
            variaveis = linha["variaveis"]
            try:
                ingresso = int(variaveis["ingresso"].get())
                tp = int(variaveis["tp"].get())
                prioridade = int(variaveis["prioridade"].get())
            except ValueError:
                raise ValueError(
                    f"tarefa {identificador}: ingresso, tp e prioridade devem ser numeros inteiros"
                )

            uso_de_r = None
            if variaveis["usa_r"].get():
                try:
                    inicio = int(variaveis["sc_inicio"].get())
                    duracao = int(variaveis["sc_duracao"].get())
                except ValueError:
                    raise ValueError(
                        f"tarefa {identificador}: informe inicio e duracao da secao critica"
                    )
                uso_de_r = (inicio, duracao)

            tarefa = Tarefa(identificador, ingresso, tp, prioridade, uso_de_r)
            validar(tarefa)
            tarefas.append(tarefa)
        return tarefas

    def _ler_parametros(self) -> dict:
        try:
            quantum = int(self.var_quantum.get())
        except ValueError:
            raise ValueError("o quantum deve ser um numero inteiro")
        try:
            custo = int(self.var_custo.get())
        except ValueError:
            raise ValueError("o custo da troca de contexto deve ser um numero inteiro")
        try:
            alfa = int(self.var_alfa.get())
        except ValueError:
            raise ValueError("o passo do envelhecimento deve ser um numero inteiro")

        if custo < 0:
            raise ValueError("o custo da troca de contexto nao pode ser negativo")
        if alfa < 0:
            raise ValueError("o passo do envelhecimento nao pode ser negativo")

        protocolo = next(
            chave for chave, texto in PROTOCOLOS_VISIVEIS.items()
            if texto == self.var_protocolo.get()
        )
        return {
            "quantum": quantum,
            "custo_troca": custo,
            "alfa": alfa,
            "protocolo": protocolo,
        }

    # ------------------------------------------------------------------ acoes

    def _sortear(self):
        try:
            quantidade = int(self.var_quantidade.get())
            if quantidade < 1 or quantidade > 20:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valor invalido", "O numero de tarefas deve estar entre 1 e 20.")
            return
        self._preencher(sortear(quantidade, com_recurso=True))

    def _simular(self):
        try:
            tarefas = self._ler_tarefas()
            parametros = self._ler_parametros()
            sigla = self.var_algoritmo.get()
            resultado = simular(
                tarefas,
                sigla,
                quantum=parametros["quantum"],
                custo_troca=parametros["custo_troca"],
                protocolo=parametros["protocolo"],
                alfa=parametros["alfa"],
            )
        except ValueError as erro:
            messagebox.showerror("Entrada recusada", str(erro))
            return
        except RuntimeError as erro:
            messagebox.showerror("Simulacao interrompida", str(erro))
            return

        self.ultimo_resultado = resultado
        metricas = calcular(resultado)

        self.tabela.delete(*self.tabela.get_children())
        for linha in metricas.linhas:
            self.tabela.insert(
                "",
                "end",
                values=(
                    f"t{linha.id}",
                    linha.ingresso,
                    linha.tp,
                    linha.prioridade,
                    linha.conclusao,
                    linha.tt,
                    linha.tw,
                    linha.primeira,
                ),
            )
        nome = ALGORITMOS[self.var_algoritmo.get()].nome
        self.var_resumo.set(f"{nome}   |   {metricas.resumo()}")
        self.var_sequencia.set("Sequencia: " + sequencia_de_execucao(resultado))
        self._desenhar(resultado)

    def _comparar_protocolos(self):
        """R7: compara heranca e teto sobre o mesmo conjunto de tarefas."""
        try:
            tarefas = self._ler_tarefas()
            parametros = self._ler_parametros()
        except ValueError as erro:
            messagebox.showerror("Entrada recusada", str(erro))
            return

        if not any(tarefa.uso_de_r for tarefa in tarefas):
            messagebox.showinfo(
                "Nenhum recurso declarado",
                "Marque Usa R em pelo menos uma tarefa para comparar os protocolos.",
            )
            return

        janela = tk.Toplevel(self)
        janela.title("Heranca x teto sobre o mesmo conjunto de tarefas")
        janela.geometry("760x300")
        tabela = ttk.Treeview(
            janela, columns=("protocolo", "tt", "tw", "sequencia"), show="headings"
        )
        for coluna, titulo, largura in (
            ("protocolo", "Protocolo", 150),
            ("tt", "Tt", 70),
            ("tw", "Tw", 70),
            ("sequencia", "Sequencia de execucao", 460),
        ):
            tabela.heading(coluna, text=titulo)
            tabela.column(coluna, width=largura, anchor="w")
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        for protocolo in ("nenhum", "heranca", "teto"):
            resultado = simular(
                tarefas,
                "PRIOp",
                quantum=parametros["quantum"],
                custo_troca=parametros["custo_troca"],
                protocolo=protocolo,
                alfa=parametros["alfa"],
            )
            metricas = calcular(resultado)
            tabela.insert(
                "",
                "end",
                values=(
                    PROTOCOLOS_VISIVEIS[protocolo],
                    f"{metricas.tt_medio:.2f}",
                    f"{metricas.tw_medio:.2f}",
                    sequencia_de_execucao(resultado),
                ),
            )

        ttk.Label(
            janela,
            text="A heranca age depois que a disputa aparece; o teto age na obtencao do recurso.",
            foreground="#555555",
        ).pack(anchor="w", padx=10, pady=(0, 8))

    def _comparar_lote(self):
        """R9: compara os seis algoritmos sobre um lote de cenarios sorteados."""
        try:
            parametros = self._ler_parametros()
            quantidade = int(self.var_quantidade.get())
        except ValueError as erro:
            messagebox.showerror("Entrada recusada", str(erro))
            return

        janela = tk.Toplevel(self)
        janela.title("Comparacao sobre 50 cenarios sorteados")
        janela.geometry("620x300")

        medias = comparar_em_lote(
            cenarios=50,
            tarefas_por_cenario=max(2, quantidade),
            quantum=max(parametros["quantum"], parametros["custo_troca"] + 1),
            custo_troca=parametros["custo_troca"],
        )

        tabela = ttk.Treeview(janela, columns=("alg", "tt", "tw", "primeira"), show="headings")
        for coluna, titulo in (
            ("alg", "Algoritmo"),
            ("tt", "Tt"),
            ("tw", "Tw"),
            ("primeira", "1a execucao"),
        ):
            tabela.heading(coluna, text=titulo)
            tabela.column(coluna, width=140, anchor="center")
        tabela.pack(fill="both", expand=True, padx=10, pady=10)

        for sigla, valores in medias.items():
            tabela.insert(
                "",
                "end",
                values=(
                    sigla,
                    f"{valores['tt']:.2f}",
                    f"{valores['tw']:.2f}",
                    f"{valores['primeira']:.2f}",
                ),
            )

        menor_tw = min(medias, key=lambda s: medias[s]["tw"])
        menor_primeira = min(medias, key=lambda s: medias[s]["primeira"])
        ttk.Label(
            janela,
            text=f"Menor Tw: {menor_tw}.   Menor tempo ate a primeira execucao: {menor_primeira}.\n"
            "Os valores absolutos mudam a cada execucao; a ordenacao se mantem.",
            foreground="#555555",
            justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 8))

    def _gravar(self):
        try:
            tarefas = self._ler_tarefas()
        except ValueError as erro:
            messagebox.showerror("Entrada recusada", str(erro))
            return
        caminho = filedialog.asksaveasfilename(
            title="Gravar cenario",
            defaultextension=".json",
            filetypes=[("Cenario JSON", "*.json")],
            initialdir="cenarios",
        )
        if not caminho:
            return
        try:
            gravar(tarefas, caminho)
        except OSError as erro:
            messagebox.showerror("Nao foi possivel gravar", str(erro))
            return
        messagebox.showinfo("Cenario gravado", f"Conjunto de tarefas gravado em:\n{caminho}")

    def _carregar(self):
        caminho = filedialog.askopenfilename(
            title="Carregar cenario",
            filetypes=[("Cenario JSON", "*.json"), ("Todos os arquivos", "*.*")],
            initialdir="cenarios",
        )
        if not caminho:
            return
        try:
            tarefas = carregar(caminho)
        except (ValueError, OSError, KeyError) as erro:
            messagebox.showerror("Nao foi possivel carregar", str(erro))
            return
        self._preencher(tarefas)
        messagebox.showinfo("Cenario carregado", f"{len(tarefas)} tarefas carregadas.")

    # --------------------------------------------------------------- diagrama

    def _desenhar(self, resultado):
        self.tela.delete("all")
        if not resultado.linha_do_tempo:
            return

        tarefas = sorted(resultado.tarefas, key=lambda t: t.id)
        duracao = max(instante for instante, _ in resultado.linha_do_tempo) + 1
        largura_unidade = max(18, min(40, 1000 // max(duracao, 1)))
        margem_esquerda = 60
        altura_linha = 26
        topo = 28

        # Escala de tempo
        for instante in range(duracao + 1):
            x = margem_esquerda + instante * largura_unidade
            self.tela.create_line(x, topo - 6, x, topo + altura_linha * len(tarefas), fill="#e2e2e2")
            if instante % max(1, duracao // 25) == 0:
                self.tela.create_text(x, topo - 14, text=str(instante), font=("TkDefaultFont", 8))

        ocupacao = {instante: rotulo for instante, rotulo in resultado.linha_do_tempo}

        for indice, tarefa in enumerate(tarefas):
            y = topo + indice * altura_linha
            self.tela.create_text(
                margem_esquerda - 22, y + altura_linha / 2, text=f"t{tarefa.id}",
                font=("TkDefaultFont", 9, "bold"),
            )
            for instante in range(duracao):
                rotulo = ocupacao.get(instante)
                x0 = margem_esquerda + instante * largura_unidade
                x1 = x0 + largura_unidade
                y0 = y + 3
                y1 = y + altura_linha - 3

                if rotulo == tarefa.id:
                    detem = self._detinha_recurso(tarefa, resultado, instante)
                    self.tela.create_rectangle(
                        x0, y0, x1, y1,
                        fill=COR_RECURSO if detem else COR_EXECUCAO,
                        outline="white",
                    )
                elif rotulo == TROCA and self._envolvida_na_troca(tarefa, resultado, instante):
                    self.tela.create_rectangle(x0, y0, x1, y1, fill=COR_TROCA, outline="white")
                elif (
                    rotulo not in (None, OCIOSO)
                    and tarefa.ingresso <= instante
                    and (tarefa.conclusao is None or instante < tarefa.conclusao)
                ):
                    suspensa = tarefa.id in resultado.suspensas_por_instante.get(instante, set())
                    self.tela.create_rectangle(
                        x0, y0, x1, y1,
                        fill=COR_SUSPENSA if suspensa else COR_AGUARDANDO,
                        outline="white",
                    )

        altura = topo + altura_linha * len(tarefas) + 16
        self.tela.configure(
            height=min(altura, 320),
            scrollregion=(0, 0, margem_esquerda + duracao * largura_unidade + 30, altura),
        )

    def _detinha_recurso(self, tarefa, resultado, instante) -> bool:
        """Reconstroi, a partir da linha do tempo, se a tarefa detinha R nesse instante."""
        if not tarefa.uso_de_r:
            return False
        inicio, duracao = tarefa.uso_de_r
        executado = sum(
            1 for momento, rotulo in resultado.linha_do_tempo
            if rotulo == tarefa.id and momento < instante
        )
        return inicio <= executado < inicio + duracao

    def _envolvida_na_troca(self, tarefa, resultado, instante) -> bool:
        """A troca e desenhada na linha da tarefa que esta para ser despachada."""
        for momento, rotulo in resultado.linha_do_tempo:
            if momento > instante and rotulo != TROCA:
                return rotulo == tarefa.id
        return False


def abrir():
    Aplicacao().mainloop()
