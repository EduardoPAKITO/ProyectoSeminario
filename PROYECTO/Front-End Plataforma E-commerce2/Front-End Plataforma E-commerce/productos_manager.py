# productos_manager.py
import json
import os
import uuid #Sirve para generar identificadores únicos universales

RUTA_PRODUCTOS = os.path.join("data", "productos.json")
CARPETA_IMAGENES = "images"

def asegurar_productos_iniciales():
    #Crea una carpeta llamada data en el directorio actual 
    os.makedirs("data", exist_ok=True) #exist_ok=True significa que no dará error si la carpeta ya existe
    os.makedirs(CARPETA_IMAGENES, exist_ok=True) 
    if not os.path.exists(RUTA_PRODUCTOS):
        # Estructura: categorías -> productos -> datos (precio, imagen, stock_por_sucursal)
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
        with open(RUTA_PRODUCTOS, "w", encoding="utf-8") as f:
            json.dump(ejemplo, f, indent=2, ensure_ascii=False) 
            #indent=2 Añade sangrías de 2 espacios para que el archivo JSON sea fácil de leer (formateado)
            #ensure_ascii=False Permite que se guarden correctamente los caracteres especiales (como tildes, ñ, emojis, etc.)

def cargar_productos():
    asegurar_productos_iniciales()
    with open(RUTA_PRODUCTOS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_productos(dic_productos):
    asegurar_productos_iniciales()
    with open(RUTA_PRODUCTOS, "w", encoding="utf-8") as f:
        json.dump(dic_productos, f, indent=2, ensure_ascii=False)

def obtener_sucursales(dic_productos):
    """
    Devuelve la lista única de sucursales encontradas en todos los productos.
    """
    sucursales = set()
    for categoria, productos in dic_productos.items():
        for p in productos.values():
            for s in p.get("stock_por_sucursal", {}).keys():
                sucursales.add(s)
    return sorted(list(sucursales))

def agregar_sucursal(nueva_sucursal):
    """
    Agrega una sucursal a todos los productos con stock 0 por defecto.
    """
    productos = cargar_productos()
    for categoria, lista in productos.items():
        for nombre, datos in lista.items():
            if "stock_por_sucursal" not in datos:
                datos["stock_por_sucursal"] = {}
            if nueva_sucursal not in datos["stock_por_sucursal"]:
                datos["stock_por_sucursal"][nueva_sucursal] = 0
    guardar_productos(productos)

def eliminar_sucursal(sucursal):
    productos = cargar_productos()
    for categoria, lista in productos.items():
        for nombre, datos in lista.items():
            if "stock_por_sucursal" in datos and sucursal in datos["stock_por_sucursal"]:
                del datos["stock_por_sucursal"][sucursal]
    guardar_productos(productos)

def agregar_producto(categoria, nombre, precio, imagen_archivo, stock_por_sucursal):
    productos = cargar_productos()
    if categoria not in productos:
        productos[categoria] = {}
    productos[categoria][nombre] = {
        "id": str(uuid.uuid4()),
        "precio": float(precio),
        "imagen": imagen_archivo or "",
        "stock_por_sucursal": stock_por_sucursal or {}
    }
    guardar_productos(productos)

def eliminar_producto(categoria, nombre):
    productos = cargar_productos()
    if categoria in productos and nombre in productos[categoria]:
        del productos[categoria][nombre]
        guardar_productos(productos)
        return True
    return False

def actualizar_stock(categoria, nombre, sucursal, nuevo_stock):
    productos = cargar_productos()
    if categoria in productos and nombre in productos[categoria]:
        productos[categoria][nombre].setdefault("stock_por_sucursal", {})
        productos[categoria][nombre]["stock_por_sucursal"][sucursal] = int(nuevo_stock)
        guardar_productos(productos)
        return True
    return False

def reducir_stock_al_comprar(categoria, nombre, sucursal, cantidad):
    productos = cargar_productos()
    if categoria in productos and nombre in productos[categoria]:
        actual = productos[categoria][nombre].get("stock_por_sucursal", {}).get(sucursal, 0)
        if cantidad > actual:
            return False, f"Stock insuficiente en {sucursal}. Disponible: {actual}"
        productos[categoria][nombre]["stock_por_sucursal"][sucursal] = actual - cantidad
        guardar_productos(productos)
        return True, "Compra registrada y stock actualizado."
    return False, "Producto no encontrado."
