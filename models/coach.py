from flask_login import UserMixin
from datetime import datetime

class Coach(UserMixin):
    def __init__(self, email, nombre, password_hash):
        self.email = email
        self.nombre = nombre
        self.password_hash = password_hash
        self.fecha_registro = datetime.now()

    def get_id(self):
        return self.email
