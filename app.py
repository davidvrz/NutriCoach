from flask import Flask, redirect, g
from flask_login import LoginManager
import sirope
from datetime import datetime

from models.coach import Coach
from controllers import auth, cliente, semana, plan 

# Create a global Sirope instance
srp = sirope.Sirope()

def create_app():
    app = Flask(__name__)
    app.secret_key = "nutricoach-clave-secreta"

    # Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def user_loader(email):
        return srp.find_first(Coach, lambda c: c.email == email)

    # Make srp available to all requests via Flask's g object
    @app.before_request
    def before_request():
        g.srp = srp

    # Añadir contexto global para las plantillas
    @app.context_processor
    def inject_now():
        return {
            'now': datetime.now(),
        }

    # Registrar blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(cliente.bp)
    app.register_blueprint(semana.bp)
    app.register_blueprint(plan.bp)

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
