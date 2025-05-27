from datetime import datetime

class PlanAlimenticioDiario:
    def __init__(self, id_semana, fecha, estado, notas, comidas):
        self.id_semana = id_semana 
        self.fecha = fecha          
        self.estado = estado       
        self.notas = notas          
        self.comidas = comidas      # dict con claves: desayuno, comida, etc.
        self.creado = datetime.now()


class PlanPredefinido:
    def __init__(self, coach_email, nombre, descripcion, comidas, tipo="general"):
        self.coach_email = coach_email  # Email del coach que crea el plan
        self.nombre = nombre            # Nombre descriptivo del plan (ej: "Alto en proteínas")
        self.descripcion = descripcion  # Descripción detallada
        self.comidas = comidas          # dict con claves: desayuno, comida, etc.
        self.tipo = tipo                # Categoría del plan (ej: "volumen", "definición")
        self.creado = datetime.now()
        self.actualizado = datetime.now()
