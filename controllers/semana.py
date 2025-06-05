"""Módulo para gestionar las semanas nutricionales en la aplicación NutriCoach."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_required, current_user
from models.cliente import Cliente
from models.semana_nutricional import SemanaNutricional
from models.plan_diario import PlanAlimenticioDiario
from datetime import datetime, timedelta

bp = Blueprint("semana", __name__, url_prefix="/semanas")

# Función auxiliar para obtener días y planes de una semana
def get_dias_semana(semana):
    """Obtiene los días y los planes alimenticios asociados a una semana nutricional.

    :param semana: Objeto de la semana nutricional.
    :return: Lista de tuplas con los días y sus respectivos planes alimenticios.
    """
    dias = []
    
    planes = list(g.srp.filter(PlanAlimenticioDiario, lambda p: p.id_semana == semana.__oid__))
    planes_por_fecha = {p.fecha.strftime('%Y-%m-%d'): p for p in planes}
    
    for i in range(7):
        dia = semana.fecha_inicio + timedelta(days=i)
        clave = dia.strftime('%Y-%m-%d')
        plan = planes_por_fecha.get(clave)
        dias.append((dia, plan))
        
    return dias

@bp.app_template_filter('get_dias_semana')
def get_dias_semana_filter(semana):
    """Filtro de plantilla para obtener los días y planes de una semana nutricional.

    :param semana: Objeto de la semana nutricional.
    :return: Lista de días y planes alimenticios.
    """
    return get_dias_semana(semana)

@bp.route("/<cliente_email>/nueva", methods=["GET", "POST"])
@login_required
def nueva_semana(cliente_email):
    """Crea una nueva semana nutricional para un cliente específico.

    :param cliente_email: Correo electrónico del cliente.
    :return: Redirige al dashboard del cliente o renderiza el formulario de creación de semana.
    """
    cliente = g.srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for("cliente.lista_clientes"))

    if request.method == "POST":
        estado = request.form["estado"]
        notas = request.form["notas"]
        
        if not estado or not notas or len(estado) < 3 or len(notas) < 5:
            flash("El estado debe tener al menos 3 caracteres y las notas al menos 5", "error")
            return redirect(url_for("semana.nueva_semana", cliente_email=cliente_email))
        
        try:
            calorias = int(request.form["calorias"])
            proteinas = int(request.form["proteinas"])
            hidratos = int(request.form["hidratos"])
            grasas = int(request.form["grasas"])
            
            if not (500 <= calorias <= 10000 and 10 <= proteinas <= 500 and 
                   10 <= hidratos <= 1000 and 5 <= grasas <= 500):
                flash("Algunos valores nutricionales están fuera del rango permitido", "error")
                return redirect(url_for("semana.nueva_semana", cliente_email=cliente_email))
                
        except ValueError:
            flash("Los valores nutricionales deben ser números válidos", "error")
            return redirect(url_for("semana.nueva_semana", cliente_email=cliente_email))

        ultimas_semanas = list(g.srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente_email))
        ultimas_semanas.sort(key=lambda s: s.fecha_fin, reverse=True)
        
        # Determinar fecha de inicio para la nueva semana
        if ultimas_semanas:
            ultima_semana = ultimas_semanas[0]
            fecha_inicio = ultima_semana.fecha_fin + timedelta(days=1)
        else:
            hoy = datetime.today().date()
            dias_hasta_lunes = (7 - hoy.weekday()) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7 
            fecha_inicio = hoy + timedelta(days=dias_hasta_lunes)
        
        fecha_fin = fecha_inicio + timedelta(days=6)
        
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
        g.srp.save(semana)
        flash("Nueva semana creada correctamente", "success")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

    # rellenar con última semana si existe
    ultimas_semanas = list(g.srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente_email))
    ultimas_semanas.sort(key=lambda s: s.fecha_inicio, reverse=True)
    objetivos_default = {"calorias": "", "proteinas": "", "hidratos": "", "grasas": ""}
    ult_obj = ultimas_semanas[0].objetivos if ultimas_semanas else objetivos_default

    return render_template("semana_nutricional/nueva_semana.html", cliente=cliente, objetivos=ult_obj)

@bp.route("/<cliente_email>/ver/<safe_id>")
@login_required
def ver_semana(cliente_email, safe_id):
    """Muestra los detalles de una semana nutricional específica.

    :param cliente_email: Correo electrónico del cliente.
    :param safe_id: Identificador seguro de la semana nutricional.
    :return: Plantilla renderizada con los detalles de la semana.
    """
    try:
        oid = g.srp.oid_from_safe(safe_id)
        semana = g.srp.load(oid)
        
        if not semana or semana.cliente_email != cliente_email:
            flash("Semana no encontrada", "error")
            return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))
            
        return render_template("semana_nutricional/semana.html", semana=semana, cliente_email=cliente_email, safe_id=safe_id)
        
    except Exception:
        flash("ID de semana no válido", "error")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

@bp.route("/<cliente_email>/editar/<safe_id>", methods=["GET", "POST"])
@login_required
def editar_semana(cliente_email, safe_id):
    """Edita los detalles de una semana nutricional existente.

    :param cliente_email: Correo electrónico del cliente.
    :param safe_id: Identificador seguro de la semana nutricional.
    :return: Redirige a la vista de la semana o renderiza el formulario de edición.
    """
    cliente = g.srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for("cliente.lista_clientes"))
        
    try:
        oid = g.srp.oid_from_safe(safe_id)
        semana = g.srp.load(oid)
        
        if not semana or semana.cliente_email != cliente_email:
            flash("Semana no encontrada", "error")
            return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))
    except Exception:
        flash("ID de semana no válido", "error")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))
    
    if request.method == "POST":
        estado = request.form["estado"]
        notas = request.form["notas"]
        
        if not estado or not notas or len(estado) < 3 or len(notas) < 5:
            flash("El estado debe tener al menos 3 caracteres y las notas al menos 5", "error")
            return redirect(url_for("semana.editar_semana", cliente_email=cliente_email, safe_id=safe_id))
        
        try:
            calorias = int(request.form["calorias"])
            proteinas = int(request.form["proteinas"])
            hidratos = int(request.form["hidratos"])
            grasas = int(request.form["grasas"])
            
            if not (500 <= calorias <= 10000 and 10 <= proteinas <= 500 and 
                   10 <= hidratos <= 1000 and 5 <= grasas <= 500):
                flash("Algunos valores nutricionales están fuera del rango permitido", "error")
                return redirect(url_for("semana.editar_semana", cliente_email=cliente_email, safe_id=safe_id))
                
        except ValueError:
            flash("Los valores nutricionales deben ser números válidos", "error")
            return redirect(url_for("semana.editar_semana", cliente_email=cliente_email, safe_id=safe_id))
        
        semana.estado_general = estado
        semana.notas = notas
        semana.objetivos = {
            "calorias": calorias,
            "proteinas": proteinas,
            "hidratos": hidratos,
            "grasas": grasas
        }
        
        g.srp.save(semana)
        flash("Semana actualizada correctamente", "success")
        return redirect(url_for("semana.ver_semana", cliente_email=cliente_email, safe_id=safe_id))
        
    return render_template("semana_nutricional/editar_semana.html", cliente=cliente, semana=semana, safe_id=safe_id)

@bp.route("/<cliente_email>/eliminar/<safe_id>")
@login_required
def eliminar_semana(cliente_email, safe_id):
    """Elimina una semana nutricional y sus planes alimenticios asociados.

    :param cliente_email: Correo electrónico del cliente.
    :param safe_id: Identificador seguro de la semana nutricional.
    :return: Redirige al dashboard del cliente.
    """
    cliente = g.srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for("cliente.lista_clientes"))
    
    try:
        oid = g.srp.oid_from_safe(safe_id)
        semana = g.srp.load(oid)
        
        if not semana or semana.cliente_email != cliente_email:
            flash("Semana no encontrada", "error")
            return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))
            
        planes = list(g.srp.filter(PlanAlimenticioDiario, lambda p: p.id_semana == oid))
        
        for plan in planes:
            g.srp.delete(plan.__oid__)
        
        g.srp.delete(oid)
        
        flash("Semana eliminada correctamente", "success")
        
    except Exception as e:
        flash(f"Error al eliminar la semana: {str(e)}", "error")
        
    return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))