"""Regras de negócio: o que se pode fazer com as tarefas."""

from __future__ import annotations

from datetime import date

from .modelos import Prioridade, Tarefa
from .repositorio import RepositorioJSON


class TarefaNaoEncontrada(Exception):
    """Nenhuma tarefa com o id informado."""


class GerenciadorTarefas:
    """Coordena as operações sobre a lista de tarefas.

    Recebe o repositório pronto de fora (injeção de dependência). A classe
    não precisa saber onde os dados ficam guardados, só que pode pedir para
    carregar e salvar.
    """

    def __init__(self, repositorio: RepositorioJSON) -> None:
        self._repositorio = repositorio
        self._tarefas = repositorio.carregar()

    def adicionar(
        self,
        titulo: str,
        prioridade: Prioridade = Prioridade.MEDIA,
        prazo: date | None = None,
    ) -> Tarefa:
        tarefa = Tarefa(
            id=self._proximo_id(), titulo=titulo, prioridade=prioridade, prazo=prazo
        )
        self._tarefas.append(tarefa)
        self._salvar()
        return tarefa

    def listar(
        self,
        apenas_pendentes: bool = False,
        prioridade: Prioridade | None = None,
    ) -> list[Tarefa]:
        """Devolve as tarefas filtradas e ordenadas.

        Ordem: pendentes primeiro, depois maior prioridade, depois prazo
        mais próximo (tarefas sem prazo vão para o fim do grupo) e, por
        último, a ordem de criação.
        """
        resultado = self._tarefas
        if apenas_pendentes:
            resultado = [t for t in resultado if not t.concluida]
        if prioridade is not None:
            resultado = [t for t in resultado if t.prioridade is prioridade]
        return sorted(
            resultado,
            key=lambda t: (
                t.concluida,
                -t.prioridade.peso,
                t.prazo is None,
                t.prazo or date.max,
                t.id,
            ),
        )

    def concluir(self, id_tarefa: int) -> Tarefa:
        tarefa = self._buscar(id_tarefa)
        tarefa.concluir()
        self._salvar()
        return tarefa

    def remover(self, id_tarefa: int) -> Tarefa:
        tarefa = self._buscar(id_tarefa)
        self._tarefas.remove(tarefa)
        self._salvar()
        return tarefa

    def _buscar(self, id_tarefa: int) -> Tarefa:
        for tarefa in self._tarefas:
            if tarefa.id == id_tarefa:
                return tarefa
        raise TarefaNaoEncontrada(f"Não existe tarefa com id {id_tarefa}.")

    def _proximo_id(self) -> int:
        # Usamos o maior id + 1 (e não o tamanho da lista) para garantir que
        # dois ids nunca colidam. Exemplo: com as tarefas 1, 2 e 3, remover a
        # 2 deixa [1, 3]; usar o tamanho (2) + 1 geraria outro id 3.
        return max((t.id for t in self._tarefas), default=0) + 1

    def _salvar(self) -> None:
        self._repositorio.salvar(self._tarefas)
