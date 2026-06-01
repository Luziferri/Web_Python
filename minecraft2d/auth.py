# views.py


from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from models import Database, User


# Blueprint agrupa rotas com prefixo comum (aqui sem prefixo).aaaaa
auth_bp = Blueprint("auth", __name__)


def get_db():
    return current_app.config["db"]


def create_default_slots(user):
    database = get_db()
    database.create_default_slots(user.id, Database.DEFAULT_SLOT_COUNT)
    database.add_action_log(user.id, "Conta criada com recursos iniciais.")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("game.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        database = get_db()

        if not username or not email or not password:
            flash("Preenche username, email e password.", "error")
            return render_template("register.html")

        if len(password) < 4:
            flash("A password tem de ter pelo menos 4 caracteres.", "error")
            return render_template("register.html")

        if database.get_user_by_username(username):
            flash("Esse username já existe.", "error")
            return render_template("register.html")

        if database.get_user_by_email(email):
            flash("Esse email já existe.", "error")
            return render_template("register.html")

        user = database.create_user(username, email, password)
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

        user = get_db().get_user_by_username(username)

        if user is None or not user.check_password(password):
            flash("Credenciais inválidas.", "error")
            return render_template("login.html")

        login_user(user)
        return redirect(url_for("game.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
