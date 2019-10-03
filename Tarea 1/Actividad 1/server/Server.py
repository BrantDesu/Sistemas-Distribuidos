import socket
import errno
import sys

HEADERSIZE = 10

IP = socket.gethostname()
PUERTO = 5000

def handshake(socket):

	flag = True
	while flag:
		client_socket, client_address = socket.accept()
		if client_socket:
			flag = False

		print(f"Conexión con {client_address} establecida.")

		client_message_header = client_socket.recv(HEADERSIZE)
		if not len(client_message_header):
			print("Conexion perdida con el cliente")
			sys.exit()
		client_message_length = int(client_message_header.decode('utf-8').strip())
		client_message = client_socket.recv(client_message_length).decode('utf-8')

		#print(client_message)
		f = open('log.txt', 'a')
		f.write(f"'{client_message}' recibido de {client_address}\n")
		f.close()

		msg = f"Bienvenido al server {client_address}, ya puedes enviar solicitudes..."
		msg = f"{len(msg):<{HEADERSIZE}}" + msg

		client_socket.send(bytes(msg, "utf-8"))
	return client_socket, client_address


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #para no bloquear el puerto

server_socket.bind((IP, PUERTO))
server_socket.listen()



client_socket, client_address = handshake(server_socket)

while True:

	try:
		while True:
			# Seccion de escucha, Recibir mensajes
			client_message_header = client_socket.recv(HEADERSIZE)
			if not len(client_message_header):
				print("Conexion perdida con el cliente")
				sys.exit()
			client_message_length = int(client_message_header.decode('utf-8').strip())
			client_message = client_socket.recv(client_message_length).decode('utf-8')

			#print(client_message)
			f = open('log.txt', 'a')
			f.write(f"'{client_message}' recibido de {client_address}\n")
			f.close()

			message = f"Solicitud: '{client_message}' recibida".encode('utf-8')
			message_header = f"{len(message):<{HEADERSIZE}}".encode('utf-8')
			client_socket.send(message_header + message)


	except IOError as e:
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print('Reading error', str(e))
			sys.exit()
		continue

	except Exception as e:
		print('General error', str(e))
		pass

