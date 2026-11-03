from datetime import date

import pytest

from gerenciador_tarefas.modelos import Prioridade, Tarefa
from gerenciador_tarefas.repositorio import ErroArmazenamento, RepositorioJSON


def test_carregar_arquivo_inexistente_devolve_lista_vazia(tmp_path):
    repositorio = RepositorioJSON(tmp_path / "nao_existe.json")
    assert repositorio.carregar() == []


def test_salvar_e_carregar_preserva_as_tarefas(tmp_path):
    repositorio = RepositorioJSON(tmp_path / "tarefas.json")
    tarefas = [
        Tarefa(id=1, titulo="Estudar", prioridade=Prioridade.ALTA, prazo=date(2026, 12, 1)),
        Tarefa(id=2, titulo="Lavar a louça", concluida=True),
    ]

    repositorio.salvar(tarefas)

    assert repositorio.carregar() == tarefas


def test_salvar_cria_pastas_que_nao_existem(tmp_path):
    repositorio = RepositorioJSON(tmp_path / "a" / "b" / "tarefas.json")
    repositorio.salvar([Tarefa(id=1, titulo="Estudar")])
    assert (tmp_path / "a" / "b" / "tarefas.json").exists()


def test_salvar_nao_deixa_arquivos_temporarios(tmp_path):
    repositorio = RepositorioJSON(tmp_path / "tarefas.json")
    repositorio.salvar([Tarefa(id=1, titulo="Estudar")])
    assert [arquivo.name for arquivo in tmp_path.iterdir()] == ["tarefas.json"]


def test_salvar_preserva_acentos_no_arquivo(tmp_path):
    caminho = tmp_path / "tarefas.json"
    RepositorioJSON(caminho).salvar([Tarefa(id=1, titulo="Revisão de matemática")])
    assert "Revisão de matemática" in caminho.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "conteudo",
    [
        "isto não é json",
        '{"id": 1}',
        '[{"id": 1}]',
        '[{"id": 1, "titulo": "X", "prioridade": "inexistente"}]',
    ],
)
def test_arquivo_corrompido_gera_erro_claro(tmp_path, conteudo):
    caminho = tmp_path / "tarefas.json"
    caminho.write_text(conteudo, encoding="utf-8")

    with pytest.raises(ErroArmazenamento, match="inválido ou corrompido"):
        RepositorioJSON(caminho).carregar()
