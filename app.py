"""Aplicación principal de NutriCoach.

Este módulo configura y ejecuta la aplicación Flask, registrando los blueprints y configurando la gestión de usuarios.
"""

from flask import Flask, redirect, g, url_for
from flask_login import LoginManager
import sirope
from datetime import datetime

from models.coach import Coach
from controllers import auth, cliente, semana, plan 

srp = sirope.Sirope()

def create_app():
    """Crea y configura la aplicación Flask.

    :return: La instancia de la aplicación Flask configurada.
    """
    app = Flask(__name__)
    app.secret_key = "nutricoach-clave-secreta"

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def user_loader(email):
        """Carga un usuario basado en su correo electrónico.

        :param email: Correo electrónico del usuario.
        :return: Instancia del usuario Coach o None si no se encuentra.
        """
        return srp.find_first(Coach, lambda c: c.email == email)

    @app.before_request
    def before_request():
        """Configura el objeto global g antes de cada solicitud.

        Asigna la instancia de Sirope al objeto global g.
        """
        g.srp = srp

    @app.context_processor
    def inject_now():
        """Inyecta la fecha y hora actual en el contexto de las plantillas.

        :return: Diccionario con la clave 'now' y la fecha y hora actual.
        """
        return {
            'now': datetime.now(),
        }

    app.register_blueprint(auth.bp)
    app.register_blueprint(cliente.bp)
    app.register_blueprint(semana.bp)
    app.register_blueprint(plan.bp)

    @app.route("/")
    def index():
        """Redirige a la lista de clientes.

        :return: Redirección a la ruta de lista de clientes.
        """
        return redirect(url_for("cliente.lista_clientes"))

    @app.route("/home")
    def home():
        """Redirige a la lista de clientes.

        :return: Redirección a la ruta de lista de clientes.
        """
        return redirect(url_for("cliente.lista_clientes"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
