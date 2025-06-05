from flask_login import UserMixin
from datetime import datetime

"""Clase que representa a un coach en la aplicación NutriCoach."""

class Coach(UserMixin):
    """Modelo para almacenar información de un coach.

    :param email: Correo electrónico del coach.
    :param nombre: Nombre del coach.
    :param password_hash: Contraseña encriptada del coach.
    """

    def __init__(self, email, nombre, password_hash):
        self.email = email
        self.nombre = nombre
        self.password_hash = password_hash
        self.fecha_registro = datetime.now()

    def get_id(self):
        """Obtiene el identificador único del coach.

        :return: Correo electrónico del coach.
        """
        return self.email
