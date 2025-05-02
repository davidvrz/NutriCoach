from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sirope
from models.cliente import Cliente
from models.semana_nutricional import SemanaNutricional
from models.plan_diario import PlanAlimenticioDiario
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

@bp.route("/<cliente_email>/semana/<safe_id>")
@login_required
def ver_semana(cliente_email, safe_id):
    oid = sirope.oid_from_safe(safe_id)
    semana = srp.load(oid)

    if not semana or semana.cliente_email != cliente_email:
        flash("Semana no encontrada.")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

    # Obtener planes existentes
    planes = list(srp.filter(PlanAlimenticioDiario, lambda p: p.id_semana == oid))
    planes_por_fecha = {p.fecha.strftime('%Y-%m-%d'): p for p in planes}

    # Generar los 7 días
    dias = []
    for i in range(7):
        dia = semana.fecha_inicio + timedelta(days=i)
        clave = dia.strftime('%Y-%m-%d')
        plan = planes_por_fecha.get(clave)
        dias.append((dia, plan))

    return render_template("clientes/semana.html", semana=semana, dias=dias, cliente_email=cliente_email, safe_id=safe_id)

@bp.route("/<cliente_email>/semana/<safe_id>/editar/<fecha>", methods=["GET", "POST"])
@login_required
def editar_dia(cliente_email, safe_id, fecha):
    oid = sirope.oid_from_safe(safe_id)
    semana = srp.load(oid)

    if not semana or semana.cliente_email != cliente_email:
        flash("Semana no encontrada.")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()

    # Buscar si ya existe un plan para ese día
    plan_existente = srp.find_first(PlanAlimenticioDiario, lambda p: p.id_semana == oid and p.fecha == fecha_obj)

    if request.method == "POST":
        estado = request.form["estado"]
        notas = request.form["notas"]
        comidas = {}
        for comida in ["desayuno", "comida", "merienda", "cena", "snacks"]:
            comidas[comida] = {
                "descripcion": request.form[f"{comida}_desc"],
                "calorias": int(request.form[f"{comida}_cal"]),
                "proteinas": int(request.form[f"{comida}_prot"]),
                "hidratos": int(request.form[f"{comida}_hidr"]),
                "grasas": int(request.form[f"{comida}_gras"])
            }

        plan = plan_existente or PlanAlimenticioDiario(oid, fecha_obj, estado, notas, comidas)

        # Si es nuevo, guardar. Si ya existía, actualizar campos.
        if plan_existente:
            plan.estado = estado
            plan.notas = notas
            plan.comidas = comidas
        else:
            srp.save(plan)

        return redirect(url_for("cliente.ver_semana", cliente_email=cliente_email, safe_id=safe_id))

    return render_template("clientes/plan_diario.html", cliente_email=cliente_email, semana=semana,
                           fecha=fecha_obj, plan=plan_existente, safe_id=safe_id)
