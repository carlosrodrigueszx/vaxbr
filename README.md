# 🩺 API REST — Sistema de Gestão de Vacinação Municipal

API REST desenvolvida com **FastAPI** para gerenciamento de registros de vacinação municipal, com persistência em **Delta Lake**. O projeto faz parte do Trabalho Prático da disciplina de Desenvolvimento de Software para Persistência (UFC).

---

## 📋 Descrição

O sistema expõe endpoints para gerenciamento completo de registros vacinais, operando diretamente sobre arquivos Delta Lake sem carregar os dados integralmente na memória. A entidade central é **Vacina**, integrada ao domínio de controle vacinal municipal já modelado na primeira entrega da disciplina.

---

## 🗂️ Entidade Principal

**Vacina**

| Atributo | Tipo | Descrição |
|---|---|---|
| `id` | `int` | Identificador único (autoincremento via `.seq`) |
| `nome` | `str` | Nome da vacina |
| `fabricante` | `str` | Nome do fabricante |
| `publico_alvo` | `str` | Público-alvo (ex: crianças, adultos, idosos) |
| `numero_doses` | `int` | Quantidade de doses necessárias |
| `validade` | `date` | Data de validade do lote |
| `doenca` | `str` | Doença que a vacina previne |

---

## ⚙️ Funcionalidades

| ID | Endpoint | Método | Descrição |
|---|---|---|---|
| F1 | `/vacinas` | `POST` | Inserção de nova vacina |
| F2 | `/vacinas` | `GET` | Listagem paginada (`page` e `page_size` via query string) |
| F3 | `/vacinas/{id}` | `GET` `PUT` `DELETE` | CRUD completo por ID |
| F4 | `/vacinas/count` | `GET` | Contagem total de registros |
| F5 | `/vacinas/export/csv` | `GET` | Exportação CSV via streaming |
| F6 | `/vacinas/export/csv/zip` | `GET` | Exportação CSV compactada (`.zip`) via streaming |
| F7 | `/hash` | `POST` | Geração de hash (`MD5`, `SHA-1` ou `SHA-256`) de um valor |

---

## 🗃️ Estrutura do Projeto

```
.
├── app/
│   ├── main.py                  # Entrypoint FastAPI
│   ├── entity/
│   │   └── vacina.py            # Modelo Pydantic da entidade
│   ├── db/
│   │   └── delta_repository.py  # Classe de persistência Delta Lake (CRUD)
│   └── routers/
│       ├── vacinas.py           # Endpoints F1, F2, F3, F4
│       ├── export.py            # Endpoints F5, F6
│       └── hash_router.py       # Endpoint F7
├── scripts/
│   └── seed.py                  # Script de carga inicial (1000+ registros via Faker)
├── divisao_tarefas.txt          # Distribuição de tarefas da equipe
└── pyproject.toml               # Dependências do projeto
```

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.12
- [uv](https://docs.astral.sh/uv/) ou `pip`

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/vacinacao-api.git
cd vacinacao-api

# Instale as dependências
pip install .
```

### Executando a API

```bash
uvicorn app.main:app --reload
```

A documentação interativa estará disponível em `http://localhost:8000/docs`.

### Populando o banco com dados iniciais

```bash
python scripts/seed.py
```

Isso irá gerar **1.000+ registros** realistas usando a biblioteca `Faker` com localização `pt_BR`.

---

## 🛠️ Stack

| Tecnologia | Uso |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web |
| [Pydantic](https://docs.pydantic.dev/) | Validação de dados |
| [deltalake](https://delta-io.github.io/delta-rs/) | Persistência em Delta Lake |
| [Faker](https://faker.readthedocs.io/) | Geração de dados realistas |
| Python 3.12 | Linguagem base |

---

## 👥 Equipe

| Nome | Matrícula | Curso |
|---|---|---|
| Carlos Daniel Rodrigues de Oliveira | 566429 | Ciência da Computação |
| Milena Helen Diniz Gomes | 564757 | Ciência da Computação |
| Yasmin de Lima Marques | 567615 | Ciência da Computação |

---

## 📄 Licença

Projeto acadêmico — Desenvolvimento de Software para Persistência · UFC
