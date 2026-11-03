"""Persistência: guarda e recupera tarefas de um arquivo JSON."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .modelos import Tarefa


class ErroArmazenamento(Exception):
    """Problema ao ler ou gravar o arquivo de tarefas."""


class RepositorioJSON:
    """Guarda a lista de tarefas em um arquivo JSON.

    Esta classe só sabe *onde e como* os dados ficam salvos. As regras de
    negócio (adicionar, concluir...) ficam em outra camada. Separar assim
    permite trocar o JSON por um banco de dados no futuro sem mexer no resto.
    """

    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho)

    def carregar(self) -> list[Tarefa]:
        """Lê as tarefas do arquivo. Se ele não existir, devolve lista vazia."""
        if not self.caminho.exists():
            return []
        mensagem = f"O arquivo de tarefas está inválido ou corrompido: {self.caminho}"
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
        except json.JSONDecodeError as erro:
            raise ErroArmazenamento(mensagem) from erro

        # Validamos a forma dos dados antes de usá-los: o arquivo pode ter
        # sido editado à mão e não podemos confiar no que vem de fora.
        if not isinstance(dados, list) or not all(isinstance(i, dict) for i in dados):
            raise ErroArmazenamento(mensagem)

        try:
            return [Tarefa.de_dict(item) for item in dados]
        except (KeyError, ValueError, TypeError) as erro:
            raise ErroArmazenamento(mensagem) from erro

    def salvar(self, tarefas: list[Tarefa]) -> None:
        """Grava as tarefas de forma segura.

        Escrevemos num arquivo temporário na mesma pasta e depois o trocamos
        pelo original com os.replace, que é uma operação atômica. Assim, uma
        falha no meio da gravação nunca deixa o arquivo final pela metade.
        """
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        conteudo = json.dumps(
            [tarefa.para_dict() for tarefa in tarefas], ensure_ascii=False, indent=2
        )
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=self.caminho.parent,
            suffix=".tmp",
            delete=False,
        ) as temporario:
            temporario.write(conteudo)
            caminho_temporario = Path(temporario.name)
        os.replace(caminho_temporario, self.caminho)
