# API Documentation — Minecraft 2D

## Base URL

```
http://127.0.0.1:8001
```

All routes require authentication via Flask-Login (session cookie), except `/login` and `/register`.

---

## Authentication Routes (Blueprint: `auth`)

### `POST /register`

Cria uma nova conta de jogador.

Campo:    Tipo:     Localização:
username  string    form-data
email     string    form-data 
password  string    form-data   

Respostas:
- `302` - Redirect para `/dashboard` em caso de sucesso
- `200` - Renderiza `register.html` com mensagem de erro (flash)

### `POST /login`

Autentica um jogador existente.

Campo:    Tipo:     Localização:
username  string    form-data 
password  string    form-data

Respostas:
- `302` - Redirect para `/dashboard` em caso de sucesso
- `200` - Renderiza `login.html` com flash "Credenciais inválidas."

### `GET /login`

Renderiza o formulário de login (`login.html`).

### `GET /register`

Renderiza o formulário de registo (`register.html`).

### `GET /logout` | `POST /logout`

Termina a sessão do jogador.

Respostas:
- `302` - Redirect para `/login`

---

## Game Routes (Blueprint: `game`)

### `GET /` | `GET /dashboard`

Renderiza a página principal do jogo (`dashboard.html`).

Respostas:
- `200` - Página HTML com o estado do jogo

---

### `GET /api/state`

Devolve o estado completo do jogo em JSON.

Respostas:
- `200` - JSON com:

```json
{
  "user": {
    "username": "string",
    "wood": "int",
    "stone": "int",
    "iron": "int",
    "diamonds": "int",
    "has_axe": "int (0|1)",
    "axe_level": "int",
    "skin": "string"
  },
  "slots": [
    {
      "id": "int",
      "slot_number": "int",
      "building_type": "string|null",
      "building_name": "string|null",
      "state": "empty|building|ready|working|collectable",
      "action_type": "string|null",
      "started_at": "ISO datetime|null",
      "ready_at": "ISO datetime|null",
      "construction_seconds": "int|null",
      "task_seconds": "int|null",
      "description": "string|null",
      "seconds_left": "int"
    }
  ],
  "logs": [
    {
      "message": "string",
      "created_at": "ISO datetime"
    }
  ],
  "buildings": { "...": { ... } },
  "trees": [
    {
      "column": "int",
      "available": "bool",
      "seconds_left": "int"
    }
  ],
  "stones": [
    {
      "column": "int",
      "available": "bool",
      "seconds_left": "int"
    }
  ]
}
```

---

### `POST /api/build/<slot_id>`

Inicia a construção de um edifício num slot vazio.

Parâmetro:    Tipo:   Localização:
building_key  string  JSON body

Respostas:
- `200` - `{"ok": true}`
- `400` - `{"ok": false, "message": "..."}` (slot ocupado, recursos insuficientes, construção inválida)
- `404` - `{"ok": false, "message": "Slot inválido."}`

---

### `POST /api/task/<slot_id>/start`

Inicia a tarefa de um edifício já construído (estado `ready`).

Respostas:
- `200` - `{"ok": true}`
- `400` - `{"ok": false, "message": "..."}` (slot não está ready, recursos insuficientes para upgrade do machado)
- `404` - `{"ok": false, "message": "Slot inválido."}`

Para a Mesa de Trabalho (`cabana`), os custos variam conforme o nível do machado:
- Nível 0 (Fabricar): 15 madeira
- Nível 1 (Upgrade): 20 madeira + 20 pedra
- Nível 2 (Upgrade): 31 madeira + 18 pedra + 5 ferro
- Nível 3+ (Upgrade): madeira+pedra crescentes + diamantes

---

### `POST /api/task/<slot_id>/collect`

Recolhe a recompensa de uma tarefa concluída (estado `collectable`).

Respostas:
- `200` - `{"ok": true}`
- `400` - `{"ok": false, "message": "..."}` (sem recompensa para recolher)
- `404` - `{"ok": false, "message": "Slot inválido."}`

**Recompensas por edifício:**
Edifício:             Recompensa:
Mesa de Trabalho      Machado (nível 1) ou upgrade de nível
Fornalha              +1 ferro
Mineradora Diamantes  +1 diamante

---

### `POST /api/chop

Corta uma árvore numa coluna do mapa.

Parâmetro:  Tipo:   Localização:
column      int     JSON body

Respostas:
- `200` - `{"ok": true, "wood": "int", "respawn_seconds": 10}`
- `400` - `{"ok": false, "message": "..."}` (cooldown ativo, árvore inexistente, coluna inválida)

O rendimento de madeira é multiplicado por `(axe_level + 1)` se o jogador tiver machado.

---

### `POST /api/mine-stone`

Mina uma pedra numa coluna do mapa.

Parâmetro:    Tipo:   Localização:
column        int     JSON body

Respostas:
- `200` - `{"ok": true, "stone": "int", "respawn_seconds": 10}`
- `400` - `{"ok": false, "message": "..."}` (cooldown ativo, pedra inexistente, coluna inválida)

---

### `POST /api/slot/<slot_id>/remove`

Remove a construção de um slot, deixando-o vazio.

Respostas:
- `200` - `{"ok": true}`
- `400` - `{"ok": false, "message": "O slot já está vazio."}`
- `404` - `{"ok": false, "message": "Slot inválido."}`

---

### `POST /api/inventory/remove`

Remove manualmente recursos do inventário do jogador.

Parâmetro:    Tipo:   Localização:
resource      string  JSON body
amount        int     JSON body

`resource` pode ser: `wood`, `stone`, `iron`, `diamonds`.

Respostas:
- `200` - `{"ok": true, "wood": "int", "stone": "int", "iron": "int", "diamonds": "int"}`
- `400` - `{"ok": false, "message": "..."}` (recurso inválido, quantidade inválida, inventário insuficiente)

---

### `GET /leaderboard`

Renderiza a página de classificação (`leaderboard.html`).

---

### `GET /api/leaderboard`

Devolve o ranking dos 10 melhores jogadores em JSON.

Respostas
- `200` -

```json
{
  "ranking": [
    { "username": "string", "score": "int" }
  ]
}
```

A pontuação é calculada como `wood + stone + iron + diamonds`.

---

### `GET /skins`

Renderiza a página de seleção de skins (`skins.html`).

---

### `GET /api/skins`

Devolve todas as skins disponíveis e a skin atual do jogador.

Respostas:
- `200` -

```json
{
  "skins": {
    "default": { "name": "Steve", "desc": "Clássico.", "img": "steeve.png" },
    "gold": { "name": "Steve Dourado", "desc": "...", "img": "steeve.png", "filter": "..." },
    "dark": { ... },
    "fire": { ... },
    "ender": { ... }
  },
  "current_skin": "string"
}
```

---

### `POST /api/skin/select`

Seleciona uma skin para o jogador.

Parâmetro:    Tipo:      Localização:
skin          string    JSON body

Respostas:
- `200` - `{"ok": true, "skin": "string"}`
- `400` - `{"ok": false, "message": "Skin inválida."}`
