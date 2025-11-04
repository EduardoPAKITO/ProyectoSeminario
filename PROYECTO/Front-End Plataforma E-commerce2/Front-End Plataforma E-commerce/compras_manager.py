# compras_manager.py
import json
import os
from datetime import datetime

RUTA_COMPRAS = os.path.join("data", "compras.json")

def asegurar_archivo_compras():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(RUTA_COMPRAS):
        with open(RUTA_COMPRAS, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)

def registrar_compra(usuario, categoria, producto, cantidad, sucursal, metodo_pago, total):
    asegurar_archivo_compras()
    with open(RUTA_COMPRAS, "r", encoding="utf-8") as f:
        datos = json.load(f)
    if usuario not in datos:
        datos[usuario] = []
    registro = {
        "categoria": categoria,
        "producto": producto,
        "cantidad": int(cantidad),
        "sucursal": sucursal,
        "metodo_pago": metodo_pago,
        "total": float(total),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    datos[usuario].append(registro)
    with open(RUTA_COMPRAS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    return True

def obtener_compras_por_usuario(usuario):
    asegurar_archivo_compras()
    with open(RUTA_COMPRAS, "r", encoding="utf-8") as f:
        datos = json.load(f)
    return datos.get(usuario, [])
