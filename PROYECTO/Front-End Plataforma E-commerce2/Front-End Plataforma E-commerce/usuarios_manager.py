# usuarios_manager.py
import csv
import os

RUTA_USUARIOS = os.path.join("data", "usuarios.csv")

def asegurar_archivo_usuarios():
    #Crea una carpeta llamada data en el directorio actual 
    os.makedirs("data", exist_ok=True) #exist_ok=True significa que no dará error si la carpeta ya existe
    if not os.path.exists(RUTA_USUARIOS):
        # Crear archivo con un único administrador por defecto
        with open(RUTA_USUARIOS, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["usuario", "clave", "rol"])  # rol: "admin" o "cliente"
            writer.writerow(["admin", "admin", "admin"])
            writer.writerow(["cliente", "cliente", "cliente"])

def cargar_usuarios():
    asegurar_archivo_usuarios()
    usuarios = {}
    with open(RUTA_USUARIOS, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            usuarios[fila["usuario"]] = {
                "clave": fila["clave"],
                "rol": fila["rol"]
            }
    return usuarios

def guardar_usuarios(dic_usuarios):
    asegurar_archivo_usuarios()
    with open(RUTA_USUARIOS, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["usuario", "clave", "rol"])
        for usuario, info in dic_usuarios.items():
            writer.writerow([usuario, info["clave"], info["rol"]])

def crear_usuario_cliente(usuario, clave):
    """
    Crea un nuevo usuario con rol 'cliente' (nunca 'admin' desde registro).
    """
    usuarios = cargar_usuarios()
    if usuario in usuarios:
        return False, "El usuario ya existe."
    usuarios[usuario] = {"clave": clave, "rol": "cliente"}
    guardar_usuarios(usuarios)
    return True, "Usuario cliente creado correctamente."
