# Minecraft 2D — Jogo Web de Gestão de Recursos

Projeto final da unidade curricular **Desenvolvimento de Aplicações Web (DAW)**  
Escola Superior de Ciências Empresariais — IPS  
Ano Letivo 2025/2026

---

## 📋 Requisitos

- Python 3.12+
- pip (gestor de pacotes Python)
- Navegador atual (Chrome, Firefox, Safari, Edge)

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/Luziferri/Web_Python.git
cd minecraft2d
```

### 2. Criar ambiente virtual (recomendado)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux / macOS
# ou
.venv\Scripts\activate      # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

O ficheiro `requirements.txt` contém apenas:

```
Flask
Flask-Login
```

### 4. (Opcional) Base de dados

A base de dados SQLite (`models/minecraft2d.sqlite`) é criada automaticamente na primeira execução.  
Para recriar do zero, basta apagar esse ficheiro.

Para importar o esquema manualmente:

```bash
sqlite3 models/minecraft2d.sqlite < base_dados.sql
```

---

## ▶️ Execução

```bash
python server.py
```

O servidor arranca em: **http://127.0.0.1:8001**

> **Nota:** O servidor corre em modo `debug=False` por predefinição.

---

## 🎮 Como jogar

1. Abrir http://127.0.0.1:8001
2. Registar uma nova conta (username, email, password)
3. No **Dashboard**:
   - **Mover o Steve**: setas direcionais, teclas A/D ou botões na interface
   - **Cortar árvores**: clicar nas árvores no mapa (colunas 2, 8, 15)
   - **Minerar pedras**: clicar nas pedras no mapa (colunas 1, 4, 7, 10)
   - **Construir**: escolher uma receita e clicar num slot vazio
   - **Iniciar tarefa**: após construção pronta, clicar em "Iniciar"
   - **Recolher recompensa**: após tarefa concluída, clicar em "Recolher"
4. **Leaderboard**: ranking global por total de recursos acumulados
5. **Skins**: loja de skins para personalizar o Steve

---

## 🏗️ Estrutura do Projeto

```
minecraft2d/
├── server.py              # Ponto de entrada
├── auth.py                # Rotas de autenticação (Blueprint)
├── game.py                # Rotas do jogo (Blueprint)
├── settings.py            # Configurações
├── extensions.py          # Flask-Login
├── requirements.txt       # Dependências
├── base_dados.sql         # Esquema SQL
├── api_documentacao.md    # Documentação da API
├── README.md              # Este ficheiro
├── models/
│   ├── __init__.py        # Modelos + user_loader
│   ├── database.py        # Classe Database + modelos (User, BuildingSlot, etc.)
│   └── minecraft2d.sqlite # Base de dados SQLite (gerada automaticamente)
├── templates/             # Jinja2 templates
│   ├── base.html, login.html, register.html
│   ├── dashboard.html, leaderboard.html, skins.html
└── static/
    ├── css/               # Folhas de estilo modulares
    ├── js/                # game.js, theme.js
    └── img/               # Imagens do jogo
```

---

## 🔌 API

A documentação completa das rotas está em [`api_documentacao.md`](api_documentacao.md).

### Endpoints principais

| Método | Rota                | Descrição                     |
|--------|---------------------|-------------------------------|
| POST   | `/register`         | Registar nova conta           |
| POST   | `/login`            | Autenticar                    |
| GET    | `/dashboard`        | Página principal do jogo      |
| GET    | `/api/state`        | Estado completo do jogo (JSON)|
| POST   | `/api/build/<id>`   | Iniciar construção            |
| POST   | `/api/task/<id>/start` | Iniciar tarefa              |
| POST   | `/api/task/<id>/collect` | Recolher recompensa        |
| POST   | `/api/chop`         | Cortar árvore                 |
| POST   | `/api/mine-stone`   | Minerar pedra                 |
| GET    | `/api/leaderboard`  | Top 10 jogadores              |
| GET    | `/skins`            | Loja de skins                 |
| POST   | `/api/skin/select`  | Selecionar skin               |

---

## 🧪 Testes

Não existe suite de testes automatizados. Para testar manualmente:

1. Registar dois utilizadores diferentes
2. Construir cada tipo de edifício (Mesa de Trabalho, Fornalha, Mineradora de Diamantes)
3. Completar tarefas e recolher recompensas
4. Verificar leaderboard
5. Testar responsividade (redimensionar janela / mobile)

---

## 🛠️ Tecnologias

- **Backend:** Flask, Flask-Login, SQLite, passlib
- **Frontend:** HTML5, CSS3 (Flexbox, Grid), JavaScript (Fetch API)
- **Autenticação:** Sessões com cookies, password hashing (pbkdf2_sha256)
- **Base de Dados:** SQLite 3 com `sqlite3.Row` factory

---

## 👥 Grupo

**Minecraft2D** — Projeto desenvolvido para a UC de Desenvolvimento de Aplicações Web.
