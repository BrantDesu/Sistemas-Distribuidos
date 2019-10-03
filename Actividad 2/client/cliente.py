import socket
import errno
import sys
import time

HEADERSIZE = 10

IP_MASTER = socket.gethostname()
PUERTO = 5000


def handshake(socket):
	client_message = "Hola servidor"
	client_message = client_message.encode('utf-8')
	client_message_header = f"{len(client_message):<{HEADERSIZE}}".encode('utf-8')
	socket.send(client_message_header + client_message)
	flag = True
	while flag:
		server_message_header = socket.recv(HEADERSIZE)
		if not len(server_message_header):
			print("Conexion perdida/cerrada por el servidor")
			sys.exit()
		server_message_length = int(server_message_header.decode('utf-8').strip())
		server_message = client_socket.recv(server_message_length).decode('utf-8')
		if server_message:
			print(server_message)
			#f = open('respuestas.txt', 'a')
			#f.write(f"Server: {server_message}\n")
			#f.close()
			flag = False
	return True


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP_MASTER, PUERTO))


handshake(client_socket)

client_socket.setblocking(False)

while True:

	client_message = input("Ingrese Petición: ")
	if client_message:
		client_message = client_message.encode('utf-8')
		client_message_header = f"{len(client_message):<{HEADERSIZE}}".encode('utf-8')
		client_socket.send(client_message_header + client_message)
	time.sleep(0.05) #para evitar bug, no alcanzaba a recibir mensaje del server cuando ya estaba pidiendo otra peticion
	try:
		while True:
			#Seccion de escucha, Recibir mensajes
			server_message_header = client_socket.recv(HEADERSIZE)
			if not len(server_message_header):
				print("Conexion perdida/cerrada por el servidor")
				sys.exit()
			server_message_length = int(server_message_header.decode('utf-8').strip())
			server_message = client_socket.recv(server_message_length).decode('utf-8')

			print(server_message)
			f = open('registro_cliente.txt', 'a')
			f.write(f"{server_message}\n")
			f.close()

	except IOError as e:
		if e.errno != errno.EAGAIN and   e.errno != errno.EWOULDBLOCK:
			print('Reading error', str(e))
			sys.exit()
		continue

	except Exception as e:
		print('General error', str(e))
		pass
