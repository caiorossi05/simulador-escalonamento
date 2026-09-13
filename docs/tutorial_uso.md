# Tutorial de Uso

Simulador de Escalonamento de Tarefas — Sistemas Operacionais

> **Antes de converter para PDF:** substitua cada marcador `[CAPTURA N]` pela
> imagem correspondente.

---

## 1. Definir o conjunto de tarefas

1. No campo **Numero de tarefas**, informe a quantidade desejada e clique em
   **Aplicar**. A tabela passa a exibir esse numero de linhas;
2. Preencha cada linha com o instante de ingresso, o tempo de processamento `tp`
   e a prioridade. Valor maior de prioridade significa prioridade mais alta.

> `[CAPTURA 1]` — a tabela de tarefas preenchida.

Valores fora das faixas validas sao recusados com mensagem, e a tabela continua
disponivel para correcao. As faixas sao: ingresso nao negativo, tempo de
processamento positivo, e secao critica contida na duracao da tarefa.

> `[CAPTURA 2]` — a mensagem exibida ao informar um tempo de processamento
> negativo.

## 2. Sortear tarefas

Em vez de digitar, informe o **Numero de tarefas** e clique em **Sortear
tarefas**. A tabela e preenchida com um conjunto aleatorio, e parte das tarefas
pode receber uma secao critica.

> `[CAPTURA 3]` — a tabela apos o sorteio.

## 3. Definir os parametros de tempo

- **Quantum tq**: tamanho da fatia do Round-Robin;
- **Custo da troca ttc**: custo de uma troca de contexto, valido para todos os
  algoritmos. Pode ser zero.

O quantum precisa ser maior que o custo da troca. Informar um quantum menor ou
igual ao custo e clicar em **Simular** sob Round-Robin produz a mensagem:

```
o quantum precisa ser maior que o custo da troca de contexto:
com quantum 1 e custo 2 nenhum trabalho util seria feito
```

> `[CAPTURA 4]` — a mensagem de quantum invalido.

## 4. Escolher o algoritmo

No campo **Algoritmo**, escolha entre FCFS, SJF, SRTF, RR, PRIOc e PRIOp.

No campo **Protocolo**, escolha **Nenhum**, **Heranca de prioridade** ou **Teto
de prioridade**. Os dois protocolos sao alternativos e nao se combinam.

No campo **Envelhecimento alfa**, informe o passo do envelhecimento. Zero o
desativa.

## 5. Declarar o uso do recurso

Para indicar que uma tarefa disputa o recurso R:

1. Marque a caixa **Usa R** na linha da tarefa;
2. Informe o **Inicio da SC**: apos quantas unidades uteis de execucao propria a
   tarefa obtem o recurso;
3. Informe a **Duracao da SC**: por quantas unidades uteis ela o mantem.

Inicio 1 e duracao 4 significa que a tarefa obtem R apos executar 1 unidade util
e o mantem ate ter executado 5. A contagem e feita no tempo de execucao propria
da tarefa, e nao no relogio.

> `[CAPTURA 5]` — duas tarefas com a secao critica declarada.

## 6. Ler os resultados

Apos clicar em **Simular**:

**Tabela de metricas**, uma linha por tarefa:

| Coluna | Significado |
|--------|-------------|
| Conclusao | Instante em que a tarefa terminou |
| tt | Tempo de execucao: conclusao menos ingresso |
| tw | Tempo de espera: `tt - tp` |
| 1a execucao | Tempo ate a tarefa receber o processador pela primeira vez |

**Linha de resumo**: as medias, o numero de trocas de contexto e a eficiencia
`E = tq / (tq + ttc)`. Fora do Round-Robin a eficiencia aparece como *nao
definida*, porque so existe com quantum.

**Sequencia**: os intervalos de execucao no formato `t1[0,5) t4[5,8)`.

**Diagrama de tempo**, com uma linha por tarefa:

| Cor | Significado |
|-----|-------------|
| Azul | A tarefa esta executando |
| Verde | A tarefa esta executando e detem o recurso R |
| Vermelho | Troca de contexto antes do despacho da tarefa |
| Bege claro | A tarefa esta pronta, aguardando na fila |
| Marrom | A tarefa esta suspensa a espera de R |

> `[CAPTURA 6]` — a tabela de metricas e o diagrama de tempo.

## 7. Comparar os dois protocolos

Com pelo menos uma tarefa usando R, clique em **Comparar heranca x teto**. Uma
janela exibe as medias e a sequencia de execucao sob os tres casos: sem
protocolo, com heranca e com teto, sobre o mesmo conjunto de tarefas.

> `[CAPTURA 7]` — a janela de comparacao dos protocolos.

## 8. Comparar os algoritmos em lote

Clique em **Comparar algoritmos (lote)**. O programa sorteia 50 cenarios e
apresenta as medias dos seis algoritmos.

Os valores absolutos mudam a cada execucao. O que se mantem e a ordenacao: o
SRTF apresenta o menor `Tw` e o Round-Robin o menor tempo medio ate a primeira
execucao.

> `[CAPTURA 8]` — a janela de comparacao em lote.

## 9. Gravar e recarregar um cenario

Para preservar um conjunto de tarefas:

1. Clique em **Gravar cenario**;
2. Escolha o nome e a pasta. A pasta `cenarios/` e sugerida;
3. O arquivo e gravado em JSON.

Para recarregar, clique em **Carregar cenario** e escolha o arquivo. A tabela e
preenchida com as tarefas gravadas.

> `[CAPTURA 9]` — a caixa de dialogo de gravacao.

A pasta `cenarios/` ja traz os conjuntos do enunciado: `aula5.json`,
`aula6_inversao.json`, `teto_sem_disputa.json` e `inanicao.json`.

## 10. Conferir um resultado conhecido

Para confirmar que o programa funciona corretamente na sua maquina:

1. Clique em **Carregar cenario** e escolha `cenarios/aula5.json`;
2. Informe quantum **2** e custo da troca **0**;
3. Para cada algoritmo, escolha-o no campo **Algoritmo** e clique em **Simular**.

Os valores obtidos devem ser exatamente estes:

| Algoritmo | Tt | Tw | 1a execucao | Trocas |
|-----------|-----|-----|-------------|--------|
| FCFS | 8,00 | 5,20 | 5,20 | 5 |
| RR (q = 2) | 8,40 | 5,60 | 2,80 | 8 |
| SJF | 5,80 | 3,00 | 3,00 | 5 |
| SRTF | 5,40 | 2,60 | 2,40 | 6 |
| PRIOc | 6,60 | 3,80 | 3,80 | 5 |
| PRIOp | 5,60 | 2,80 | 2,20 | 7 |

Em seguida, carregue `cenarios/aula6_inversao.json`, escolha **PRIOp** e compare
os tres protocolos:

| Protocolo | Tt | Tw | Conclusao de t4 |
|-----------|-----|-----|-----------------|
| Nenhum | 9,75 | 5,75 | 15 |
| Heranca | 9,50 | 5,50 | 8 |
| Teto | 9,50 | 5,50 | 8 |

> `[CAPTURA 10]` — o resultado do cenario da Aula 5 sob FCFS.
