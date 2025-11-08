# login_frame.py
import customtkinter as ctk
from data.data_manager import DataManager
from tkinter import messagebox, simpledialog

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, funcion_on_login, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.funcion_on_login = funcion_on_login
        self._construir()

    def _construir(self):
        self.grid_columnconfigure((0,1), weight=1) #estaba (0,1,2) tres columnas
        titulo = ctk.CTkLabel(self, text="Iniciar sesión", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.grid(row=0, column=0, columnspan=3, pady=(80,10)) #(60,10)

        ctk.CTkLabel(self, text="Usuario:").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        self.entry_usuario = ctk.CTkEntry(self, width=240)
        self.entry_usuario.grid(row=1, column=1, columnspan=2, sticky="w", padx=8, pady=6)

        ctk.CTkLabel(self, text="Clave:").grid(row=2, column=0, sticky="e", padx=8, pady=6)
        self.entry_clave = ctk.CTkEntry(self, width=240, show="*")
        self.entry_clave.grid(row=2, column=1, columnspan=2, sticky="w", padx=8, pady=6)

        boton_ingresar = ctk.CTkButton(self, text="Ingresar", command=self.intent_login)
        boton_ingresar.grid(row=3, column=0, columnspan=3, pady=(12,6))

        separador = ctk.CTkLabel(self, text="— ¿No tienes cuenta? —")
        separador.grid(row=4, column=0, columnspan=3, pady=(10,4))

        boton_registro = ctk.CTkButton(self, text="Crear cuenta", command=self.crear_cuenta_cliente)
        boton_registro.grid(row=5, column=0, columnspan=3, pady=(6,20))

    def intent_login(self):
        usuario = self.entry_usuario.get().strip() #strip() Elimina los espacios en blanco al principio y al final del texto
        clave = self.entry_clave.get().strip()
        if not usuario or not clave:
            messagebox.showwarning("Datos incompletos", "Ingrese usuario y clave.")
            return
        usuarios = DataManager.cargar_usuarios()
        info = usuarios.get(usuario) #Busca por la clave y devuelve su valor (xq es un diccionario)
        if not info or info.get("clave") != clave:
            messagebox.showerror("Error", "Usuario o clave incorrectos.")
            return
        # Llamada al callback con usuario y rol
        self.funcion_on_login(usuario, info.get("rol", "cliente")) #si no existe devuelve cliente por defecto

    def crear_cuenta_cliente(self):
        usuario = simpledialog.askstring("Crear cuenta", "Nombre de usuario:", parent=self)
        if not usuario:
            return
        email = simpledialog.askstring("Crear cuenta", "Email:", parent=self)
        if not email:
            return
        nombre = simpledialog.askstring("Crear cuenta", "Nombre completo:", parent=self)
        if not nombre:
            return
        clave = simpledialog.askstring("Crear cuenta", "Contraseña:", parent=self, show="*")
        if not clave:
            return
        ok, msg = DataManager.crear_usuario_cliente(usuario, clave, email=email, nombre=nombre)
        if ok:
            messagebox.showinfo("Cuenta creada", msg)
        else:
            messagebox.showerror("Error", msg)