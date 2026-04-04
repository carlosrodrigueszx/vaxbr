# 🩺 VaxBR — API REST de Gestão de Vacinação

API REST desenvolvida com **FastAPI** e persistência em **Delta Lake** para gerenciamento de registros de vacinação municipal.  
Projeto da disciplina de **Desenvolvimento de Software para Persistência** — UFC, campus Quixadá.

---

## 📋 Descrição

O sistema expõe endpoints para gerenciamento completo de registros vacinais, operando diretamente sobre arquivos Delta Lake **sem carregar os dados integralmente na memória**. A entidade central é **Vacina (vax)**.

---

## 🗂️ Entidade Principal — `Vacina`

| Atributo     | Tipo  | Descrição                                       |
|--------------|-------|-------------------------------------------------|
| `vax_id`     | `int` | Identificador único (autoincremento via `.seq`) |
| `name`       | `str` | Nome da vacina                                  |
| `target`     | `str` | Vírus-alvo (ex: Influenza, Rinovírus)           |
| `illness`    | `str` | Doença combatida (ex: COVID-19, HPV)            |
| `quantity`   | `int` | Quantidade de doses armazenadas                 |
| `id_manufac` | `int` | Identificador do fabricante                     |

---

## ⚙️ Endpoints

### Vacinas — `/vax`

| ID | Método | Rota | Descrição |
|----|--------|------|-----------|
| F1 | `POST` | `/vax/insert` | Insere uma nova vacina |
| F2 | `GET` | `/vax/all` | Listagem paginada (`page`, `page_size`, filtros opcionais por `illness` e `target`) |
| F3 | `GET` | `/vax/{vax_id}` | Busca vacina por ID |
| F3 | `PATCH` | `/vax/{vax_id}` | Atualiza campos de uma vacina |
| F3 | `PUT` | `/vax/{vax_id}` | Substitui (upsert) uma vacina |
| F3 | `DELETE` | `/vax/{vax_id}` | Remove uma vacina (retorna 404 se não encontrada) |
| F4 | `GET` | `/vax/count` | Retorna total de registros |
| F5 | `GET` | `/vax/export/csv` | Exportação CSV via streaming |
| F6 | `GET` | `/vax/export/zip` | Exportação CSV compactada `.zip` via streaming |

### Hash — `/hash`

| ID | Método | Rota | Descrição |
|----|--------|------|-----------|
| F7 | `POST` | `/hash/` | Gera hash de um valor (`MD5`, `SHA-1` ou `SHA-256`) |

**Exemplo de requisição F7:**
```json
{
  "value": "texto qualquer",
  "algorithm": "SHA-256"
}
```

**Exemplo de resposta:**
```json
{
  "value": "texto qualquer",
  "algorithm": "SHA-256",
  "hash": "b94d27b9934d3e08a52e52d7da7dabfa..."
}
```

---

## 🗃️ Estrutura do Projeto

```
vaxbr/
├── app/
│   ├── __init__.py
│   ├── main.py                   # Entrypoint da aplicação
│   ├── core/
│   │   ├── __init__.py
│   │   └── logger.py             # Configuração centralizada de logs
│   ├── data/
│   │   └── .seq                  # Controle de autoincremento de ID
│   ├── db/
│   │   ├── __init__.py
│   │   └── utils.py              # Utilitários Delta Lake (GenID, etc.)
│   ├── internal/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── vax_repo.py           # Operações CRUD no Delta Lake
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── vax_router.py         # Rotas da entidade Vacina
│   │   └── hash_router.py        # Rota de geração de hash (F7)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── vax.py                # Schemas Pydantic
│   ├── services/
│   │   └── __init__.py
│   └── tools/
│       ├── __init__.py
│       ├── faker_utils.py        # Geração de dados com Faker
│       └── csv_loader.py         # Carga de dados a partir de CSV
├── tests/
│   └── __init__.py
├── vax.csv                   # Dataset inicial de vacinas
├── .gitignore
├── divisao_tarefas.txt
├── pyproject.toml
└── README.md
```

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) ou `pip`

### 1. Clone o repositório

```bash
git clone https://github.com/carlosrodrigueszx/vaxbr.git
cd vaxbr
```

### 2. Crie e ative o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

**Com uv (recomendado):**
```bash
uv sync
```

**Com pip:**
```bash
pip install .
```

### 4. Execute a API

```bash
uvicorn app.main:app --reload
```

A documentação interativa estará disponível em:  
👉 `http://localhost:8000/docs`

---

## 🗄️ Populando o banco com dados iniciais

### Opção 1 — CSV (recomendado)

Utiliza o arquivo `vax.csv` já incluso no repositório, preservando os IDs originais:

```bash
python app/tools/csv_loader.py
```

### Opção 2 — Faker

Gera 1.000+ registros realistas com a biblioteca `Faker` (localização `pt_BR`):

```bash
python app/tools/faker_utils.py
```

> ⚠️ No Linux/Mac, substitua `python` por `python3` caso necessário.

### Resetando o banco

Para apagar todos os dados e recomeçar do zero:

**Windows (PowerShell):**
```powershell
Remove-Item -Recurse -Force app/tmp/vax
```

**Linux/Mac:**
```bash
rm -rf app/tmp/vax
```

---

## 📝 Logs

Configurados em `app/core/logger.py` e aplicados em todas as camadas (routers e repositório).  
Os logs são exibidos no terminal no formato:

```
[YYYY-MM-DD HH:MM:SS] LEVEL - module - mensagem
```

Exemplo de saída:
```
[2026-04-03 21:30:32] INFO    - app.main                   - VaxBR API iniciada com sucesso
[2026-04-03 21:30:45] INFO    - app.routers.vax_router     - Inserindo nova vacina: {...}
[2026-04-03 21:30:50] WARNING - app.routers.vax_router     - Vacina não encontrada: vax_id=999
[2026-04-03 21:31:00] INFO    - app.repositories.vax_repo  - Vacina deletada com sucesso — vax_id=24
```

---

## 🛠️ Stack

| Tecnologia | Uso |
|------------|-----|
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web |
| [Pydantic](https://docs.pydantic.dev/) | Validação de dados |
| [deltalake](https://delta-io.github.io/delta-rs/) | Persistência em Delta Lake |
| [Faker](https://faker.readthedocs.io/) | Geração de dados realistas |
| Python `logging` | Registro centralizado de eventos |
| Python 3.12+ | Linguagem base |

---

## 👥 Equipe

| Nome | Matrícula | Curso |
|------|-----------|-------|
| Carlos Daniel Rodrigues de Oliveira | 566429 | Ciência da Computação |
| Milena Helen Diniz Gomes | 564757 | Ciência da Computação |
| Yasmin de Lima Marques | 567615 | Ciência da Computação |

---

## 📄 Licença

Projeto acadêmico — Desenvolvimento de Software para Persistência · UFC
