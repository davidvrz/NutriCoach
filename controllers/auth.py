from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import sirope

from models.coach import Coach

bp = Blueprint("auth", __name__)
srp = sirope.Sirope()

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        nombre = request.form["nombre"]
        password = request.form["password"]

        if srp.find_first(Coach, lambda c: c.email == email):
            flash("Ya existe un coach con ese email.")
            return redirect("/register")

        coach = Coach(email, nombre, generate_password_hash(password))
        srp.save(coach)
        login_user(coach)
        return redirect("/dashboard")

    return render_template("auth/register.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        coach = srp.find_first(Coach, lambda c: c.email == email)
        if not coach or not check_password_hash(coach.password_hash, password):
            flash("Credenciales incorrectas.")
            return redirect("/login")

        login_user(coach)
        return redirect("/dashboard")

    return render_template("auth/login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
