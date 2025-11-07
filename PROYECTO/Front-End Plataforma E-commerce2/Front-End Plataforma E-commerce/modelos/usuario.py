class Usuario:
    def __init__(self, usuario, clave, rol):
        self.usuario = usuario
        self.clave = clave
        self.rol = rol

    def to_dict(self):
        return {
            "usuario": self.usuario,
            "clave": self.clave,
            "rol": self.rol
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["usuario"], data["clave"], data["rol"])