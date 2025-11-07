class Sucursal:
    def __init__(self, nombre, direccion=None, telefono=None):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nombre"], data.get("direccion"), data.get("telefono"))