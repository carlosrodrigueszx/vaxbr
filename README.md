# 🩺 API REST — Sistema de Gestão de Vacinação

API REST desenvolvida com **FastAPI** para gerenciamento de registros de vacinação municipal, com persistência em **Delta Lake**. O projeto faz parte do Trabalho Prático da disciplina de Desenvolvimento de Software para Persistência (UFC - campus Quixadá).

---

## 📋 Descrição

O sistema expõe endpoints para gerenciamento completo de registros vacinais, operando diretamente sobre arquivos Delta Lake sem carregar os dados integralmente na memória. A entidade central é **Vacina (vax)**, integrada ao domínio de controle vacinal já modelado na primeira entrega da disciplina.

---

## 🗂️ Entidade Principal

**Vacina**

| Atributo | Tipo | Descrição |
|---|---|---|
| `id` | `int` | Identificador único (autoincremento via `.seq`) |
| `name` | `str` | Nome da vacina |
| `target` | `str` | Vírus da doença (ex: Influenza, Rinovírus) |
| `illness` | `str` | Doença combatida (ex: COVID-19, HPV) |
| `quantity` | `int` | Quantidade de doses armazenadas |

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
vaxbr/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   ├── internal/
│   │   ├── __init__.py
│   │   └── admin.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── vax.py
│   ├── services/
│   │   ├── __init__.py
│   └── db/
│       ├── __init__.py
│       ├── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_crud.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── run.sh
```

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.12
- [uv](https://docs.astral.sh/uv/) ou `pip`

### Instalação

```bash
# Clone o repositório
git clone https://github.com/carlosrodrigueszx/vaxbr.git
cd vaxbr

# Instale as dependências
pip install .

# Com uv
uv sync
```

### Executando a API

```bash
uvicorn app.main:app --reload
```

A documentação interativa estará disponível em `http://localhost:8000/docs`.

### Populando o banco com dados iniciais

```bash
python3 tools/faker_gen.py
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
