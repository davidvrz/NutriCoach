"""Clase que representa a un cliente en la aplicación NutriCoach."""

class Cliente:
    """Modelo para almacenar información de un cliente.

    :param nombre: Nombre del cliente.
    :param email: Correo electrónico del cliente.
    :param edad: Edad del cliente.
    :param peso: Peso del cliente en kilogramos.
    :param altura: Altura del cliente en centímetros.
    :param objetivo: Objetivo nutricional del cliente.
    :param coach_email: Correo electrónico del coach asociado al cliente.
    """

    def __init__(self, nombre, email, edad, peso, altura, objetivo, coach_email):
        self.nombre = nombre
        self.email = email
        self.edad = edad
        self.peso = peso
        self.altura = altura
        self.objetivo = objetivo
        self.coach_email = coach_email  # Relación directa con Coach
