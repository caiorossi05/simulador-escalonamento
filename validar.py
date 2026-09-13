"""Confere o simulador contra os cenarios de validacao do enunciado.

Executa e compara com os valores da secao 4. Uso: python validar.py
"""

from simulador.metricas import calcular, sequencia_de_execucao
from simulador.modelo import Tarefa
from simulador.motor import simular

falhas = []


def conferir(rotulo, obtido, esperado, casas=2):
    ok = round(obtido, casas) == round(esperado, casas)
    marca = "ok  " if ok else "ERRO"
    print(f"  [{marca}] {rotulo}: obtido {obtido:.2f}  esperado {esperado:.2f}")
    if not ok:
        falhas.append(rotulo)


def conferir_texto(rotulo, obtido, esperado):
    ok = obtido == esperado
    marca = "ok  " if ok else "ERRO"
    print(f"  [{marca}] {rotulo}")
    if not ok:
        print(f"         obtido:   {obtido}")
        print(f"         esperado: {esperado}")
        falhas.append(rotulo)


def aula5():
    return [
        Tarefa(1, 0, 5, 2),
        Tarefa(2, 0, 2, 3),
        Tarefa(3, 1, 4, 1),
        Tarefa(4, 3, 1, 4),
        Tarefa(5, 5, 2, 5),
    ]


def aula6():
    return [
        Tarefa(1, 0, 6, 1, (1, 4)),
        Tarefa(2, 4, 4, 2),
        Tarefa(3, 6, 3, 3),
        Tarefa(4, 2, 3, 4, (1, 1)),
    ]


print("4.1 Cenario da Aula 5 (sem custo de troca)")
esperados = {
    "FCFS": (8.0, 5.2, 5.2, 5),
    "RR": (8.4, 5.6, 2.8, 8),
    "SJF": (5.8, 3.0, 3.0, 5),
    "SRTF": (5.4, 2.6, 2.4, 6),
    "PRIOc": (6.6, 3.8, 3.8, 5),
    "PRIOp": (5.6, 2.8, 2.2, 7),
}
for sigla, (tt, tw, primeira, trocas) in esperados.items():
    m = calcular(simular(aula5(), sigla, quantum=2, custo_troca=0))
    print(f" {sigla}")
    conferir("Tt", m.tt_medio, tt)
    conferir("Tw", m.tw_medio, tw)
    conferir("1a exec", m.primeira_media, primeira)
    conferir("trocas", float(m.trocas), float(trocas))

print("\n4.2 Cenario da Aula 5 com custo de troca (c=1, q=4)")
m = calcular(simular(aula5(), "FCFS", custo_troca=1))
print(" FCFS")
conferir("Tt", m.tt_medio, 11.0)
conferir("Tw", m.tw_medio, 8.2)
m = calcular(simular(aula5(), "RR", quantum=4, custo_troca=1))
print(" RR")
conferir("Tt", m.tt_medio, 13.4)
conferir("Tw", m.tw_medio, 10.6)
conferir("E", m.eficiencia, 0.8, casas=3)

print("\n4.3 Inversao de prioridades (PRIOp, sem protocolo)")
r = simular(aula6(), "PRIOp", protocolo="nenhum")
m = calcular(r)
for linha, conclusao in zip(m.linhas, [16, 11, 9, 15]):
    conferir(f"conclusao t{linha.id}", float(linha.conclusao), float(conclusao))
conferir("Tt", m.tt_medio, 9.75)
conferir("Tw", m.tw_medio, 5.75)

print("\n4.4 Heranca de prioridade")
r = simular(aula6(), "PRIOp", protocolo="heranca")
m = calcular(r)
for linha, conclusao in zip(m.linhas, [16, 15, 11, 8]):
    conferir(f"conclusao t{linha.id}", float(linha.conclusao), float(conclusao))
conferir("Tt", m.tt_medio, 9.50)
conferir("Tw", m.tw_medio, 5.50)

print("\n4.5 Teto de prioridade")
r = simular(aula6(), "PRIOp", protocolo="teto")
m = calcular(r)
conferir("Tt", m.tt_medio, 9.50)
conferir("Tw", m.tw_medio, 5.50)
conferir_texto(
    "sequencia",
    sequencia_de_execucao(r),
    "t1[0,5) t4[5,8) t3[8,11) t2[11,15) t1[15,16)",
)

print("\n4.5b O preco do teto quando a disputa nao ocorre")
sem_disputa = [
    Tarefa(1, 0, 6, 1, (1, 4)),
    Tarefa(2, 2, 3, 2),
    Tarefa(4, 12, 2, 4, (0, 1)),
]
r = simular(sem_disputa, "PRIOp", protocolo="heranca")
m = calcular(r)
conferir_texto(
    "heranca",
    sequencia_de_execucao(r),
    "t1[0,2) t2[2,5) t1[5,9) t4[12,14)",
)
conferir("tw de t2 sob heranca", float(m.linhas[1].tw), 0.0)
conferir("Tw sob heranca", m.tw_medio, 1.00)
r = simular(sem_disputa, "PRIOp", protocolo="teto")
m = calcular(r)
conferir_texto(
    "teto",
    sequencia_de_execucao(r),
    "t1[0,5) t2[5,8) t1[8,9) t4[12,14)",
)
conferir("tw de t2 sob teto", float(m.linhas[1].tw), 3.0)
conferir("Tw sob teto", m.tw_medio, 2.00)

print("\n4.6 Inanicao e envelhecimento (PRIOc)")
inanicao = [
    Tarefa(1, 0, 4, 1),
    Tarefa(2, 0, 2, 5),
    Tarefa(3, 2, 2, 5),
    Tarefa(4, 4, 2, 5),
    Tarefa(5, 6, 2, 5),
    Tarefa(6, 8, 2, 5),
]
casos = [
    (0, "t2[0,2) t3[2,4) t4[4,6) t5[6,8) t6[8,10) t1[10,14)", 10, 1.67),
    (1, "t2[0,2) t3[2,4) t1[4,8) t4[8,10) t5[10,12) t6[12,14)", 4, 2.67),
    (2, "t2[0,2) t1[2,6) t3[6,8) t4[8,10) t5[10,12) t6[12,14)", 2, 3.00),
]
for alfa, sequencia, tw_t1, tw_medio in casos:
    r = simular(inanicao, "PRIOc", alfa=alfa)
    m = calcular(r)
    print(f" alfa = {alfa}")
    conferir_texto("sequencia", sequencia_de_execucao(r), sequencia)
    conferir("tw de t1", float(m.linhas[0].tw), float(tw_t1))
    conferir("Tw", m.tw_medio, tw_medio)

print()
if falhas:
    print(f"{len(falhas)} divergencia(s): " + ", ".join(falhas))
else:
    print("Todos os cenarios de referencia foram reproduzidos.")
