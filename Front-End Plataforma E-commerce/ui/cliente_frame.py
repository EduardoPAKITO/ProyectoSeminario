# cliente_frame.py
import tkinter as tk
import customtkinter as ctk
from data.data_manager import DataManager
from tkinter import messagebox
from PIL import Image, ImageTk
from customtkinter import CTkImage
import os

#CARPETA_IMAGENES = "images"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio raíz del proyecto
CARPETA_IMAGENES = os.path.join(BASE_DIR, "images")

class ClienteFrame(ctk.CTkFrame):
    def __init__(self, master, funcion_get_usuario, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.funcion_get_usuario = funcion_get_usuario
        self.productos_mostrados = []  # lista de tuples (categoria, nombre, datos)
        self.imagen_actual = None
        self._construir()

    def _construir(self):
        # Layout: izquierda buscar/listado, derecha detalle/imagen/compra
        izquierdo = ctk.CTkFrame(self)
        izquierdo.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        derecho = ctk.CTkScrollableFrame(self, width=360)
        derecho.pack(side="right", fill="y", padx=8, pady=8)

        # Buscador con selector de categoría
        filtro_fr = ctk.CTkFrame(izquierdo)
        filtro_fr.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(filtro_fr, text="Buscar en:").pack(side="left", padx=6)
        self.categoria_var = ctk.StringVar(value="Celulares")
        ctk.CTkOptionMenu(filtro_fr, values=["Celulares", "Accesorios"], variable=self.categoria_var).pack(side="left", padx=6)
        self.buscar_entry = ctk.CTkEntry(filtro_fr, placeholder_text="Nombre del producto...")
        self.buscar_entry.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(filtro_fr, text="Buscar", command=self.buscar).pack(side="left", padx=6)
        ctk.CTkButton(filtro_fr, text="Mostrar todo", command=self.mostrar_todo).pack(side="left", padx=6)

        # Listado (scrollable)
        #self.listado = ctk.CTkTextbox(izquierdo, state="disabled", height=20)
        #self.listado.pack(fill="both", expand=True, padx=6, pady=6)
        self.scroll_frame = ctk.CTkScrollableFrame(izquierdo)
        self.scroll_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.row = 0
        self.column = 0

        # Selección por índice
        sel_fr = ctk.CTkFrame(izquierdo)
        sel_fr.pack(fill="x", pady=(4,0))
        ctk.CTkLabel(sel_fr, text="Índice:").pack(side="left", padx=6)
        self.idx_entry = ctk.CTkEntry(sel_fr, width=80)
        self.idx_entry.pack(side="left", padx=6)
        ctk.CTkButton(sel_fr, text="Seleccionar", command=self.seleccionar_por_indice).pack(side="left", padx=6)

        # DETALLE DERECHO
        self.lbl_nombre = ctk.CTkLabel(derecho, text="Producto: -", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_nombre.pack(anchor="w", pady=(6,4))

        # label para imagen (se ajusta)
        self.label_imagen = ctk.CTkLabel(derecho, text="(sin imagen)", width=300, height=200)
        self.label_imagen.pack(pady=6)

        self.lbl_precio = ctk.CTkLabel(derecho, text="Precio: -")
        self.lbl_precio.pack(anchor="w", padx=8, pady=(6,0))
        self.lbl_stock = ctk.CTkLabel(derecho, text="Stock en sucursal: -")
        self.lbl_stock.pack(anchor="w", padx=8, pady=(2,0))

        ctk.CTkLabel(derecho, text="Sucursal:").pack(anchor="w", padx=8, pady=(8,0))
        self.sucursal_menu = ctk.CTkOptionMenu(derecho, values=[])
        self.sucursal_menu.pack(anchor="w", padx=8, pady=(0,8))

        ctk.CTkLabel(derecho, text="Cantidad:").pack(anchor="w", padx=8)
        self.cantidad_entry = ctk.CTkEntry(derecho, width=80)
        self.cantidad_entry.insert(0, "1")
        self.cantidad_entry.pack(anchor="w", padx=8, pady=(0,8))

        ctk.CTkLabel(derecho, text="Pago:").pack(anchor="w", padx=8)
        self.metodo_pago = ctk.StringVar(value="contado")
        pay_fr = ctk.CTkFrame(derecho)
        pay_fr.pack(anchor="w", padx=8, pady=(0,8))
        ctk.CTkRadioButton(pay_fr, text="Contado", variable=self.metodo_pago, value="contado").pack(side="left", padx=6)
        ctk.CTkRadioButton(pay_fr, text="Débito", variable=self.metodo_pago, value="debito").pack(side="left", padx=6)
        ctk.CTkRadioButton(pay_fr, text="Crédito", variable=self.metodo_pago, value="credito").pack(side="left", padx=6)

        ctk.CTkButton(derecho, text="Comprar", command=self.comprar).pack(pady=(8,4))
        ctk.CTkButton(derecho, text="Limpiar", fg_color="gray70", hover_color="gray60", command=self.limpiar_detalle).pack()

        # Inicializar mostrando todo
        self.mostrar_todo()

    def mostrar_todo(self):
        self.productos_mostrados = []
        datos = DataManager.cargar_productos()
        categoria = self.categoria_var.get()
        productos_categoria = datos.get(categoria, {})
        self.productos_mostrados = [(categoria, nombre, producto) for nombre, producto in productos_categoria.items()]
        self._mostrar_listado(self.productos_mostrados)

    def buscar(self):
        termino = self.buscar_entry.get().strip().lower()
        categoria = self.categoria_var.get()
        datos = DataManager.cargar_productos()
        productos_categoria = datos.get(categoria, {})
        encontrados = []
        for nombre, producto in productos_categoria.items():
            if termino in nombre.lower():
                encontrados.append((categoria, nombre, producto))
        self.productos_mostrados = encontrados
        self._mostrar_listado(self.productos_mostrados)

    def _mostrar_listado(self, lista):
        # limpiar contenido anterior
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.row = 0
        self.column = 0

        for i, (cat, nombre, prod) in enumerate(lista, start=1):
            stock_total = sum(prod.get("stock_por_sucursal", {}).values())
            imagen_nombre = prod.get("imagen", "")
            ruta_imagen = os.path.join(CARPETA_IMAGENES, imagen_nombre) if imagen_nombre else None
            self.mostrar_articulo(i, nombre, prod.get("precio", 0), ruta_imagen, stock_total)


    def mostrar_articulo(self, indice, articulo, precio, imagen_path, stock):
        # Frame individual para cada producto
        article_frame = ctk.CTkFrame(self.scroll_frame, fg_color="white", corner_radius=8)
        article_frame.grid(row=self.row, column=self.column, padx=7, pady=10, sticky="nsew")

        # Índice negrita arriba
        ctk.CTkLabel(article_frame, text=f"{indice})", text_color="red", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=6, pady=(2, 0))

        # Imagen
        if imagen_path and os.path.exists(imagen_path):
            try:
                # 1. Abre la imagen de PIL
                pil_image = Image.open(imagen_path)

                # 2. Crea el objeto CTkImage. 
                #    CustomTkinter maneja el tamaño, pero puedes usar size=(ancho, alto) si quieres especificarlo.
                #    Normalmente, le pasas la imagen de PIL abierta.
                ctk_image_obj = CTkImage(
                    light_image=pil_image, # Imagen para modo claro (o la misma para ambos)
                    dark_image=pil_image,  # Imagen para modo oscuro (o la misma para ambos)
                    size=(150, 150)        # Tamaño deseado
                )

                # 3. Pasa el objeto CTkImage al CTkLabel
                img_label = ctk.CTkLabel(article_frame, image=ctk_image_obj, text="")

                # Ya no necesitas hacer img_label.image = ... porque CTkImage lo maneja.
                img_label.pack(expand=True, fill="both", pady=(4, 2))
                """                
                image = Image.open(imagen_path)
                image = image.resize((150, 150), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(image)
                img_label = ctk.CTkLabel(article_frame, image=img_tk, text="")
                img_label.image = img_tk  # mantener referencia
                img_label.pack(expand=True, fill="both", pady=(4, 2))
                """
            except Exception:
                ctk.CTkLabel(article_frame, text="(Error cargando imagen)", text_color="gray").pack()

        # Nombre
        ctk.CTkLabel(article_frame, text=articulo, text_color="black", wraplength=150, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(2, 0))
        # Precio
        ctk.CTkLabel(article_frame, text=f"Precio: ${precio:.2f}", text_color="black").pack()
        # Stock
        ctk.CTkLabel(article_frame, text=f"Stock total: {stock}", text_color="gray").pack(pady=(0, 4))

        # Actualizar posición de la grilla
        self.column += 1
        if self.column > 3:  # 4 columnas
            self.column = 0
            self.row += 1

        

    def seleccionar_por_indice(self):
        idx_txt = self.idx_entry.get().strip()
        if not idx_txt.isdigit():
            messagebox.showwarning("Índice inválido", "Ingrese un número de índice válido.")
            return
        idx = int(idx_txt) - 1
        if idx < 0 or idx >= len(self.productos_mostrados):
            messagebox.showwarning("Fuera de rango", "Índice fuera de rango.")
            return
        categoria, nombre, producto = self.productos_mostrados[idx]
        self.mostrar_detalle(categoria, nombre, producto)

    def mostrar_detalle(self, categoria, nombre, producto):
        self.lbl_nombre.configure(text=f"Producto: {nombre}")
        self.lbl_precio.configure(text=f"Precio: ${producto.get('precio'):.2f}")
        # cargar sucursales
        sucursales = list(producto.get("stock_por_sucursal", {}).keys())
        if sucursales:
            self.sucursal_menu.configure(values=sucursales)
            self.sucursal_menu.set(sucursales[0])
            stock_s = producto.get("stock_por_sucursal", {}).get(sucursales[0], 0)
            self.lbl_stock.configure(text=f"Stock en {sucursales[0]}: {stock_s}")
        else:
            self.sucursal_menu.configure(values=[])
            self.sucursal_menu.set("")
            self.lbl_stock.configure(text="Sin sucursales")

        # cargar imagen ajustable
        imagen_nombre = producto.get("imagen", "")
        ruta = os.path.join(CARPETA_IMAGENES, imagen_nombre) if imagen_nombre else None
        if ruta and os.path.exists(ruta):
            try:
                img = Image.open(ruta)
                # tamaño máximo relativo a label (ajustable): 300x300
                max_ancho, max_alto = 300, 300
                img.thumbnail((max_ancho, max_alto))
                self.imagen_actual = ImageTk.PhotoImage(img)
                self.label_imagen.configure(image=self.imagen_actual, text="")
            except Exception:
                self.label_imagen.configure(image=None, text="(imagen no cargada)")
        else:
            self.label_imagen.configure(image=None, text="(sin imagen)")

        # almacenar selección actual
        self.seleccion_actual = {"categoria": categoria, "nombre": nombre, "producto": producto}

    def limpiar_detalle(self):
        self.lbl_nombre.configure(text="Producto: -")
        self.lbl_precio.configure(text="Precio: -")
        self.lbl_stock.configure(text="Stock en sucursal: -")
        self.sucursal_menu.configure(values=[])
        self.sucursal_menu.set("")
        self.cantidad_entry.delete(0, "end")
        self.cantidad_entry.insert(0, "1")
        self.metodo_pago.set("contado")
        self.idx_entry.delete(0, "end")
        self.label_imagen.configure(image=None, text="(sin imagen)")
        self.productos_mostrados = []
        self.seleccion_actual = None
        # Volver a cargar la vista actual
        self.mostrar_todo()

    def comprar(self):
        usuario = self.funcion_get_usuario()
        if not usuario:
            messagebox.showwarning("Acceso", "Debes iniciar sesión para comprar.")
            return
        sel = getattr(self, "seleccion_actual", None)
        if not sel:
            messagebox.showwarning("Seleccionar", "Selecciona un producto primero.")
            return
        categoria = sel["categoria"]
        nombre = sel["nombre"]
        producto = sel["producto"]
        sucursal = self.sucursal_menu.get()
        if not sucursal:
            messagebox.showwarning("Sucursal", "Selecciona una sucursal.")
            return
        try:
            cantidad = int(self.cantidad_entry.get())
        except Exception:
            messagebox.showwarning("Cantidad", "Ingresa una cantidad válida.")
            return
        if cantidad <= 0:
            messagebox.showwarning("Cantidad", "La cantidad debe ser mayor a 0.")
            return
        # verificar stock
        stock_disponible = producto.get("stock_por_sucursal", {}).get(sucursal, 0)
        if cantidad > stock_disponible:
            messagebox.showerror("Stock insuficiente", f"Solo hay {stock_disponible} unidades en {sucursal}.")
            return
        metodo = self.metodo_pago.get()
        total = producto.get("precio") * cantidad
        confirmar = messagebox.askyesno("Confirmar compra",
                                        f"Usuario: {usuario}\nProducto: {nombre}\nCantidad: {cantidad}\nSucursal: {sucursal}\nPago: {metodo}\nTotal: ${total:.2f}\n\nConfirmar?")
        if not confirmar:
            return
        # Reducir stock y registrar compra
        ok, msg = DataManager.reducir_stock_al_comprar(categoria, nombre, sucursal, cantidad)
        if not ok:
            messagebox.showerror("Error", msg)
            return
        DataManager.registrar_venta(usuario, categoria, nombre, cantidad, sucursal, metodo, total)
        messagebox.showinfo("Compra exitosa", f"Compra registrada. Total: ${total:.2f}")
        # refrescar listado y limpiar detalle
        self.mostrar_todo()
        self.limpiar_detalle()
