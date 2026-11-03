from datetime import date

import pytest

from gerenciador_tarefas.cli import (
    CAMINHO_PADRAO,
    VARIAVEL_AMBIENTE,
    formatar_tarefa,
    main,
    resolver_caminho,
)
from gerenciador_tarefas.modelos import Prioridade, Tarefa


@pytest.fixture
def arquivo(tmp_path):
    return str(tmp_path / "tarefas.json")


def rodar(arquivo, *argumentos):
    return main(["--arquivo", arquivo, *argumentos])


def test_add_e_list_mostram_a_tarefa(arquivo, capsys):
    assert rodar(arquivo, "add", "Estudar Python", "-p", "alta") == 0
    assert rodar(arquivo, "list") == 0

    saida = capsys.readouterr().out
    assert "Tarefa 1 adicionada: Estudar Python" in saida
    assert "Estudar Python  (alta)" in saida


def test_list_sem_tarefas_avisa(arquivo, capsys):
    assert rodar(arquivo, "list") == 0
    assert "Nenhuma tarefa encontrada." in capsys.readouterr().out


def test_done_marca_com_x(arquivo, capsys):
    rodar(arquivo, "add", "Estudar")
    rodar(arquivo, "done", "1")
    capsys.readouterr()

    rodar(arquivo, "list")

    assert "[x]" in capsys.readouterr().out


def test_remove_apaga_a_tarefa(arquivo, capsys):
    rodar(arquivo, "add", "Estudar")
    rodar(arquivo, "remove", "1")
    capsys.readouterr()

    rodar(arquivo, "list")

    assert "Nenhuma tarefa encontrada." in capsys.readouterr().out


def test_list_pendentes_esconde_concluidas(arquivo, capsys):
    rodar(arquivo, "add", "Feita")
    rodar(arquivo, "add", "Pendente")
    rodar(arquivo, "done", "1")
    capsys.readouterr()

    rodar(arquivo, "list", "--pendentes")

    saida = capsys.readouterr().out
    assert "Pendente" in saida
    assert "Feita" not in saida


def test_id_inexistente_devolve_erro_e_mensagem_no_stderr(arquivo, capsys):
    assert rodar(arquivo, "done", "99") == 1
    assert "Erro: Não existe tarefa com id 99." in capsys.readouterr().err


def test_titulo_vazio_devolve_erro(arquivo, capsys):
    assert rodar(arquivo, "add", "   ") == 1
    assert "título" in capsys.readouterr().err


def test_arquivo_corrompido_devolve_erro(tmp_path, capsys):
    corrompido = tmp_path / "tarefas.json"
    corrompido.write_text("lixo", encoding="utf-8")

    assert rodar(str(corrompido), "list") == 1
    assert "corrompido" in capsys.readouterr().err


@pytest.mark.parametrize(
    "argumentos",
    [
        ["add", "X", "--prazo", "31/12/2026"],
        ["add", "X", "-p", "urgente"],
        ["done", "abc"],
        [],
    ],
)
def test_argumentos_invalidos_encerram_com_codigo_2(arquivo, argumentos):
    # O argparse encerra o programa com código 2 quando o uso está errado.
    with pytest.raises(SystemExit) as saida:
        rodar(arquivo, *argumentos)
    assert saida.value.code == 2


def test_add_com_prazo_valido(arquivo, capsys):
    assert rodar(arquivo, "add", "Entregar", "--prazo", "2099-01-01") == 0
    rodar(arquivo, "list")
    assert "prazo: 2099-01-01" in capsys.readouterr().out


class TestFormatarTarefa:
    def test_tarefa_simples(self):
        tarefa = Tarefa(id=7, titulo="Estudar", prioridade=Prioridade.BAIXA)
        assert formatar_tarefa(tarefa) == "[ ]   7  Estudar  (baixa)"

    def test_tarefa_atrasada_e_sinalizada(self):
        tarefa = Tarefa(id=1, titulo="Estudar", prazo=date(2026, 1, 1))
        linha = formatar_tarefa(tarefa, hoje=date(2026, 2, 1))
        assert linha.endswith("prazo: 2026-01-01  ATRASADA")


class TestResolverCaminho:
    def test_argumento_tem_prioridade(self, monkeypatch, tmp_path):
        monkeypatch.setenv(VARIAVEL_AMBIENTE, "/outro/lugar.json")
        escolhido = tmp_path / "meu.json"
        assert resolver_caminho(escolhido) == escolhido

    def test_variavel_de_ambiente_vence_o_padrao(self, monkeypatch):
        monkeypatch.setenv(VARIAVEL_AMBIENTE, "/via/ambiente.json")
        assert str(resolver_caminho(None)) == "/via/ambiente.json"

    def test_sem_nada_usa_o_padrao(self, monkeypatch):
        monkeypatch.delenv(VARIAVEL_AMBIENTE, raising=False)
        assert resolver_caminho(None) == CAMINHO_PADRAO
