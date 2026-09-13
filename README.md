# Simulador de Escalonamento de Tarefas

Projeto pratico da disciplina de Sistemas Operacionais, ministrada por
`Vinicius S. Borges`. Semestre `2026/2`.

## Autoria

- `Caio Alexandre Rossi`
- `Caio S. A. de Araújo`

## Como executar

Clique duas vezes em `Simulador.exe`.

Nao e necessario instalar nada, nem montar ambiente, nem digitar comando algum.
O programa nao recebe argumentos de linha de comando.

Para quem quiser executar a partir do codigo-fonte, o requisito e Python 3.10 ou
superior com `tkinter`, que acompanha a instalacao padrao. Nesse caso, execute
`python main.py` na raiz do projeto. Nenhuma biblioteca externa e utilizada.

## Descricao

Simulador de escalonamento de tarefas em um processador. Implementa seis
algoritmos (FCFS, SJF, SRTF, Round-Robin, prioridade cooperativa e prioridade
preemptiva), trata recursos de uso exclusivo e reproduz o fenomeno da inversao
de prioridades, com os mecanismos de heranca e teto de prioridade.

Toda a configuracao acontece dentro do programa: quantidade de tarefas, dados de
cada uma ou sorteio, quantum, custo da troca de contexto, algoritmo, protocolo
de correcao e passo do envelhecimento. Nada exige a edicao do codigo-fonte.

## Estrutura do repositorio

```
simulador-escalonamento/
|-- Simulador.exe          Programa pronto para executar
|-- main.py                Ponto de entrada do codigo-fonte
|-- validar.py             Confere o simulador contra os cenarios do enunciado
|-- simulador/             Codigo-fonte do simulador
|-- cenarios/              Conjuntos de tarefas gravados em JSON
`-- docs/                  Tutoriais e documentacao tecnica
```

## Arquivos de codigo

| Arquivo | O que faz |
|---------|-----------|
| `simulador/modelo.py` | Estrutura de uma tarefa e validacao das faixas |
| `simulador/motor.py` | Laco de simulacao: o mecanismo |
| `simulador/politicas.py` | Os seis algoritmos: a politica |
| `simulador/metricas.py` | Calculo de tt, tp, tw e primeira execucao |
| `simulador/gerador.py` | Sorteio de cenarios e comparacao em lote |
| `simulador/persistencia.py` | Gravacao e recarga de cenarios em JSON |
| `simulador/interface.py` | Janela do programa, em tkinter |

## Funcionalidades

| O que faz | Onde |
|-----------|------|
| Os seis algoritmos (R1) | `simulador/politicas.py` |
| Entrada e sorteio de tarefas (R2) | `simulador/interface.py`, `simulador/gerador.py` |
| Gravar e recarregar cenario (R2) | `simulador/persistencia.py` |
| Metricas por tarefa e em media (R3) | `simulador/metricas.py` |
| Quantum, custo da troca e eficiencia (R4) | `simulador/motor.py` |
| Recurso exclusivo e inversao (R5) | `simulador/motor.py` |
| Heranca de prioridade (R6) | `simulador/motor.py`, metodo `_atualizar_prioridades` |
| Teto de prioridade (R7) | `simulador/motor.py`, metodo `_atualizar_prioridades` |
| Envelhecimento (R8) | `simulador/motor.py`, metodo `_atualizar_prioridades` |
| Comparacao em lote (R9) | `simulador/gerador.py`, funcao `comparar_em_lote` |
| Diagrama de tempo | `simulador/interface.py`, metodo `_desenhar` |

## Cenarios de referencia

A pasta `cenarios/` traz os conjuntos de tarefas do enunciado, prontos para
carregar pelo botao **Carregar cenario**:

| Arquivo | Cenario |
|---------|---------|
| `aula5.json` | As cinco tarefas da Aula 5 |
| `aula6_inversao.json` | As quatro tarefas da inversao de prioridades |
| `teto_sem_disputa.json` | O caso em que o teto atrasa sem haver disputa |
| `inanicao.json` | Inanicao sob prioridade cooperativa |

Executar `python validar.py` reproduz todos os cenarios do enunciado e compara
os valores obtidos com os esperados.

## Documentacao

- [Tutorial de execucao](./docs/tutorial_execucao.pdf)
- [Tutorial de uso](./docs/tutorial_uso.pdf)
- [Documentacao tecnica](./docs/documentacao_projeto.pdf)

## Por onde comecar

1. Abra o programa e siga o tutorial de execucao;
2. Reproduza o cenario da Aula 5 pelo tutorial de uso;
3. Consulte a documentacao tecnica para entender o codigo.
