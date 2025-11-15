# cliente_frame.py
import customtkinter as ctk
from data.data_manager import DataManager
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkImage
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio raíz del proyecto
CARPETA_IMAGENES = os.path.join(BASE_DIR, "images")

class ClienteFrame(ctk.CTkFrame):
    def __init__(self, master, funcion_get_usuario, add_to_cart_callback=None, role="cliente", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.funcion_get_usuario = funcion_get_usuario
        self.add_to_cart_callback = add_to_cart_callback  # callback para agregar al carrito en App
        self.role = role
        self.productos_mostrados = []  # lista de tuples (categoria, nombre, datos)
        self.imagen_actual = None
        self.seleccion_actual = None
        self.imagen_sin_foto = ctk.CTkImage(Image.open(os.path.join(CARPETA_IMAGENES, "sinfoto.jpg")), size=(250, 200)) 
        self._construir()

    def _construir(self):
        # Layout: izquierda buscar/listado, derecha detalle/imagen/compra
        izquierdo = ctk.CTkFrame(self)
        izquierdo.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        derecho = ctk.CTkScrollableFrame(self, width=360)
        derecho.pack(side="right", fill="y", padx=8, pady=8)

        # Buscador con selector de categoría
        categorias = DataManager.obtener_categorias(DataManager.cargar_productos())
        filtro_fr = ctk.CTkFrame(izquierdo)
        filtro_fr.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(filtro_fr, text="Buscar en:").pack(side="left", padx=6)
        # Verificamos que la lista no esté vacía para evitar errores
        valor_inicial = categorias[0] if categorias else ""
        self.categoria_var = ctk.StringVar(value=valor_inicial)
        ctk.CTkOptionMenu(filtro_fr, values=categorias, variable=self.categoria_var).pack(side="left", padx=6)
        self.buscar_entry = ctk.CTkEntry(filtro_fr, placeholder_text="Nombre del producto...")
        self.buscar_entry.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(filtro_fr, text="Buscar", command=self.buscar).pack(side="left", padx=6)
        ctk.CTkButton(filtro_fr, text="Mostrar todo", command=self.mostrar_todo).pack(side="left", padx=6)

        # Listado (scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(izquierdo)
        self.scroll_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.row = 0
        self.column = 0

        # DETALLE DERECHO
        self.lbl_nombre = ctk.CTkLabel(derecho, text="Producto: -", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_nombre.pack(anchor="w", pady=(6,4))

        # descripción
        self.lbl_descripcion = ctk.CTkLabel(derecho, text="Descripción: -", wraplength=320, justify="left")
        self.lbl_descripcion.pack(anchor="w", pady=(2,4), padx=8)

        # label para imagen (se ajusta)
        self.label_imagen = ctk.CTkLabel(derecho, text="", image=self.imagen_sin_foto, width=300, height=200)
        self.label_imagen.pack(pady=6)
        self.label_imagen.image = self.imagen_sin_foto

        self.lbl_precio = ctk.CTkLabel(derecho, text="Precio: -")
        self.lbl_precio.pack(anchor="w", padx=8, pady=(6,0))
        self.lbl_stock = ctk.CTkLabel(derecho, text="Stock en sucursal: -")
        self.lbl_stock.pack(anchor="w", padx=8, pady=(2,0))

        ctk.CTkLabel(derecho, text="Sucursal:").pack(anchor="w", padx=8, pady=(8,0))
        # Creamos option menu y vinculamos comando para actualizar stock cuando cambie
        self.sucursal_menu = ctk.CTkOptionMenu(derecho, values=[], command=self.cambiar_sucursal)
        self.sucursal_menu.pack(anchor="w", padx=8, pady=(0,8))

        # Mostrar dirección de la sucursal seleccionada
        self.lbl_sucursal_info = ctk.CTkLabel(derecho, text="Dirección: -")
        self.lbl_sucursal_info.pack(anchor="w", padx=8, pady=(0,6))

        ctk.CTkLabel(derecho, text="Cantidad:").pack(anchor="w", padx=8)
        self.cantidad_entry = ctk.CTkEntry(derecho, width=80)
        self.cantidad_entry.insert(0, "1")
        self.cantidad_entry.pack(anchor="w", padx=8, pady=(0,8))

        # Si es cliente mostramos botón Agregar al carrito. Si es admin, no.
        if self.role != "admin":
            ctk.CTkButton(derecho, text="Agregar al carrito", command=self.agregar_al_carrito).pack(pady=(8,4))
        else:
            ctk.CTkLabel(derecho, text="Vista Administrador (no se permiten compras)").pack(pady=(8,4))

        ctk.CTkButton(derecho, text="Limpiar", command=self.limpiar_detalle).pack()

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
            self.mostrar_articulo(i, nombre, prod.get("precio", 0), ruta_imagen, stock_total, (cat, nombre, prod))

    def mostrar_articulo(self, indice, articulo, precio, imagen_path, stock, producto_tuple):
        # Frame individual para cada producto
        article_frame = ctk.CTkFrame(self.scroll_frame, fg_color="white", corner_radius=8)
        article_frame.grid(row=self.row, column=self.column, padx=7, pady=10, sticky="nsew")
        # ahora se puede seleccionar haciendo click en cualquier parte del producto
        article_frame.bind("<Button-1>", lambda e, t=producto_tuple: self.mostrar_detalle(*t))

        # Índice negrita arriba
        ctk.CTkLabel(article_frame, text=f"{indice})", text_color="black", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=6, pady=(2, 0))

        # Imagen
        if imagen_path and os.path.exists(imagen_path):
            try:
                pil_image = Image.open(imagen_path)
                ctk_image_obj = CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
                 #verificar si el stock total es 0
                if stock == 0:
                    img_label = ctk.CTkLabel(article_frame, image=ctk_image_obj, text="AGOTADO", text_color="red", font=ctk.CTkFont(size=32, weight="bold"))
                    #self.label_imagen.configure(text="AGOTADO", text_color="red", font=ctk.CTkFont(size=32, weight="bold"))
                else:
                    img_label = ctk.CTkLabel(article_frame, image=ctk_image_obj, text="")
                
                img_label.pack(expand=True, fill="both", pady=(4, 2))
                # click también sobre imagen
                img_label.bind("<Button-1>", lambda e, t=producto_tuple: self.mostrar_detalle(*t))
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

    def mostrar_detalle(self, categoria, nombre, producto):
        self.lbl_nombre.configure(text=f"Producto: {nombre}")
        descripcion = producto.get("descripcion", "(sin descripción)")
        self.lbl_descripcion.configure(text=f"Descripción: {descripcion}")
        self.lbl_precio.configure(text=f"Precio: ${producto.get('precio'):.2f}")
        
        #cargar sucursales
        sucursales = list(producto.get("stock_por_sucursal", {}).keys())
        # calcular el stock total en todas las sucursales
        stock_total = sum(producto.get("stock_por_sucursal", {}).values()) if sucursales else 0
        if sucursales:
            self.sucursal_menu.configure(values=sucursales)
            #establecer el primer valor si no hay una sucursal seleccionada
            sel = sucursales[0]
            try:
                self.sucursal_menu.set(sel)
            except Exception:
                pass
            stock_s = producto.get("stock_por_sucursal", {}).get(sel, 0)
            self.lbl_stock.configure(text=f"Stock en {sel}: {stock_s}")
            #muestra la dirección de la sucursal
            sucursales_info = DataManager.cargar_sucursales()
            info = sucursales_info.get(sel, {})
            direccion = info.get("direccion", "(sin dirección)")
            telefono = info.get("telefono", "")
            self.lbl_sucursal_info.configure(text=f"Dirección: {direccion} {'- Tel:' + telefono if telefono else ''}")
        else:
            self.sucursal_menu.configure(values=[])
            try:
                self.sucursal_menu.set("")
            except Exception:
                pass
            self.lbl_stock.configure(text="Sin sucursales")
            self.lbl_sucursal_info.configure(text="Dirección: -")
        # cargar imagen ajustable
        imagen_nombre = producto.get("imagen", "")
        ruta = os.path.join(CARPETA_IMAGENES, imagen_nombre) if imagen_nombre else None
        if ruta and os.path.exists(ruta):
            try:
                pil_image = Image.open(ruta)
                ctk_image_obj = CTkImage(light_image=pil_image, dark_image=pil_image, size=(300, 300))
                self.label_imagen.configure(image=ctk_image_obj, text="")
                self.label_imagen.image = ctk_image_obj
            except Exception:
                self.label_imagen.configure(image=self.imagen_sin_foto, text="(imagen no cargada)")
                self.label_imagen.image = self.imagen_sin_foto
        else:
            self.label_imagen.configure(image=self.imagen_sin_foto, text="")
            self.label_imagen.image = self.imagen_sin_foto
        # almacenar selección actual
        self.seleccion_actual = {"categoria": categoria, "nombre": nombre, "producto": producto}

    def cambiar_sucursal(self, nuevo_val):
        # actualizar label de stock según la sucursal seleccionada
        sel = getattr(self, "seleccion_actual", None)
        if not sel:
            return
        producto = sel["producto"]
        stock_s = producto.get("stock_por_sucursal", {}).get(nuevo_val, 0)
        self.lbl_stock.configure(text=f"Stock en {nuevo_val}: {stock_s}")
        # actualizar info de sucursal (dirección y teléfono)
        sucursales_info = DataManager.cargar_sucursales()
        info = sucursales_info.get(nuevo_val, {})
        direccion = info.get("direccion", "(sin dirección)")
        telefono = info.get("telefono", "")
        self.lbl_sucursal_info.configure(text=f"Dirección: {direccion} {'- Tel:' + telefono if telefono else ''}")

    def limpiar_detalle(self):
        self.lbl_nombre.configure(text="Producto: -")
        self.lbl_descripcion.configure(text="Descripción: -")
        self.lbl_precio.configure(text="Precio: -")
        self.lbl_stock.configure(text="Stock en sucursal: -")
        self.lbl_sucursal_info.configure(text="Dirección: -")
        try:
            self.sucursal_menu.configure(values=[])
            self.sucursal_menu.set("")
        except Exception:
            pass
        self.cantidad_entry.delete(0, "end")
        self.cantidad_entry.insert(0, "1")

        # volver a la imagen por defecto
        self.label_imagen.configure(image=self.imagen_sin_foto, text="")
        self.label_imagen.image = self.imagen_sin_foto
        self.productos_mostrados = []
        self.seleccion_actual = None
        
        # Volver a cargar la vista actual
        self.mostrar_todo()

    def agregar_al_carrito(self):
        usuario = self.funcion_get_usuario()
        if not usuario:
            messagebox.showwarning("Acceso", "Debes iniciar sesión para agregar al carrito.")
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
        # llamar callback para agregar al carrito en App (si existe)
        if self.add_to_cart_callback:
            self.add_to_cart_callback({
                "usuario": usuario,
                "categoria": categoria,
                "producto": nombre,
                "cantidad": cantidad,
                "sucursal": sucursal,
                "precio_unitario": producto.get("precio", 0)
            })
            messagebox.showinfo("Carrito", f"{cantidad} x {nombre} agregado al carrito.")
        else:
            messagebox.showwarning("Carrito", "No está disponible la funcionalidad de carrito.")
