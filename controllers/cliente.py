from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_required, current_user
from models.cliente import Cliente
from models.semana_nutricional import SemanaNutricional
from models.plan_diario import PlanAlimenticioDiario
from datetime import datetime

bp = Blueprint("cliente", __name__, url_prefix="/clientes")

@bp.route("/")
@login_required
def lista_clientes():
    clientes = g.srp.filter(Cliente, lambda c: c.coach_email == current_user.email)
    return render_template("clientes/lista.html", clientes=clientes)

@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    if request.method == "POST":    
        nombre = request.form["nombre"]
        email = request.form["email"]
        objetivo = request.form["objetivo"]
        
        if not nombre or not objetivo:
            flash("Todos los campos obligatorios deben ser completados", "error")
            return redirect(url_for("cliente.nuevo_cliente"))
            
        if len(nombre) < 2 or len(objetivo) < 3:
            flash("El nombre debe tener al menos 2 caracteres y el objetivo al menos 3", "error")
            return redirect(url_for("cliente.nuevo_cliente"))
            
        try:
            edad = int(request.form["edad"])
            peso = float(request.form["peso"])
            altura = float(request.form["altura"])
            
            if not (1 <= edad <= 120 and 10 <= peso <= 500 and 50 <= altura <= 300):
                flash("Los valores están fuera del rango permitido", "error")
                return redirect(url_for("cliente.nuevo_cliente"))
                
        except ValueError:
            flash("Los valores numéricos son incorrectos", "error")
            return redirect(url_for("cliente.nuevo_cliente"))
        
    # Asegurar que el email sea único
        cliente_existente = g.srp.find_first(Cliente, lambda c: c.email == email and c.coach_email == current_user.email)
        if cliente_existente:
            flash("Ya existe un cliente con este correo electrónico", "error")
            return redirect(url_for("cliente.nuevo_cliente"))

        cliente = Cliente(nombre, email, edad, peso, altura, objetivo, current_user.email)
        g.srp.save(cliente)
        flash(f"Cliente {nombre} añadido correctamente", "success")
        return redirect(url_for("cliente.lista_clientes"))

    return render_template("clientes/nuevo.html")

@bp.route("/<cliente_email>")
@login_required
def dashboard_cliente(cliente_email):
    cliente = g.srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for("cliente.lista_clientes"))   
    semanas = list(g.srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente_email))
    semanas.sort(key=lambda s: s.fecha_inicio, reverse=True)
    semanas_data = []
    for semana in semanas:
        safe_id = g.srp.safe_from_oid(semana.__oid__)
        # Asegurar que fecha_inicio y fecha_fin son objetos date
        fecha_inicio = semana.fecha_inicio
        if hasattr(fecha_inicio, 'date'):
            fecha_inicio = fecha_inicio.date()
            
        fecha_fin = semana.fecha_fin
        if hasattr(fecha_fin, 'date'):
            fecha_fin = fecha_fin.date()
            
        semanas_data.append({
            "semana": semana,
            "safe_id": safe_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })
    
    # Pasar la fecha actual como date para comparaciones en el template
    today = datetime.now().date()

    return render_template("clientes/dashboard.html", cliente=cliente, semanas=semanas_data, today=today)

@bp.route("/<cliente_email>/eliminar")
@login_required
def eliminar_cliente(cliente_email):
    try:
        # Verificar que el cliente existe y pertenece al coach actual
        cliente = g.srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
        if not cliente:
            flash("Cliente no encontrado", "error")
            return redirect(url_for("cliente.lista_clientes"))

        # Buscar y eliminar las semanas y sus planes alimenticios asociados
        cliente_id = cliente.__oid__
        
        # Eliminar todas las semanas y planes relacionados
        semanas = list(g.srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente.email))
        for semana in semanas:
            semana_oid = semana.__oid__
            planes = list(g.srp.filter(PlanAlimenticioDiario, lambda p: p.id_semana == semana_oid))
            for plan in planes:
                g.srp.delete(plan.__oid__)
            g.srp.delete(semana_oid)
        
        # Finalmente eliminar el cliente
        g.srp.delete(cliente_id)
        
        flash("Cliente eliminado con éxito", "success")
    except Exception as e:
        flash(f"Error al eliminar el cliente: {str(e)}", "error")
    
    return redirect(url_for("cliente.lista_clientes"))

@bp.route("/editar/<cliente_email>", methods=["GET", "POST"])
@login_required
def editar_cliente(cliente_email):
    # Verificar que el cliente existe y pertenece al coach actual
    cliente = g.srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for("cliente.lista_clientes"))
        
    if request.method == "POST":
        nombre = request.form["nombre"]
        objetivo = request.form.get("objetivo")
        
        # Validaciones básicas
        if not nombre or not objetivo:
            flash("Todos los campos obligatorios deben ser completados", "error")
            return redirect(url_for("cliente.editar_cliente", cliente_email=cliente_email))
            
        if len(nombre) < 2 or len(objetivo) < 3:
            flash("El nombre debe tener al menos 2 caracteres y el objetivo al menos 3", "error")
            return redirect(url_for("cliente.editar_cliente", cliente_email=cliente_email))
            
        # Validar campos numéricos
        try:
            edad = int(request.form["edad"])
            peso = float(request.form["peso"])
            altura = float(request.form["altura"])
            
            if not (1 <= edad <= 120 and 10 <= peso <= 500 and 50 <= altura <= 300):
                flash("Los valores están fuera del rango permitido", "error")
                return redirect(url_for("cliente.editar_cliente", cliente_email=cliente_email))
                
        except ValueError:
            flash("Los valores numéricos son incorrectos", "error")
            return redirect(url_for("cliente.editar_cliente", cliente_email=cliente_email))        
        
        cliente.nombre = nombre
        cliente.edad = edad
        cliente.peso = peso
        cliente.altura = altura
        cliente.objetivo = objetivo
        
        g.srp.save(cliente)
        flash(f"Cliente {nombre} actualizado correctamente", "success")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente.email))

    return render_template("clientes/editar.html", cliente=cliente)
