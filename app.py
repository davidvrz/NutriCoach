from flask import Flask, redirect
from flask_login import LoginManager, login_required, current_user
import sirope

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

    # Registrar blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(cliente.bp)  # 🔹 Añadido

    return app

app = create_app()

@app.route("/")
def index():
    return redirect("/login")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Bienvenido, {current_user.nombre}. Esta es tu área de trabajo."

if __name__ == "__main__":
    app.run(debug=True)
