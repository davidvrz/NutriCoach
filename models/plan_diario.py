from datetime import datetime

"""Clases que representan planes alimenticios en la aplicación NutriCoach."""

class PlanAlimenticioDiario:
    """Modelo para almacenar información de un plan alimenticio diario.

    :param id_semana: Identificador de la semana nutricional asociada.
    :param fecha: Fecha del plan alimenticio.
    :param estado: Estado del plan alimenticio.
    :param notas: Notas adicionales sobre el plan.
    :param comidas: Diccionario con las comidas del día.
    :param plan_predefinido_id: (Opcional) Identificador del plan predefinido asociado.
    """

    def __init__(self, id_semana, fecha, estado, notas, comidas, plan_predefinido_id=None):
        self.id_semana = id_semana 
        self.fecha = fecha          
        self.estado = estado       
        self.notas = notas          
        self.comidas = comidas      # dict con claves: desayuno, comida, etc.
        self.plan_predefinido_id = plan_predefinido_id
        self.creado = datetime.now()
    

class PlanPredefinido:
    """Modelo para almacenar información de un plan predefinido.

    :param coach_email: Correo electrónico del coach que creó el plan.
    :param nombre: Nombre del plan predefinido.
    :param descripcion: Descripción del plan predefinido.
    :param comidas: Diccionario con las comidas del plan.
    :param tipo: Tipo del plan predefinido (por defecto "general").
    """

    def __init__(self, coach_email, nombre, descripcion, comidas, tipo="general"):
        self.coach_email = coach_email 
        self.nombre = nombre            
        self.descripcion = descripcion  
        self.comidas = comidas          
        self.tipo = tipo              
        self.creado = datetime.now()
        self.actualizado = datetime.now()
