import os

from sqlalchemy import text

from flask import Flask
from flask_login import current_user

from extensions import db, login_manager
from models import ActionLog, BuildingSlot, User


class Config:
    SECRET_KEY = "dev-minecraft-2d"
    SQLALCHEMY_DATABASE_URI = "sqlite:///minecraft2d.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def ensure_sqlite_column(table_name, column_name, column_definition):
    existing_columns = {
        row[1]
        for row in db.session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    }

    if column_name not in existing_columns:
        db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"))
        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "minecraft2d.db")

    db.init_app(app)
    login_manager.init_app(app)

    from auth import auth_bp
    from game import game_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)

    with app.app_context():
        db.create_all()
        ensure_sqlite_column("tree", "removed_at", "removed_at DATETIME")
        ensure_sqlite_column("stone", "removed_at", "removed_at DATETIME")

    @app.context_processor
    def inject_user():
        return {"current_game_user": current_user}

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(debug=True, host="127.0.0.1", port=port)
