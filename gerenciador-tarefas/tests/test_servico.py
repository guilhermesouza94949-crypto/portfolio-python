from datetime import date

import pytest

from gerenciador_tarefas.modelos import Prioridade
from gerenciador_tarefas.repositorio import RepositorioJSON
from gerenciador_tarefas.servico import GerenciadorTarefas, TarefaNaoEncontrada


@pytest.fixture
def caminho(tmp_path):
    return tmp_path / "tarefas.json"


@pytest.fixture
def gerenciador(caminho):
    return GerenciadorTarefas(RepositorioJSON(caminho))


def test_adicionar_gera_ids_sequenciais(gerenciador):
    primeira = gerenciador.adicionar("Estudar")
    segunda = gerenciador.adicionar("Treinar")
    assert (primeira.id, segunda.id) == (1, 2)


def test_remover_do_meio_nao_gera_ids_repetidos(gerenciador):
    gerenciador.adicionar("A")
    gerenciador.adicionar("B")
    gerenciador.adicionar("C")
    gerenciador.remover(2)  # sobram os ids 1 e 3

    nova = gerenciador.adicionar("D")

    ids = [t.id for t in gerenciador.listar()]
    assert nova.id == 4
    assert len(ids) == len(set(ids))


def test_adicionar_titulo_vazio_falha(gerenciador):
    with pytest.raises(ValueError):
        gerenciador.adicionar("   ")


def test_tarefas_sao_persistidas_entre_execucoes(caminho):
    GerenciadorTarefas(RepositorioJSON(caminho)).adicionar("Estudar")

    novo = GerenciadorTarefas(RepositorioJSON(caminho))

    assert [t.titulo for t in novo.listar()] == ["Estudar"]


def test_concluir_marca_e_persiste(gerenciador, caminho):
    gerenciador.adicionar("Estudar")
    gerenciador.concluir(1)

    recarregado = GerenciadorTarefas(RepositorioJSON(caminho))

    assert recarregado.listar()[0].concluida is True


def test_concluir_id_inexistente_falha(gerenciador):
    with pytest.raises(TarefaNaoEncontrada, match="id 99"):
        gerenciador.concluir(99)


def test_remover_tira_a_tarefa_da_lista(gerenciador):
    gerenciador.adicionar("Estudar")
    gerenciador.remover(1)
    assert gerenciador.listar() == []


def test_remover_id_inexistente_falha(gerenciador):
    with pytest.raises(TarefaNaoEncontrada):
        gerenciador.remover(1)


def test_listar_apenas_pendentes(gerenciador):
    gerenciador.adicionar("Feita")
    gerenciador.adicionar("Pendente")
    gerenciador.concluir(1)

    titulos = [t.titulo for t in gerenciador.listar(apenas_pendentes=True)]

    assert titulos == ["Pendente"]


def test_listar_filtrando_por_prioridade(gerenciador):
    gerenciador.adicionar("Importante", prioridade=Prioridade.ALTA)
    gerenciador.adicionar("Tanto faz", prioridade=Prioridade.BAIXA)

    titulos = [t.titulo for t in gerenciador.listar(prioridade=Prioridade.ALTA)]

    assert titulos == ["Importante"]


def test_ordenacao_prioridade_depois_prazo_e_concluidas_no_fim(gerenciador):
    gerenciador.adicionar("Baixa", prioridade=Prioridade.BAIXA)
    gerenciador.adicionar("Alta sem prazo", prioridade=Prioridade.ALTA)
    gerenciador.adicionar(
        "Alta com prazo", prioridade=Prioridade.ALTA, prazo=date(2026, 12, 1)
    )
    gerenciador.adicionar("Média feita", prioridade=Prioridade.MEDIA)
    gerenciador.concluir(4)

    titulos = [t.titulo for t in gerenciador.listar()]

    assert titulos == ["Alta com prazo", "Alta sem prazo", "Baixa", "Média feita"]
