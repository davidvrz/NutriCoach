from flask import Flask, redirect
from flask_login import LoginManager
import sirope
from datetime import datetime

from models.coach import Coach
from controllers import auth, cliente 

def create_app():
    app = Flask(__name__)
    app.secret_key = "nutricoach-clave-secreta"

    # Sirope y Flask-Login
    srp = sirope.Sirope()
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def user_loader(email):
        return srp.find_first(Coach, lambda c: c.email == email)

    # Añadir contexto global para las plantillas
    @app.context_processor
    def inject_now():
        return {
            'now': datetime.now(),
            'hasattr': hasattr  # Agregar función hasattr para poder usarla en plantillas
        }

    # Registrar blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(cliente.bp)

    # Rutas simples de redirección
    @app.route("/")
    def index():
        return redirect("/clientes")

    # Mantener la ruta /home por compatibilidad, pero redirige a /clientes
    @app.route("/home")
    def home():
        return redirect("/clientes")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
