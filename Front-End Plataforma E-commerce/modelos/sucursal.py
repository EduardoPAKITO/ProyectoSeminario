class Sucursal:
    def __init__(self, nombre, direccion=None, telefono=None):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono

    def to_dict(self): #Convierte el objeto Sucursal a diccionario.
        return {
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono
        }

    @classmethod
    def from_dict(cls, data): #Crea un objeto Sucursal desde un diccionario.
        return cls(data["nombre"], data.get("direccion"), data.get("telefono"))