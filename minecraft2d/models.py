from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    wood = db.Column(db.Integer, nullable=False, default=26)
    stone = db.Column(db.Integer, nullable=False, default=26)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    slots = db.relationship("BuildingSlot", backref="user", lazy=True, cascade="all, delete-orphan", order_by="BuildingSlot.slot_number")
    actions = db.relationship("ActionLog", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BuildingSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    slot_number = db.Column(db.Integer, nullable=False)
    building_type = db.Column(db.String(40), nullable=True)
    state = db.Column(db.String(20), nullable=False, default="empty")
    action_type = db.Column(db.String(40), nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    ready_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ActionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Tree(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    column = db.Column(db.Integer, nullable=False, unique=True)
    chopped_at = db.Column(db.DateTime, nullable=True)
    removed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Stone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    column = db.Column(db.Integer, nullable=False, unique=True)
    mined_at = db.Column(db.DateTime, nullable=True)
    removed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
