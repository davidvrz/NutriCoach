from datetime import datetime

class PlanAlimenticioDiario:
    def __init__(self, id_semana, fecha, estado, notas, comidas, plan_predefinido_id=None):
        self.id_semana = id_semana 
        self.fecha = fecha          
        self.estado = estado       
        self.notas = notas          
        self.comidas = comidas      # dict con claves: desayuno, comida, etc.
        self.plan_predefinido_id = plan_predefinido_id
        self.creado = datetime.now()
    

class PlanPredefinido:
    def __init__(self, coach_email, nombre, descripcion, comidas, tipo="general"):
        self.coach_email = coach_email 
        self.nombre = nombre            
        self.descripcion = descripcion  
        self.comidas = comidas          
        self.tipo = tipo              
        self.creado = datetime.now()
        self.actualizado = datetime.now()
