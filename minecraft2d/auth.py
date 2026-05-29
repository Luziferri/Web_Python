from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from extensions import db
from game_data import DEFAULT_SLOT_COUNT
from models import ActionLog, BuildingSlot, User


auth_bp = Blueprint("auth", __name__)


def create_default_slots(user):
    for slot_number in range(1, DEFAULT_SLOT_COUNT + 1):
        slot = BuildingSlot(user_id=user.id, slot_number=slot_number)
        db.session.add(slot)
    db.session.add(ActionLog(user_id=user.id, message="Conta criada com recursos iniciais."))
    db.session.commit()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("game.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Preenche username, email e password.", "error")
            return render_template("register.html")

        if len(password) < 4:
            flash("A password tem de ter pelo menos 4 caracteres.", "error")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Esse username já existe.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Esse email já existe.", "error")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        create_default_slots(user)
        login_user(user)
        return redirect(url_for("game.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("game.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Credenciais inválidas.", "error")
            return render_template("login.html")

        login_user(user)
        return redirect(url_for("game.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
