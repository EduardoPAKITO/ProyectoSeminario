class Producto:
    def __init__(self, id, nombre, categoria, precio, imagen, stock_por_sucursal):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.imagen = imagen
        self.stock_por_sucursal = stock_por_sucursal

    def to_dict(self): #Convierte el objeto Producto a diccionario para almacenamiento.
        return {
            "id": self.id,
            "precio": self.precio,
            "imagen": self.imagen,
            "stock_por_sucursal": self.stock_por_sucursal
        }

    @classmethod
    def from_dict(cls, nombre, categoria, data): #Crea un objeto Producto desde datos almacenados.
        return cls(
            data["id"],
            nombre,
            categoria,
            data["precio"],
            data["imagen"],
            data.get("stock_por_sucursal", {})
        )

    def get_stock_total(self):
        return sum(self.stock_por_sucursal.values())

    def get_stock_en_sucursal(self, sucursal):
        return self.stock_por_sucursal.get(sucursal, 0)