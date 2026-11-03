"""Modelos de dados: o que é uma tarefa e quais prioridades existem."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class Prioridade(Enum):
    """Níveis de prioridade de uma tarefa.

    Usar um Enum (em vez de strings soltas) impede valores inválidos
    como "urgentíssima" e deixa o código autoexplicativo.
    """

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"

    @property
    def peso(self) -> int:
        """Número usado para ordenar: quanto maior, mais importante."""
        return {Prioridade.BAIXA: 1, Prioridade.MEDIA: 2, Prioridade.ALTA: 3}[self]

    @classmethod
    def de_texto(cls, texto: str) -> Prioridade:
        """Converte um texto digitado pelo usuário em Prioridade."""
        try:
            return cls(texto.strip().lower())
        except ValueError as erro:
            validas = ", ".join(p.value for p in cls)
            raise ValueError(
                f"Prioridade inválida: {texto!r}. Use uma destas: {validas}."
            ) from erro


@dataclass
class Tarefa:
    """Uma tarefa do usuário.

    O decorador @dataclass gera automaticamente __init__, __repr__ e __eq__,
    o que deixa a classe curta e focada nos dados e nas regras dela.
    """

    id: int
    titulo: str
    prioridade: Prioridade = Prioridade.MEDIA
    prazo: date | None = None
    concluida: bool = False

    def __post_init__(self) -> None:
        # A validação mora na própria classe: não existe Tarefa sem título.
        self.titulo = self.titulo.strip()
        if not self.titulo:
            raise ValueError("O título da tarefa não pode ser vazio.")

    def concluir(self) -> None:
        """Marca a tarefa como concluída."""
        self.concluida = True

    def esta_atrasada(self, hoje: date | None = None) -> bool:
        """Uma tarefa está atrasada se tem prazo vencido e ainda não foi concluída.

        O parâmetro `hoje` existe para facilitar os testes: assim não
        dependemos da data real do computador.
        """
        if self.concluida or self.prazo is None:
            return False
        return self.prazo < (hoje or date.today())

    def para_dict(self) -> dict:
        """Converte para um dicionário simples, pronto para virar JSON."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "prioridade": self.prioridade.value,
            "prazo": self.prazo.isoformat() if self.prazo else None,
            "concluida": self.concluida,
        }

    @classmethod
    def de_dict(cls, dados: dict) -> Tarefa:
        """Reconstrói uma Tarefa a partir do dicionário lido do JSON."""
        prazo = dados.get("prazo")
        return cls(
            id=dados["id"],
            titulo=dados["titulo"],
            prioridade=Prioridade(dados["prioridade"]),
            prazo=date.fromisoformat(prazo) if prazo else None,
            concluida=dados.get("concluida", False),
        )
