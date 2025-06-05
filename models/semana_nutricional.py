from datetime import datetime

"""Clase que representa una semana nutricional en la aplicación NutriCoach."""

class SemanaNutricional:
    """Modelo para almacenar información de una semana nutricional.

    :param cliente_email: Correo electrónico del cliente asociado.
    :param fecha_inicio: Fecha de inicio de la semana nutricional.
    :param fecha_fin: Fecha de fin de la semana nutricional.
    :param estado_general: Estado general de la semana nutricional.
    :param notas: Notas adicionales sobre la semana.
    :param objetivos: Diccionario con los objetivos nutricionales de la semana.
    """

    def __init__(self, cliente_email, fecha_inicio, fecha_fin, estado_general, notas, objetivos):
        self.cliente_email = cliente_email
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado_general = estado_general
        self.notas = notas
        self.objetivos = objetivos 
        self.creado = datetime.now()
