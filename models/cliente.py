from datetime import datetime

class Cliente:
    def __init__(self, nombre, nacimiento):
        self.nombre = nombre
        self.nacimiento = nacimiento
        self.creado = datetime.now()

    def __str__(self):
        return f"{self.nombre} ({self.nacimiento.strftime('%Y-%m-%d')})"
