-- ============================================================
-- Esquema SQL da Base de Dados — Minecraft 2D
-- SQLite 3
-- ============================================================

-- Tabela de utilizadores: autenticação + recursos do jogo
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
);

-- Tabela de slots de construção: 4 slots por jogador
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
);

-- Tabela de histórico de ações do jogador
CREATE TABLE IF NOT EXISTS action_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message VARCHAR(255) NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabela de árvores no mapa (cooldown de 10s após corte)
CREATE TABLE IF NOT EXISTS trees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column INTEGER NOT NULL UNIQUE,
    chopped_at TEXT,
    removed_at TEXT,
    created_at TEXT NOT NULL
);

-- Tabela de pedras no mapa (cooldown de 10s após mineração)
CREATE TABLE IF NOT EXISTS stones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column INTEGER NOT NULL UNIQUE,
    mined_at TEXT,
    removed_at TEXT,
    created_at TEXT NOT NULL
);

-- Tabela de catálogo de construções (dados estáticos)
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
);

-- ============================================================
-- Dados Iniciais (Seed)
-- ============================================================

-- Árvores nas colunas 2, 8, 15
INSERT OR IGNORE INTO trees (column, created_at)
VALUES (2, datetime('now')),
       (8, datetime('now')),
       (15, datetime('now'));

-- Pedras nas colunas 1, 4, 7, 10
INSERT OR IGNORE INTO stones (column, created_at)
VALUES (1, datetime('now')),
       (4, datetime('now')),
       (7, datetime('now')),
       (10, datetime('now'));

-- Mesa de Trabalho (cabana): fabrica/upgrade do machado
INSERT OR IGNORE INTO buildings
    (key, name, cost_wood, cost_stone, cost_iron, construction_seconds,
     task_name, task_seconds, reward_wood, reward_stone, reward_iron,
     reward_diamond, description)
VALUES
    ('cabana', 'Mesa de Trabalho', 15, 5, 0, 20,
     'Fabricar Machado', 20, 0, 0, 0, 0,
     'Produz ferramentas de madeira para construir.');

-- Fornalha (mina): funde minério em lingotes de ferro
INSERT OR IGNORE INTO buildings
    (key, name, cost_wood, cost_stone, cost_iron, construction_seconds,
     task_name, task_seconds, reward_wood, reward_stone, reward_iron,
     reward_diamond, description)
VALUES
    ('mina', 'Fornalha', 10, 15, 0, 25,
     'Fundir minerio', 25, 0, 0, 1, 0,
     'Funde minerio em lingotes de ferro.');

-- Mineradora de Diamantes (forja): extrai diamantes
INSERT OR IGNORE INTO buildings
    (key, name, cost_wood, cost_stone, cost_iron, construction_seconds,
     task_name, task_seconds, reward_wood, reward_stone, reward_iron,
     reward_diamond, description)
VALUES
    ('forja', 'Mineradora de Diamantes', 10, 10, 20, 30,
     'Extrair diamantes', 30, 0, 0, 0, 1,
     'Extrai diamantes preciosos.');
