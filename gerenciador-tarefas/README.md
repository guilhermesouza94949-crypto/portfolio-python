# Gerenciador de Tarefas

Gerenciador de tarefas em linha de comando, feito em Python com orientação a objetos e testes automatizados. Permite adicionar tarefas com prioridade e prazo, listar, concluir e remover, e guarda tudo em um arquivo JSON.

## Exemplo de uso

```console
$ tarefas add "Entregar trabalho de POO" -p alta --prazo 2026-12-10
Tarefa 1 adicionada: Entregar trabalho de POO
$ tarefas add "Revisar anotações"
Tarefa 2 adicionada: Revisar anotações
$ tarefas done 2
Tarefa 2 concluída: Revisar anotações
$ tarefas list
[ ]   1  Entregar trabalho de POO  (alta)  prazo: 2026-12-10
[x]   2  Revisar anotações  (media)
```

Tarefas com prazo vencido e ainda abertas aparecem com o aviso `ATRASADA`.

## Como instalar e rodar

Requer Python 3.10 ou mais novo.

```console
# 1. entre na pasta do projeto
cd gerenciador-tarefas

# 2. crie e ative um ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux ou macOS

# 3. instale o projeto (com as ferramentas de teste)
pip install -e ".[dev]"
```

Depois da instalação, o comando `tarefas` fica disponível. Também dá para rodar com `python -m gerenciador_tarefas`.

## Comandos

| Comando | O que faz |
| --- | --- |
| `tarefas add "texto" [-p baixa\|media\|alta] [--prazo AAAA-MM-DD]` | adiciona uma tarefa |
| `tarefas list [--pendentes] [-p prioridade]` | lista, ordenando por situação, prioridade e prazo |
| `tarefas done ID` | marca como concluída |
| `tarefas remove ID` | remove a tarefa |

Por padrão, as tarefas ficam em `~/.gerenciador_tarefas/tarefas.json`. Para usar outro arquivo, passe `--arquivo caminho.json` antes do comando ou defina a variável de ambiente `GERENCIADOR_TAREFAS_ARQUIVO`.

## Como o código está organizado

```text
src/gerenciador_tarefas/
├── modelos.py       # Tarefa e Prioridade: os dados e as regras da própria tarefa
├── repositorio.py   # RepositorioJSON: ler e gravar o arquivo
├── servico.py       # GerenciadorTarefas: adicionar, listar, concluir, remover
└── cli.py           # interface de linha de comando (argparse)
tests/               # testes de cada camada
```

O código é dividido em camadas, e cada uma tem uma responsabilidade só:

- **Modelo:** a `Tarefa` valida a si mesma (não existe tarefa sem título) e sabe dizer se está atrasada.
- **Repositório:** só sabe guardar e recuperar dados. Trocar o JSON por um banco de dados só mexeria nessa camada.
- **Serviço:** concentra as regras de negócio e recebe o repositório pronto de fora (injeção de dependência), o que facilita os testes.
- **CLI:** só traduz o que o usuário digitou em chamadas ao serviço e formata a saída.

### Decisões de design

- **Gravação atômica:** o arquivo é escrito primeiro num temporário e depois trocado com `os.replace`. Se o programa travar no meio, o arquivo anterior continua intacto.
- **Validação do que vem de fora:** um JSON editado à mão ou corrompido gera uma mensagem de erro clara, e não um traceback.
- **Ids sem colisão:** o próximo id é o maior existente mais um, e não o tamanho da lista.
- **Testabilidade:** `esta_atrasada` aceita a data de "hoje" como parâmetro, então os testes não dependem do relógio do computador.

## Testes

```console
pytest
```

Os testes cobrem o modelo, a persistência (incluindo arquivos corrompidos), as regras do serviço e a linha de comando, tanto nos caminhos de sucesso quanto nos de erro.

## Licença

MIT. Veja o arquivo [LICENSE](../LICENSE) na raiz do repositório.
