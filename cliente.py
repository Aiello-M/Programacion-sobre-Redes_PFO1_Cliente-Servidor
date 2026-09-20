import socket


# Configurar parámetros del servidor
HOST = "localhost"
PORT = 5000


# Configurar y conectar el socket TCP/IP
def conectar_servidor():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORT))
    return cliente


# Gestionar el intercambio de mensajes con el servidor
def gestionar_mensajes(cliente):
    print(f"Conectado al servidor {HOST}:{PORT}")
    print("Escribí 'éxito' para finalizar la sesión.\n")

    while True:
        mensaje = input("Mensaje: ")

        # Finalizar la sesión si el usuario escribe "éxito"
        if mensaje.strip().lower() == "éxito":
            print("Conexión finalizada.")
            break

        # Evitar el envío de mensajes vacíos
        if not mensaje.strip():
            print("El mensaje no puede estar vacío.")
            continue

        # Enviar el mensaje codificado al servidor
        cliente.sendall(mensaje.encode("utf-8"))

        # Recibir la respuesta del servidor
        datos_respuesta = cliente.recv(1024)

        # Validar si el servidor cerró la conexión
        if not datos_respuesta:
            print("El servidor cerró la conexión.")
            break

        respuesta = datos_respuesta.decode("utf-8")
        print(f"Servidor: {respuesta}\n")


# Ejecutar y coordinar el cliente
def ejecutar_cliente():
    try:
        # Cerrar automáticamente el socket al finalizar
        with conectar_servidor() as cliente:
            gestionar_mensajes(cliente)

    except ConnectionRefusedError:
        # Manejar error si el servidor no está disponible
        print("No se pudo conectar al servidor.")
        print("Verificá que servidor.py esté ejecutándose.")

    except OSError as error:
        # Manejar otros errores de red
        print(f"Error de red: {error}")


if __name__ == "__main__":
    ejecutar_cliente()