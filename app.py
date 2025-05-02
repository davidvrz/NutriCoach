from flask import Flask
from flask_login import LoginManager, login_required, current_user
import sirope

from models.coach import Coach
from controllers import auth

def create_app():
    app = Flask(__name__)
    app.secret_key = "nutricoach-clave-secreta"

    # Sirope y Flask-Login
    srp = sirope.Sirope()
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"  # Redirige a /login si no está logueado

    @login_manager.user_loader
    def user_loader(email):
        return srp.find_first(Coach, lambda c: c.email == email)

    # Registrar blueprints
    app.register_blueprint(auth.bp)

    return app

# Crear app
app = create_app()

from flask import redirect

@app.route("/")
def index():
    return redirect("/login")

# Ruta protegida de bienvenida al coach
@app.route("/dashboard")
@login_required
def dashboard():
    return f"Bienvenido, {current_user.nombre}. Esta es tu área de trabajo."

# Ejecutar servidor
if __name__ == "__main__":
    app.run(debug=True)
