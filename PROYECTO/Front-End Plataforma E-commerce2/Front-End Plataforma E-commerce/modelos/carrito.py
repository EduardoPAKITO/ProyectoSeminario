class ItemCarrito:
    def __init__(self, producto, cantidad, sucursal):
        self.producto = producto
        self.cantidad = cantidad
        self.sucursal = sucursal
        self.subtotal = producto.precio * cantidad

class Carrito:
    def __init__(self):
        self.items = []

    def agregar_item(self, producto, cantidad, sucursal):
        # Verificar si el producto ya está en el carrito
        for item in self.items:
            if item.producto.nombre == producto.nombre and item.sucursal == sucursal:
                item.cantidad += cantidad
                item.subtotal = item.producto.precio * item.cantidad
                return
        
        # Si no existe, agregar nuevo item
        self.items.append(ItemCarrito(producto, cantidad, sucursal))

    def eliminar_item(self, producto_nombre, sucursal):
        self.items = [item for item in self.items 
                     if not (item.producto.nombre == producto_nombre and item.sucursal == sucursal)]

    def actualizar_cantidad(self, producto_nombre, sucursal, nueva_cantidad):
        for item in self.items:
            if item.producto.nombre == producto_nombre and item.sucursal == sucursal:
                item.cantidad = nueva_cantidad
                item.subtotal = item.producto.precio * nueva_cantidad
                break

    def calcular_total(self):
        return sum(item.subtotal for item in self.items)

    def vaciar(self):
        self.items = []

    def esta_vacio(self):
        return len(self.items) == 0