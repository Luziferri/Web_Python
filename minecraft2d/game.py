# views.py
import json
from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, render_template, request, url_for
from flask_login import current_user, login_required


# Blueprint: ❌ fora (labs 07-08 organizam rotas no mesmo ficheiro). Usado para separar rotas de auth e de jogo em ficheiros diferentes.
game_bp = Blueprint("game", __name__)

# Constantes de jogabilidade: ❌ fora (não existem nos labs). Controlam o equilíbrio do jogo no browser.
RESOURCE_RESPAWN_SECONDS = 10   # Segundos até árvore/pedra poder ser extraída outra vez
RESOURCE_MAX_AMOUNT = 64        # Máximo de recursos que o jogador pode ter
TREE_WOOD_YIELD = 4             # Madeira obtida por árvore cortada
STONE_STONE_YIELD = 2           # Pedra obtida por pedra minerada


# Devolve o objeto Database guardado na app. ❌ fora (labs usam uma variável global ou passam a BD diretamente).
def get_db():
    return current_app.config["db"]


# Verifica se uma construção/tarefa já terminou comparando o tempo atual com ready_at.
# ❌ fora (labs não usam timestamps). Necessário porque o jogo tem ações temporizadas sem usar um cron job.
# Se o tempo já passou, muda o estado do slot e regista no histórico.
def sync_slot(slot):
    database = get_db()
    now = datetime.utcnow()
    if slot.ready_at is None:
        return

    if slot.state == "building" and now >= slot.ready_at:
        slot.state = "ready"
        slot.started_at = None
        slot.ready_at = None
        database.update_slot(slot)
        database.add_action_log(slot.user_id, f"A construção no slot {slot.slot_number} terminou.")
    elif slot.state == "working" and now >= slot.ready_at:
        slot.state = "collectable"
        slot.started_at = None
        slot.ready_at = None
        database.update_slot(slot)
        database.add_action_log(slot.user_id, f"A tarefa no slot {slot.slot_number} terminou. Podes recolher a recompensa.")


# Sincroniza todos os slots do user e limita os recursos ao máximo (cap).
# ❌ fora (labs não têm lógica de sincronização nem capping de recursos). Necessário para garantir que o estado está atualizado antes de cada ação ou refresh.
def ensure_state(user):
    database = get_db()
    for slot in database.list_user_slots(user.id):
        sync_slot(slot)

    if user.wood > RESOURCE_MAX_AMOUNT:
        user.wood = RESOURCE_MAX_AMOUNT
    if user.stone > RESOURCE_MAX_AMOUNT:
        user.stone = RESOURCE_MAX_AMOUNT
    if user.iron > RESOURCE_MAX_AMOUNT:
        user.iron = RESOURCE_MAX_AMOUNT
    database.update_user_resources(user)


# Converte um objeto BuildingSlot num dicionário para enviar como JSON ao frontend.
# ❌ fora (labs não usam JSON APIs). Necessário porque o frontend em JavaScript precisa dos dados do slot em formato JSON.
# .isoformat() também não foi dado nos labs — usado para serializar datetime numa string legível.
def slot_payload(slot):
    building = get_db().get_building(slot.building_type) if slot.building_type else None
    return {
        "id": slot.id,
        "slot_number": slot.slot_number,
        "building_type": slot.building_type,
        "building_name": building["name"] if building else None,
        "state": slot.state,
        "action_type": slot.action_type,
        "started_at": slot.started_at.isoformat() if slot.started_at else None,
        "ready_at": slot.ready_at.isoformat() if slot.ready_at else None,
        "construction_seconds": building["construction_seconds"] if building else None,
        "task_seconds": building["task_seconds"] if building else None,
        "description": building["description"] if building else None,
    }


@game_bp.route("/")
@game_bp.route("/dashboard")
@login_required
def dashboard():
    # Rota que renderiza a página principal do jogo. ✅ (Lab 07 - render_template).
    # @login_required ✅ (Lab 08).
    ensure_state(current_user)
    buildings = get_db().get_buildings()
    # Mapa de imagens para cada construção. Extra (não existia nos labs).
    building_images = {
        'cabana': 'craftingTable.png',
        'mina': 'fornalha.png',
    }
    for key, b in buildings.items():
        img = building_images.get(key)
        b['image'] = url_for('static', filename='img/' + img) if img else None
    return render_template("dashboard.html", buildings=buildings, buildings_json=json.dumps(buildings))


@game_bp.route("/api/state")
@login_required
def api_state():
    # Endpoint JSON que envia ao frontend o estado completo do jogo (user, slots, logs, recursos do mapa).
    # ❌ fora (labs só usam render_template, nunca jsonify). Necessário porque o frontend em JS busca dados assíncronos com fetch().
    # .isoformat() e .total_seconds() também não foram dados — usados para serializar timestamps e calcular cooldowns.
    # has_axe: ✅ (atributo do user, igual a wood/stone). Funcionalidade extra do projeto (machado da Mesa de Trabalho).
    database = get_db()
    ensure_state(current_user)
    logs = database.list_action_logs(current_user.id, limit=8)
    database.ensure_trees()
    database.ensure_stones()

    now = datetime.utcnow()
    trees = []
    for tree in database.list_trees():
        available = True
        seconds_left = 0
        if tree.chopped_at:
            elapsed = (now - tree.chopped_at).total_seconds()
            if elapsed < RESOURCE_RESPAWN_SECONDS:
                available = False
                seconds_left = int(RESOURCE_RESPAWN_SECONDS - elapsed)
            else:
                tree.chopped_at = None
                database.update_tree(tree)
        trees.append(
            {
                "column": tree.column,
                "available": available,
                "seconds_left": seconds_left,
            }
        )

    stones = []
    for stone in database.list_stones():
        available = True
        seconds_left = 0
        if stone.mined_at:
            elapsed = (now - stone.mined_at).total_seconds()
            if elapsed < RESOURCE_RESPAWN_SECONDS:
                available = False
                seconds_left = int(RESOURCE_RESPAWN_SECONDS - elapsed)
            else:
                stone.mined_at = None
                database.update_stone(stone)
        stones.append(
            {
                "column": stone.column,
                "available": available,
                "seconds_left": seconds_left,
            }
        )

    slots = []
    for slot in database.list_user_slots(current_user.id):
        payload = slot_payload(slot)
        # calcula seconds_left no servidor para não depender de parsing no cliente
        if slot.ready_at:
            seconds_left = int(max(0, (slot.ready_at - now).total_seconds()))
        else:
            seconds_left = 0
        payload["seconds_left"] = seconds_left
        slots.append(payload)

    logs_list = []
    for log in logs:
        logs_list.append({"message": log.message, "created_at": log.created_at.isoformat()})

    return jsonify(
        {
            "user": {
                "username": current_user.username,
                "wood": current_user.wood,
                "stone": current_user.stone,
                "iron": current_user.iron,
                "has_axe": current_user.has_axe,
                "axe_level": current_user.axe_level,
                "skin": current_user.skin,
            },
            "slots": slots,
            "logs": logs_list,
            "buildings": get_db().get_buildings(),
            "trees": trees,
            "stones": stones,
        }
    )


@game_bp.route("/api/build/<int:slot_id>", methods=["POST"])
@login_required
def api_build(slot_id):
    # Inicia uma construção num slot vazio: valida slot, verifica recursos, deduz custo e marca início.
    # ❌ fora (labs usam formulários HTML, não JSON API). Usa request.get_json para receber dados do fetch() do frontend.
    # datetime + timedelta ❌ fora — usado para calcular quando a construção termina.
    database = get_db()
    slot = database.get_slot(slot_id, current_user.id)
    if slot is None:
        return jsonify({"ok": False, "message": "Slot inválido."}), 404

    ensure_state(current_user)

    payload = request.get_json(silent=True) or {}
    building_key = payload.get("building_key") if request.is_json else request.form.get("building_key")
    building = get_db().get_building(building_key)

    if building is None:
        return jsonify({"ok": False, "message": "Construção inválida."}), 400

    if slot.state != "empty":
        return jsonify({"ok": False, "message": "Esse slot já tem uma construção."}), 400

    if current_user.wood < building["cost_wood"] or current_user.stone < building["cost_stone"]:
        return jsonify({"ok": False, "message": "Recursos insuficientes."}), 400

    current_user.wood -= building["cost_wood"]
    current_user.stone -= building["cost_stone"]
    slot.building_type = building_key
    slot.state = "building"
    slot.action_type = None
    slot.started_at = datetime.utcnow()
    slot.ready_at = slot.started_at + timedelta(seconds=building["construction_seconds"])
    database.update_user_resources(current_user)
    database.update_slot(slot)
    database.add_action_log(current_user.id, f"Iniciada construção de {building['name']} no slot {slot.slot_number}.")
    return jsonify({"ok": True})


@game_bp.route("/api/task/<int:slot_id>/start", methods=["POST"])
@login_required
def api_task_start(slot_id):
    # Inicia a tarefa de um edifício já construído (slot em estado "ready").
    # ❌ fora (labs não têm lógica de tarefas temporizadas). Usa timedelta para calcular o fim da tarefa.
    database = get_db()
    slot = database.get_slot(slot_id, current_user.id)
    if slot is None:
        return jsonify({"ok": False, "message": "Slot inválido."}), 404

    ensure_state(current_user)

    if slot.state != "ready" or slot.building_type is None:
        return jsonify({"ok": False, "message": "O slot ainda não está pronto para tarefa."}), 400

    building = get_db().get_building(slot.building_type)
    slot.state = "working"
    slot.started_at = datetime.utcnow()

    # Mesa de Trabalho: task dinamica conforme nivel do machado (funcionalidade extra do projeto).
    if slot.building_type == "cabana":
        if current_user.has_axe:
            slot.action_type = f"Upgrade Machado Nivel {current_user.axe_level + 1}"
        else:
            slot.action_type = "Fabricar Machado"
        task_seconds = building["task_seconds"] + (current_user.axe_level * 8)
        if current_user.axe_level == 0:
            cost_wood = 15
            cost_stone = 0
            cost_iron = 0
        elif current_user.axe_level == 1:
            cost_wood = 20
            cost_stone = 20
            cost_iron = 0
        else:
            cost_wood = 15 + (current_user.axe_level * 8)
            cost_stone = 8 + (current_user.axe_level * 5)
            cost_iron = 3 + (current_user.axe_level - 1) * 2
        if current_user.wood < cost_wood or current_user.stone < cost_stone or current_user.iron < cost_iron:
            parts = []
            if cost_wood > 0: parts.append(f"{cost_wood} madeira")
            if cost_stone > 0: parts.append(f"{cost_stone} pedra")
            if cost_iron > 0: parts.append(f"{cost_iron} ferro")
            msg = "Precisas de " + ", ".join(parts) + "."
            return jsonify({"ok": False, "message": msg}), 400
        current_user.wood -= cost_wood
        current_user.stone -= cost_stone
        current_user.iron -= cost_iron
        database.update_user_resources(current_user)
    else:
        slot.action_type = building["task_name"]
        task_seconds = building["task_seconds"]

    slot.ready_at = slot.started_at + timedelta(seconds=task_seconds)
    database.update_slot(slot)
    database.add_action_log(current_user.id, f"Tarefa '{slot.action_type}' iniciada no slot {slot.slot_number}.")
    return jsonify({"ok": True})


@game_bp.route("/api/task/<int:slot_id>/collect", methods=["POST"])
@login_required
def api_task_collect(slot_id):
    # Recolhe a recompensa de uma tarefa concluída (slot em estado "collectable").
    # Adiciona os recursos ao inventário e volta o slot a "ready" para nova tarefa.
    # ❌ fora (labs não têm sistema de recompensas nem máquina de estados).
    database = get_db()
    slot = database.get_slot(slot_id, current_user.id)
    if slot is None:
        return jsonify({"ok": False, "message": "Slot inválido."}), 404

    ensure_state(current_user)

    if slot.state != "collectable" or slot.building_type is None:
        return jsonify({"ok": False, "message": "Não há recompensa para recolher."}), 400

    building = get_db().get_building(slot.building_type)

    # Mesa de Trabalho: em vez de recursos, da o machado ou upgrade (funcionalidade extra do projeto).
    if slot.building_type == "cabana":
        if "Fabricar" in slot.action_type:
            current_user.has_axe = 1
            current_user.axe_level = 1
            database.update_user_axe(current_user.id, 1, 1)
            database.add_action_log(current_user.id, "Machado fabricado! A madeira rende o dobro.")
        elif "Upgrade" in slot.action_type:
            current_user.axe_level += 1
            database.update_user_axe(current_user.id, 1, current_user.axe_level)
            database.add_action_log(current_user.id, f"Machado upgraded para Nivel {current_user.axe_level}!")
    else:
        current_user.wood += building["reward_wood"]
        current_user.stone += building["reward_stone"]
        current_user.iron += building.get("reward_iron", 0)
        database.update_user_resources(current_user)

    slot.state = "ready"
    slot.action_type = None
    database.update_slot(slot)
    database.add_action_log(current_user.id, f"Recompensa recolhida do slot {slot.slot_number}.")
    return jsonify({"ok": True})


@game_bp.route("/api/chop", methods=["POST"])
@login_required
def api_chop():
    # Corta uma árvore: verifica cooldown, adiciona madeira ao inventário e regista o momento do corte.
    # ❌ fora (labs não usam JSON API nem lógica de cooldown com timestamps). request.get_json para receber a coluna vinda do fetch().
    database = get_db()
    data = request.get_json(silent=True) or {}
    column = data.get("column")
    wood_amount = TREE_WOOD_YIELD
    if column is None:
        return jsonify({"ok": False, "message": "Coluna inválida."}), 400

    tree = database.get_tree_by_column(int(column))
    if not tree:
        return jsonify({"ok": False, "message": "Árvore inexistente."}), 400

    now = datetime.utcnow()
    if tree.chopped_at:
        elapsed = (now - tree.chopped_at).total_seconds()
        if elapsed < RESOURCE_RESPAWN_SECONDS:
            return jsonify({"ok": False, "message": "Árvore ainda não regenerou."}), 400
        tree.chopped_at = None

    tree.chopped_at = now
    # axe_level: multiplicador de madeira (nivel 1=x2, nivel 2=x3, ...). Funcionalidade extra do projeto.
    wood_amount = wood_amount * (current_user.axe_level + 1) if current_user.has_axe else wood_amount
    current_user.wood += wood_amount
    if current_user.wood > RESOURCE_MAX_AMOUNT:
        current_user.wood = RESOURCE_MAX_AMOUNT
    database.update_tree(tree)
    database.update_user_resources(current_user)
    database.add_action_log(current_user.id, f"Árvore cortada: +{wood_amount} madeira.")
    return jsonify({"ok": True, "wood": current_user.wood, "respawn_seconds": RESOURCE_RESPAWN_SECONDS})


@game_bp.route("/api/mine-stone", methods=["POST"])
@login_required
def api_mine_stone():
    # Mina uma pedra: equivalente a api_chop mas para o recurso pedra.
    # ❌ fora (mesma lógica de JSON API, cooldown e capping).
    database = get_db()
    data = request.get_json(silent=True) or {}
    column = data.get("column")
    stone_amount = STONE_STONE_YIELD
    if column is None:
        return jsonify({"ok": False, "message": "Coluna inválida."}), 400

    stone = database.get_stone_by_column(int(column))
    if not stone:
        return jsonify({"ok": False, "message": "Pedra inexistente."}), 400

    now = datetime.utcnow()
    if stone.mined_at:
        elapsed = (now - stone.mined_at).total_seconds()
        if elapsed < RESOURCE_RESPAWN_SECONDS:
            return jsonify({"ok": False, "message": "Pedra ainda não regenerou."}), 400
        stone.mined_at = None

    stone.mined_at = now
    current_user.stone += stone_amount
    if current_user.stone > RESOURCE_MAX_AMOUNT:
        current_user.stone = RESOURCE_MAX_AMOUNT
    database.update_stone(stone)
    database.update_user_resources(current_user)
    database.add_action_log(current_user.id, f"Pedra minerada: +{stone_amount} pedra.")
    return jsonify({"ok": True, "stone": current_user.stone, "respawn_seconds": RESOURCE_RESPAWN_SECONDS})


@game_bp.route("/api/inventory/remove", methods=["POST"])
@login_required
def api_inventory_remove():
    # Remove uma quantidade de um recurso do inventário do jogador.
    # ❌ fora (labs não têm gestão de inventário). Usa if/else ✅ para selecionar o recurso certo.
    database = get_db()
    data = request.get_json(silent=True) or {}
    resource = data.get("resource")
    amount = data.get("amount", 1)

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "Quantidade inválida."}), 400

    if resource not in {"wood", "stone", "iron"}:
        return jsonify({"ok": False, "message": "Recurso inválido."}), 400

    if amount <= 0:
        return jsonify({"ok": False, "message": "A quantidade tem de ser maior que zero."}), 400

    if resource == "wood":
        current_value = current_user.wood
    elif resource == "stone":
        current_value = current_user.stone
    else:
        current_value = current_user.iron

    if current_value < amount:
        return jsonify({"ok": False, "message": "Inventário insuficiente."}), 400

    if resource == "wood":
        current_user.wood = current_value - amount
    elif resource == "stone":
        current_user.stone = current_value - amount
    else:
        current_user.iron = current_value - amount

    label = {"wood": "madeira", "stone": "pedra", "iron": "ferro"}[resource]
    database.update_user_resources(current_user)
    database.add_action_log(current_user.id, f"{amount} {label} removida do inventário.")

    return jsonify({"ok": True, "wood": current_user.wood, "stone": current_user.stone, "iron": current_user.iron})

@game_bp.route("/leaderboard")
@login_required
def leaderboard():
    #renderiza a página base do ranking
    return render_template("leaderboard.html")

@game_bp.route("/api/leaderboard")
@login_required
def api_leaderboard():
    #envia o ranking para o frontend
    #atualizar a página em tempo real sem fazer refresh
    database = get_db()
    ranking = database.get_leaderboard()
    return jsonify({"ranking": ranking})

SKINS = {
    "default": {"name": "Steve", "desc": "Clássico.", "img": "steeve.png"},
    "gold": {"name": "Steve Dourado", "desc": "Douradinho.", "img": "steeve.png", "filter": "brightness(1.2) sepia(0.6) saturate(2)"},
    "dark": {"name": "Steve Das Sombras", "desc": "Sombrio.", "img": "steeve.png", "filter": "brightness(0.5) contrast(1.3)"},
    "fire": {"name": "Steve Bronseado", "desc": "Apanhou solzinho.", "img": "steeve.png", "filter": "brightness(1.1) hue-rotate(-20deg) saturate(2.5)"},
    "ender": {"name": "Steve Rosa", "desc": "Rosinha.", "img": "steeve.png", "filter": "brightness(0.9) hue-rotate(280deg) saturate(1.5)"},
    "sunset": {"name": "Alex Bela", "desc": "Brilho do pôr-do-sol.", "img": "steeve.png", "filter": "brightness(1.1) hue-rotate(-10deg) saturate(1.8) sepia(0.2)"},
    "rose": {"name": "Alex Rosa", "desc": "Suave e romântica.", "img": "steeve.png", "filter": "brightness(1.05) hue-rotate(300deg) saturate(1.6)"},
    "lavender": {"name": "Alex Lavanda", "desc": "Toque de lavanda.", "img": "steeve.png", "filter": "brightness(1.0) hue-rotate(240deg) saturate(1.3) sepia(0.2)"},
    "aqua": {"name": "Alex Água", "desc": "Refrescante.", "img": "steeve.png", "filter": "brightness(1.0) hue-rotate(180deg) saturate(1.5)"},
    "peach": {"name": "Alex Pêssego", "desc": "Doce como pêssego.", "img": "steeve.png", "filter": "brightness(1.1) hue-rotate(-30deg) saturate(1.4) sepia(0.3)"},
}

@game_bp.route("/skins")
@login_required
def skins():
    return render_template("skins.html", skins=SKINS)

@game_bp.route("/api/skins")
@login_required
def api_skins():
    return jsonify({"skins": SKINS, "current_skin": current_user.skin})

@game_bp.route("/api/skin/select", methods=["POST"])
@login_required
def api_skin_select():
    data = request.get_json(silent=True) or {}
    skin = data.get("skin")
    if skin not in SKINS:
        return jsonify({"ok": False, "message": "Skin inválida."}), 400
    database = get_db()
    database.update_user_skin(current_user.id, skin)
    current_user.skin = skin
    return jsonify({"ok": True, "skin": skin})