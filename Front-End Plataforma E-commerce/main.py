# main.py
import customtkinter as ctk
from ui import LoginFrame, ClienteFrame, AdminFrame, PerfilFrame
from data.data_manager import DataManager
import os

# Inicializar archivos si faltan
DataManager.asegurar_archivos()

ctk.set_appearance_mode("Dark")  # modo claro
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Front-End Plataforma E-commerce")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # sesión
        self.usuario_actual = None
        self.rol_actual = None

        # header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=8, pady=6) #fill="x" Hace que el widget se expanda horizontalmente para llenar todo el ancho
        self.lbl_titulo = ctk.CTkLabel(header, text="Tienda - Celulares y Accesorios", font=ctk.CTkFont(size=18, weight="bold"))
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

    def on_login(self, usuario, rol):
        # cerrar frame login
        self.frame_login.pack_forget()
        self.frame_login.destroy()
        self.usuario_actual = usuario
        self.rol_actual = rol
        self.lbl_sesion.configure(text=f"Conectado: {usuario} ({rol})")
        self.btn_logout.configure(state="normal")

        # Crear pestañas (usamos CTkTabview)
        self.tabview = ctk.CTkTabview(self.contenedor_principal)
        self.tabview.pack(fill="both", expand=True)
        # Siempre: Catálogo y Mi Perfil (para clientes), si admin: agregar Administracion
        self.tabview.add("Catálogo y Compra")
        self.tabview.add("Mi Perfil")
        if rol == "admin":
            self.tabview.add("Administración")

        # Instanciar frames dentro de pestañas
        self.frame_cliente = ClienteFrame(self.tabview.tab("Catálogo y Compra"), self.get_usuario_actual)
        self.frame_cliente.pack(fill="both", expand=True)
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

if __name__ == "__main__":
    app = App()
    app.mainloop()
