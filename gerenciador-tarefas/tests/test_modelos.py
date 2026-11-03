from datetime import date

import pytest

from gerenciador_tarefas.modelos import Prioridade, Tarefa


class TestPrioridade:
    def test_de_texto_aceita_maiusculas_e_espacos(self):
        assert Prioridade.de_texto("  ALTA ") is Prioridade.ALTA

    def test_de_texto_rejeita_valor_invalido(self):
        with pytest.raises(ValueError, match="Prioridade inválida"):
            Prioridade.de_texto("urgentissima")

    def test_pesos_seguem_a_ordem_de_importancia(self):
        assert Prioridade.BAIXA.peso < Prioridade.MEDIA.peso < Prioridade.ALTA.peso


class TestTarefa:
    def test_valores_padrao(self):
        tarefa = Tarefa(id=1, titulo="Estudar")
        assert tarefa.prioridade is Prioridade.MEDIA
        assert tarefa.prazo is None
        assert tarefa.concluida is False

    def test_titulo_e_limpo_de_espacos(self):
        assert Tarefa(id=1, titulo="  Estudar  ").titulo == "Estudar"

    def test_titulo_vazio_e_rejeitado(self):
        with pytest.raises(ValueError, match="título"):
            Tarefa(id=1, titulo="   ")

    def test_concluir_marca_como_concluida(self):
        tarefa = Tarefa(id=1, titulo="Estudar")
        tarefa.concluir()
        assert tarefa.concluida is True

    def test_atrasada_quando_prazo_venceu(self):
        tarefa = Tarefa(id=1, titulo="Estudar", prazo=date(2026, 1, 1))
        assert tarefa.esta_atrasada(hoje=date(2026, 1, 2)) is True

    def test_nao_atrasada_no_proprio_dia_do_prazo(self):
        tarefa = Tarefa(id=1, titulo="Estudar", prazo=date(2026, 1, 1))
        assert tarefa.esta_atrasada(hoje=date(2026, 1, 1)) is False

    def test_concluida_nunca_esta_atrasada(self):
        tarefa = Tarefa(id=1, titulo="Estudar", prazo=date(2026, 1, 1))
        tarefa.concluir()
        assert tarefa.esta_atrasada(hoje=date(2026, 6, 1)) is False

    def test_sem_prazo_nunca_esta_atrasada(self):
        assert Tarefa(id=1, titulo="Estudar").esta_atrasada() is False

    def test_ida_e_volta_para_dict(self):
        original = Tarefa(
            id=3,
            titulo="Entregar trabalho",
            prioridade=Prioridade.ALTA,
            prazo=date(2026, 11, 10),
            concluida=True,
        )
        assert Tarefa.de_dict(original.para_dict()) == original
