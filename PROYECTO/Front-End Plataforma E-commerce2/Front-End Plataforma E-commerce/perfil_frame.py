# perfil_frame.py
import customtkinter as ctk
from compras_manager import obtener_compras_por_usuario
from tkinter import messagebox

class PerfilFrame(ctk.CTkFrame):
    def __init__(self, master, funcion_get_usuario, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.funcion_get_usuario = funcion_get_usuario
        self._construir()

    def _construir(self):
        titulo = ctk.CTkLabel(self, text="Mi Perfil", font=ctk.CTkFont(size=18, weight="bold"))
        titulo.pack(anchor="w", padx=12, pady=(12,8))

        self.info_usuario = ctk.CTkLabel(self, text="Usuario: -")
        self.info_usuario.pack(anchor="w", padx=12, pady=(4,4))

        ctk.CTkLabel(self, text="Historial de compras:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=12, pady=(12,4))
        self.historial_box = ctk.CTkTextbox(self, height=300, state="disabled")
        self.historial_box.pack(fill="both", expand=True, padx=12, pady=6)

        ctk.CTkButton(self, text="Refrescar historial", command=self.refrescar_historial).pack(pady=(6,12))

    def actualizar_info(self):
        usuario = self.funcion_get_usuario()
        if not usuario:
            self.info_usuario.configure(text="Usuario: -")
            self.historial_box.configure(state="normal")
            self.historial_box.delete("0.0", "end")
            self.historial_box.configure(state="disabled")
            return
        self.info_usuario.configure(text=f"Usuario: {usuario}")
        self.refrescar_historial()

    def refrescar_historial(self):
        usuario = self.funcion_get_usuario()
        if not usuario:
            messagebox.showwarning("Acceso", "Debes iniciar sesión.")
            return
        compras = obtener_compras_por_usuario(usuario)
        self.historial_box.configure(state="normal")
        self.historial_box.delete("0.0", "end")
        if not compras:
            self.historial_box.insert("end", "No se encontraron compras.\n")
        else:
            for c in compras:
                linea = f"{c.get('fecha')} - {c.get('categoria')} / {c.get('producto')} x{c.get('cantidad')} - {c.get('sucursal')} - {c.get('metodo_pago')} - ${c.get('total'):.2f}\n"
                self.historial_box.insert("end", linea)
        self.historial_box.configure(state="disabled")
