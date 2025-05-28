from datetime import datetime

class SemanaNutricional:
    def __init__(self, cliente_email, fecha_inicio, fecha_fin, estado_general, notas, objetivos):
        self.cliente_email = cliente_email
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado_general = estado_general
        self.notas = notas
        self.objetivos = objetivos 
        self.creado = datetime.now()
