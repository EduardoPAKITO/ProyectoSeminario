# admin_frame.py
import tkinter as tk
import customtkinter as ctk
from data.data_manager import DataManager
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio raíz del proyecto
CARPETA_IMAGENES = os.path.join(BASE_DIR, "images")

class AdminFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.image_folder = CARPETA_IMAGENES
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
        self._construir()

    def _construir(self):
        # panel superior con botones
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(top, text="Panel de Administración", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=6)

        # contenedor principal
        cont = ctk.CTkFrame(self)
        cont.pack(fill="both", expand=True, padx=8, pady=8)

        # Izquierda: usuarios y sucursales
        izquierda = ctk.CTkFrame(cont)
        izquierda.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        ctk.CTkLabel(izquierda, text="Usuarios", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=6, pady=(6,2))
        self.usuarios_box = ctk.CTkTextbox(izquierda, height=200, state="disabled")
        self.usuarios_box.pack(fill="both", expand=False, padx=6, pady=6)
        btns_u = ctk.CTkFrame(izquierda)
        btns_u.pack(fill="x", padx=6, pady=6)
        # SE QUITA boton Agregar cliente 
        ctk.CTkButton(btns_u, text="Eliminar usuario", command=self.eliminar_usuario).pack(side="left", padx=6)
        ctk.CTkButton(btns_u, text="Refrescar", command=self.refrescar_usuarios).pack(side="right", padx=6)

        ctk.CTkLabel(izquierda, text="Sucursales", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=6, pady=(12,2))
        self.sucursales_box = ctk.CTkTextbox(izquierda, height=120, state="disabled")
        self.sucursales_box.pack(fill="both", padx=6, pady=6)
        btns_s = ctk.CTkFrame(izquierda)
        btns_s.pack(fill="x", padx=6, pady=6)
        ctk.CTkButton(btns_s, text="Agregar sucursal", command=self.agregar_sucursal_dialog).pack(side="left", padx=6)
        ctk.CTkButton(btns_s, text="Eliminar sucursal", command=self.eliminar_sucursal_dialog).pack(side="left", padx=6)
        ctk.CTkButton(btns_s, text="Refrescar", command=self.refrescar_sucursales).pack(side="right", padx=6)

        # Derecha: productos (separados por categoría)
        derecha = ctk.CTkFrame(cont)
        derecha.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(derecha, text="Productos", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=6, pady=(6,2))
        self.productos_box = ctk.CTkTextbox(derecha, height=320, state="disabled")
        self.productos_box.pack(fill="both", expand=True, padx=6, pady=6)
        btns_p = ctk.CTkFrame(derecha)
        btns_p.pack(fill="x", padx=6, pady=6)
        ctk.CTkButton(btns_p, text="Agregar producto", command=self.agregar_producto).pack(side="left", padx=6)
        ctk.CTkButton(btns_p, text="Editar stock", command=self.editar_stock_dialog).pack(side="left", padx=6)
        ctk.CTkButton(btns_p, text="Eliminar producto", command=self.eliminar_producto_dialog).pack(side="left", padx=6)
        ctk.CTkButton(btns_p, text="Refrescar", command=self.refrescar_todo).pack(side="right", padx=6)

        self.refrescar_todo()

    def refrescar_todo(self):
        self.refrescar_usuarios()
        self.refrescar_productos()
        self.refrescar_sucursales()

    def refrescar_usuarios(self):
        usuarios = DataManager.cargar_usuarios()
        self.usuarios_box.configure(state="normal")
        self.usuarios_box.delete("0.0", "end")
        for u, info in usuarios.items():
            self.usuarios_box.insert("end", f"{u} - {info.get('rol')} - {info.get('email','')}\n")
        self.usuarios_box.configure(state="disabled")

    def refrescar_productos(self):
        productos = DataManager.cargar_productos()
        self.productos_box.configure(state="normal")
        self.productos_box.delete("0.0", "end")
        for categoria, lista in productos.items():
            self.productos_box.insert("end", f"--- {categoria} ---\n")
            for nombre, datos in lista.items():
                suc_info = ", ".join([f"{s}:{c}" for s, c in datos.get("stock_por_sucursal", {}).items()])
                img = datos.get("imagen", "")
                desc = datos.get("descripcion", "")
                # mejor separación: linea por producto + descripción corta
                self.productos_box.insert("end", f"{nombre} - ${datos.get('precio'):.2f} - [{suc_info}] - img:{img}\n")
                if desc:
                    self.productos_box.insert("end", f"    Desc: {desc}\n")
                self.productos_box.insert("end", "\n")
        self.productos_box.configure(state="disabled")

    def refrescar_sucursales(self):
        productos = DataManager.cargar_productos()
        sucursales = DataManager.obtener_sucursales(productos)
        self.sucursales_box.configure(state="normal")
        self.sucursales_box.delete("0.0", "end")
        for s in sucursales:
            self.sucursales_box.insert("end", f"{s}\n")
        self.sucursales_box.configure(state="disabled")

    # Usuarios
    def eliminar_usuario(self):
        usuario = simpledialog.askstring("Eliminar usuario", "Usuario a eliminar:", parent=self)
        if not usuario:
            return
        usuarios = DataManager.cargar_usuarios()
        if usuario not in usuarios:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return
        if usuarios[usuario].get("rol") == "admin":
            messagebox.showwarning("Protegido", "No se puede eliminar al administrador.")
            return
        confirm = messagebox.askyesno("Confirmar", f"Eliminar usuario {usuario}?")
        if not confirm:
            return
        del usuarios[usuario]
        DataManager.guardar_usuarios(usuarios)
        messagebox.showinfo("OK", "Usuario eliminado.")
        self.refrescar_usuarios()

    # Sucursales 
    def agregar_sucursal_dialog(self):
        nombre = simpledialog.askstring("Agregar sucursal", "Nombre de la nueva sucursal:", parent=self)
        if not nombre:
            return
        DataManager.agregar_sucursal(nombre)
        messagebox.showinfo("OK", "Sucursal agregada (stock inicial 0 en productos).")
        self.refrescar_sucursales()
        self.refrescar_productos()

    def eliminar_sucursal_dialog(self):
        nombre = simpledialog.askstring("Eliminar sucursal", "Nombre de la sucursal a eliminar:", parent=self)
        if not nombre:
            return
        DataManager.eliminar_sucursal(nombre)
        messagebox.showinfo("OK", "Sucursal eliminada de todos los productos.")
        self.refrescar_sucursales()
        self.refrescar_productos()

    # Productos
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            image = image.resize((200,200), Image.LANCZOS)
            image_name = os.path.basename(file_path)
            image_save_path = os.path.join(self.image_folder, image_name)
            image.save(image_save_path)

            self.image_tk = ImageTk.PhotoImage(image)

            self.product_image = self.image_tk
            self.image_path = image_name

            img_label = tk.Label(self.frameimg, image = self.image_tk)
            img_label.place(x=0, y=0, width=200, height=200)
    
    def agregar_producto(self):
        top = tk.Toplevel(self)
        top.title("Agregar articulo")
        top.geometry("700x400+200+50")
        top.config(bg="#C6D9E3")
        top.resizable(False, False)

        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        tk.Label(top, text="Categoria: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=20, width=80, height=25)
        entry_categoria = ttk.Entry(top, font="arial 12 bold")
        entry_categoria.place(x=120, y=20, width=250, height=30)

        tk.Label(top, text="Nombre:", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=60, width=80, height=25)
        entry_nombre = ttk.Entry(top, font="arial 12 bold")
        entry_nombre.place(x=120, y=60, width=250, height=30)

        tk.Label(top, text="Precio: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=100, width=80, height=25)
        entry_precio = ttk.Entry(top, font="arial 12 bold")
        entry_precio.place(x=120, y=100, width=250, height=30)

        tk.Label(top, text="Sucursal: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=140, width=80, height=25)
        entry_sucursal = ttk.Entry(top, font="arial 12 bold")
        entry_sucursal.place(x=120, y=140, width=250, height=30)

        tk.Label(top, text="Stock: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=180, width=80, height=25)
        entry_stock = ttk.Entry(top, font="arial 12 bold")
        entry_stock.place(x=120, y=180, width=250, height=30)

        tk.Label(top, text="Descripcion: ", font="arial 12 bold", bg="#C6D9E3").place(x=20, y=220, width=100, height=25)
        entry_desc = ttk.Entry(top, font="arial 12 bold")
        entry_desc.place(x=120, y=220, width=250, height=30)

        self.frameimg = tk.Frame(top, bg="white", highlightbackground="gray", highlightthickness=1)
        self.frameimg.place(x=440, y=30, width=200, height=200)

        btnimage = tk.Button(top, text="Cargar imagen", font="arial 12 bold", command=self. load_image)
        btnimage.place(x=470, y=260, width=150, height=40)

        def guardar():
            categoria = entry_categoria.get().strip()
            precio = entry_precio.get().strip()
            stock = entry_stock.get().strip()
            nombre = entry_nombre.get().strip()
            sucursal = entry_sucursal.get().strip()
            descripcion = entry_desc.get().strip()

            if not categoria or not precio or not nombre:
                messagebox.showerror ("Error", "Categoria, precio y nombre son obligatorios")
                return
            
            try:
                precio = float (precio)
            except ValueError:
                messagebox. showerror ("Error", "precio debe ser un numero valido")
                return
            
            if hasattr(self, 'image_path'):
                image_path = self.image_path
            else:
                image_path = (r"default.jpg")

            stock_por_sucursal = {}
            if sucursal:
                # validar que sucursal exista EN EL SISTEMA
                sucursales_existentes = DataManager.obtener_sucursales()
                if sucursal not in sucursales_existentes:
                    messagebox.showerror("Error", f"La sucursal '{sucursal}' no existe. Primero crea la sucursal.")
                    return
                try:
                    stock_val = int(stock) if stock else 0
                except Exception:
                    messagebox.showerror("Error", "Stock debe ser un número entero.")
                    return
                stock_por_sucursal[sucursal] = stock_val

            ok, mensaje = DataManager.agregar_producto(categoria, nombre, precio, image_path or "", stock_por_sucursal, descripcion=descripcion)
            if not ok:
                messagebox.showerror("Error", mensaje)
                return
            messagebox.showinfo("OK", "Producto agregado.")
            top. destroy()
            self.refrescar_productos()
            self.refrescar_sucursales()

        tk.Button(top, text="Guardar", font="arial 12 bold", command=guardar).place(x=50, y=260, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy).place(x=260, y=260, width=150, height=40)
    #ESTE ESTA DE GANAS NO? Porque el que funciona es el otro
    def agregar_producto_dialog(self):
        categoria = simpledialog.askstring("Categoria", "Categoria (Celulares o Accesorios):", parent=self)
        if not categoria:
            return
        nombre = simpledialog.askstring("Nombre", "Nombre del producto:", parent=self)
        if not nombre:
            return
        precio = simpledialog.askstring("Precio", "Precio (ej. 199.99):", parent=self)
        stock_txt = simpledialog.askstring("Stock por sucursal", "Formato: Sucursal1:10,Sucursal2:5 (puedes dejar vacío):", parent=self)
        imagen = simpledialog.askstring("Imagen", "Nombre de archivo dentro de folder 'images' (opcional):", parent=self)
        try:
            precio_f = float(precio)
        except Exception:
            messagebox.showerror("Error", "Precio inválido.")
            return
        stock_por_sucursal = {}
        if stock_txt:
            for parte in stock_txt.split(","):
                if ":" in parte:
                    s, c = parte.split(":", 1)
                    s = s.strip()
                    c = c.strip()
                    # validar sucursal existente
                    sucursales_existentes = DataManager.obtener_sucursales()
                    if s not in sucursales_existentes:
                        messagebox.showerror("Error", f"La sucursal '{s}' no existe.")
                        return
                    try:
                        stock_por_sucursal[s] = int(c)
                    except Exception:
                        stock_por_sucursal[s] = 0
        ok, mensaje = DataManager.agregar_producto(categoria, nombre, precio_f, imagen or "", stock_por_sucursal)
        if not ok:
            messagebox.showerror("Error", mensaje)
            return
        messagebox.showinfo("OK", "Producto agregado.")
        self.refrescar_productos()
        self.refrescar_sucursales()

    def editar_stock_dialog(self):
        categoria = simpledialog.askstring("Categoria", "Categoria del producto:", parent=self)
        nombre = simpledialog.askstring("Nombre", "Nombre exacto del producto:", parent=self)
        if not categoria or not nombre:
            return
        sucursal = simpledialog.askstring("Sucursal", "Sucursal a modificar:", parent=self)
        if not sucursal:
            return
        # validar sucursal
        sucursales_existentes = DataManager.obtener_sucursales()
        if sucursal not in sucursales_existentes:
            messagebox.showerror("Error", f"La sucursal '{sucursal}' no existe.")
            return
        nuevo = simpledialog.askinteger("Nuevo stock", f"Nuevo stock para {nombre} en {sucursal}:", parent=self, minvalue=0)
        if nuevo is None:
            return
        ok = DataManager.actualizar_stock(categoria, nombre, sucursal, nuevo)
        if ok:
            messagebox.showinfo("OK", "Stock actualizado.")
            self.refrescar_productos()
        else:
            messagebox.showerror("Error", "No se pudo actualizar (revisar categoría/nombre).")

    def eliminar_producto_dialog(self):
        categoria = simpledialog.askstring("Categoria", "Categoria del producto:", parent=self)
        nombre = simpledialog.askstring("Nombre", "Nombre exacto del producto:", parent=self)
        if not categoria or not nombre:
            return
        confirm = messagebox.askyesno("Confirmar", f"Eliminar producto {nombre} en {categoria}?")
        if not confirm:
            return
        ok = DataManager.eliminar_producto(categoria, nombre)
        if ok:
            messagebox.showinfo("OK", "Producto eliminado.")
            self.refrescar_productos()
            self.refrescar_sucursales()
        else:
            messagebox.showerror("Error", "No se encontró el producto.")
