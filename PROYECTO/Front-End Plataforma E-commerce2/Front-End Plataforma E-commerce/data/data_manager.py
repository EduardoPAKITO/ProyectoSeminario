import json
import csv
import os
import uuid
from datetime import datetime

class DataManager:
    # Rutas CORREGIDAS - relativas al directorio del proyecto
    """""
    Atributos de Clase:
        BASE_DIR (str): Directorio raíz del proyecto
        DATA_DIR (str): Directorio de archivos de datos
        RUTA_USUARIOS (str): Ruta al archivo CSV de usuarios
        RUTA_PRODUCTOS (str): Ruta al archivo JSON de productos
        RUTA_VENTAS (str): Ruta al archivo JSON de ventas
        CARPETA_IMAGENES (str): Ruta a la carpeta de imágenes
    """""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio raíz del proyecto
    DATA_DIR = os.path.join(BASE_DIR, "data")
    RUTA_USUARIOS = os.path.join(DATA_DIR, "usuarios.csv")
    RUTA_PRODUCTOS = os.path.join(DATA_DIR, "productos.json")
    RUTA_VENTAS = os.path.join(DATA_DIR, "ventas.json")
    CARPETA_IMAGENES = os.path.join(BASE_DIR, "images")

    @staticmethod
    def asegurar_archivos():
        """Asegura que todos los archivos y carpetas necesarios existan"""
        os.makedirs(DataManager.DATA_DIR, exist_ok=True)
        os.makedirs(DataManager.CARPETA_IMAGENES, exist_ok=True)
        DataManager._asegurar_archivo_usuarios()
        DataManager._asegurar_productos_iniciales()
        DataManager._asegurar_archivo_ventas()

    @staticmethod
    def _asegurar_archivo_usuarios():
        if not os.path.exists(DataManager.RUTA_USUARIOS):
            with open(DataManager.RUTA_USUARIOS, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["usuario", "clave", "rol"])
                writer.writerow(["admin", "admin", "admin"])
                writer.writerow(["cliente", "cliente", "cliente"])

    @staticmethod
    def _asegurar_productos_iniciales():
        if not os.path.exists(DataManager.RUTA_PRODUCTOS):
            ejemplo = {
                "Celulares": {
                    "Teléfono Modelo A": {
                        "id": str(uuid.uuid4()),
                        "precio": 699.90,
                        "imagen": "ejemplo_telefono.jpg",
                        "stock_por_sucursal": {"Sucursal Centro": 4, "Sucursal Norte": 2}
                    }
                },
                "Accesorios": {
                    "Funda Protectora": {
                        "id": str(uuid.uuid4()),
                        "precio": 19.90,
                        "imagen": "ejemplo_funda.jpg",
                        "stock_por_sucursal": {"Sucursal Centro": 30, "Sucursal Sur": 20}
                    },
                    "Cargador Rápido 30W": {
                        "id": str(uuid.uuid4()),
                        "precio": 29.50,
                        "imagen": "ejemplo_cargador.jpg",
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

    # Métodos para usuarios
    @staticmethod
    def cargar_usuarios():
        usuarios = {}
        with open(DataManager.RUTA_USUARIOS, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for fila in reader:
                usuarios[fila["usuario"]] = {
                    "clave": fila["clave"],
                    "rol": fila["rol"]
                }
        return usuarios

    @staticmethod
    def guardar_usuarios(dic_usuarios):
        with open(DataManager.RUTA_USUARIOS, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["usuario", "clave", "rol"])
            for usuario, info in dic_usuarios.items():
                writer.writerow([usuario, info["clave"], info["rol"]])

    @staticmethod
    def crear_usuario_cliente(usuario, clave):
        usuarios = DataManager.cargar_usuarios()
        if usuario in usuarios:
            return False, "El usuario ya existe."
        usuarios[usuario] = {"clave": clave, "rol": "cliente"}
        DataManager.guardar_usuarios(usuarios)
        return True, "Usuario cliente creado correctamente."

    # Métodos para productos
    @staticmethod
    def cargar_productos():
        with open(DataManager.RUTA_PRODUCTOS, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def guardar_productos(dic_productos):
        with open(DataManager.RUTA_PRODUCTOS, "w", encoding="utf-8") as f:
            json.dump(dic_productos, f, indent=2, ensure_ascii=False)

    @staticmethod
    def obtener_sucursales(dic_productos=None):
        if dic_productos is None:
            dic_productos = DataManager.cargar_productos()
        sucursales = set()
        for categoria, productos in dic_productos.items():
            for p in productos.values():
                for s in p.get("stock_por_sucursal", {}).keys():
                    sucursales.add(s)
        return sorted(list(sucursales))

    @staticmethod
    def agregar_sucursal(nueva_sucursal):
        productos = DataManager.cargar_productos()
        for categoria, lista in productos.items():
            for nombre, datos in lista.items():
                if "stock_por_sucursal" not in datos:
                    datos["stock_por_sucursal"] = {}
                if nueva_sucursal not in datos["stock_por_sucursal"]:
                    datos["stock_por_sucursal"][nueva_sucursal] = 0
        DataManager.guardar_productos(productos)

    @staticmethod
    def eliminar_sucursal(sucursal):
        productos = DataManager.cargar_productos()
        for categoria, lista in productos.items():
            for nombre, datos in lista.items():
                if "stock_por_sucursal" in datos and sucursal in datos["stock_por_sucursal"]:
                    del datos["stock_por_sucursal"][sucursal]
        DataManager.guardar_productos(productos)

    @staticmethod
    def agregar_producto(categoria, nombre, precio, imagen_archivo, stock_por_sucursal):
        productos = DataManager.cargar_productos()
        if categoria not in productos:
            productos[categoria] = {}
        productos[categoria][nombre] = {
            "id": str(uuid.uuid4()),
            "precio": float(precio),
            "imagen": imagen_archivo or "",
            "stock_por_sucursal": stock_por_sucursal or {}
        }
        DataManager.guardar_productos(productos)

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
            return True, "Compra registrada y stock actualizado."
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