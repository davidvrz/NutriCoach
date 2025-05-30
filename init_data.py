"""
Script de inicialización de datos para NutriCoach.
Este script crea un coach, dos clientes, una semana nutricional por cliente,
un plan predefinido y un plan diario por semana.

Ejecutar con: python init_data.py
"""

import sirope
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models.coach import Coach
from models.cliente import Cliente
from models.semana_nutricional import SemanaNutricional
from models.plan_diario import PlanAlimenticioDiario, PlanPredefinido

def init_data():
    print("Inicializando datos de ejemplo para NutriCoach...")
    srp = sirope.Sirope()
    
    # Crear coach de ejemplo
    password = "password"
    hashed_password = generate_password_hash(password)
    coach = Coach("coach@example.com", "Nutricoach Demo", hashed_password)
    srp.save(coach)
    print(f"✅ Coach creado: email=coach@example.com, nombre=Nutricoach Demo, password={password}")

    # Crear clientes de ejemplo
    cliente1 = Cliente(
        nombre="Ana García",
        email="cliente1@example.com",
        edad=30,
        peso=65.5,
        altura=165,
        objetivo="Definición",
        coach_email="coach@example.com"
    )
    
    cliente2 = Cliente(
        nombre="Pablo López",
        email="cliente2@example.com",
        edad=42,
        peso=80,
        altura=178,
        objetivo="Volumen",
        coach_email="coach@example.com"
    )
    
    # Guardar clientes
    srp.save(cliente1)
    srp.save(cliente2)
    print("✅ Clientes creados:")
    print("   - email=cliente1@example.com")
    print("   - email=cliente2@example.com")
    # Crear un plan predefinido
    comidas_plan_predefinido = {
        "desayuno": {
            "descripcion": "Tostadas integrales con aguacate y huevos revueltos",
            "calorias": 350,
            "proteinas": 20,
            "hidratos": 30,
            "grasas": 15
        },
        "comida": {
            "descripcion": "Salmón al horno con patatas y brócoli",
            "calorias": 450,
            "proteinas": 35,
            "hidratos": 40,
            "grasas": 15
        },
        "merienda": {
            "descripcion": "Yogur griego con frutos secos",
            "calorias": 220,
            "proteinas": 15,
            "hidratos": 10,
            "grasas": 10
        },
        "cena": {
            "descripcion": "Ensalada de quinoa con pollo y verduras",
            "calorias": 380,
            "proteinas": 30,
            "hidratos": 35,
            "grasas": 8
        }
    }
    
    plan_predefinido = PlanPredefinido(
        coach_email="coach@example.com",
        nombre="Plan Alto en Proteínas",
        descripcion="Plan equilibrado con énfasis en proteínas para recuperación muscular y saciedad",
        comidas=comidas_plan_predefinido,
        tipo="Definición"
    )
    
    # Guardar plan predefinido
    oid_plan_predefinido = srp.save(plan_predefinido)
    print(f"✅ Plan predefinido creado: '{plan_predefinido.nombre}'")
    
    # Fecha actual para las semanas
    hoy = datetime.now()
    
    # --- CLIENTE 1 ---
    
    # Crear semana nutricional para cliente1
    fecha_inicio_c1 = hoy - timedelta(days=hoy.weekday())  # Lunes de la semana actual
    fecha_fin_c1 = fecha_inicio_c1 + timedelta(days=6)  # Domingo

    objetivos_c1 = {
        'calorias': 1800,
        'proteinas': 120,
        'hidratos': 200,
        'grasas': 60
    }
    
    semana_c1 = SemanaNutricional(
        cliente_email="cliente1@example.com",
        fecha_inicio=fecha_inicio_c1,
        fecha_fin=fecha_fin_c1,
        objetivos=objetivos_c1,
        estado_general="En curso",
        notas="Primera semana de seguimiento para pérdida de peso"
    )
    
    # Guardar semana cliente1
    oid_semana_c1 = srp.save(semana_c1)
    print(f"✅ Semana nutricional creada para cliente1 ({fecha_inicio_c1.strftime('%d/%m/%Y')} - {fecha_fin_c1.strftime('%d/%m/%Y')})")
    # Crear plan diario para cliente1 (para el día de hoy)
    comidas_c1 = {
        "desayuno": {
            "descripcion": "Avena con leche y plátano",
            "calorias": 320,
            "proteinas": 15,
            "hidratos": 45,
            "grasas": 5
        },
        "comida": {
            "descripcion": "Pechuga de pollo con arroz integral y verduras",
            "calorias": 420,
            "proteinas": 35,
            "hidratos": 40,
            "grasas": 8
        },
        "merienda": {
            "descripcion": "Yogur desnatado con manzana",
            "calorias": 180,
            "proteinas": 10,
            "hidratos": 20,
            "grasas": 2
        },
        "cena": {
            "descripcion": "Pescado a la plancha con ensalada",
            "calorias": 290,
            "proteinas": 30,
            "hidratos": 10,
            "grasas": 12
        }
    }
    
    plan_hoy_c1 = PlanAlimenticioDiario(
        id_semana=oid_semana_c1,
        fecha=hoy.date(),
        estado="Completado",
        notas="La cliente ha seguido bien el plan de hoy",
        comidas=comidas_c1,
        plan_predefinido_id=None  # Este plan no está basado en uno predefinido
    )
    
    srp.save(plan_hoy_c1)
    print(f"✅ Plan diario creado para cliente1, fecha: {hoy.strftime('%d/%m/%Y')}")
    
    # --- CLIENTE 2 ---
    
    # Crear semana nutricional para cliente2
    fecha_inicio_c2 = hoy - timedelta(days=hoy.weekday())  # Lunes de la semana actual
    fecha_fin_c2 = fecha_inicio_c2 + timedelta(days=6)  # Domingo
    objetivos_c2 = {
        'calorias': 2500,
        'proteinas': 180,
        'hidratos': 280,
        'grasas': 80
    }
    
    semana_c2 = SemanaNutricional(
        cliente_email="cliente2@example.com",
        fecha_inicio=fecha_inicio_c2,
        fecha_fin=fecha_fin_c2,
        objetivos=objetivos_c2,
        estado_general="En curso",
        notas="Semana de entrenamiento intenso para ganancia muscular"
    )
    
    # Guardar semana cliente2
    oid_semana_c2 = srp.save(semana_c2)
    print(f"✅ Semana nutricional creada para cliente2 ({fecha_inicio_c2.strftime('%d/%m/%Y')} - {fecha_fin_c2.strftime('%d/%m/%Y')})")
    
    # Crear plan diario para cliente2 (usando el plan predefinido, para mañana)
    mañana = hoy + timedelta(days=1)    # Usar el plan predefinido para el cliente2
    # Convertir el OID a safe_id que es lo que espera la aplicación
    plan_predefinido_safe_id = srp.safe_from_oid(oid_plan_predefinido)
    
    plan_mañana_c2 = PlanAlimenticioDiario(
        id_semana=oid_semana_c2,
        fecha=mañana.date(),
        estado="Pendiente",
        notas="Plan basado en el predefinido 'Plan Alto en Proteínas'",
        comidas=comidas_plan_predefinido,
        plan_predefinido_id=plan_predefinido_safe_id  # Este plan está basado en uno predefinido (como safe_id)
    )
    
    srp.save(plan_mañana_c2)
    print(f"✅ Plan diario creado para cliente2, fecha: {mañana.strftime('%d/%m/%Y')}")
    
    print("\nDatos inicializados correctamente. Ahora puedes ejecutar la aplicación con:")
    print("python app.py")
    print("\nDatos de acceso:")
    print("Email: coach@example.com")
    print("Password: password")

if __name__ == "__main__":
    try:
        init_data()
    except Exception as e:
        print(f"❌ Error al inicializar datos: {e}")
        sys.exit(1)
