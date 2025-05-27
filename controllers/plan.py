from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from flask_login import login_required, current_user
from models.plan_diario import PlanAlimenticioDiario, PlanPredefinido
from models.semana_nutricional import SemanaNutricional
from datetime import datetime

bp = Blueprint("plan", __name__, url_prefix="/planes")

# Rutas existentes
@bp.route("/<cliente_email>/semana/<safe_id>/editar/<fecha>", methods=["GET", "POST"])
@login_required
def editar_dia(cliente_email, safe_id, fecha):
    # Validar y cargar la semana
    try:
        oid = g.srp.oid_from_safe(safe_id)
        semana = g.srp.load(oid)
        if not semana or semana.cliente_email != cliente_email:
            flash("Semana no encontrada", "error")
            return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))
            
        # Validar formato de fecha
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except Exception:
        flash("Datos de semana o fecha no válidos", "error")
        return redirect(url_for("cliente.dashboard_cliente", cliente_email=cliente_email))

    # Buscar si ya existe un plan para ese día
    plan_existente = g.srp.find_first(PlanAlimenticioDiario, lambda p: p.id_semana == oid and p.fecha == fecha_obj)
      # Obtener los planes predefinidos del coach
    planes_predefinidos = list(g.srp.filter(PlanPredefinido, lambda p: p.coach_email == current_user.email))
    
    # Preparar los planes predefinidos con IDs seguros para la plantilla
    planes_con_safe_id = []
    for plan in planes_predefinidos:
        plan_data = plan.__dict__.copy()
        plan_data['safe_id'] = g.srp.safe_from_oid(plan.__oid__)
        planes_con_safe_id.append(plan_data)

    if request.method == "POST":
        estado = request.form["estado"]
        notas = request.form["notas"]
        
        # Verificar si se está utilizando un plan predefinido
        plan_predefinido_id = request.form.get("plan_predefinido", "")
        if plan_predefinido_id and plan_predefinido_id != "ninguno":
            try:
                # Cargar el plan predefinido seleccionado
                predefinido_oid = g.srp.oid_from_safe(plan_predefinido_id)
                plan_predefinido = g.srp.load(predefinido_oid)
                
                # Usar las comidas del plan predefinido
                comidas = plan_predefinido.comidas.copy()
                
                # Actualizar cualquier valor específico modificado en el formulario
                for comida in ["desayuno", "comida", "merienda", "cena", "snacks"]:
                    if comida in comidas and (request.form.get(f"{comida}_desc") or request.form.get(f"{comida}_cal")):
                        # Si hay valores personalizados, actualizarlos
                        try:
                            valores = {
                                "calorias": int(request.form.get(f"{comida}_cal", comidas[comida]["calorias"])),
                                "proteinas": int(request.form.get(f"{comida}_prot", comidas[comida]["proteinas"])),
                                "hidratos": int(request.form.get(f"{comida}_hidr", comidas[comida]["hidratos"])),
                                "grasas": int(request.form.get(f"{comida}_gras", comidas[comida]["grasas"]))
                            }
                            
                            # Validar rangos
                            if not (0 <= valores["calorias"] <= 5000 and 
                                   0 <= valores["proteinas"] <= 300 and 
                                   0 <= valores["hidratos"] <= 500 and 
                                   0 <= valores["grasas"] <= 300):
                                flash(f"Algunos valores nutricionales para {comida} están fuera de rango", "error")
                                return redirect(url_for("plan.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))
                            
                            # Actualizar descripción y valores
                            nueva_desc = request.form.get(f"{comida}_desc", comidas[comida]["descripcion"])
                            comidas[comida] = {
                                "descripcion": nueva_desc,
                                **valores
                            }
                        except ValueError:
                            flash(f"Los valores para {comida} deben ser números válidos", "error")
                            return redirect(url_for("plan.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))
            except Exception:
                flash("Plan predefinido no encontrado", "error")
                return redirect(url_for("plan.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))
        else:
            # Procesar datos de comidas manualmente (código existente)
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
                            return redirect(url_for("plan.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))
                        
                        # Guardar datos de esta comida
                        comidas[comida] = {
                            "descripcion": request.form[f"{comida}_desc"],
                            **valores  # Incorporar todos los valores nutricionales
                        }
                    except ValueError:
                        flash(f"Los valores para {comida} deben ser números válidos", "error")
                        return redirect(url_for("plan.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))
        
        # Validación básica del estado
        if not estado or len(estado) < 3:
            flash("El estado del día debe tener al menos 3 caracteres", "error")
            return redirect(url_for("plan.editar_dia", cliente_email=cliente_email, safe_id=safe_id, fecha=fecha))

        # Crear nuevo plan o actualizar el existente
        if plan_existente:
            plan_existente.estado = estado
            plan_existente.notas = notas
            plan_existente.comidas = comidas
            plan = plan_existente
        else:
            plan = PlanAlimenticioDiario(oid, fecha_obj, estado, notas, comidas)
            g.srp.save(plan)
        flash("Plan alimenticio actualizado correctamente", "success")
        return redirect(url_for("semana.ver_semana", cliente_email=cliente_email, safe_id=safe_id))
        
    return render_template(
        "plan_diario/plan_diario.html", 
        cliente_email=cliente_email, 
        semana=semana,
        fecha=fecha_obj, 
        plan=plan_existente, 
        safe_id=safe_id,
        planes_predefinidos=planes_con_safe_id
    )

# Ruta para obtener plan predefinido mediante AJAX
@bp.route("/predefinido/<safe_id>", methods=["GET"])
@login_required
def obtener_plan_predefinido(safe_id):
    try:
        oid = g.srp.oid_from_safe(safe_id)
        plan = g.srp.load(oid)
        
        # Verificar que el plan pertenece al coach actual
        if not plan or plan.coach_email != current_user.email:
            return jsonify({"error": "Plan no encontrado"}), 404
            
        return jsonify({
            "nombre": plan.nombre,
            "descripcion": plan.descripcion,
            "tipo": plan.tipo,
            "comidas": plan.comidas
        })
        
    except Exception:
        return jsonify({"error": "Error al cargar el plan"}), 500

# Nuevas rutas para gestionar los planes predefinidos
@bp.route("/predefinidos")
@login_required
def lista_planes_predefinidos():
    planes = list(g.srp.filter(PlanPredefinido, lambda p: p.coach_email == current_user.email))
    planes.sort(key=lambda p: p.actualizado, reverse=True)  # Ordenar por fecha de actualización
    
    # Preparar los datos para la plantilla con los IDs convertidos
    planes_con_safe_id = []
    for plan in planes:
        plan_data = plan.__dict__.copy()
        plan_data['safe_id'] = g.srp.safe_from_oid(plan.__oid__)
        planes_con_safe_id.append(plan_data)
    
    return render_template("plan_diario/planes_predefinidos.html", planes=planes_con_safe_id)

@bp.route("/predefinidos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_plan_predefinido():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        tipo = request.form["tipo"]
        
        # Validaciones básicas
        if not nombre or len(nombre) < 3:
            flash("El nombre debe tener al menos 3 caracteres", "error")
            return redirect(url_for("plan.nuevo_plan_predefinido"))
            
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
                        return redirect(url_for("plan.nuevo_plan_predefinido"))
                    
                    # Guardar datos de esta comida
                    comidas[comida] = {
                        "descripcion": request.form[f"{comida}_desc"],
                        **valores  # Incorporar todos los valores nutricionales
                    }
                except ValueError:
                    flash(f"Los valores para {comida} deben ser números válidos", "error")
                    return redirect(url_for("plan.nuevo_plan_predefinido"))

        # Crear y guardar el plan predefinido
        plan = PlanPredefinido(current_user.email, nombre, descripcion, comidas, tipo)
        g.srp.save(plan)
        flash("Plan predefinido creado correctamente", "success")
        return redirect(url_for("plan.lista_planes_predefinidos"))

    return render_template("plan_diario/nuevo_plan_predefinido.html")

@bp.route("/predefinidos/editar/<safe_id>", methods=["GET", "POST"])
@login_required
def editar_plan_predefinido(safe_id):
    try:
        oid = g.srp.oid_from_safe(safe_id)
        plan = g.srp.load(oid)
        
        # Verificar que el plan pertenece al coach actual
        if not plan or plan.coach_email != current_user.email:
            flash("Plan predefinido no encontrado", "error")
            return redirect(url_for("plan.lista_planes_predefinidos"))
    except Exception:
        flash("ID de plan no válido", "error")
        return redirect(url_for("plan.lista_planes_predefinidos"))
    
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        tipo = request.form["tipo"]
        
        # Validaciones básicas
        if not nombre or len(nombre) < 3:
            flash("El nombre debe tener al menos 3 caracteres", "error")
            return redirect(url_for("plan.editar_plan_predefinido", safe_id=safe_id))
            
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
                        return redirect(url_for("plan.editar_plan_predefinido", safe_id=safe_id))
                    
                    # Guardar datos de esta comida
                    comidas[comida] = {
                        "descripcion": request.form[f"{comida}_desc"],
                        **valores  # Incorporar todos los valores nutricionales
                    }
                except ValueError:
                    flash(f"Los valores para {comida} deben ser números válidos", "error")
                    return redirect(url_for("plan.editar_plan_predefinido", safe_id=safe_id))

        # Actualizar el plan
        plan.nombre = nombre
        plan.descripcion = descripcion
        plan.tipo = tipo
        plan.comidas = comidas
        plan.actualizado = datetime.now()
        
        g.srp.save(plan)
        flash("Plan predefinido actualizado correctamente", "success")
        return redirect(url_for("plan.lista_planes_predefinidos"))

    return render_template("plan_diario/editar_plan_predefinido.html", plan=plan, safe_id=safe_id)

@bp.route("/predefinidos/eliminar/<safe_id>")
@login_required
def eliminar_plan_predefinido(safe_id):
    try:
        oid = g.srp.oid_from_safe(safe_id)
        plan = g.srp.load(oid)
        
        # Verificar que el plan pertenece al coach actual
        if not plan or plan.coach_email != current_user.email:
            flash("Plan predefinido no encontrado", "error")
            return redirect(url_for("plan.lista_planes_predefinidos"))
            
        # Eliminar el plan
        g.srp.delete(oid)
        flash("Plan predefinido eliminado correctamente", "success")
        
    except Exception as e:
        flash(f"Error al eliminar el plan: {str(e)}", "error")
        
    return redirect(url_for("plan.lista_planes_predefinidos"))