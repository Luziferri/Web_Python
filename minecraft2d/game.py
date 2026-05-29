from datetime import datetime, timedelta

import os

from flask import Blueprint, jsonify, render_template, request, send_from_directory
from flask_login import current_user, login_required

from extensions import db
from game_data import BUILDINGS
from models import ActionLog, BuildingSlot, Tree


game_bp = Blueprint("game", __name__)


def sync_slot(slot):
    now = datetime.utcnow()
    if slot.ready_at is None:
        return

    if slot.state == "building" and now >= slot.ready_at:
        slot.state = "ready"
        slot.started_at = None
        slot.ready_at = None
        db.session.add(ActionLog(user_id=slot.user_id, message=f"A construção no slot {slot.slot_number} terminou."))

    elif slot.state == "working" and now >= slot.ready_at:
        slot.state = "collectable"
        slot.started_at = None
        slot.ready_at = None
        db.session.add(ActionLog(user_id=slot.user_id, message=f"A tarefa no slot {slot.slot_number} terminou. Podes recolher a recompensa."))


def ensure_state(user):
    for slot in user.slots:
        sync_slot(slot)
    db.session.commit()


def slot_payload(slot):
    building = BUILDINGS.get(slot.building_type, None)
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
    ensure_state(current_user)
    return render_template("dashboard.html", buildings=BUILDINGS)


@game_bp.route("/api/state")
@login_required
def api_state():
    ensure_state(current_user)
    logs = ActionLog.query.filter_by(user_id=current_user.id).order_by(ActionLog.created_at.desc()).limit(8).all()
    # ensure default trees exist
    ensure_trees()

    # build tree payload with availability and seconds until respawn
    now = datetime.utcnow()
    respawn_seconds = 10
    trees = []
    for t in Tree.query.order_by(Tree.column).all():
        available = True
        seconds_left = 0
        if t.chopped_at:
            elapsed = (now - t.chopped_at).total_seconds()
            if elapsed < respawn_seconds:
                available = False
                seconds_left = int(respawn_seconds - elapsed)
            else:
                # respawn
                t.chopped_at = None
                db.session.add(t)
        trees.append({
            "column": t.column,
            "available": available,
            "seconds_left": seconds_left,
        })

    db.session.commit()

    return jsonify(
        {
            "user": {
                "username": current_user.username,
                "wood": current_user.wood,
                "stone": current_user.stone,
            },
            "slots": [slot_payload(slot) for slot in current_user.slots],
            "logs": [
                {"message": log.message, "created_at": log.created_at.isoformat()} for log in logs
            ],
            "buildings": BUILDINGS,
            "trees": trees,
        }
    )


@game_bp.route("/api/build/<int:slot_id>", methods=["POST"])
@login_required
def api_build(slot_id):
    slot = BuildingSlot.query.filter_by(id=slot_id, user_id=current_user.id).first_or_404()
    ensure_state(current_user)

    building_key = request.json.get("building_key") if request.is_json else request.form.get("building_key")
    building = BUILDINGS.get(building_key)

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
    db.session.add(ActionLog(user_id=current_user.id, message=f"Iniciada construção de {building['name']} no slot {slot.slot_number}."))
    db.session.commit()
    return jsonify({"ok": True})


@game_bp.route("/api/task/<int:slot_id>/start", methods=["POST"])
@login_required
def api_task_start(slot_id):
    slot = BuildingSlot.query.filter_by(id=slot_id, user_id=current_user.id).first_or_404()
    ensure_state(current_user)

    if slot.state != "ready" or slot.building_type is None:
        return jsonify({"ok": False, "message": "O slot ainda não está pronto para tarefa."}), 400

    building = BUILDINGS.get(slot.building_type)
    slot.state = "working"
    slot.action_type = building["task_name"]
    slot.started_at = datetime.utcnow()
    slot.ready_at = slot.started_at + timedelta(seconds=building["task_seconds"])
    db.session.add(ActionLog(user_id=current_user.id, message=f"Tarefa '{building['task_name']}' iniciada no slot {slot.slot_number}."))
    db.session.commit()
    return jsonify({"ok": True})


@game_bp.route("/api/task/<int:slot_id>/collect", methods=["POST"])
@login_required
def api_task_collect(slot_id):
    slot = BuildingSlot.query.filter_by(id=slot_id, user_id=current_user.id).first_or_404()
    ensure_state(current_user)

    if slot.state != "collectable" or slot.building_type is None:
        return jsonify({"ok": False, "message": "Não há recompensa para recolher."}), 400

    building = BUILDINGS.get(slot.building_type)
    current_user.wood += building["reward_wood"]
    current_user.stone += building["reward_stone"]
    slot.state = "ready"
    slot.action_type = None
    db.session.add(ActionLog(user_id=current_user.id, message=f"Recompensa recolhida do slot {slot.slot_number}."))
    db.session.commit()
    return jsonify({"ok": True})


@game_bp.route('/api/chop', methods=['POST'])
@login_required
def api_chop():
    data = request.get_json() or {}
    # expect column in payload
    col = data.get('column')
    wood_amount = int(data.get('amount', 5)) if data.get('amount') else 5
    if col is None:
        return jsonify({"ok": False, "message": "Coluna inválida."}), 400

    tree = Tree.query.filter_by(column=int(col)).first()
    if not tree:
        return jsonify({"ok": False, "message": "Árvore inexistente."}), 400

    # check availability
    now = datetime.utcnow()
    respawn_seconds = 10
    if tree.chopped_at:
        elapsed = (now - tree.chopped_at).total_seconds()
        if elapsed < respawn_seconds:
            return jsonify({"ok": False, "message": "Árvore ainda não regenerou."}), 400
        else:
            tree.chopped_at = None

    # mark chopped
    tree.chopped_at = now
    current_user.wood += wood_amount
    db.session.add(tree)
    db.session.add(ActionLog(user_id=current_user.id, message=f"Árvore cortada: +{wood_amount} madeira."))
    db.session.commit()
    return jsonify({"ok": True, "wood": current_user.wood, "respawn_seconds": respawn_seconds})


def ensure_trees():
    # default columns where trees should exist
    default_columns = [2, 5, 9]
    for c in default_columns:
        if not Tree.query.filter_by(column=c).first():
            db.session.add(Tree(column=c))
    db.session.commit()


@game_bp.route("/img/<path:filename>")
def image_file(filename):
    image_folder = os.path.join(os.path.dirname(__file__), "img")
    return send_from_directory(image_folder, filename)
