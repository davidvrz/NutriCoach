from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sirope
from models.cliente import Cliente
from models.semana_nutricional import SemanaNutricional
from models.plan_diario import PlanAlimenticioDiario
from datetime import datetime, timedelta

bp = Blueprint("cliente", __name__, url_prefix="/clientes")
srp = sirope.Sirope()

# Función auxiliar para obtener días y planes de una semana
def get_dias_semana(semana):
    dias = []
    
    # Obtener planes existentes
    planes = list(srp.filter(PlanAlimenticioDiario, lambda p: p.id_semana == semana.__oid__))
    planes_por_fecha = {p.fecha.strftime('%Y-%m-%d'): p for p in planes}
    
    # Generar los 7 días de la semana
    for i in range(7):
        dia = semana.fecha_inicio + timedelta(days=i)
        clave = dia.strftime('%Y-%m-%d')
        plan = planes_por_fecha.get(clave)
        dias.append((dia, plan))
        
    return dias

# Exponemos la función como un helper para las plantillas
@bp.app_template_filter('get_dias_semana')
def get_dias_semana_filter(semana):
    return get_dias_semana(semana)

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
        email = request.form.get("email")
        objetivo = request.form.get("objetivo")
        
        # Validaciones básicas
        if not nombre or not objetivo:
            flash("Todos los campos obligatorios deben ser completados", "error")
            return redirect(url_for("cliente.nuevo_cliente"))
            
        if len(nombre) < 2 or len(objetivo) < 3:
            flash("El nombre debe tener al menos 2 caracteres y el objetivo al menos 3", "error")
            return redirect(url_for("cliente.nuevo_cliente"))
            
        # Validar campos numéricos
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
        cliente_existente = srp.find_first(Cliente, lambda c: hasattr(c, 'email') and c.email == email and c.coach_email == current_user.email)
        if cliente_existente:
            flash("Ya existe un cliente con este correo electrónico", "error")
            return redirect(url_for("cliente.nuevo_cliente"))

        cliente = Cliente(nombre, email, edad, peso, altura, objetivo, current_user.email)
        srp.save(cliente)
        flash(f"Cliente {nombre} añadido correctamente", "success")
        return redirect(url_for("cliente.lista_clientes"))

    return render_template("clientes/nuevo.html")

@bp.route("/<cliente_email>")
@login_required
def dashboard_cliente(cliente_email):
    # Encontrar el cliente por email
    cliente = srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for("cliente.lista_clientes"))

    # Buscar semanas asociadas al cliente
    semanas = list(srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente_email))
    semanas.sort(key=lambda s: s.fecha_inicio, reverse=True)

    semanas_data = []
    for semana in semanas:
        safe_id = srp.safe_from_oid(semana.__oid__)
        semanas_data.append({
            "semana": semana,
            "safe_id": safe_id,
        })

    return render_template("clientes/dashboard.html", cliente=cliente, semanas=semanas_data)

@bp.route("/<cliente_email>/nueva-semana", methods=["GET", "POST"])
@login_required
def nueva_semana(cliente_email):
    # Verificar que el cliente existe
    cliente = srp.find_first(Cliente, lambda c: c.email == cliente_email and c.coach_email == current_user.email)
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for("cliente.lista_clientes"))

    if request.method == "POST":
        estado = request.form["estado"]
        notas = request.form["notas"]
        
        # Validaciones básicas
        if not estado or not notas or len(estado) < 3 or len(notas) < 5:
            flash("El estado debe tener al menos 3 caracteres y las notas al menos 5", "error")
            return redirect(url_for("cliente.nueva_semana", cliente_email=cliente_email))
        
        # Validar valores nutricionales
        try:
            calorias = int(request.form["calorias"])
            proteinas = int(request.form["proteinas"])
            hidratos = int(request.form["hidratos"])
            grasas = int(request.form["grasas"])
            
            # Validar rangos en una sola condición
            if not (500 <= calorias <= 10000 and 10 <= proteinas <= 500 and 
                   10 <= hidratos <= 1000 and 5 <= grasas <= 500):
                flash("Algunos valores nutricionales están fuera del rango permitido", "error")
                return redirect(url_for("cliente.nueva_semana", cliente_email=cliente_email))
                
        except ValueError:
            flash("Los valores nutricionales deben ser números válidos", "error")
            return redirect(url_for("cliente.nueva_semana", cliente_email=cliente_email))

        # Crear semana con fecha actual
        hoy = datetime.today()
        objetivos = {
            "calorias": calorias,
            "proteinas": proteinas,
            "hidratos": hidratos,
            "grasas": grasas
        }

        semana = SemanaNutricional(
            cliente_email,
            hoy,
            hoy + timedelta(days=6),
            estado,
            notas,
            objetivos
        )
        srp.save(semana)
        flash("Nueva semana creada correctamente", "success")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

    # GET → pre-rellenar con última semana si existe
    ultimas_semanas = list(srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente_email))
    ultimas_semanas.sort(key=lambda s: s.fecha_inicio, reverse=True)
    objetivos_default = {"calorias": "", "proteinas": "", "hidratos": "", "grasas": ""}
    ult_obj = ultimas_semanas[0].objetivos if ultimas_semanas else objetivos_default

    return render_template("clientes/nueva_semana.html", cliente=cliente, objetivos=ult_obj)

@bp.route("/<cliente_email>/semana/<safe_id>")
@login_required
def ver_semana(cliente_email, safe_id):
    # Intentar cargar la semana por su ID seguro
    try:
        oid = srp.oid_from_safe(safe_id)
        semana = srp.load(oid)
        
        # Verificar que la semana existe y pertenece al cliente
        if not semana or semana.cliente_email != cliente_email:
            flash("Semana no encontrada", "error")
            return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))
            
        # Obtener días y planes de la semana
        return render_template("clientes/semana.html", semana=semana, cliente_email=cliente_email, safe_id=safe_id)
        
    except Exception:
        flash("ID de semana no válido", "error")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

@bp.route("/<cliente_email>/semana/<safe_id>/editar/<fecha>", methods=["GET", "POST"])
@login_required
def editar_dia(cliente_email, safe_id, fecha):
    # Validar y cargar la semana
    try:
        oid = srp.oid_from_safe(safe_id)
        semana = srp.load(oid)
        if not semana or semana.cliente_email != cliente_email:
            flash("Semana no encontrada", "error")
            return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))
            
        # Validar formato de fecha
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except Exception:
        flash("Datos de semana o fecha no válidos", "error")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

    # Buscar si ya existe un plan para ese día
    plan_existente = srp.find_first(PlanAlimenticioDiario, lambda p: p.id_semana == oid and p.fecha == fecha_obj)

    if request.method == "POST":
        estado = request.form["estado"]
        notas = request.form["notas"]
        
        # Validación básica del estado
        if not estado or len(estado) < 3:
            flash("El estado del día debe tener al menos 3 caracteres", "error")
            return redirect(url_for("cliente.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))
        
        # Procesar datos de comidas
        comidas = {}
        for comida in ["desayuno", "comida", "merienda", "cena", "snacks"]:
            # Solo procesar si hay datos para esta comida
            if request.form.get(f"{comida}_desc") or request.form.get(f"{comida}_cal"):
                try:
                    # Capturar y validar valores nutricionales
                    valores = {
                        "calorias": int(request.form.get(f"{comida}_cal", 0)),
                        "proteinas": int(request.form.get(f"{comida}_prot", 0)),
                        "hidratos": int(request.form.get(f"{comida}_hidr", 0)),
                        "grasas": int(request.form.get(f"{comida}_gras", 0))
                    }
                    
                    # Validar rangos en una sola condición
                    if not (0 <= valores["calorias"] <= 5000 and 
                           0 <= valores["proteinas"] <= 300 and 
                           0 <= valores["hidratos"] <= 500 and 
                           0 <= valores["grasas"] <= 300):
                        flash(f"Algunos valores nutricionales para {comida} están fuera de rango", "error")
                        return redirect(url_for("cliente.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))
                    
                    # Guardar datos de esta comida
                    comidas[comida] = {
                        "descripcion": request.form[f"{comida}_desc"],
                        **valores  # Incorporar todos los valores nutricionales
                    }
                except ValueError:
                    flash(f"Los valores para {comida} deben ser números válidos", "error")
                    return redirect(url_for("cliente.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))

        # Crear nuevo plan o actualizar el existente
        if plan_existente:
            plan_existente.estado = estado
            plan_existente.notas = notas
            plan_existente.comidas = comidas
            plan = plan_existente
        else:
            plan = PlanAlimenticioDiario(oid, fecha_obj, estado, notas, comidas)
        
        srp.save(plan)
        flash("Plan alimenticio actualizado correctamente", "success")
        return redirect(url_for("cliente.ver_semana", cliente_email=cliente_email, safe_id=safe_id))

    return render_template("clientes/plan_diario.html", 
                          cliente_email=cliente_email, 
                          semana=semana,
                          fecha=fecha_obj, 
                          plan=plan_existente, 
                          safe_id=safe_id)

@bp.route("/<cliente_email>/eliminar")
@login_required
def eliminar_cliente(cliente_email):
    try:
        # Verificar que el cliente existe y pertenece al coach actual
        cliente = srp.find_first(Cliente, lambda c: hasattr(c, 'email') and c.email == cliente_email and c.coach_email == current_user.email)
        if not cliente:
            # Intentar buscar por nombre si el email falla (para clientes antiguos)
            clientes = list(srp.filter(Cliente, lambda c: c.coach_email == current_user.email))
            cliente = next((c for c in clientes if getattr(c, 'nombre', '').lower() in cliente_email.lower()), None)
            
            if not cliente:
                flash("Cliente no encontrado", "error")
                return redirect(url_for("cliente.lista_clientes"))

        # Buscar y eliminar las semanas y sus planes alimenticios asociados
        cliente_id = cliente.__oid__
        # Para clientes antiguos, usamos el OID como identificador en lugar del email
        cliente_identifier = getattr(cliente, 'email', str(cliente_id))
        
        semanas = list(srp.filter(SemanaNutricional, lambda s: s.cliente_email == cliente_identifier))
        for semana in semanas:
            # Obtener el OID de la semana
            semana_oid = semana.__oid__
            
            # Buscar y eliminar los planes diarios asociados a esta semana
            planes = list(srp.filter(PlanAlimenticioDiario, lambda p: p.id_semana == semana_oid))
            for plan in planes:
                srp.delete(plan.__oid__)
            
            # Eliminar la semana
            srp.delete(semana_oid)
        
        # Finalmente eliminar el cliente
        srp.delete(cliente_id)
        
        flash("Cliente eliminado con éxito", "success")
    except Exception as e:
        flash(f"Error al eliminar el cliente: {str(e)}", "error")
    
    return redirect(url_for("cliente.lista_clientes"))

@bp.route("/editar/<cliente_email>", methods=["GET", "POST"])
@login_required
def editar_cliente(cliente_email):
    # Verificar que el cliente existe y pertenece al coach actual
    cliente = srp.find_first(Cliente, lambda c: hasattr(c, 'email') and c.email == cliente_email and c.coach_email == current_user.email)
    
    # Si no lo encuentra, intentar buscar por nombre (para clientes antiguos)
    if not cliente:
        clientes = list(srp.filter(Cliente, lambda c: c.coach_email == current_user.email))
        cliente = next((c for c in clientes if getattr(c, 'nombre', '').lower() in cliente_email.lower()), None)
        
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

        # Actualizar los datos del cliente
        cliente.nombre = nombre
        cliente.edad = edad
        cliente.peso = peso
        cliente.altura = altura
        cliente.objetivo = objetivo
        
        # Si no tenía email, añadirlo
        if not hasattr(cliente, 'email'):
            cliente.email = nombre.lower().replace(' ', '.') + '@nutricoach.com'
        
        srp.save(cliente)
        flash(f"Cliente {nombre} actualizado correctamente", "success")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente.email))

    return render_template("clientes/editar.html", cliente=cliente)
