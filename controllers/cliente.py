from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sirope
from models.cliente import Cliente

bp = Blueprint("cliente", __name__, url_prefix="/clientes")
srp = sirope.Sirope()

@bp.route("/")
@login_required
def lista_clientes():
    clientes = srp.filter(Cliente, lambda c: c.coach_email == current_user.email)
    return render_template("clientes/lista.html", clientes=clientes)

@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    if request.method == "POST":
        nombre = request.form["nombre"]
        edad = int(request.form["edad"])
        peso = float(request.form["peso"])
        altura = float(request.form["altura"])
        objetivo = request.form["objetivo"]

        cliente = Cliente(nombre, edad, peso, altura, objetivo, current_user.email)
        srp.save(cliente)
        return redirect(url_for("cliente.lista_clientes"))

    return render_template("clientes/nuevo.html")
