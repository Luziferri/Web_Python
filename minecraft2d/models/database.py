import os
import sqlite3

from datetime import datetime

from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256 as hasher

# ─── Utilitários de data/hora ─────────────────────────────────────────────────
# O jogo usa temporizadores (construção, tarefas, cooldown de recursos).
# As datas são guardadas na BD como string "AAAA-MM-DDTHH:MM:SS" porque o SQLite
# não tem um tipo datetime nativo. Estas funções convertem entre string e objeto datetime.

# Converte uma string "AAAA-MM-DDTHH:MM:SS" guardada na BD para um objeto datetime do Python.
# _parse_datetime / _format_datetime: ❌ fora (labs não usam timestamps). Necessário para calcular tempos de construção, tarefas e cooldown de recursos.
def _parse_datetime(value):
    if value is None or value == "":
        return None
    if type(value) == datetime:
        return value
    # Parte a string pelo "T" para separar data de hora
    parts = value.split("T")
    date_parts = parts[0].split("-")
    time_parts = parts[1].split(":") if len(parts) > 1 else ["0", "0", "0"]
    return datetime(
        int(date_parts[0]),
        int(date_parts[1]),
        int(date_parts[2]),
        int(time_parts[0]),
        int(time_parts[1]),
        int(time_parts[2]) if len(time_parts) > 2 else 0,
    )


# Converte um objeto datetime do Python para string "AAAA-MM-DDTHH:MM:SS" para guardar na BD.
def _format_datetime(value):
    if value is None:
        return None
    if type(value) == str:
        return value
    return "%04d-%02d-%02dT%02d:%02d:%02d" % (value.year, value.month, value.day, value.hour, value.minute, value.second)


# ─── Modelos ──────────────────────────────────────────────────────────────────
# Cada modelo representa uma tabela da BD e tem:
#   - Um construtor __init__ com os campos da tabela
#   - Um método de classe from_row que converte uma linha sqlite3.Row para o objeto
#   - Os objetos são usados tanto na lógica do jogo como na serialização JSON

# Modelo User com UserMixin para integração com Flask-Login ✅ (Lab 08).
# set_password / check_password com passlib: ✅ (Lab 08).
# Representa um jogador. Tem os recursos (wood, stone, iron, diamonds) que o
# jogador acumula, o nível do machado (has_axe, axe_level) e a skin escolhida.
class User(UserMixin):
    # Construtor: guarda os dados do user vindos da BD ou do registo.
    # wood/stone começam a 26 (recursos iniciais do jogo).
    def __init__(self, id, username, email, password_hash, wood=26, stone=26, iron=0, diamonds=0, created_at=None, has_axe=0, axe_level=0, skin="default"):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        # wood e stone são específicos do jogo (não existem no modelo User do Lab 08).
        self.wood = wood      # Recurso madeira, obtido ao cortar árvores
        self.stone = stone    # Recurso pedra, obtido ao minerar pedras
        self.iron = iron      # Recurso ferro, obtido como recompensa da Fornalha
        self.diamonds = diamonds  # Recurso diamante, obtido como recompensa da Mineradora
        self.created_at = created_at
        # has_axe / axe_level: ✅ (INTEGER DEFAULT, igual a wood/stone). Funcionalidade extra do projeto (machado da Mesa de Trabalho).
        self.has_axe = has_axe      # 1 se o jogador já fabricou um machado, 0 caso contrário
        self.axe_level = axe_level  # Nível do machado (1, 2, 3...), aumenta o rendimento de madeira
        self.skin = skin

    # Recebe uma password em texto limpo e guarda o seu hash. ✅ (Lab 08).
    def set_password(self, password):
        self.password_hash = hasher.hash(password)

    # Verifica se a password em texto limpo corresponde ao hash guardado. ✅ (Lab 08).
    def check_password(self, password):
        return hasher.verify(password, self.password_hash)

    # from_row com sqlite3.Row: ❌ fora da matéria (lab usa tuple unpacking, não Row factory). Usado para mapear colunas da BD para atributos do modelo de forma legível e evitar erros de índice.
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            wood=row["wood"],
            stone=row["stone"],
            created_at=_parse_datetime(row["created_at"]),
            has_axe=row["has_axe"] if "has_axe" in row.keys() else 0,
            axe_level=row["axe_level"] if "axe_level" in row.keys() else 0,
            iron=row["iron"] if "iron" in row.keys() else 0,
            diamonds=row["diamonds"] if "diamonds" in row.keys() else 0,
            skin=row["skin"] if "skin" in row.keys() else "default",
        )


# BuildingSlot: modelo para slots de construção (inexistente nos labs). ❌ fora.
# Faz parte das mecânicas do projeto (3+ construções, estados, temporizadores). Necessário para gerir os 4 slots de construção por jogador.
# Estados possíveis de um slot:
#   empty       → vazio, pode receber uma construção nova
#   building    → construção em progresso (temporizador ativo)
#   ready       → construção terminada, pronta para iniciar tarefa
#   working     → tarefa em progresso (a produzir recursos)
#   collectable → tarefa terminada, recompensa pronta para recolher
class BuildingSlot:
    # Cada slot tem um número (1-4), um tipo de construção opcional, um estado (empty/building/ready/working/collectable),
    # e timestamps para controlar quando a construção/tarefa termina.
    def __init__(self, id, user_id, slot_number, building_type=None, state="empty", action_type=None, started_at=None, ready_at=None, created_at=None):
        self.id = id
        self.user_id = user_id      # ID do jogador dono do slot
        self.slot_number = slot_number  # Número do slot (1 a 4), único por jogador
        self.building_type = building_type  # Chave da construção (ex: "cabana", "mina", "forja")
        self.state = state          # Estado atual: empty/building/ready/working/collectable
        self.action_type = action_type  # Descrição da tarefa atual (ex: "Extrair diamantes")
        self.started_at = started_at    # Quando a construção/tarefa começou
        self.ready_at = ready_at        # Quando a construção/tarefa vai terminar
        self.created_at = created_at

    # Converte uma linha da BD (sqlite3.Row) num objeto BuildingSlot. ❌ fora (lab usa tuple unpacking).
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            slot_number=row["slot_number"],
            building_type=row["building_type"],
            state=row["state"],
            action_type=row["action_type"],
            started_at=_parse_datetime(row["started_at"]),
            ready_at=_parse_datetime(row["ready_at"]),
            created_at=_parse_datetime(row["created_at"]),
        )


# ActionLog: histórico de ações do jogador (inexistente nos labs). ❌ fora. Necessário para registar e mostrar o histórico de ações na dashboard.
# Cada vez que o jogador faz uma ação importante (cortar árvore, construir, recolher recompensa...),
# é criado um registo com uma mensagem de texto e a data/hora.
class ActionLog:
    # Armazena uma mensagem de texto (ex: "Árvore cortada: +4 madeira") com a data em que ocorreu.
    def __init__(self, id, user_id, message, created_at=None):
        self.id = id
        self.user_id = user_id
        self.message = message    # Texto descritivo da ação
        self.created_at = created_at  # Quando a ação ocorreu

    # Converte uma linha da BD num objeto ActionLog.
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            message=row["message"],
            created_at=_parse_datetime(row["created_at"]),
        )


# Tree: modelo para árvores no mapa (inexistente nos labs). ❌ fora. Necessário para gerir recursos naturais no mapa com sistema de cooldown.
# Cada árvore está numa posição fixa do mapa (coluna). Quando o jogador a corta,
# o campo chopped_at regista o momento, e a árvore fica indisponível durante
# RESOURCE_RESPAWN_SECONDS segundos (cooldown).
class Tree:
    # Cada árvore está numa coluna do mapa (column). chopped_at regista quando foi cortada (para cooldown).
    def __init__(self, id, column, chopped_at=None, removed_at=None, created_at=None):
        self.id = id
        self.column = column          # Coluna do mapa onde a árvore está
        self.chopped_at = chopped_at  # Momento em que foi cortada (None = disponível)
        self.removed_at = removed_at  # Se foi removida permanentemente
        self.created_at = created_at

    # Converte uma linha da BD num objeto Tree.
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            column=row["column"],
            chopped_at=_parse_datetime(row["chopped_at"]),
            removed_at=_parse_datetime(row["removed_at"]),
            created_at=_parse_datetime(row["created_at"]),
        )


# Stone: modelo para pedras no mapa (inexistente nos labs). ❌ fora. Necessário para o segundo recurso do jogo, com a mesma lógica de cooldown das árvores.
# Funciona exatamente como Tree mas para o recurso pedra.
class Stone:
    # Cada pedra está numa coluna do mapa. mined_at regista quando foi minerada (para cooldown).
    def __init__(self, id, column, mined_at=None, removed_at=None, created_at=None):
        self.id = id
        self.column = column          # Coluna do mapa onde a pedra está
        self.mined_at = mined_at      # Momento em que foi minerada (None = disponível)
        self.removed_at = removed_at
        self.created_at = created_at

    # Converte uma linha da BD num objeto Stone.
    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            column=row["column"],
            mined_at=_parse_datetime(row["mined_at"]),
            removed_at=_parse_datetime(row["removed_at"]),
            created_at=_parse_datetime(row["created_at"]),
        )


# ─── Database ─────────────────────────────────────────────────────────────────
# Classe principal que gere toda a interação com a base de dados SQLite.
# Fornece métodos para criar tabelas, inserir/consultar/atualizar dados de users,
# slots, construções, árvores, pedras e histórico de ações.
# Cada conexão usa sqlite3.Row como row_factory para aceder colunas por nome.
class Database:
    # Construtor: recebe o caminho do ficheiro .sqlite, cria o diretório se necessário e cria as tabelas.
    def __init__(self, dbfile):
        self.dbfile = dbfile
        directory = os.path.dirname(dbfile)
        # Criar diretório se não existir: ❌ fora da matéria (lab assume que a pasta já existe). Usado para garantir que a BD é criada na primeira execução sem erro de diretório inexistente.
        if directory:
            os.makedirs(directory, exist_ok=True)
        self.create_table()

    # Abre uma ligação à BD com row_factory configurado para devolver dicionários.
    # _connect com row_factory = sqlite3.Row: ❌ fora (lab não usa Row factory). Usado para aceder a colunas por nome (ex: row["username"]) em vez de índice numérico, mais legível e menos sujeito a erros.
    def _connect(self):
        connection = sqlite3.connect(self.dbfile)
        connection.row_factory = sqlite3.Row

        return connection

    # ─── Criação de tabelas e dados iniciais ──────────────────────────────
    # Criação de tabelas: CREATE TABLE IF NOT EXISTS ✅ (Lab 07).
    # Parâmetros com ?, INSERT OR IGNORE ✅ (Lab 07).
    # FOREIGN KEY, UNIQUE composto: ❌ fora (lab só tem tabelas simples sem FK). Usado para garantir integridade referencial (ex: apagar slots se o user for removido) e evitar slots duplicados por utilizador.
    # buildings + seed data: específico do projeto, não existe no lab.
    # trees + stones com INSERT OR IGNORE por coluna: específico do jogo.
    # has_axe / axe_level: ✅ (INTEGER DEFAULT 0, igual a wood/stone em Lab 07). Colunas para o machado da Mesa de Trabalho (funcionalidade extra do projeto).
    #
    # Fluxo de inicialização:
    # 1. Cria as tabelas se não existirem (CREATE TABLE IF NOT EXISTS)
    # 2. Remove tabelas de esquemas anteriores (drop_legacy_tables)
    # 3. Adiciona colunas novas a tabelas existentes (migrate_schema)
    # 4. Insere dados iniciais (construções, árvores, pedras) com INSERT OR IGNORE
    # 5. Atualiza a construção "forja" para os valores atuais (UPDATE)
    def create_table(self):
        with self._connect() as connection:
            cursor = connection.cursor()
            # Tabela de utilizadores: guarda autenticação + recursos do jogo
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    wood INTEGER NOT NULL DEFAULT 26,
                    stone INTEGER NOT NULL DEFAULT 26,
                    iron INTEGER NOT NULL DEFAULT 0,
                    diamonds INTEGER NOT NULL DEFAULT 0,
                    has_axe INTEGER NOT NULL DEFAULT 0,
                    axe_level INTEGER NOT NULL DEFAULT 0,
                    skin TEXT NOT NULL DEFAULT 'default',
                    created_at TEXT NOT NULL
                )
                """
            )
            # Tabela de slots: 4 slots por jogador, cada um pode ter uma construção
            # Estado (state) controla o ciclo de vida: empty → building → ready → working → collectable → ready
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS building_slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    slot_number INTEGER NOT NULL,
                    building_type VARCHAR(40),
                    state VARCHAR(20) NOT NULL DEFAULT 'empty',
                    action_type VARCHAR(40),
                    started_at TEXT,
                    ready_at TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE (user_id, slot_number)
                )
                """
            )
            # Tabela de histórico: regista todas as ações do jogador com timestamp
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message VARCHAR(255) NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            # Árvores do mapa: cada árvore ocupa uma coluna fixa
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    column INTEGER NOT NULL UNIQUE,
                    chopped_at TEXT,
                    removed_at TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            # Pedras do mapa: cada pedra ocupa uma coluna fixa (lógica igual às árvores)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    column INTEGER NOT NULL UNIQUE,
                    mined_at TEXT,
                    removed_at TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            # Insere árvores nas colunas 2, 8, 15 (posições fixas do mapa)
            for column in (2, 8, 15):
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO trees (column, created_at)
                    VALUES (?, ?)
                    """,
                    (column, _format_datetime(datetime.utcnow())),
                )
            # Insere pedras nas colunas 1, 4, 7, 10 (posições fixas do mapa)
            for column in (1, 4, 7, 10):
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO stones (column, created_at)
                    VALUES (?, ?)
                    """,
                    (column, _format_datetime(datetime.utcnow())),
                )
            # Tabela de catálogo de construções: define custos, tempos e recompensas
            # Cada construção tem:
            #   - key: identificador único (cabana, mina, forja)
            #   - cost_wood/stone/iron: recursos necessários para construir
            #   - construction_seconds: tempo de construção
            #   - task_name/seconds: nome e duração da tarefa
            #   - reward_wood/stone/iron/diamond: recompensa ao completar a tarefa
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS buildings (
                    key VARCHAR(40) PRIMARY KEY,
                    name VARCHAR(80) NOT NULL,
                    cost_wood INTEGER NOT NULL,
                    cost_stone INTEGER NOT NULL,
                    cost_iron INTEGER NOT NULL DEFAULT 0,
                    construction_seconds INTEGER NOT NULL,
                    task_name VARCHAR(80) NOT NULL,
                    task_seconds INTEGER NOT NULL,
                    reward_wood INTEGER NOT NULL DEFAULT 0,
                    reward_stone INTEGER NOT NULL DEFAULT 0,
                    reward_iron INTEGER NOT NULL DEFAULT 0,
                    reward_diamond INTEGER NOT NULL DEFAULT 0,
                    description VARCHAR(255)
                )
                """
            )
            # Limpa tabelas de esquemas anteriores (desenvolvimento)
            self.drop_legacy_tables(cursor)
            # Adiciona colunas novas a tabelas que já existem em produção
            self.migrate_schema(cursor)
            # ─── Dados iniciais das construções ────────────────────────────
            # Mesa de Trabalho (cabana): fabrica/upgrade do machado
            # Custo: 15 madeira + 5 pedra | Constrói em 20s | Tarefa: 20s | Sem recompensa de recursos
            cursor.execute(
                "INSERT OR IGNORE INTO buildings VALUES ('cabana','Mesa de Trabalho',15,5,0,20,'Fabricar Machado',20,0,0,0,0,'Produz ferramentas de madeira para construir.')"
            )
            # Fornalha (mina): funde minério em ferro
            # Custo: 10 madeira + 15 pedra | Constrói em 25s | Tarefa: 25s | Recompensa: 1 ferro
            cursor.execute(
                "INSERT OR IGNORE INTO buildings VALUES ('mina','Fornalha',10,15,0,25,'Fundir minerio',25,0,0,1,0,'Funde minerio em lingotes de ferro.')"
            )
            # Mineradora de Diamantes (forja): extrai diamantes
            # Custo: 10 madeira + 10 pedra + 20 ferro | Constrói em 30s | Tarefa: 30s | Recompensa: 1 diamante
            cursor.execute(
                "INSERT OR IGNORE INTO buildings (key, name, cost_wood, cost_stone, cost_iron, construction_seconds, task_name, task_seconds, reward_wood, reward_stone, reward_iron, reward_diamond, description) VALUES ('forja','Mineradora de Diamantes',10,10,20,30,'Extrair diamantes',30,0,0,0,1,'Extrai diamantes preciosos.')"
            )
            # Atualiza a forja caso já exista na BD (migração de dados antigos)
            cursor.execute(
                "UPDATE buildings SET name='Mineradora de Diamantes', cost_wood=10, cost_stone=10, cost_iron=20, task_name='Extrair diamantes', reward_wood=0, reward_stone=0, reward_iron=0, reward_diamond=1, description='Extrai diamantes preciosos.' WHERE key='forja'"
            )
            connection.commit()

    # Remove tabelas de versões anteriores do esquema (usado durante desenvolvimento)
    def drop_legacy_tables(self, cursor):
        for table_name in ("action_log", "building_slot", "stone", "tree", "user"):
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Migração de esquema: adiciona colunas novas a tabelas existentes sem perder dados.
    # Cada ALTER TABLE está dentro de try/except porque a coluna pode já existir
    # (se a migração já tiver sido executada antes).
    def migrate_schema(self, cursor):
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN skin TEXT NOT NULL DEFAULT 'default'")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN diamonds INTEGER NOT NULL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE buildings ADD COLUMN cost_iron INTEGER NOT NULL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE buildings ADD COLUMN reward_diamond INTEGER NOT NULL DEFAULT 0")
        except sqlite3.OperationalError:
            pass

    # ─── CRUD de utilizadores ────────────────────────────────────────────

    # Cria um novo utilizador: guarda na BD com password hasheada e recursos iniciais (26 madeira, 26 pedra).
    def create_user(self, username, email, password):
        password_hash = hasher.hash(password)
        created_at = _format_datetime(datetime.utcnow())
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, wood, stone, skin, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (username, email, password_hash, 26, 26, 'default', created_at),
            )
            connection.commit()
            return self.get_user_by_id(cursor.lastrowid)

    # Procura um user pelo seu ID na BD. Devolve None se não existir.
    def get_user_by_id(self, user_id):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return User.from_row(row)

    # Procura um user pelo nome de utilizador (username). Usado no login e no register.
    def get_user_by_username(self, username):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return User.from_row(row)

    # Procura um user pelo email. Usado no register para verificar se o email já existe.
    def get_user_by_email(self, email):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        return User.from_row(row)

    # Atualiza todos os campos de um user na BD (username, email, password_hash, recursos).
    def update_user(self, user):
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE users
                SET username = ?, email = ?, password_hash = ?, wood = ?, stone = ?
                WHERE id = ?
                """,
                (user.username, user.email, user.password_hash, user.wood, user.stone, user.id),
            )
            connection.commit()

    # Atualiza os recursos (wood, stone, iron, diamonds) de um user. Usado após cada ação de jogo.
    def update_user_resources(self, user):
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE users
                SET wood = ?, stone = ?, iron = ?, diamonds = ?
                WHERE id = ?
                """,
                (user.wood, user.stone, user.iron, user.diamonds, user.id),
            )
            connection.commit()

    # Atualiza has_axe e axe_level do user (machado da Mesa de Trabalho).
    def update_user_axe(self, user_id, has_axe, axe_level):
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET has_axe = ?, axe_level = ? WHERE id = ?",
                (has_axe, axe_level, user_id),
            )
            connection.commit()

    # Atualiza a skin do user.
    def update_user_skin(self, user_id, skin):
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET skin = ? WHERE id = ?",
                (skin, user_id),
            )
            connection.commit()

    # ─── Gestão de slots de construção ────────────────────────────────────

    # Cria N slots vazios (estado "empty") para um user quando ele se regista.
    # Cada jogador tem DEFAULT_SLOT_COUNT slots (4).
    def create_default_slots(self, user_id, slot_count):
        with self._connect() as connection:
            cursor = connection.cursor()
            for slot_number in range(1, slot_count + 1):
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO building_slots (
                        user_id, slot_number, building_type, state, action_type,
                        started_at, ready_at, created_at
                    )
                    VALUES (?, ?, NULL, 'empty', NULL, NULL, NULL, ?)
                    """,
                    (user_id, slot_number, _format_datetime(datetime.utcnow())),
                )
            connection.commit()

    # Devolve todos os slots de construção de um user, ordenados por número de slot.
    def list_user_slots(self, user_id):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM building_slots
                WHERE user_id = ?
                ORDER BY slot_number
                """,
                (user_id,),
            ).fetchall()
        return [BuildingSlot.from_row(row) for row in rows]

    # Devolve um slot específico pelo seu ID. Se user_id for fornecido, verifica se o slot pertence a esse user.
    def get_slot(self, slot_id, user_id=None):
        query = "SELECT * FROM building_slots WHERE id = ?"
        params = [slot_id]
        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        with self._connect() as connection:
            row = connection.execute(query, params).fetchone()
        return BuildingSlot.from_row(row)

    # Atualiza todos os campos de um slot na BD (tipo de construção, estado, timestamps, etc.).
    def update_slot(self, slot):
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE building_slots
                SET user_id = ?, slot_number = ?, building_type = ?, state = ?,
                    action_type = ?, started_at = ?, ready_at = ?, created_at = ?
                WHERE id = ?
                """,
                (
                    slot.user_id,
                    slot.slot_number,
                    slot.building_type,
                    slot.state,
                    slot.action_type,
                    _format_datetime(slot.started_at),
                    _format_datetime(slot.ready_at),
                    _format_datetime(slot.created_at),
                    slot.id,
                ),
            )
            connection.commit()

    # ─── Gestão do catálogo de construções ────────────────────────────────

    # Devolve um dicionário com todos os tipos de construção disponíveis (cabana, mina, forja).
    # A chave é o identificador (ex: "cabana") e o valor é outro dicionário com nome, custos, tempos, recompensas.
    def get_buildings(self):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM buildings ORDER BY key"
            ).fetchall()
        result = {}
        for row in rows:
            result[row["key"]] = {
                "name": row["name"],
                "cost_wood": row["cost_wood"],
                "cost_stone": row["cost_stone"],
                "cost_iron": row["cost_iron"] if "cost_iron" in row.keys() else 0,
                "construction_seconds": row["construction_seconds"],
                "task_name": row["task_name"],
                "task_seconds": row["task_seconds"],
                "reward_wood": row["reward_wood"],
                "reward_stone": row["reward_stone"],
                "reward_iron": row["reward_iron"],
                "reward_diamond": row["reward_diamond"] if "reward_diamond" in row.keys() else 0,
                "description": row["description"],
            }
        return result

    # Devolve os dados de uma construção específica pela sua key (ex: "cabana") ou None se não existir.
    def get_building(self, key):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM buildings WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return None
        return {
            "name": row["name"],
            "cost_wood": row["cost_wood"],
            "cost_stone": row["cost_stone"],
            "cost_iron": row["cost_iron"] if "cost_iron" in row.keys() else 0,
            "construction_seconds": row["construction_seconds"],
            "task_name": row["task_name"],
            "task_seconds": row["task_seconds"],
            "reward_wood": row["reward_wood"],
            "reward_stone": row["reward_stone"],
            "reward_iron": row["reward_iron"] if "reward_iron" in row.keys() else 0,
            "reward_diamond": row["reward_diamond"] if "reward_diamond" in row.keys() else 0,
            "description": row["description"],
        }

    # ─── Histórico de ações ──────────────────────────────────────────────

    # Regista uma ação no histórico do jogador (ex: "Árvore cortada: +4 madeira") com a data/hora atual.
    def add_action_log(self, user_id, message):
        created_at = _format_datetime(datetime.utcnow())
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO action_logs (user_id, message, created_at)
                VALUES (?, ?, ?)
                """,
                (user_id, message, created_at),
            )
            connection.commit()

    # Devolve as últimas N ações do jogador, ordenadas da mais recente para a mais antiga.
    def list_action_logs(self, user_id, limit=8):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM action_logs
                WHERE user_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [ActionLog.from_row(row) for row in rows]

    # ─── Recursos do mapa (árvores e pedras) ─────────────────────────────

    # Garante que as 3 árvores do mapa existem na BD (INSERT OR IGNORE para não duplicar).
    # Chamado a cada refresh de estado para garantir que árvores removidas acidentalmente são recriadas.
    def ensure_trees(self):
        with self._connect() as connection:
            cursor = connection.cursor()
            for column in (2, 8, 15):
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO trees (column, created_at)
                    VALUES (?, ?)
                    """,
                    (column, _format_datetime(datetime.utcnow())),
                )
            connection.commit()

    # Garante que as 4 pedras do mapa existem na BD.
    def ensure_stones(self):
        with self._connect() as connection:
            cursor = connection.cursor()
            for column in (1, 4, 7, 10):
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO stones (column, created_at)
                    VALUES (?, ?)
                    """,
                    (column, _format_datetime(datetime.utcnow())),
                )
            connection.commit()

    # Número de slots de construção por jogador.
    DEFAULT_SLOT_COUNT = 4

    # Devolve todas as árvores do mapa, com opção de incluir ou excluir as que foram removidas.
    def list_trees(self, include_removed=False):
        query = "SELECT * FROM trees"
        params = []
        if not include_removed:
            query += " WHERE removed_at IS NULL"
        query += " ORDER BY column"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [Tree.from_row(row) for row in rows]

    # Devolve todas as pedras do mapa, com opção de incluir ou excluir as que foram removidas.
    def list_stones(self, include_removed=False):
        query = "SELECT * FROM stones"
        params = []
        if not include_removed:
            query += " WHERE removed_at IS NULL"
        query += " ORDER BY column"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [Stone.from_row(row) for row in rows]

    # Devolve uma árvore específica pela sua coluna no mapa (ou None se não existir nessa coluna).
    def get_tree_by_column(self, column, include_removed=False):
        query = "SELECT * FROM trees WHERE column = ?"
        params = [column]
        if not include_removed:
            query += " AND removed_at IS NULL"
        with self._connect() as connection:
            row = connection.execute(query, params).fetchone()
        return Tree.from_row(row)

    # Devolve uma pedra específica pela sua coluna no mapa (ou None se não existir nessa coluna).
    def get_stone_by_column(self, column, include_removed=False):
        query = "SELECT * FROM stones WHERE column = ?"
        params = [column]
        if not include_removed:
            query += " AND removed_at IS NULL"
        with self._connect() as connection:
            row = connection.execute(query, params).fetchone()
        return Stone.from_row(row)

    # Atualiza os dados de uma árvore na BD (ex: depois de ser cortada, regista chopped_at).
    def update_tree(self, tree):
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE trees
                SET column = ?, chopped_at = ?, removed_at = ?, created_at = ?
                WHERE id = ?
                """,
                (
                    tree.column,
                    _format_datetime(tree.chopped_at),
                    _format_datetime(tree.removed_at),
                    _format_datetime(tree.created_at),
                    tree.id,
                ),
            )
            connection.commit()

    # Atualiza os dados de uma pedra na BD (ex: depois de ser minerada, regista mined_at).
    def update_stone(self, stone):
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE stones
                SET column = ?, mined_at = ?, removed_at = ?, created_at = ?
                WHERE id = ?
                """,
                (
                    stone.column,
                    _format_datetime(stone.mined_at),
                    _format_datetime(stone.removed_at),
                    _format_datetime(stone.created_at),
                    stone.id,
                ),
            )
            connection.commit()

    # ─── Leaderboard ──────────────────────────────────────────────────────

    # Calcula o ranking dos 10 melhores jogadores com base no total de recursos (wood + stone + iron + diamonds).
    def get_leaderboard(self):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT username, (wood + stone + iron + diamonds) AS score
                FROM users
                ORDER BY score DESC
                LIMIT 10
                """
            ).fetchall()
        return [{"username": row["username"], "score": row["score"]} for row in rows]