import json
import csv
import os
import uuid
from datetime import datetime

class DataManager:
    # Rutas relativas al directorio del proyecto
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio raíz del proyecto
    DATA_DIR = os.path.join(BASE_DIR, "data") #Directorio de archivos de datos
    RUTA_USUARIOS = os.path.join(DATA_DIR, "usuarios.csv") #Ruta al archivo CSV de usuarios
    RUTA_PRODUCTOS = os.path.join(DATA_DIR, "productos.json") #Ruta al archivo JSON de productos
    RUTA_VENTAS = os.path.join(DATA_DIR, "ventas.json") #Ruta al archivo JSON de ventas
    RUTA_SUCURSALES = os.path.join(DATA_DIR, "sucursales.json") #Ruta al archivo JSON de sucursales
    CARPETA_IMAGENES = os.path.join(BASE_DIR, "images") #Ruta a la carpeta de imágenes

    @staticmethod
    def asegurar_archivos():
        """Asegura que todos los archivos y carpetas necesarios existan"""
        os.makedirs(DataManager.DATA_DIR, exist_ok=True)
        os.makedirs(DataManager.CARPETA_IMAGENES, exist_ok=True)
        DataManager._asegurar_archivo_usuarios()
        # NOTA: se comenta la inicialización automática de productos para no sobreescribir productos reales
        # DataManager._asegurar_productos_iniciales()
        DataManager._asegurar_archivo_ventas()
        DataManager._asegurar_archivo_sucursales()

    @staticmethod
    def _asegurar_archivo_usuarios():
        if not os.path.exists(DataManager.RUTA_USUARIOS):
            with open(DataManager.RUTA_USUARIOS, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["usuario", "clave", "rol", "email", "nombre"])
                writer.writerow(["admin", "admin", "admin", "admin@local", "Administrador"])
                writer.writerow(["cliente", "cliente", "cliente", "cliente@local", "Cliente"])

    @staticmethod
    def _asegurar_productos_iniciales():
        # Esta función crea un productos.json de ejemplo. Se dejó implementada por compatibilidad,
        # pero su llamado fue comentado en asegurar_archivos() para evitar sobreescribir datos reales.
        if not os.path.exists(DataManager.RUTA_PRODUCTOS):
            ejemplo = {
                "Celulares": {
                    "Teléfono Modelo A": {
                        "id": str(uuid.uuid4()),
                        "precio": 699.90,
                        "imagen": "ejemplo_telefono.jpg",
                        "descripcion": "Teléfono modelo A con buenas prestaciones.",
                        "stock_por_sucursal": {"Sucursal Centro": 4, "Sucursal Norte": 2}
                    }
                },
                "Accesorios": {
                    "Funda Protectora": {
                        "id": str(uuid.uuid4()),
                        "precio": 19.90,
                        "imagen": "ejemplo_funda.jpg",
                        "descripcion": "Funda de silicona resistente.",
                        "stock_por_sucursal": {"Sucursal Centro": 30, "Sucursal Sur": 20}
                    },
                    "Cargador Rápido 30W": {
                        "id": str(uuid.uuid4()),
                        "precio": 29.50,
                        "imagen": "ejemplo_cargador.jpg",
                        "descripcion": "Cargador rápido compatible con la mayoría de modelos.",
                        "stock_por_sucursal": {"Sucursal Norte": 15, "Sucursal Sur": 10}
                    }
                }
            }
            with open(DataManager.RUTA_PRODUCTOS, "w", encoding="utf-8") as f:
                json.dump(ejemplo, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _asegurar_archivo_ventas():
        if not os.path.exists(DataManager.RUTA_VENTAS):
            with open(DataManager.RUTA_VENTAS, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _asegurar_archivo_sucursales():
        # Nuevo archivo para guardar sucursales con dirección y teléfono
        if not os.path.exists(DataManager.RUTA_SUCURSALES):
            ejemplo = {
                "Sucursal Centro": {"direccion": "Av. Principal 123", "telefono": "000-000"},
                "Sucursal Norte": {"direccion": "Ruta 9 km 10", "telefono": "111-111"}
            }
            with open(DataManager.RUTA_SUCURSALES, "w", encoding="utf-8") as f:
                json.dump(ejemplo, f, indent=2, ensure_ascii=False)

    # Métodos para usuarios
    @staticmethod
    def cargar_usuarios():
        usuarios = {}
        # Acepta archivos con o sin email/nombre
        if not os.path.exists(DataManager.RUTA_USUARIOS):
            return usuarios
        with open(DataManager.RUTA_USUARIOS, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for fila in reader:
                usuarios[fila["usuario"]] = {
                    "clave": fila.get("clave", ""),
                    "rol": fila.get("rol", "cliente"),
                    "email": fila.get("email", "") or "",
                    "nombre": fila.get("nombre", "") or ""
                }
        return usuarios

    @staticmethod
    def guardar_usuarios(dic_usuarios):
        with open(DataManager.RUTA_USUARIOS, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["usuario", "clave", "rol", "email", "nombre"])
            for usuario, info in dic_usuarios.items():
                writer.writerow([usuario, info.get("clave",""), info.get("rol","cliente"),
                                 info.get("email",""), info.get("nombre","")])

    @staticmethod
    def crear_usuario_cliente(usuario, clave, email="", nombre=""):
        usuarios = DataManager.cargar_usuarios()
        # Validar nombre de usuario y email únicos
        if usuario in usuarios:
            return False, "El usuario ya existe."
        # validar email duplicado
        for u, info in usuarios.items():
            if info.get("email") and email and info.get("email").lower() == email.lower():
                return False, "El email ya está registrado."
            if info.get("nombre") and nombre and info.get("nombre").strip().lower() == nombre.strip().lower() and u != usuario:
                # previene crear varias cuentas con mismo nombre "visible"
                return False, "Ya existe una cuenta con el mismo nombre."
        usuarios[usuario] = {"clave": clave, "rol": "cliente", "email": email, "nombre": nombre}
        DataManager.guardar_usuarios(usuarios)
        return True, "Usuario cliente creado correctamente."

    # Métodos para productos y sucursales
    @staticmethod
    def cargar_productos():
        if not os.path.exists(DataManager.RUTA_PRODUCTOS):
            return {}
        with open(DataManager.RUTA_PRODUCTOS, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def guardar_productos(dic_productos):
        with open(DataManager.RUTA_PRODUCTOS, "w", encoding="utf-8") as f:
            json.dump(dic_productos, f, indent=2, ensure_ascii=False)

    @staticmethod
    def obtener_categorias(dic_productos=None):
        if dic_productos is None:
            dic_productos = DataManager.cargar_productos()
        return list(dic_productos.keys())

    @staticmethod
    def obtener_sucursales(dic_productos=None):
        sucursales = []
        if os.path.exists(DataManager.RUTA_SUCURSALES):
            with open(DataManager.RUTA_SUCURSALES, "r", encoding="utf-8") as f:
                data = json.load(f)
                sucursales = sorted(list(data.keys()))
        else:
            # Fallback: obtener de productos
            if dic_productos is None:
                dic_productos = DataManager.cargar_productos()
            s = set()
            for categoria, productos in dic_productos.items():
                for p in productos.values():
                    for suc in p.get("stock_por_sucursal", {}).keys():
                        s.add(suc)
            sucursales = sorted(list(s))
        return sucursales

    @staticmethod
    def cargar_sucursales():
        if not os.path.exists(DataManager.RUTA_SUCURSALES):
            return {}
        with open(DataManager.RUTA_SUCURSALES, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def guardar_sucursales(dic_sucursales):
        with open(DataManager.RUTA_SUCURSALES, "w", encoding="utf-8") as f:
            json.dump(dic_sucursales, f, indent=2, ensure_ascii=False)

    @staticmethod
    def agregar_sucursal(nueva_sucursal, direccion="", telefono=""):
        # Agrega la sucursal en sucursales.json y la añade con stock 0 en productos existentes
        sucursales = DataManager.cargar_sucursales()
        if nueva_sucursal in sucursales:
            return False, "La sucursal ya existe."
        sucursales[nueva_sucursal] = {"direccion": direccion, "telefono": telefono}
        DataManager.guardar_sucursales(sucursales)

        productos = DataManager.cargar_productos()
        for categoria, lista in productos.items():
            for nombre, datos in lista.items():
                if "stock_por_sucursal" not in datos:
                    datos["stock_por_sucursal"] = {}
                if nueva_sucursal not in datos["stock_por_sucursal"]:
                    datos["stock_por_sucursal"][nueva_sucursal] = 0
        DataManager.guardar_productos(productos)
        return True, "Sucursal agregada."

    @staticmethod
    def editar_sucursal(nombre, direccion=None, telefono=None):
        sucursales = DataManager.cargar_sucursales()
        if nombre not in sucursales:
            return False, "Sucursal no encontrada."
        if direccion is not None:
            sucursales[nombre]["direccion"] = direccion
        if telefono is not None:
            sucursales[nombre]["telefono"] = telefono
        DataManager.guardar_sucursales(sucursales)
        return True, "Sucursal actualizada."

    @staticmethod
    def eliminar_sucursal(sucursal):
        # Elimina la sucursal de sucursales.json y de stock en productos
        sucursales = DataManager.cargar_sucursales()
        if sucursal in sucursales:
            del sucursales[sucursal]
            DataManager.guardar_sucursales(sucursales)
        productos = DataManager.cargar_productos()
        changed = False
        for categoria, lista in productos.items():
            for nombre, datos in lista.items():
                if "stock_por_sucursal" in datos and sucursal in datos["stock_por_sucursal"]:
                    del datos["stock_por_sucursal"][sucursal]
                    changed = True
        if changed:
            DataManager.guardar_productos(productos)
        return True

    @staticmethod
    def agregar_producto(categoria, nombre, precio, imagen_archivo, stock_por_sucursal, descripcion=""):
        productos = DataManager.cargar_productos()
        if categoria not in productos:
            productos[categoria] = {}
        # Validar si existe producto con el mismo nombre en esa categoría
        if nombre in productos[categoria]:
            return False, "El producto ya existe en esa categoría."
        productos[categoria][nombre] = {
            "id": str(uuid.uuid4()),
            "precio": float(precio),
            "imagen": imagen_archivo or "",
            "descripcion": descripcion or "",
            "stock_por_sucursal": stock_por_sucursal or {}
        }
        DataManager.guardar_productos(productos)
        return True, "Producto agregado."

    @staticmethod
    def eliminar_producto(categoria, nombre):
        productos = DataManager.cargar_productos()
        if categoria in productos and nombre in productos[categoria]:
            del productos[categoria][nombre]
            DataManager.guardar_productos(productos)
            return True
        return False

    @staticmethod
    def actualizar_stock(categoria, nombre, sucursal, nuevo_stock):
        productos = DataManager.cargar_productos()
        if categoria in productos and nombre in productos[categoria]:
            productos[categoria][nombre].setdefault("stock_por_sucursal", {})
            productos[categoria][nombre]["stock_por_sucursal"][sucursal] = int(nuevo_stock)
            DataManager.guardar_productos(productos)
            return True
        return False

    @staticmethod
    def reducir_stock_al_comprar(categoria, nombre, sucursal, cantidad):
        productos = DataManager.cargar_productos()
        if categoria in productos and nombre in productos[categoria]:
            actual = productos[categoria][nombre].get("stock_por_sucursal", {}).get(sucursal, 0)
            if cantidad > actual:
                return False, f"Stock insuficiente en {sucursal}. Disponible: {actual}"
            productos[categoria][nombre]["stock_por_sucursal"][sucursal] = actual - cantidad
            DataManager.guardar_productos(productos)
            return True, "Compra registrada."
        return False, "Producto no encontrado."

    # Métodos para ventas
    @staticmethod
    def registrar_venta(usuario, categoria, producto, cantidad, sucursal, metodo_pago, total):
        ventas = DataManager.cargar_ventas()
        if usuario not in ventas:
            ventas[usuario] = []
        registro = {
            "categoria": categoria,
            "producto": producto,
            "cantidad": int(cantidad),
            "sucursal": sucursal,
            "metodo_pago": metodo_pago,
            "total": float(total),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        ventas[usuario].append(registro)
        DataManager.guardar_ventas(ventas)
        return True

    @staticmethod
    def cargar_ventas():
        if not os.path.exists(DataManager.RUTA_VENTAS):
            return {}
        with open(DataManager.RUTA_VENTAS, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def guardar_ventas(dic_ventas):
        with open(DataManager.RUTA_VENTAS, "w", encoding="utf-8") as f:
            json.dump(dic_ventas, f, indent=2, ensure_ascii=False)

    @staticmethod
    def obtener_ventas_por_usuario(usuario):
        ventas = DataManager.cargar_ventas()
        return ventas.get(usuario, [])

