class Cliente:
    def __init__(self, nombre, edad, peso, altura, objetivo, coach_email):
        self.nombre = nombre
        self.edad = edad
        self.peso = peso
        self.altura = altura
        self.objetivo = objetivo
        self.coach_email = coach_email  # Relación directa con Coach
