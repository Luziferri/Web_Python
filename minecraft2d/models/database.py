import os
import sqlite3

from datetime import datetime

from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256 as hasher


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


# Modelo User com UserMixin para integração com Flask-Login ✅ (Lab 08).
# set_password / check_password com passlib: ✅ (Lab 08).
class User(UserMixin):
    # Construtor: guarda os dados do user vindos da BD ou do registo.
    # wood/stone começam a 26 (recursos iniciais do jogo).
    def __init__(self, id, username, email, password_hash, wood=26, stone=26, iron=0, created_at=None, has_axe=0, axe_level=0, skin="default"):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        # wood e stone são específicos do jogo (não existem no modelo User do Lab 08).
        self.wood = wood
        self.stone = stone
        self.iron = iron
        self.created_at = created_at
        # has_axe / axe_level: ✅ (INTEGER DEFAULT, igual a wood/stone). Funcionalidade extra do projeto (machado da Mesa de Trabalho).
        self.has_axe = has_axe
        self.axe_level = axe_level
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
            skin=row["skin"] if "skin" in row.keys() else "default",
        )


# BuildingSlot: modelo para slots de construção (inexistente nos labs). ❌ fora.
# Faz parte das mecânicas do projeto (3+ construções, estados, temporizadores). Necessário para gerir os 4 slots de construção por jogador.
class BuildingSlot:
    # Cada slot tem um número (1-4), um tipo de construção opcional, um estado (empty/building/ready/working/collectable),
    # e timestamps para controlar quando a construção/tarefa termina.
    def __init__(self, id, user_id, slot_number, building_type=None, state="empty", action_type=None, started_at=None, ready_at=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.slot_number = slot_number
        self.building_type = building_type
        self.state = state
        self.action_type = action_type
        self.started_at = started_at
        self.ready_at = ready_at
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
class ActionLog:
    # Armazena uma mensagem de texto (ex: "Árvore cortada: +4 madeira") com a data em que ocorreu.
    def __init__(self, id, user_id, message, created_at=None):
        self.id = id
        self.user_id = user_id
        self.message = message
        self.created_at = created_at

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
class Tree:
    # Cada árvore está numa coluna do mapa (column). chopped_at regista quando foi cortada (para cooldown).
    def __init__(self, id, column, chopped_at=None, removed_at=None, created_at=None):
        self.id = id
        self.column = column
        self.chopped_at = chopped_at
        self.removed_at = removed_at
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
class Stone:
    # Cada pedra está numa coluna do mapa. mined_at regista quando foi minerada (para cooldown).
    def __init__(self, id, column, mined_at=None, removed_at=None, created_at=None):
        self.id = id
        self.column = column
        self.mined_at = mined_at
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


# Classe principal que gere toda a interação com a base de dados SQLite.
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

    # Criação de tabelas: CREATE TABLE IF NOT EXISTS ✅ (Lab 07).
    # Parâmetros com ?, INSERT OR IGNORE ✅ (Lab 07).
    # FOREIGN KEY, UNIQUE composto: ❌ fora (lab só tem tabelas simples sem FK). Usado para garantir integridade referencial (ex: apagar slots se o user for removido) e evitar slots duplicados por utilizador.
    # buildings + seed data: específico do projeto, não existe no lab.
    # trees + stones com INSERT OR IGNORE por coluna: específico do jogo.
    # has_axe / axe_level: ✅ (INTEGER DEFAULT 0, igual a wood/stone em Lab 07). Colunas para o machado da Mesa de Trabalho (funcionalidade extra do projeto).
    def create_table(self):
        with self._connect() as connection:
            cursor = connection.cursor()
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
                    has_axe INTEGER NOT NULL DEFAULT 0,
                    axe_level INTEGER NOT NULL DEFAULT 0,
                    skin TEXT NOT NULL DEFAULT 'default',
                    created_at TEXT NOT NULL
                )
                """
            )
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
            #localizalçao da arvore
            for column in (2, 8, 15):
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO trees (column, created_at)
                    VALUES (?, ?)
                    """,
                    (column, _format_datetime(datetime.utcnow())),
                )
            for column in (1, 4, 7, 10):
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO stones (column, created_at)
                    VALUES (?, ?)
                    """,
                    (column, _format_datetime(datetime.utcnow())),
                )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS buildings (
                    key VARCHAR(40) PRIMARY KEY,
                    name VARCHAR(80) NOT NULL,
                    cost_wood INTEGER NOT NULL,
                    cost_stone INTEGER NOT NULL,
                    construction_seconds INTEGER NOT NULL,
                    task_name VARCHAR(80) NOT NULL,
                    task_seconds INTEGER NOT NULL,
                    reward_wood INTEGER NOT NULL DEFAULT 0,
                    reward_stone INTEGER NOT NULL DEFAULT 0,
                    reward_iron INTEGER NOT NULL DEFAULT 0,
                    description VARCHAR(255)
                )
                """
            )
            cursor.execute(
                "INSERT OR IGNORE INTO buildings VALUES ('cabana','Mesa de Trabalho',15,5,20,'Fabricar Machado',20,0,0,0,'Produz ferramentas de madeira para construir.')"
            )
            cursor.execute(
                "INSERT OR IGNORE INTO buildings VALUES ('mina','Fornalha',10,15,25,'Fundir minerio',25,0,0,1,'Funde minerio em lingotes de ferro.')"
            )
            cursor.execute(
                "INSERT OR IGNORE INTO buildings VALUES ('forja','Quinta',20,10,30,'Colher colheitas',30,4,4,0,'Cultiva alimentos e gera madeira.')"
            )
            self.drop_legacy_tables(cursor)
            connection.commit()

            # drop_legacy_tables: ❌ fora (função de limpeza de esquemas anteriores, não existe no lab). Usada durante desenvolvimento para remover tabelas de versões anteriores do esquema.
    def drop_legacy_tables(self, cursor):
        for table_name in ("action_log", "building_slot", "stone", "tree", "user"):
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    # hasher.hash(password) ✅ (Lab 08), INSERT com ? ✅ (Lab 07).
    # cursor.lastrowid: ❌ fora (lab faz return do objeto criado de outra forma). Usado para obter o ID do novo user imediatamente após o INSERT, evitando uma segunda query à BD.
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

    # SELECT * FROM ... WHERE id = ? com fetchone: ✅ (Lab 07).
    # from_row: ❌ fora (lab usa tuple unpacking). Usado para consistência com os restantes modelos que também usam from_row.
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

    # UPDATE com ?: ✅ (Lab 07 - update_movie).
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

    # Atualiza os recursos (wood, stone, iron) de um user. Usado após cada ação de jogo.
    def update_user_resources(self, user):
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE users
                SET wood = ?, stone = ?, iron = ?
                WHERE id = ?
                """,
                (user.wood, user.stone, user.iron, user.id),
            )
            connection.commit()

    # Atualiza has_axe e axe_level do user (machado da Mesa de Trabalho).
    # UPDATE com parametros ?: ✅ (Lab 07). Funcionalidade extra do projeto.
    def update_user_axe(self, user_id, has_axe, axe_level):
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET has_axe = ?, axe_level = ? WHERE id = ?",
                (has_axe, axe_level, user_id),
            )
            connection.commit()

    def update_user_skin(self, user_id, skin):
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET skin = ? WHERE id = ?",
                (skin, user_id),
            )
            connection.commit()

    # INSERT em loop com for: ❌ fora (lab faz inserts individuais). Usado para criar todos os slots de construção de um user de uma só vez, de forma eficiente.
    # Cria N slots vazios (estado "empty") para um user quando ele se regista.
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

    # SELECT * com fetchall e ORDER BY: ✅ (Lab 07 - get_movies).
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

    # Query construída dinamicamente com condicional: ❌ fora (lab usa queries fixas). Usado para reutilizar o mesmo método com ou sem filtro de user_id, evitando duplicar código.
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

    # fetchall com ORDER BY + dicionário: ✅ (semelhante a get_movies no Lab 07).
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
                "construction_seconds": row["construction_seconds"],
                "task_name": row["task_name"],
                "task_seconds": row["task_seconds"],
                "reward_wood": row["reward_wood"],
                "reward_stone": row["reward_stone"],
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
            "construction_seconds": row["construction_seconds"],
            "task_name": row["task_name"],
            "task_seconds": row["task_seconds"],
            "reward_wood": row["reward_wood"],
            "reward_stone": row["reward_stone"],
            "reward_iron": row["reward_iron"] if "reward_iron" in row.keys() else 0,
            "description": row["description"],
        }

    # SELECT com LIMIT e ORDER BY DESC: ❌ fora (lab não usa LIMIT nem ORDER BY DESC). Usado para mostrar apenas as ações mais recentes no histórico.
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

    # ensure_trees / ensure_stones: ❌ fora (específicos do jogo). Necessário para garantir que árvores e pedras existem no mapa mesmo depois de reiniciar o servidor.
    # Garante que as 3 árvores do mapa existem na BD (INSERT OR IGNORE para não duplicar).
    # As colunas das árvores foram ajustadas (2, 6, 11) durante o desenvolvimento.
    # Matéria: SQL INSERT OR IGNORE, iteração sobre tuplo.
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

    # Número de slots de construção por jogador (definido como constante da classe).
    DEFAULT_SLOT_COUNT = 4

    # Query construída dinamicamente (WHERE condicional): ❌ fora (lab tem queries fixas). Usado para listar recursos incluindo ou excluindo os removidos, conforme necessário.
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

#Leaderboard
    def get_leaderboard(self):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT username, (wood + stone + iron) AS score
                FROM users
                ORDER BY score DESC
                LIMIT 10
                """
            ).fetchall()
        #Converte as linhas para uma lista de dicionários
        return [{"username": row["username"], "score": row["score"]} for row in rows]