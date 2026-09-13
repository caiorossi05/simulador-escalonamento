# Tutorial de Execucao

Simulador de Escalonamento de Tarefas — Sistemas Operacionais

> **Antes de converter para PDF:** substitua cada marcador `[CAPTURA N]` pela
> imagem correspondente. O tutorial e avaliado sendo seguido ao pe da letra.

---

## 1. Pre-requisitos

- Windows 10 ou superior;
- Nenhuma instalacao adicional. O executavel e independente e nao exige Python
  nem bibliotecas externas.

Para executar a partir do codigo-fonte, em vez do executavel, e necessario
Python 3.10 ou superior com `tkinter`, que acompanha a instalacao padrao.

## 2. Abertura

1. Descompacte o arquivo entregue em uma pasta qualquer;
2. Abra a pasta descompactada;
3. De dois cliques em **`Simulador.exe`**.

> `[CAPTURA 1]` — a pasta descompactada, com o arquivo `Simulador.exe` visivel.

Nao e necessario abrir terminal, ativar ambiente nem digitar comando algum.

## 3. Primeira tela

A janela abre ja preenchida com as cinco tarefas do cenario da Aula 5.

> `[CAPTURA 2]` — a janela inicial completa.

A janela se divide em quatro areas:

**Parametros**, no topo:

| Campo | Funcao |
|-------|--------|
| Numero de tarefas | Quantidade de linhas da tabela |
| Aplicar | Redimensiona a tabela para a quantidade informada |
| Sortear tarefas | Preenche a tabela com um conjunto aleatorio |
| Quantum tq | Tamanho da fatia do Round-Robin |
| Custo da troca ttc | Custo de uma troca de contexto |
| Algoritmo | Escolha entre os seis algoritmos |
| Protocolo | Nenhum, heranca de prioridade ou teto de prioridade |
| Envelhecimento alfa | Passo do envelhecimento; zero o desativa |

E os botoes: **Simular**, **Comparar heranca x teto**, **Comparar algoritmos
(lote)**, **Gravar cenario** e **Carregar cenario**.

**Tarefas**, no meio: uma linha por tarefa, com ingresso, tempo de processamento,
prioridade e a declaracao do uso do recurso R.

**Metricas**: a tabela de resultados por tarefa e a linha de medias.

**Diagrama de tempo**: os intervalos de execucao, com legenda de cores.

## 4. Execucao minima

A sequencia mais curta que produz um resultado na tela:

1. Com a janela recem-aberta, sem alterar nada, clique em **Simular**.

## 5. Resultado esperado

A tabela de metricas passa a exibir cinco linhas e a linha de resumo mostra:

```
First-Come, First-Served   |   Tt=8.00  Tw=5.20  1a exec=5.20  trocas=5  E=nao definida
```

O diagrama de tempo exibe as cinco tarefas com os seus intervalos de execucao.

> `[CAPTURA 3]` — a janela apos o clique em Simular, com a tabela e o diagrama
> preenchidos.

Se esses valores aparecerem, o programa esta funcionando na sua maquina.

## 6. Problemas conhecidos

| Sintoma | O que fazer |
|---------|-------------|
| A janela nao abre | Confirme que a pasta foi descompactada antes de executar. Executar de dentro do arquivo compactado nao funciona. |
| O antivirus bloqueia o executavel | Executaveis gerados com PyInstaller sao ocasionalmente sinalizados. Autorize a execucao, ou execute `python main.py` na raiz do projeto. |
| Uma janela de erro aparece | A janela permanece aberta com o detalhe do erro. Feche-a pelo botao Fechar. |
| O diagrama aparece cortado | Use a barra de rolagem horizontal abaixo do diagrama. |
