"""Módulo de autenticación para NutriCoach.
Este módulo gestiona el registro, inicio de sesión y cierre de sesión de los usuarios (coaches).
"""

from flask import Blueprint, render_template, request, redirect, flash, url_for, session, g
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models.coach import Coach

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["GET", "POST"])
def register():
    """Maneja el registro de nuevos coaches.
    
    :return: Redirige al dashboard del cliente si el registro es exitoso, o vuelve al formulario con errores.
    """
    errors = {}
    if request.method == "POST":
        email = request.form["email"]
        nombre = request.form["nombre"]
        password = request.form["password"]
        valid = True

        if not email:
            errors['email'] = "El email es obligatorio"
            valid = False
            
        if not nombre:
            errors['nombre'] = "El nombre es obligatorio"
            valid = False
            
        if not password:
            errors['password'] = "La contraseña es obligatoria"
            valid = False
            
        if len(nombre) < 3:
            errors['nombre'] = "El nombre debe tener al menos 3 caracteres"
            valid = False
            
        if len(password) < 6:
            errors['password'] = "La contraseña debe tener al menos 6 caracteres"
            valid = False

        if g.srp.find_first(Coach, lambda c: c.email == email):
            errors['email'] = "Ya existe un coach con ese email"
            valid = False

        if valid:
            coach = Coach(email, nombre, generate_password_hash(password))
            g.srp.save(coach)
            login_user(coach)
            return redirect(url_for("cliente.lista_clientes"))
        else:
            flash("Por favor, corrige los errores en el formulario", "error")
            session['form_values'] = request.form
            session['form_errors'] = errors
            return redirect(url_for("auth.register"))

    form_values = session.pop('form_values', {})
    form_errors = session.pop('form_errors', {})
    return render_template("auth/register.html", form_values=form_values, errors=form_errors)

@bp.route("/login", methods=["GET", "POST"])
def login():
    """Maneja el inicio de sesión de los coaches.

    :return: Redirige al dashboard del cliente si el inicio de sesión es exitoso, o vuelve al formulario con errores.
    """
    errors = {}
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        valid = True

        if not email:
            errors['email'] = "El email es obligatorio"
            valid = False
            
        if not password:
            errors['password'] = "La contraseña es obligatoria"
            valid = False

        if valid:
            coach = g.srp.find_first(Coach, lambda c: c.email == email)
            if not coach or not check_password_hash(coach.password_hash, password):
                flash("Credenciales incorrectas", "error")
                return redirect(url_for("auth.login"))

            login_user(coach)
            return redirect(url_for("cliente.lista_clientes"))
        else:
            flash("Por favor, corrige los errores en el formulario", "error")
            session['form_values'] = request.form
            session['form_errors'] = errors
            return redirect(url_for("auth.login"))

    form_values = session.pop('form_values', {})
    form_errors = session.pop('form_errors', {})
    return render_template("auth/login.html", form_values=form_values, errors=form_errors)

@bp.route("/logout")
@login_required
def logout():
    """Maneja el cierre de sesión de los coaches.

    :return: Redirige al formulario de inicio de sesión después de cerrar la sesión.
    """
    logout_user()
    return redirect(url_for("auth.login"))
