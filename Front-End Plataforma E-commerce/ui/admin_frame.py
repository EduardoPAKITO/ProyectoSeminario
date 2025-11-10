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
        # Ajuste: altura reducida para que los botones no se oculten
        self.sucursales_box = ctk.CTkTextbox(izquierda, height=100, state="disabled")
        self.sucursales_box.pack(fill="both", padx=6, pady=(6, 4))

        # Aseguramos que el frame de botones se vea siempre
        btns_s = ctk.CTkFrame(izquierda)
        btns_s.pack(fill="x", padx=6, pady=(0, 6))

        ctk.CTkButton(btns_s, text="Agregar sucursal", command=self.agregar_sucursal).pack(side="left", padx=4)
        ctk.CTkButton(btns_s, text="Editar sucursal", command=self.editar_sucursal).pack(side="left", padx=4)
        ctk.CTkButton(btns_s, text="Eliminar sucursal", command=self.eliminar_sucursal).pack(side="left", padx=4)
        ctk.CTkButton(btns_s, text="Refrescar", command=self.refrescar_sucursales).pack(side="right", padx=4)

        # Derecha: productos (separados por categoría)
        derecha = ctk.CTkFrame(cont)
        derecha.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(derecha, text="Productos", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=6, pady=(6,2))
        self.productos_box = ctk.CTkTextbox(derecha, height=320, state="disabled")
        self.productos_box.pack(fill="both", expand=True, padx=6, pady=6)
        btns_p = ctk.CTkFrame(derecha)
        btns_p.pack(fill="x", padx=6, pady=6)
        ctk.CTkButton(btns_p, text="Agregar producto", command=self.agregar_producto).pack(side="left", padx=6)
        ctk.CTkButton(btns_p, text="Editar stock", command=self.editar_stock).pack(side="left", padx=6)
        ctk.CTkButton(btns_p, text="Eliminar producto", command=self.eliminar_producto).pack(side="left", padx=6)
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
        sucursales = DataManager.cargar_sucursales()
        self.sucursales_box.configure(state="normal")
        self.sucursales_box.delete("0.0", "end")
        for nombre, datos in sucursales.items():
            direccion = datos.get("direccion","")
            telefono = datos.get("telefono","")
            self.sucursales_box.insert("end", f"{nombre} - {direccion} - {telefono}\n")
        self.sucursales_box.configure(state="disabled")

    # Usuarios
    def eliminar_usuario(self):
        top = ctk.CTkToplevel(self)
        top.title("Eliminar Usuario")
        top.geometry("700x300+200+50")
        top.resizable(False, False)

        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        tk.Label(top, text="Email:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=150, y=100, width=80, height=25)
        entry_email = ttk.Entry(top, font="arial 12 bold")
        entry_email.place(x=260, y=100, width=250, height=30)

        def eliminar():
            email = entry_email.get().strip()
            if not email:
                messagebox.showerror("Error", "Debe completar el campo de email.")
                return

            usuarios = DataManager.cargar_usuarios()

            # Buscar usuario por email
            usuario_encontrado = None
            datos_usuario = None
            for usuario, datos in usuarios.items():
                if datos.get("email") == email:
                    usuario_encontrado = usuario
                    datos_usuario = datos
                    break

            if not usuario_encontrado:
                messagebox.showerror("Error", "Usuario no encontrado.")
                return

            if datos_usuario.get("rol") == "admin":
                messagebox.showwarning("Protegido", "No se puede eliminar al administrador.")
                return

            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar usuario '{datos_usuario.get('nombre')}' ({email})?")
            if not confirm:
                return

            del usuarios[usuario_encontrado]
            DataManager.guardar_usuarios(usuarios)
            messagebox.showinfo("OK", f"Usuario '{datos_usuario.get('nombre')}' eliminado correctamente.")
            top.destroy()
            self.refrescar_usuarios()
        
        tk.Button(top, text="Eliminar", font="arial 12 bold", command=eliminar, fg="white", bg="#2E8B64").place(x=150, y=180, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy, fg="white", bg="#2E8B64").place(x=350, y=180, width=150, height=40)

    # Sucursales 
    def agregar_sucursal(self):
        top = ctk.CTkToplevel(self)
        top.title("Agregar Sucursal")
        top.geometry("700x320+200+50")
        top.resizable(False, False)

        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        tk.Label(top, text="Nombre:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=80, y=40, width=120, height=25)
        entry_nombre = ttk.Entry(top, font="arial 12 bold")
        entry_nombre.place(x=220, y=40, width=350, height=30)

        tk.Label(top, text="Dirección:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=80, y=90, width=120, height=25)
        entry_direccion = ttk.Entry(top, font="arial 12 bold")
        entry_direccion.place(x=220, y=90, width=350, height=30)

        tk.Label(top, text="Teléfono:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=80, y=140, width=120, height=25)
        entry_telefono = ttk.Entry(top, font="arial 12 bold")
        entry_telefono.place(x=220, y=140, width=350, height=30)

        def agregar():
            nombre = entry_nombre.get().strip()
            direccion = entry_direccion.get().strip()
            telefono = entry_telefono.get().strip()
            if not nombre:
                messagebox.showerror ("Error", "Debe completar el campo nombre")
                return
            ok, msg = DataManager.agregar_sucursal(nombre, direccion=direccion, telefono=telefono)
            if ok:
                messagebox.showinfo("OK", msg)
                top.destroy()
                self.refrescar_productos()
                self.refrescar_sucursales()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(top, text="Guardar", font="arial 12 bold", command=agregar, fg="white", bg="#2E8B64").place(x=180, y=220, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy, fg="white", bg="#2E8B64").place(x=370, y=220, width=150, height=40)

    def editar_sucursal(self):
        top = ctk.CTkToplevel(self)
        top.title("Editar Sucursal")
        top.geometry("700x360+200+50")
        top.resizable(False, False)

        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        sucursales = DataManager.cargar_sucursales()
        nombres = list(sucursales.keys())
        if not nombres:
            messagebox.showinfo("Info", "No hay sucursales para editar.")
            top.destroy()
            return

        nombre_var = ctk.StringVar(value=nombres[0])

        ctk.CTkLabel(top, text="Sucursal:", width=100, height=25).place(x=40, y=30)
        ctk.CTkOptionMenu(top, values=nombres, variable=nombre_var, width=400).place(x=150, y=30)

        tk.Label(top, text="Dirección:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=40, y=80, width=120, height=25)
        entry_direccion = ttk.Entry(top, font="arial 12 bold")
        entry_direccion.place(x=150, y=80, width=400, height=30)

        tk.Label(top, text="Teléfono:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=40, y=130, width=120, height=25)
        entry_telefono = ttk.Entry(top, font="arial 12 bold")
        entry_telefono.place(x=150, y=130, width=400, height=30)

        def cargar_actual(_=None):
            sel = nombre_var.get()
            datos = sucursales.get(sel, {})
            entry_direccion.delete(0, "end")
            entry_telefono.delete(0, "end")
            entry_direccion.insert(0, datos.get("direccion", ""))
            entry_telefono.insert(0, datos.get("telefono", ""))

        cargar_actual()
        nombre_var.trace("w", lambda *a: cargar_actual())

        def guardar():
            sel = nombre_var.get()
            direccion = entry_direccion.get().strip()
            telefono = entry_telefono.get().strip()
            ok, msg = DataManager.editar_sucursal(sel, direccion=direccion, telefono=telefono)
            if ok:
                messagebox.showinfo("OK", msg)
                top.destroy()
                self.refrescar_sucursales()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(top, text="Guardar", font="arial 12 bold", command=guardar, fg="white", bg="#2E8B64").place(x=180, y=220, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy, fg="white", bg="#2E8B64").place(x=370, y=220, width=150, height=40)

    def eliminar_sucursal(self):
        top = ctk.CTkToplevel(self)
        top.title("Eliminar Sucursal")
        top.geometry("700x300+200+50")
        top.resizable(False, False)

        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        tk.Label(top, text="Nombre:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=150, y=100, width=80, height=25)
        entry_nombre = ttk.Entry(top, font="arial 12 bold")
        entry_nombre.place(x=260, y=100, width=250, height=30)

        def eliminar():
            nombre = entry_nombre.get()
            if not nombre:
                messagebox.showerror ("Error", "Debe completar el campo")
                return
            
            ok = DataManager.eliminar_sucursal(nombre)
            if ok:
                messagebox.showinfo("OK", "Sucursal eliminada de todos los productos.")
                top. destroy()
                self.refrescar_productos()
                self.refrescar_sucursales()
            else:
                messagebox.showerror("Error", "No se encontró la sucursal.")

        tk.Button(top, text="Eliminar", font="arial 12 bold", command=eliminar, fg="white", bg="#2E8B64").place(x=150, y=180, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy, fg="white", bg="#2E8B64").place(x=350, y=180, width=150, height=40)

    # Productos (resto del archivo sin cambios funcionales importantes)
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
        # Implementación para agregar productos (igual que antes, con validaciones)
        top = ctk.CTkToplevel(self)
        top.title("Agregar artículo")
        top.geometry("700x400+200+50")
        top.resizable(False, False)

        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        self.image_path = None 

        #Obtener lista de categorías
        categorias = DataManager.obtener_categorias(DataManager.cargar_productos())
        valor_inicial = categorias[0] if categorias else ""
        self.categoria_var = ctk.StringVar(value=valor_inicial) 

        tk.Label(top, text="Categoría:", font="arial 12 bold", fg="white", bg=top["bg"], anchor=tk.W).place(x=20, y=40, width=80, height=25)
        entry_categoria = ctk.CTkOptionMenu(master=top, values=categorias, variable=self.categoria_var, width=250, height=30)
        entry_categoria.place(x=125, y=40)

        tk.Label(top, text="Nombre:", font="arial 12 bold", fg="white", bg=top["bg"], anchor=tk.W).place(x=20, y=80, width=80, height=25)
        entry_nombre = ttk.Entry(top, font="arial 12 bold")
        entry_nombre.place(x=125, y=80, width=250, height=30)

        tk.Label(top, text="Precio:", font="arial 12 bold", fg="white", bg=top["bg"], anchor=tk.W).place(x=20, y=120, width=80, height=25)
        entry_precio = ttk.Entry(top, font="arial 12 bold")
        entry_precio.place(x=125, y=120, width=250, height=30)

        tk.Label(top, text="Descripción: ", font="arial 12 bold", fg="white", bg=top["bg"], anchor=tk.W).place(x=20, y=160, width=100, height=25)
        text_desc = tk.Text(top, font="arial 12")
        text_desc.place(x=125, y=160, width=250, height=78)

        self.frameimg = tk.Frame(top, bg="white", highlightbackground="gray", highlightthickness=1)
        self.frameimg.place(x=440, y=30, width=200, height=200)

        btnimage = tk.Button(top, text="Cargar imagen", font="arial 12 bold", command=self.load_image, fg="white", bg="#2E8B64")
        btnimage.place(x=470, y=245, width=150, height=40)

        sucursales = DataManager.obtener_sucursales(DataManager.cargar_productos())  # lista de nombres de sucursales
        stock_por_sucursal = {s: 0 for s in sucursales}  # inicializa todo en 0 

        def agregar_stock_sucursal():
            """Abre una ventana para agregar stock por sucursal."""
            sub = ctk.CTkToplevel(top)
            sub.title("Agregar stock por sucursal")
            sub.geometry("350x200+300+150")
            sub.resizable(False, False)

            sub.transient(self.master)
            sub.grab_set()
            sub.focus_set()
            sub.lift()

            sucursal_var = ctk.StringVar(value=sucursales[0] if sucursales else "")
            stock_var = tk.StringVar()

            tk.Label(sub, text="Sucursal:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=20, y=30, width=100, height=25)
            ctk.CTkOptionMenu(sub, values=sucursales, variable=sucursal_var, width=180).place(x=130, y=30)

            tk.Label(sub, text="Stock:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=20, y=70, width=100, height=25)
            ttk.Entry(sub, textvariable=stock_var, font="arial 12 bold").place(x=130, y=70, width=180, height=30)
            
            def guardar_stock():
                    sucursal = sucursal_var.get()
                    try:
                        cantidad = int(stock_var.get())
                        stock_por_sucursal[sucursal] = cantidad
                        messagebox.showinfo("OK", f"Stock asignado a {sucursal}: {cantidad}")
                        sub.destroy()
                    except ValueError:
                        messagebox.showerror("Error", "El stock debe ser un número entero válido.")
            
            tk.Button(sub, text="Guardar", font="arial 12 bold", command=guardar_stock, fg="white", bg="#2E8B64").place(x=110, y=120, width=120, height=35)

        def guardar():
            categoria = self.categoria_var.get()
            nombre = entry_nombre.get()
            precio = entry_precio.get()
            descripcion = text_desc.get("1.0", tk.END).strip()  

            if not categoria or not precio or not nombre:
                messagebox.showerror ("Error", "Categoria, precio y nombre son obligatorios")
                return
            
            try:
                precio = float (precio)
            except ValueError:
                messagebox. showerror ("Error", "precio debe ser un numero valido")
                return
            
            if self.image_path:
                image_path = self.image_path
            else:
                if categoria == "Celulares":
                    image_path = "default.jpg"
                else:
                    image_path = "default2.png"

            ok, mensaje = DataManager.agregar_producto(categoria, nombre, precio, image_path or "", stock_por_sucursal, descripcion)
            if not ok:
                messagebox.showerror("Error", mensaje)
                return
            messagebox.showinfo("OK", "Producto agregado.")
            top. destroy()
            self.refrescar_productos()
            self.refrescar_sucursales()

        # Botón principal para agregar stock por sucursal
        tk.Button(top, text="Agregar stock por sucursal", font="arial 12 bold", command=agregar_stock_sucursal, fg="white", bg="#2E8B64").place(x=125, y=245, width=250, height=35)       
        tk.Button(top, text="Guardar", font="arial 12 bold", command=guardar, fg="white", bg="#2E8B64").place(x=170, y=330, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy, fg="white", bg="#2E8B64").place(x=380, y=330, width=150, height=40)

    def editar_stock(self):
        top = ctk.CTkToplevel(self)
        top.title("Editar stock")
        top.geometry("700x400+200+50")
        top.resizable(False, False)

        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        #Obtener lista de categorias
        categorias = DataManager.obtener_categorias(DataManager.cargar_productos())
        valor_inicial = categorias[0] if categorias else ""
        self.categoria_var = ctk.StringVar(value=valor_inicial) 

        tk.Label(top, text="Categoría:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=150, y=60, width=80, height=25)
        entry_categoria = ctk.CTkOptionMenu(master=top, values=categorias, variable=self.categoria_var, width=250, height=30)
        entry_categoria.place(x=260, y=60)

        tk.Label(top, text="Nombre:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=150, y=100, width=80, height=25)
        entry_nombre = ttk.Entry(top, font="arial 12 bold")
        entry_nombre.place(x=260, y=100, width=250, height=30)

        #Obtener lista de nombres de sucursales
        sucursales = DataManager.obtener_sucursales(DataManager.cargar_productos())
        sucursal_var = ctk.StringVar(value=sucursales[0] if sucursales else "")
        stock_var = tk.StringVar()

        tk.Label(top, text="Sucursal:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=150, y=140, width=100, height=25)
        ctk.CTkOptionMenu(top, values=sucursales, variable=sucursal_var, width=180).place(x=260, y=140)

        tk.Label(top, text="Stock:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=150, y=180, width=100, height=25)
        ttk.Entry(top, textvariable=stock_var, font="arial 12 bold").place(x=260, y=180, width=180, height=30)
        
        def actualizar():
            categoria = self.categoria_var.get()
            nombre = entry_nombre.get()
            sucursal = sucursal_var.get()
            nuevo = stock_var.get()

            if not nuevo or not nombre:
                messagebox.showerror ("Error", "Todos los campos deben ser completados")
                return
            
            try:
                stock = float (nuevo)
            except ValueError:
                messagebox. showerror ("Error", "Stock debe ser un número valido")
                return

            ok = DataManager.actualizar_stock(categoria, nombre, sucursal, stock)
            if ok:
                messagebox.showinfo("OK", "Stock actualizado.")
                top. destroy()
                self.refrescar_productos()
            else:
                messagebox.showerror("Error", "No se pudo actualizar (revisar que los datos esten correctos).")

        tk.Button(top, text="Actualizar Stock", font="arial 12 bold", command=actualizar, fg="white", bg="#2E8B64").place(x=150, y=260, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy, fg="white", bg="#2E8B64").place(x=350, y=260, width=150, height=40)

    def eliminar_producto(self):
        top = ctk.CTkToplevel(self)
        top.title("Eliminar producto")
        top.geometry("700x300+200+50")
        top.resizable(False, False)

        top.transient(self.master)
        top.grab_set()
        top.focus_set()
        top.lift()

        #Obtener lista de categorias
        categorias = DataManager.obtener_categorias(DataManager.cargar_productos())
        valor_inicial = categorias[0] if categorias else ""
        self.categoria_var = ctk.StringVar(value=valor_inicial) 

        tk.Label(top, text="Categoría:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=150, y=60, width=80, height=25)
        entry_categoria = ctk.CTkOptionMenu(master=top, values=categorias, variable=self.categoria_var, width=250, height=30)
        entry_categoria.place(x=260, y=60)

        tk.Label(top, text="Nombre:", font="arial 12 bold", fg="white", bg=top["bg"]).place(x=150, y=100, width=80, height=25)
        entry_nombre = ttk.Entry(top, font="arial 12 bold")
        entry_nombre.place(x=260, y=100, width=250, height=30)

        def eliminar():
            categoria = self.categoria_var.get()
            nombre = entry_nombre.get()

            if not nombre:
                messagebox.showerror ("Error", "Debe completar el campo")
                return
            
            ok = DataManager.eliminar_producto(categoria, nombre)
            if ok:
                messagebox.showinfo("OK", "Producto eliminado.")
                top. destroy()
                self.refrescar_productos()
                self.refrescar_sucursales()
            else:
                messagebox.showerror("Error", "No se encontró el producto.")
        tk.Button(top, text="Eliminar producto", font="arial 12 bold", command=eliminar, fg="white", bg="#2E8B64").place(x=150, y=180, width=150, height=40)
        tk.Button(top, text="Cancelar", font="arial 12 bold", command=top.destroy, fg="white", bg="#2E8B64").place(x=350, y=180, width=150, height=40)
