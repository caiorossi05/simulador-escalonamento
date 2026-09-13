"""Ponto de entrada do simulador de escalonamento de tarefas.

O programa abre com dois cliques e nao recebe argumentos de linha de comando.
Diante de um erro inesperado, a mensagem permanece na tela ate ser fechada.
"""

import sys
import traceback


def main() -> None:
    from simulador.interface import abrir

    abrir()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        detalhe = traceback.format_exc()
        try:
            import tkinter as tk
            from tkinter import scrolledtext

            janela = tk.Tk()
            janela.title("Erro ao iniciar o simulador")
            janela.geometry("760x420")
            tk.Label(
                janela,
                text="O simulador encontrou um erro e nao pode continuar.",
                font=("TkDefaultFont", 11, "bold"),
            ).pack(anchor="w", padx=12, pady=(12, 4))
            area = scrolledtext.ScrolledText(janela, wrap="word")
            area.insert("1.0", detalhe)
            area.configure(state="disabled")
            area.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            tk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=(0, 12))
            janela.mainloop()
        except Exception:
            # Sem interface grafica disponivel: a janela do console nao fecha sozinha.
            print(detalhe, file=sys.stderr)
            input("\nPressione Enter para fechar.")
