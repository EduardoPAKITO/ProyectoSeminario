from datetime import datetime

class Venta:
    def __init__(self, usuario, categoria, producto, cantidad, sucursal, metodo_pago, total, fecha=None):
        self.usuario = usuario
        self.categoria = categoria
        self.producto = producto
        self.cantidad = cantidad
        self.sucursal = sucursal
        self.metodo_pago = metodo_pago
        self.total = total
        self.fecha = fecha or datetime.now()

    def to_dict(self): #Convierte el objeto Venta a diccionario para almacenamiento.
        return {
            "categoria": self.categoria,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "sucursal": self.sucursal,
            "metodo_pago": self.metodo_pago,
            "total": self.total,
            "fecha": self.fecha.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_dict(cls, data): #Crea un objeto Venta desde datos almacenados.
        fecha = datetime.strptime(data["fecha"], "%Y-%m-%d %H:%M:%S")
        return cls(
            data.get("usuario"),
            data["categoria"],
            data["producto"],
            data["cantidad"],
            data["sucursal"],
            data["metodo_pago"],
            data["total"],
            fecha
        )