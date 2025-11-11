# carrito_frame.py
import customtkinter as ctk
from tkinter import messagebox
from data.data_manager import DataManager
import tkinter as tk
import tkinter.font as tkfont

class CarritoFrame(ctk.CTkFrame):
    def __init__(self, master, funcion_get_usuario, obtener_carrito_callback, vaciar_carrito_callback, procesar_compra_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.funcion_get_usuario = funcion_get_usuario
        self.obtener_carrito_callback = obtener_carrito_callback
        self.vaciar_carrito_callback = vaciar_carrito_callback
        self.procesar_compra_callback = procesar_compra_callback
        self._construir()

    def _construir(self):
        # Cabecera con título y botón refrescar 
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=12, pady=(12,6))
        ctk.CTkLabel(header, text="Carrito de Compras", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="Refrescar", command=self.refrescar).pack(side="right")

        self.lista_box = ctk.CTkTextbox(self, height=300, state="disabled")
        self.lista_box.pack(fill="both", expand=True, padx=12, pady=6)

        # Totales y opciones de pago
        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=12, pady=8)

        self.lbl_total_final = ctk.CTkLabel(bottom, text="Total final: $0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_total_final.pack(side="left")

        # Info de descuento/recargo
        self.lbl_info_pago = ctk.CTkLabel(bottom, text="", font=ctk.CTkFont(size=12))
        self.lbl_info_pago.pack(side="left", padx=8)

        # Forma de pago
        self.forma = ctk.StringVar(value="Efectivo")
        pay_fr = ctk.CTkFrame(bottom)
        pay_fr.pack(side="right")
        ctk.CTkLabel(pay_fr, text="Pago:").pack(side="left", padx=6)
        ctk.CTkOptionMenu(pay_fr, values=["Efectivo", "Débito", "Crédito"], variable=self.forma, command=self.actualizar_total).pack(side="left", padx=6)

        acciones = ctk.CTkFrame(self)
        acciones.pack(fill="x", padx=12, pady=(0,12))
        # Centramos los botones en un frame interno
        center = ctk.CTkFrame(acciones)
        center.pack(expand=True)
        ctk.CTkButton(center, text="Finalizar compra", command=self.finalizar_compra).pack(side="left", padx=12)
        ctk.CTkButton(center, text="Vaciar carrito", fg_color="gray70", hover_color="gray60", command=self.vaciar_carrito).pack(side="left", padx=12)

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
        info_text = ""
        if forma == "Efectivo":
            total_final = total * 0.90  # 10% descuento
            info_text = "10% de descuento aplicado."
        elif forma == "Crédito":
            total_final = total * 1.05  # 5% recargo
            info_text = "5% de recargo aplicado."
        
        self.lbl_total_final.configure(text=f"Total final: ${total_final:.2f}")
        self.lbl_info_pago.configure(text=info_text)
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
        top = ctk.CTkToplevel(self)
        top.title("Datos tarjeta")
        top.geometry("420x320")
        top.transient(self.master)
        top.grab_set()
        top.focus_set()

        ctk.CTkLabel(top, text="Tipo de tarjeta:").place(x=20, y=20)
        tipo_var = ctk.StringVar(value="Visa")
        ctk.CTkOptionMenu(top, values=["Visa", "MasterCard", "Naranja", "Macro"], variable=tipo_var).place(x=150, y=20)

        ctk.CTkLabel(top, text="N° de tarjeta:").place(x=20, y=70)
        entry_num = ctk.CTkEntry(top, width=260)
        entry_num.place(x=150, y=70)

        ctk.CTkLabel(top, text="Nombre en la tarjeta:").place(x=20, y=110)
        entry_nombre = ctk.CTkEntry(top, width=260)
        entry_nombre.place(x=150, y=110)

        ctk.CTkLabel(top, text="Vencimiento (MM/AA):").place(x=20, y=150)
        entry_venc = ctk.CTkEntry(top, width=120)
        entry_venc.place(x=180, y=150)

        ctk.CTkLabel(top, text="CVV:").place(x=20, y=190)
        entry_cvv = ctk.CTkEntry(top, width=80, show="*")
        entry_cvv.place(x=80, y=190)

        result = {}

        def enviar():
            numero = entry_num.get().strip()
            nombre = entry_nombre.get().strip()
            venc = entry_venc.get().strip()
            cvv = entry_cvv.get().strip()
            tipo = tipo_var.get()
            if not numero or not nombre or not venc or not cvv:
                messagebox.showwarning("Pago", "Completar todos los datos de la tarjeta.")
                return
            result.update({"numero": numero, "nombre": nombre, "vencimiento": venc, "cvv": cvv, "tipo": tipo})
            top.destroy()

        ctk.CTkButton(top, text="Enviar", command=enviar).place(x=160, y=260, width=100)

        self.wait_window(top)
        return result if result else None

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
        # si tarjeta pedir datos (CTk)
        if forma in ("Débito", "Crédito"):
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
            messagebox.showerror("Error", msg or "No se pudo realizar la compra.")
