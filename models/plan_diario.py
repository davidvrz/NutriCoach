from datetime import datetime

class PlanAlimenticioDiario:
    def __init__(self, id_semana, fecha, estado, notas, comidas):
        self.id_semana = id_semana  # OID o identificador string de la semana
        self.fecha = fecha          
        self.estado = estado       
        self.notas = notas          
        self.comidas = comidas      # dict con claves: desayuno, comida, etc.
        self.creado = datetime.now()
