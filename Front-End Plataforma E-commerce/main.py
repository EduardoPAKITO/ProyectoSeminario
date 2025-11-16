# main.py
import customtkinter as ctk
from ui import LoginFrame, ClienteFrame, AdminFrame, PerfilFrame, CarritoFrame
from data.data_manager import DataManager
import os

# Inicializar archivos si faltan
DataManager.asegurar_archivos()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tienda - Celulares y Accesorios")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # sesión
        self.usuario_actual = None
        self.rol_actual = None

        # Carrito (lista de items)
        self.carrito = []

        # header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=8, pady=6)
        self.lbl_titulo = ctk.CTkLabel(header, text="TIENDATECNO", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_titulo.pack(side="left", padx=8)
        self.lbl_sesion = ctk.CTkLabel(header, text="No conectado")
        self.lbl_sesion.pack(side="left", padx=8)
        self.btn_logout = ctk.CTkButton(header, text="Cerrar sesión", command=self.logout, state="disabled")
        self.btn_logout.pack(side="right", padx=8)

        # Contenedor principal donde iremos agregando pestañas dinámicamente
        self.contenedor_principal = ctk.CTkFrame(self)
        self.contenedor_principal.pack(fill="both", expand=True, padx=8, pady=8)

        # Mostrar inicialmente solo Login
        self.frame_login = LoginFrame(self.contenedor_principal, self.on_login)
        self.frame_login.pack(fill="both", expand=True)

        # referencias a frames que se crearán tras login
        self.frame_cliente = None
        self.frame_admin = None
        self.frame_perfil = None
        self.frame_carrito = None

    def on_login(self, usuario, rol):
        # cerrar frame login
        self.frame_login.pack_forget()
        self.frame_login.destroy()
        self.usuario_actual = usuario
        self.rol_actual = rol
        self.lbl_sesion.configure(text=f"Conectado: {usuario} ({rol})")
        self.btn_logout.configure(state="normal")

        # Crear pestañas
        self.tabview = ctk.CTkTabview(self.contenedor_principal)
        self.tabview.pack(fill="both", expand=True)
        # Siempre: Catálogo; si cliente: Carrito y Mi Perfil; si admin: Administracion
        self.tabview.add("Catálogo")
        if rol != "admin":
            self.tabview.add("Carrito")
            self.tabview.add("Mi Perfil")
        if rol == "admin":
            self.tabview.add("Administración")

        # Instanciar frames dentro de pestañas
        # pasar callback para agregar al carrito a ClienteFrame
        if rol == "admin":
            self.frame_cliente = ClienteFrame(self.tabview.tab("Catálogo"), self.get_usuario_actual, add_to_cart_callback=None, role="admin")
        else:
            self.frame_cliente = ClienteFrame(self.tabview.tab("Catálogo"), self.get_usuario_actual, add_to_cart_callback=self.agregar_al_carrito, role="cliente")
        self.frame_cliente.pack(fill="both", expand=True)

        if rol != "admin":
            self.frame_carrito = CarritoFrame(self.tabview.tab("Carrito"), self.get_usuario_actual,
                                              obtener_carrito_callback=self.obtener_carrito,
                                              vaciar_carrito_callback=self.vaciar_carrito,
                                              procesar_compra_callback=self.procesar_compra)
            self.frame_carrito.pack(fill="both", expand=True)

            self.frame_perfil = PerfilFrame(self.tabview.tab("Mi Perfil"), self.get_usuario_actual)
            self.frame_perfil.pack(fill="both", expand=True)
            # actualizar perfil
            self.frame_perfil.actualizar_info()

        if rol == "admin":
            self.frame_admin = AdminFrame(self.tabview.tab("Administración"))
            self.frame_admin.pack(fill="both", expand=True)

    def logout(self):
        # destruir tabview y volver a login
        if hasattr(self, "tabview") and self.tabview:
            self.tabview.pack_forget()
            self.tabview.destroy()
            self.tabview = None
        # destruir frames si existen
        if self.frame_cliente:
            self.frame_cliente.pack_forget()
            self.frame_cliente.destroy()
            self.frame_cliente = None
        if self.frame_admin:
            self.frame_admin.pack_forget()
            self.frame_admin.destroy()
            self.frame_admin = None
        if self.frame_perfil:
            self.frame_perfil.pack_forget()
            self.frame_perfil.destroy()
            self.frame_perfil = None
        if self.frame_carrito:
            self.frame_carrito.pack_forget()
            self.frame_carrito.destroy()
            self.frame_carrito = None
        
        self.vaciar_carrito()

        # reset sesión
        self.usuario_actual = None
        self.rol_actual = None
        self.lbl_sesion.configure(text="No conectado")
        self.btn_logout.configure(state="disabled")

        # volver a mostrar login
        self.frame_login = LoginFrame(self.contenedor_principal, self.on_login)
        self.frame_login.pack(fill="both", expand=True)

    def get_usuario_actual(self):
        return self.usuario_actual

    # Carrito: funciones para manejar carrito desde main
    def agregar_al_carrito(self, item):
        # item: diccionario con keys categoria, producto, cantidad, sucursal, precio_unitario, usuario
        # si ya existe mismo producto+sucursal en carrito, sumar cantidad
        found = False
        for it in self.carrito:
            if it["producto"] == item["producto"] and it["sucursal"] == item["sucursal"]:
                it["cantidad"] += item["cantidad"]
                found = True
                break
        if not found:
            self.carrito.append(item)
        # refrescar vista del carrito 
        try:
            if self.frame_carrito:
                self.frame_carrito.refrescar()
        except Exception:
            pass

    def obtener_carrito(self):
        return self.carrito

    def vaciar_carrito(self):
        self.carrito = []

    def procesar_compra(self, carrito, forma_pago):
        # intentar reducir stock para cada item y registrar venta por usuario
        usuario = self.get_usuario_actual()
        errores = []
        total = 0.0
        productos = DataManager.cargar_productos()
        for it in carrito:
            cat = it["categoria"]
            nombre = it["producto"]
            suc = it["sucursal"]
            cant = int(it["cantidad"])
            prod = productos.get(cat, {}).get(nombre)
            if not prod:
                errores.append(f"Producto {nombre} no encontrado.")
                continue
            disponible = prod.get("stock_por_sucursal", {}).get(suc, 0)
            if cant > disponible:
                errores.append(f"Stock insuficiente de {nombre} en {suc} (disponible: {disponible}).")
            total += prod.get("precio", 0) * cant
        if errores:
            return False, "\n".join(errores)
        total_final = total
        if forma_pago == "Efectivo":
            total_final = total * 0.90
        elif forma_pago == "Crédito":
            total_final = total * 1.05
        # factor para distribuir el total_final proporcionalmente entre los items
        factor = (total_final / total) if total > 0 else 1.0
        # proceder: reducir stock y registrar ventas (grabando el total ajustado por item)
        for it in carrito:
            cat = it["categoria"]
            nombre = it["producto"]
            suc = it["sucursal"]
            cant = int(it["cantidad"])
            prod = productos.get(cat, {}).get(nombre)
            precio_unit = prod.get("precio", 0)
            subtotal = precio_unit * cant
            subtotal_ajustado = subtotal * factor
            ok, msg = DataManager.reducir_stock_al_comprar(cat, nombre, suc, cant)
            if not ok:
                return False, msg
            # registrar venta con subtotal ajustado (para que el historial conserve el precio según forma de pago)
            DataManager.registrar_venta(usuario, cat, nombre, cant, suc, forma_pago, subtotal_ajustado)
        return True, f"Compra realizada. Total cobrado: ${total_final:.2f}"

if __name__ == "__main__":
    app = App()
    app.mainloop()
