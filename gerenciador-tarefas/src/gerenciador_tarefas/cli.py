"""Interface de linha de comando (o que o usuário digita no terminal)."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path

from .modelos import Prioridade, Tarefa
from .repositorio import ErroArmazenamento, RepositorioJSON
from .servico import GerenciadorTarefas, TarefaNaoEncontrada

VARIAVEL_AMBIENTE = "GERENCIADOR_TAREFAS_ARQUIVO"
CAMINHO_PADRAO = Path.home() / ".gerenciador_tarefas" / "tarefas.json"


def _data(texto: str) -> date:
    """Converte 'AAAA-MM-DD' em data, com mensagem de erro amigável."""
    try:
        return date.fromisoformat(texto)
    except ValueError as erro:
        raise argparse.ArgumentTypeError(
            f"Data inválida: {texto!r}. Use o formato AAAA-MM-DD (ex.: 2026-12-31)."
        ) from erro


def _prioridade(texto: str) -> Prioridade:
    try:
        return Prioridade.de_texto(texto)
    except ValueError as erro:
        raise argparse.ArgumentTypeError(str(erro)) from erro


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tarefas", description="Gerenciador de tarefas em linha de comando."
    )
    parser.add_argument(
        "--arquivo",
        type=Path,
        help=(
            "Arquivo JSON onde as tarefas ficam salvas "
            f"(padrão: {CAMINHO_PADRAO}, ou a variável {VARIAVEL_AMBIENTE})."
        ),
    )
    comandos = parser.add_subparsers(dest="comando", required=True)

    adicionar = comandos.add_parser("add", help="adiciona uma tarefa")
    adicionar.add_argument("titulo", help="texto da tarefa")
    adicionar.add_argument(
        "-p",
        "--prioridade",
        type=_prioridade,
        default=Prioridade.MEDIA,
        help="baixa, media ou alta (padrão: media)",
    )
    adicionar.add_argument(
        "--prazo", type=_data, help="data limite no formato AAAA-MM-DD"
    )

    listar = comandos.add_parser("list", help="lista as tarefas")
    listar.add_argument(
        "--pendentes", action="store_true", help="mostra só as não concluídas"
    )
    listar.add_argument(
        "-p", "--prioridade", type=_prioridade, help="filtra por prioridade"
    )

    concluir = comandos.add_parser("done", help="marca uma tarefa como concluída")
    concluir.add_argument("id", type=int, help="id da tarefa")

    remover = comandos.add_parser("remove", help="remove uma tarefa")
    remover.add_argument("id", type=int, help="id da tarefa")

    return parser


def formatar_tarefa(tarefa: Tarefa, hoje: date | None = None) -> str:
    """Monta a linha de texto que representa uma tarefa na listagem."""
    marca = "x" if tarefa.concluida else " "
    partes = [f"[{marca}] {tarefa.id:>3}  {tarefa.titulo}  ({tarefa.prioridade.value})"]
    if tarefa.prazo:
        partes.append(f"prazo: {tarefa.prazo.isoformat()}")
    if tarefa.esta_atrasada(hoje):
        partes.append("ATRASADA")
    return "  ".join(partes)


def resolver_caminho(arquivo: Path | None) -> Path:
    """Escolhe o arquivo: argumento > variável de ambiente > padrão."""
    if arquivo is not None:
        return arquivo
    do_ambiente = os.environ.get(VARIAVEL_AMBIENTE)
    return Path(do_ambiente) if do_ambiente else CAMINHO_PADRAO


def _executar(args: argparse.Namespace, gerenciador: GerenciadorTarefas) -> None:
    if args.comando == "add":
        tarefa = gerenciador.adicionar(args.titulo, args.prioridade, args.prazo)
        print(f"Tarefa {tarefa.id} adicionada: {tarefa.titulo}")
    elif args.comando == "list":
        tarefas = gerenciador.listar(args.pendentes, args.prioridade)
        if not tarefas:
            print("Nenhuma tarefa encontrada.")
        for tarefa in tarefas:
            print(formatar_tarefa(tarefa))
    elif args.comando == "done":
        tarefa = gerenciador.concluir(args.id)
        print(f"Tarefa {tarefa.id} concluída: {tarefa.titulo}")
    elif args.comando == "remove":
        tarefa = gerenciador.remover(args.id)
        print(f"Tarefa {tarefa.id} removida: {tarefa.titulo}")


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada. Devolve 0 em caso de sucesso e 1 em caso de erro."""
    args = criar_parser().parse_args(argv)
    caminho = resolver_caminho(args.arquivo)
    try:
        gerenciador = GerenciadorTarefas(RepositorioJSON(caminho))
        _executar(args, gerenciador)
    except (TarefaNaoEncontrada, ErroArmazenamento, ValueError) as erro:
        # Erros esperados viram uma mensagem curta, sem despejar um traceback
        # assustador para quem só errou o id de uma tarefa.
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    return 0
