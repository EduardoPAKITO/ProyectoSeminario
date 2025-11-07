# carrito_frame.py
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from data.data_manager import DataManager

class CarritoFrame(ctk.CTkFrame):
    def __init__(self, master, funcion_get_usuario, obtener_carrito_callback, vaciar_carrito_callback, procesar_compra_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.funcion_get_usuario = funcion_get_usuario
        self.obtener_carrito_callback = obtener_carrito_callback
        self.vaciar_carrito_callback = vaciar_carrito_callback
        self.procesar_compra_callback = procesar_compra_callback
        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="Carrito de Compras", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=12, pady=(12,8))
        self.lista_box = ctk.CTkTextbox(self, height=300, state="disabled")
        self.lista_box.pack(fill="both", expand=True, padx=12, pady=6)

        # Totales y opciones de pago
        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=12, pady=8)
        self.lbl_total = ctk.CTkLabel(bottom, text="Total: $0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_total.pack(side="left")

        # Forma de pago
        self.forma = ctk.StringVar(value="efectivo")
        pay_fr = ctk.CTkFrame(bottom)
        pay_fr.pack(side="right")
        ctk.CTkLabel(pay_fr, text="Pago:").pack(side="left", padx=6)
        ctk.CTkOptionMenu(pay_fr, values=["efectivo", "debito", "credito"], variable=self.forma, command=self.actualizar_total).pack(side="left", padx=6)

        acciones = ctk.CTkFrame(self)
        acciones.pack(fill="x", padx=12, pady=(0,12))
        ctk.CTkButton(acciones, text="Finalizar compra", command=self.finalizar_compra).pack(side="left", padx=6)
        ctk.CTkButton(acciones, text="Vaciar carrito", fg_color="gray70", hover_color="gray60", command=self.vaciar_carrito).pack(side="left", padx=6)
        ctk.CTkButton(acciones, text="Refrescar", command=self.refrescar).pack(side="right", padx=6)

        self.refrescar()

    def refrescar(self, *_):
        carrito = self.obtener_carrito_callback()
        self.lista_box.configure(state="normal")
        self.lista_box.delete("0.0", "end")
        total = 0.0
        if not carrito:
            self.lista_box.insert("end", "Carrito vacío.\n")
        else:
            for i, item in enumerate(carrito, start=1):
                nombre = item.get("producto")
                cant = int(item.get("cantidad", 0))
                precio = float(item.get("precio_unitario", 0))
                subtotal = precio * cant
                total += subtotal
                self.lista_box.insert("end", f"{i}) {nombre} x{cant} - ${precio:.2f} c/u - Subtotal: ${subtotal:.2f}\n")
        # aplicar forma de pago
        forma = self.forma.get()
        total_final = total
        if forma == "efectivo":
            total_final = total * 0.90  # 10% descuento
        elif forma == "credito":
            total_final = total * 1.05  # 5% recargo
        # debito -> precio normal
        self.lbl_total.configure(text=f"Total: ${total_final:.2f}")
        self.lista_box.configure(state="disabled")

    def actualizar_total(self, *_):
        self.refrescar()

    def vaciar_carrito(self):
        confirm = messagebox.askyesno("Confirmar", "Vaciar el carrito?")
        if not confirm:
            return
        self.vaciar_carrito_callback()
        messagebox.showinfo("OK", "Carrito vaciado.")
        self.refrescar()

    def pedir_datos_tarjeta(self):
        numero = simpledialog.askstring("Tarjeta", "N° de tarjeta (solo números):", parent=self)
        if not numero:
            return None
        nombre = simpledialog.askstring("Tarjeta", "Nombre en la tarjeta:", parent=self)
        if not nombre:
            return None
        venc = simpledialog.askstring("Tarjeta", "Vencimiento MM/AA:", parent=self)
        if not venc:
            return None
        cvv = simpledialog.askstring("Tarjeta", "CVV (3 dígitos):", parent=self)
        if not cvv:
            return None
        # No almacenamos, solo simulamos validación mínima
        return {"numero": numero, "nombre": nombre, "vencimiento": venc, "cvv": cvv}

    def finalizar_compra(self):
        usuario = self.funcion_get_usuario()
        if not usuario:
            messagebox.showwarning("Acceso", "Debes iniciar sesión para finalizar la compra.")
            return
        carrito = self.obtener_carrito_callback()
        if not carrito:
            messagebox.showwarning("Carrito", "El carrito está vacío.")
            return
        forma = self.forma.get()
        # si tarjeta pedir datos
        if forma in ("debito", "credito"):
            datos = self.pedir_datos_tarjeta()
            if not datos:
                messagebox.showwarning("Pago", "Datos de tarjeta incompletos.")
                return
        # procesar compra: el callback debe intentar registrar ventas y reducir stock
        ok, msg = self.procesar_compra_callback(carrito, forma)
        if ok:
            messagebox.showinfo("Compra exitosa", msg or "Compra realizada correctamente.")
            self.vaciar_carrito_callback()
            self.refrescar()
        else:
            messagebox.showerror("Error", msg or "No se pudo completar la compra.")
