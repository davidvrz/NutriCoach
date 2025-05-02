from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sirope
from models.cliente import Cliente
from models.semana_nutricional import SemanaNutricional
from datetime import datetime, timedelta

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

@bp.route("/<cliente_email>")
@login_required
def dashboard_cliente(cliente_email):
    # Asegurarse de que el cliente pertenece al coach actual
    cliente = srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    if not cliente:
        flash("Cliente no encontrado.")
        return redirect(url_for("cliente.lista_clientes"))

    semanas = list(srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente_email))
    semanas.sort(key=lambda s: s.fecha_inicio, reverse=True)

    return render_template("clientes/dashboard.html", cliente=cliente, semanas=semanas)

@bp.route("/<cliente_email>/nueva-semana", methods=["GET", "POST"])
@login_required
def nueva_semana(cliente_email):
    cliente = srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    if not cliente:
        flash("Cliente no encontrado.")
        return redirect(url_for("cliente.lista_clientes"))

    if request.method == "POST":
        estado = request.form["estado"]
        notas = request.form["notas"]
        calorias = int(request.form["calorias"])
        proteinas = int(request.form["proteinas"])
        hidratos = int(request.form["hidratos"])
        grasas = int(request.form["grasas"])

        hoy = datetime.today()
        fecha_inicio = hoy
        fecha_fin = hoy + timedelta(days=6)

        objetivos = {
            "calorias": calorias,
            "proteinas": proteinas,
            "hidratos": hidratos,
            "grasas": grasas
        }

        semana = SemanaNutricional(
            cliente_email,
            fecha_inicio,
            fecha_fin,
            estado,
            notas,
            objetivos
        )
        srp.save(semana)
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

    # GET → pre-rellenar con última semana
    ultima = srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente_email)
    ultima = sorted(ultima, key=lambda s: s.fecha_inicio, reverse=True)
    ult_obj = ultima[0].objetivos if ultima else {"calorias": "", "proteinas": "", "hidratos": "", "grasas": ""}

    return render_template("clientes/nueva_semana.html", cliente=cliente, objetivos=ult_obj)
