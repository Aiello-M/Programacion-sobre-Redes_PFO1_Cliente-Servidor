import socket
import sqlite3
from datetime import datetime


# Configurar parámetros de servidor y BD
HOST = "localhost"
PORT = 5000
DB_NAME = "chat.db"


# Inicializar la BD SQLite
def inicializar_bd():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    # Crear la tabla de mensajes si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contenido TEXT NOT NULL,
            fecha_envio TEXT NOT NULL,
            ip_cliente TEXT NOT NULL
        )
    """)

    conexion.commit()
    return conexion


# Configurar el socket TCP/IP
def inicializar_socket():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))  # Vincular el socket al host y puerto
    servidor.listen(1)  # Escuchar conexiones entrantes
    return servidor


# Guardar mensaje recibido 
def guardar_mensaje(conexion_bd, contenido, fecha_envio, ip_cliente):
    cursor = conexion_bd.cursor()

    # Insertar el mensaje en la BD
    cursor.execute("""
        INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
        VALUES (?, ?, ?)
    """, (contenido, fecha_envio, ip_cliente))

    conexion_bd.commit()


# Atender mensajes de un cliente conectado
def atender_cliente(conexion, direccion, conexion_bd):
    ip_cliente = direccion[0]

    with conexion:
        while True:
            # Recibir datos enviados por el cliente
            datos = conexion.recv(1024)

            # Si no hay datos, el cliente cerró la conexión
            if not datos:
                break  

            contenido = datos.decode("utf-8")
            fecha_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"Mensaje recibido de {ip_cliente}: {contenido}")

            try:
                # Guardar el mensaje en la BD
                guardar_mensaje(conexion_bd, contenido, fecha_envio, ip_cliente)
                respuesta = f"Mensaje recibido: {fecha_envio}"

            except sqlite3.Error as error:
                # Manejar error al guardar el mensaje
                print(f"Error al guardar el mensaje: {error}")
                respuesta = "Error al guardar el mensaje"

            # Enviar la respuesta al cliente
            conexion.sendall(respuesta.encode("utf-8"))

    print(f"Cliente {ip_cliente} desconectado.")


# Aceptar conexiones de clientes
def aceptar_conexiones(servidor, conexion_bd):
    while True:
        conexion, direccion = servidor.accept()
        print(f"Conexión aceptada desde {direccion}")

        atender_cliente(conexion, direccion, conexion_bd)


# Ejecutar y coordinar el servidor
def ejecutar_servidor():
    try:
        conexion_bd = inicializar_bd()

    except sqlite3.Error as error:
        # Manejar error si BD no es accesible
        print(f"Error al acceder a la base de datos: {error}")
        return

    try:
        servidor = inicializar_socket()

    except OSError as error:
        # Manejar errores de inicialización (ej. si el puerto está ocupado)
        print(f"Error al inicializar el socket: {error}")
        conexion_bd.close()
        return

    print(f"Servidor escuchando en {HOST}:{PORT}...")

    try:
        with servidor:
            aceptar_conexiones(servidor, conexion_bd)

    finally:
        # Cerrar conexión con BD al finalizar el servidor
        conexion_bd.close()


if __name__ == "__main__":
    ejecutar_servidor()


