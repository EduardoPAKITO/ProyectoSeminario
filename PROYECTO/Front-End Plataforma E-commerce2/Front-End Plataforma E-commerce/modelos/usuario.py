class Usuario:
    def __init__(self, usuario, clave, rol):
        self.usuario = usuario
        self.clave = clave
        self.rol = rol

    def to_dict(self):
        # Convierte el objeto Usuario a diccionario para serialización.
        return {
            "usuario": self.usuario,
            "clave": self.clave,
            "rol": self.rol
        }

    @classmethod #Crea un objeto Usuario desde un diccionario.
    def from_dict(cls, data):
        return cls(data["usuario"], data["clave"], data["rol"])