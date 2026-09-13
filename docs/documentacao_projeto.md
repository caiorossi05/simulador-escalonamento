# Documentacao do Projeto

Simulador de Escalonamento de Tarefas — Sistemas Operacionais

---

## 1. Visao geral

O simulador reproduz o escalonamento de um conjunto de tarefas em um unico
processador, sob tempo discreto. O modelo implementado e o de escalonamento de
curto prazo: um conjunto de tarefas ingressa ao longo do tempo, disputa o
processador segundo uma politica, e o simulador registra o instante de cada
despacho ate que todas concluam, alem dos intervalos ociosos, das trocas de
contexto e dos periodos em que cada tarefa fica bloqueada no recurso.

A partir desse registro o programa apresenta, por tarefa e em media, o tempo de
execucao, o tempo de processamento, o tempo de espera e o tempo ate a primeira
execucao, alem do diagrama de tempo.

Sobre esse nucleo o simulador trata ainda o recurso de uso exclusivo, o que
permite reproduzir a inversao de prioridades e comparar os dois protocolos de
correcao, heranca e teto, sobre o mesmo conjunto de tarefas.

## 2. Separacao entre politica e mecanismo

Este e o eixo do projeto.

O **mecanismo** e o laco de simulacao, em `simulador/motor.py`. Ele avanca o
relogio, monta o conjunto de tarefas prontas, cobra a troca de contexto,
controla a posse do recurso, suspende e libera tarefas e recalcula a prioridade
efetiva sob envelhecimento, heranca e teto. O mecanismo e unico: nao existe um
laco por algoritmo.

A **politica** e a decisao de qual tarefa recebe o processador, em
`simulador/politicas.py`. Uma politica e uma funcao que recebe a lista de
tarefas prontas e devolve a tarefa escolhida. Ela nao conhece o relogio, o custo
da troca de contexto, o recurso nem os protocolos de correcao.

A fronteira entre as duas e a assinatura da funcao de escolha:

```python
def escolher(prontas: list[Tarefa], fila: list[Tarefa]) -> Tarefa
```

Cada uma das seis politicas cabe em uma linha, porque a unica coisa que muda de
um algoritmo para outro e o criterio de ordenacao sobre `prontas`:

| Algoritmo | Criterio |
|-----------|----------|
| FCFS | menor `ingresso` |
| SJF | menor `tp` |
| SRTF | menor `restante` |
| RR | primeiro da fila circular mantida pelo motor |
| PRIOc, PRIOp | maior `prioridade_efetiva` |

O que distingue um algoritmo cooperativo de um preemptivo nao esta na politica,
e sim em duas propriedades declaradas na estrutura `Algoritmo`: `preemptivo` e
`usa_quantum`. O motor as consulta para decidir quando reavaliar a escolha —
a cada unidade de tempo nos preemptivos sem quantum, ao fim da fatia sob
Round-Robin, e apenas quando o processador se libera nos cooperativos.

O motor nao conhece o criterio de escolha, e a politica nao conhece o relogio.

## 3. Diagrama de modulos

```
                          +---------------------+
                          |    interface.py     |
                          |  janela em tkinter  |
                          +----------+----------+
                                     |
       tarefas e parametros          |          metricas e diagrama
          +--------------------------+--------------------------+
          |                          |                          |
          v                          v                          v
  +---------------+        +------------------+        +-----------------+
  |  gerador.py   |        |    motor.py      |        |  metricas.py    |
  |   sorteio e   |------->|   MECANISMO      |------->|  tt, tw, 1a     |
  |     lote      |tarefas |  relogio, fila,  |Resultado|   execucao      |
  +---------------+        |  troca, recurso  |        +-----------------+
                           +---------+--------+
                                     | prontas
                                     v
                           +------------------+
                           |   politicas.py   |
                           |     POLITICA     |
                           |  escolhe a tarefa|
                           +------------------+

  +------------------+                      +---------------------+
  |    modelo.py     |<---------------------|   persistencia.py   |
  |  estrutura de    |   Tarefa <-> JSON    |  gravar e carregar  |
  |   uma tarefa     |                      +---------------------+
  +------------------+
```

O fluxo de dados percorre a interface, que reune as tarefas e os parametros; o
motor, que executa a simulacao consultando a politica a cada decisao; e o modulo
de metricas, que converte o resultado nos numeros apresentados. O modulo
`modelo.py` fornece a estrutura de dados comum a todos, e `persistencia.py`
converte essa estrutura de e para JSON.

## 4. Estrutura de uma tarefa

Definida em `simulador/modelo.py`. Os campos se dividem em dados de definicao,
informados por quem executa o simulador, e campos de estado, mantidos pelo motor
durante a simulacao.

### Campos de definicao

| Campo | Tipo | Funcao |
|-------|------|--------|
| `id` | inteiro | Identificador da tarefa |
| `ingresso` | inteiro | Instante em que a tarefa surge |
| `tp` | inteiro | Tempo de processamento demandado |
| `prioridade` | inteiro | Prioridade base; maior valor, prioridade mais alta |
| `uso_de_r` | tupla ou `None` | Quando a tarefa obtem R e por quanto tempo o mantem |

### Campos de estado

| Campo | Tipo | Funcao |
|-------|------|--------|
| `executado` | inteiro | Unidades uteis ja processadas |
| `conclusao` | inteiro ou `None` | Instante em que a tarefa terminou |
| `primeira_exec` | inteiro ou `None` | Instante do primeiro despacho efetivo |
| `suspensa` | booleano | Verdadeiro enquanto a tarefa espera o recurso R |
| `detem_r` | booleano | Verdadeiro enquanto a tarefa mantem o recurso R |
| `liberou_r` | booleano | Verdadeiro depois da devolucao; impede novo pedido |
| `ultimo_despacho` | inteiro ou `None` | Referencia do envelhecimento |
| `prioridade_efetiva` | inteiro | Prioridade apos envelhecimento, heranca ou teto |

As faixas validas sao verificadas pela funcao `validar`: ingresso nao negativo,
duracao positiva e secao critica contida na duracao da tarefa.

## 5. Interface dos modulos

### `modelo.py`

| Elemento | Recebe | Devolve | O que faz |
|----------|--------|---------|-----------|
| `Tarefa` | os campos de definicao | — | Estrutura de dados de uma tarefa |
| `Tarefa.reiniciar` | — | — | Devolve a tarefa ao estado anterior a qualquer simulacao |
| `Tarefa.copia_limpa` | — | `Tarefa` | Nova tarefa com os mesmos dados e estado zerado |
| `validar` | `Tarefa` | — | Levanta `ValueError` com mensagem clara se algum valor estiver fora da faixa |

### `politicas.py`

| Elemento | Recebe | Devolve | O que faz |
|----------|--------|---------|-----------|
| `fcfs`, `sjf`, `srtf`, `round_robin`, `prioridade` | `prontas`, `fila` | `Tarefa` | Aplicam o criterio de escolha do algoritmo |
| `Algoritmo` | sigla, nome, funcao, propriedades | — | Descreve uma politica e o que o motor precisa saber sobre ela |
| `ALGORITMOS` | — | dicionario | Mapeia a sigla ao algoritmo correspondente |

### `motor.py`

| Elemento | Recebe | Devolve | O que faz |
|----------|--------|---------|-----------|
| `Motor` | tarefas, sigla, quantum, custo, protocolo, alfa | — | Prepara a simulacao e recusa combinacoes invalidas |
| `Motor.simular` | — | `Resultado` | Executa o laco ate que todas as tarefas concluam |
| `Motor._despachar` | instante, tarefa, orcamento | instante | Executa a tarefa ate que ela perca o processador |
| `Motor._atualizar_prioridades` | instante, prontas | — | Recalcula a prioridade efetiva sob os tres mecanismos |
| `Motor._atualizar_fila` | instante, excecao | — | Mantem a ordem da fila circular do Round-Robin |
| `Motor._registrar_suspensas` | instante | — | Guarda quais tarefas estao bloqueadas no recurso a cada instante |
| `Resultado.eficiencia` | — | `float` ou `None` | Calcula tq/(tq+ttc), ou `None` fora do Round-Robin |

### `metricas.py`

| Elemento | Recebe | Devolve | O que faz |
|----------|--------|---------|-----------|
| `calcular` | `Resultado` | `Metricas` | Calcula as quatro grandezas por tarefa e em media |
| `sequencia_de_execucao` | `Resultado` | texto | Reduz a linha do tempo ao formato `t1[0,5) t4[5,8)` |

### `gerador.py`

| Elemento | Recebe | Devolve | O que faz |
|----------|--------|---------|-----------|
| `sortear` | quantidade e faixas | lista de `Tarefa` | Sorteia um conjunto de tarefas |
| `comparar_em_lote` | numero de cenarios e parametros | dicionario de medias | Compara os seis algoritmos sobre cenarios sorteados |

### `persistencia.py`

| Elemento | Recebe | Devolve | O que faz |
|----------|--------|---------|-----------|
| `gravar` | tarefas, caminho | — | Grava o conjunto em JSON |
| `carregar` | caminho | lista de `Tarefa` | Le e valida um conjunto gravado |

## 6. Parametros configuraveis

Todos sao informados na janela do programa. Nenhum esta fixado no codigo-fonte.

| Parametro | Faixa valida | Valor padrao | Observacao |
|-----------|--------------|--------------|------------|
| Numero de tarefas | 1 a 20 | 5 | Define quantas linhas a tabela exibe |
| Quantum `tq` | inteiro maior que `ttc` | 2 | So tem efeito sob Round-Robin |
| Custo da troca `ttc` | inteiro nao negativo | 0 | Vale para todos os algoritmos |
| Protocolo | nenhum, heranca, teto | nenhum | Heranca e teto sao alternativos |
| Passo do envelhecimento `alfa` | inteiro nao negativo | 0 | Zero desativa o envelhecimento |

A combinacao de quantum menor ou igual ao custo da troca e recusada com
mensagem, porque nesse caso a fatia inteira seria consumida pela troca e nenhum
trabalho util seria realizado.

A eficiencia `E = tq / (tq + ttc)` e propriedade da configuracao do escalonador,
nao do conjunto de tarefas. Nos cinco algoritmos sem quantum ela nao esta
definida, e o programa indica isso em vez de exibir um valor.

## 7. Funcionamento interno

O laco principal repete o ciclo abaixo enquanto houver tarefa nao concluida.

**1. Montagem do conjunto de prontas.** O motor reune as tarefas que ja
ingressaram, ainda nao concluiram e nao estao suspensas a espera do recurso.

**2. Relogio ocioso.** Se o conjunto estiver vazio e ainda houver tarefas por
ingressar, o relogio salta diretamente para o proximo instante de ingresso, e o
intervalo e registrado como ocioso no diagrama de tempo.

**3. Recalculo das prioridades efetivas.** Para cada tarefa pronta, a prioridade
efetiva parte da prioridade base. Havendo envelhecimento, soma-se `alfa`
multiplicado pelo tempo decorrido desde o ultimo despacho da tarefa, ou desde o
seu ingresso caso ela ainda nao tenha executado. Em seguida, se um protocolo
estiver habilitado e houver um detentor do recurso:

- sob **heranca**, e somente se existirem tarefas suspensas, o detentor assume a
  maior prioridade entre a sua propria e a das tarefas suspensas;
- sob **teto**, o detentor assume o valor do teto do recurso, independentemente
  de existir conflito.

A diferenca entre os dois protocolos e exatamente essa condicao: a heranca exige
tarefas bloqueadas, o teto exige apenas um detentor.

**4. Escolha.** O conjunto de prontas e entregue a politica, que devolve a
tarefa escolhida.

**5. Troca de contexto.** Se a tarefa escolhida difere da ultima que ocupou o
processador, ocorre uma troca, inclusive no primeiro despacho. O relogio avanca
`ttc` unidades sem trabalho util, e o intervalo e registrado como troca.

**6. Orcamento da fatia.** Sob Round-Robin, a fatia util vale `tq - ttc` quando
houve troca, e `tq` quando a mesma tarefa permanece no processador. Nos demais
algoritmos nao ha orcamento.

**7. Execucao.** Antes de cada unidade, o motor verifica se a tarefa atinge o
inicio da sua secao critica. Em caso afirmativo, se o recurso estiver livre ela
o obtem; se estiver ocupado, ela e marcada como suspensa, sai do conjunto de
prontas e da fila circular, e perde o processador. Caso contrario a tarefa
executa uma unidade, o relogio avanca e `executado` e incrementado. Apos a
unidade, o motor verifica se a tarefa atingiu o fim da secao critica, caso em
que o recurso e devolvido e todas as tarefas suspensas voltam ao conjunto de
prontas; e se a tarefa atingiu o seu `tp`, caso em que a conclusao e registrada.

**8. Fim da fatia.** A tarefa perde o processador ao concluir, ao ficar
suspensa, ao esgotar o quantum, ou, nos algoritmos preemptivos sem quantum, ao
deixar de ser a escolha da politica apos qualquer unidade de tempo. Ao esgotar o
quantum, a tarefa volta a cauda da fila circular depois das que ingressaram
naquele mesmo instante.

## 8. Convencoes de simulacao

Sao as decisoes de modelagem que determinam os numeros produzidos. Sem elas, o
mesmo conjunto de tarefas gera resultados diferentes.

| # | Convencao |
|---|-----------|
| C1 | O tempo e discreto e avanca de uma em uma unidade. Nos cenarios de referencia a unidade e o segundo. |
| C2 | Valor maior de prioridade significa prioridade mais alta. |
| C3 | O desempate entre tarefas equivalentes se da pelo menor instante de ingresso e, persistindo o empate, pelo menor identificador. |
| C4 | Ocorre troca de contexto sempre que a tarefa despachada difere da ultima que ocupou o processador, inclusive no primeiro despacho. |
| C5 | O custo da troca e descontado da fatia concedida, nunca somado a ela. Sob Round-Robin, a tarefa executa `tq - ttc` unidades uteis quando houve troca. |
| C6 | A tarefa que esgota o quantum volta a cauda da fila depois das que ingressaram naquele mesmo instante. |
| C7 | A secao critica e medida no tempo de execucao propria da tarefa. Inicio 1 e duracao 4 significa que a tarefa obtem o recurso apos executar 1 unidade util e o mantem ate ter executado 5. |
| C8 | `tw = tt - tp`. O tempo de espera engloba fila, suspensao no recurso e troca de contexto. |
| C9 | O teto de um recurso e calculado sobre as tarefas que declaram secao critica nele, ainda que a disputa nao chegue a ocorrer. Heranca e teto sao protocolos alternativos e nao se combinam. |
| C10 | O envelhecimento conta o tempo decorrido desde o ultimo despacho da tarefa, ou desde o seu ingresso caso ela ainda nao tenha executado. A prioridade volta ao valor base assim que a tarefa recebe o processador. |

Duas consequencias merecem registro explicito, porque sao as que mais alteram os
numeros:

- o custo da troca **sai de dentro** da fatia. Com `tq = 4` e `ttc = 1`, cada
  fatia ocupa 4 unidades de relogio e entrega 3 unidades de trabalho util;
- a secao critica e contada em **tempo de execucao propria**, e nao no relogio.
  Uma tarefa preemptada no meio da secao critica continua detendo o recurso.

## 9. Dependencias e ambiente

O simulador utiliza apenas a biblioteca padrao do Python. A interface grafica
usa `tkinter`, que acompanha a instalacao padrao. Nenhuma biblioteca externa e
necessaria.

- Versao do Python: 3.10 ou superior;
- Bibliotecas externas: nenhuma;
- Geracao do executavel: `pyinstaller --onefile --windowed --name Simulador main.py`,
  executado na raiz do projeto. O arquivo resultante e copiado de `dist/` para a
  raiz do repositorio.

O arquivo `validar.py` reproduz todos os cenarios de referencia do enunciado e
compara cada valor obtido com o esperado, o que permite confirmar que qualquer
alteracao no codigo preserva os resultados.
