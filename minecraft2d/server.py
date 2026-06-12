# Ponto de entrada principal do servidor. ✅ (Lab 07/08 — server.py).
# Cria a app Flask, carrega configurações, inicializa a base de dados e regista as rotas.
from flask import Flask

from extensions import login_manager
from models import Database
from settings import DATABASE_PATH, SECRET_KEY


# Cria a instância da aplicação Flask. ✅ (Lab 07 — Flask(__name__)).
app = Flask(__name__)

# Configura a chave secreta para sessões. ✅ (Lab 07/08 — SECRET_KEY).
app.config["SECRET_KEY"] = SECRET_KEY

# Inicializa a base de dados e guarda-a na config da app.
# ❌ fora (Lab 07 guarda a BD como variável global, não em app.config).
# Usado assim para que auth.py e game.py consigam aceder à BD via current_app.
database = Database(DATABASE_PATH)
app.config["db"] = database

# Liga o Flask-Login à app. ✅ (Lab 08 — login_manager.init_app(app)).
login_manager.init_app(app)

# Importa e regista os Blueprints (auth e game).
# Blueprint ❌ fora (Lab 07/08 usam add_url_rule com views.py).
# Usado para organizar rotas em ficheiros separados sem conflitos.
from auth import auth_bp
from game import game_bp

app.register_blueprint(auth_bp)
app.register_blueprint(game_bp)

# Arranca o servidor. ✅ (Lab 07 — app.run).
# debug=False ❌ fora (Lab 07 usa debug=True). Desativado em produção para evitar double-execution e segurança.
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8001)
