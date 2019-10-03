import socket
import threading 
import errno
import sys
import time
import random

HEADERSIZE = 10

IP_MASTER = socket.gethostname()
PUERTO = 5000
PUERTO_SLAVE1 = 5001
PUERTO_SLAVE2 = 5002
PUERTO_SLAVE3 = 5003


class threadClienteServidor (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		clienteServidor()
		print ("Exiting " + self.name)

class threadHeartbeat (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		heartbeat()
		print ("Exiting " + self.name)

def handshakeClient(socket):
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

		print(client_message)
		#f = open('log.txt', 'a')
		#f.write(f"'{client_message}' recibido de {client_address}\n")
		#f.close()

		msg = f"Bienvenido al server {client_address}, ya puedes enviar solicitudes..."
		msg = f"{len(msg):<{HEADERSIZE}}" + msg

		client_socket.send(bytes(msg, "utf-8"))

	return client_socket, client_address

def handshakeSlave(socket):
	flag = True
	while flag:
		client_socket, client_address = socket.accept()
		if client_socket:
			flag = False

		#print(f"Conexión con slave {client_address} establecida.")

		client_message_header = client_socket.recv(HEADERSIZE)
		if not len(client_message_header):
			print("Conexion perdida con el slave")
			sys.exit()
		client_message_length = int(client_message_header.decode('utf-8').strip())
		client_message = client_socket.recv(client_message_length).decode('utf-8')

		print(client_message)


		msg = f"Bienvenido al server {client_address}"
		msg = f"{len(msg):<{HEADERSIZE}}" + msg

		client_socket.send(bytes(msg, "utf-8"))

	return client_socket, client_address

def handshakeHeartbeat(socket):
	flag = True
	while flag:
		client_socket, client_address = socket.accept()
		if client_socket:
			flag = False
	return client_socket, client_address

def clienteServidor():
	########### Socket Servidor-Cliente ############
	masterSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	masterSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #para no bloquear el puerto
	
	###############################################

	########### Sockets Slaves ####################
	master_Slave1Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	master_Slave2Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	master_Slave3Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	master_Slave1Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #para no bloquear el puerto
	master_Slave2Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #para no bloquear el puerto
	master_Slave3Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #para no bloquear el puerto

	master_Slave1Socket.bind((IP_MASTER, PUERTO_SLAVE1))
	master_Slave2Socket.bind((IP_MASTER, PUERTO_SLAVE2))
	master_Slave3Socket.bind((IP_MASTER, PUERTO_SLAVE3))
	masterSocket.bind((IP_MASTER, PUERTO))
	
	master_Slave1Socket.listen()
	master_Slave2Socket.listen()
	master_Slave3Socket.listen()
	masterSocket.listen()
	##############################################
	
	slave1_socket, slave1_address = handshakeSlave(master_Slave1Socket)
	slave2_socket, slave2_address = handshakeSlave(master_Slave2Socket)
	slave3_socket, slave3_address = handshakeSlave(master_Slave3Socket)
	client_socket, client_address = handshakeClient(masterSocket)

	

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

				print(client_message)

				############# ENVIAR MENSAJE DEL CLIENTE AL SLAVE ##############################
				message = f"Mensaje: '{client_message}'".encode('utf-8')
				message_header = f"{len(message):<{HEADERSIZE}}".encode('utf-8')

				slaveElegido = random.randint(1, 3)

				if(slaveElegido == 1):
					slave1_socket.send(message_header + message)

					slave1_message_header = slave1_socket.recv(HEADERSIZE)
					slave1_message_length = int(slave1_message_header.decode('utf-8').strip())
					slave1_message = slave1_socket.recv(slave1_message_length).decode('utf-8')
					
					if(slave1_message == "Mensaje registrado exitosamente"):
						f = open('registro_server.txt', 'a')
						f.write(f"Slave 1 | Mensaje: '{client_message}'\n")
						f.close()

						cliente_slave_message = f"Slave 1 | Mensaje: '{client_message}'".encode('utf-8')
						cliente_slave_message_header = f"{len(cliente_slave_message):<{HEADERSIZE}}".encode('utf-8')
						client_socket.send(cliente_slave_message_header + cliente_slave_message)

				elif(slaveElegido == 2):
					slave2_socket.send(message_header + message)

					slave2_message_header = slave2_socket.recv(HEADERSIZE)
					slave2_message_length = int(slave2_message_header.decode('utf-8').strip())
					slave2_message = slave2_socket.recv(slave2_message_length).decode('utf-8')
					
					if(slave2_message == "Mensaje registrado exitosamente"):
						f = open('registro_server.txt', 'a')
						f.write(f"Slave 2 | Mensaje: '{client_message}'\n")
						f.close()

						cliente_slave_message = f"Slave 2 | Mensaje: '{client_message}'".encode('utf-8')
						cliente_slave_message_header = f"{len(cliente_slave_message):<{HEADERSIZE}}".encode('utf-8')
						client_socket.send(cliente_slave_message_header + cliente_slave_message)

				elif(slaveElegido == 3):
					slave3_socket.send(message_header + message)

					slave3_message_header = slave3_socket.recv(HEADERSIZE)
					slave3_message_length = int(slave3_message_header.decode('utf-8').strip())
					slave3_message = slave3_socket.recv(slave3_message_length).decode('utf-8')
					
					if(slave3_message == "Mensaje registrado exitosamente"):
						f = open('registro_server.txt', 'a')
						f.write(f"Slave 3 | Mensaje: '{client_message}'\n")
						f.close()

						cliente_slave_message = f"Slave 3 | Mensaje: '{client_message}'".encode('utf-8')
						cliente_slave_message_header = f"{len(cliente_slave_message):<{HEADERSIZE}}".encode('utf-8')
						client_socket.send(cliente_slave_message_header + cliente_slave_message)
				###################################################################

		except IOError as e:
			if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
				print('Reading error', str(e))
				sys.exit()
			continue

		except Exception as e:
			print('General error', str(e))
			pass


def heartbeat():
	DELAY = 5 #5 segundos

	heartbeat1Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	heartbeat2Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	heartbeat3Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	heartbeat1Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #para no bloquear el puerto
	heartbeat2Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #para no bloquear el puerto
	heartbeat3Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #para no bloquear el puerto

	heartbeat1Socket.bind((IP_MASTER, 5004))
	heartbeat2Socket.bind((IP_MASTER, 5005))
	heartbeat3Socket.bind((IP_MASTER, 5006))

	heartbeat1Socket.listen()
	heartbeat2Socket.listen()
	heartbeat3Socket.listen()

	slave1_heartbeat, slave1_heartbeat_address = handshakeHeartbeat(heartbeat1Socket)
	slave2_heartbeat, slave2_heartbeat_address = handshakeHeartbeat(heartbeat2Socket)
	slave3_heartbeat, slave3_heartbeat_address = handshakeHeartbeat(heartbeat3Socket)

	heartbeatMsg = "Hello"
	heartbeatMsg = f"{len(heartbeatMsg):<{HEADERSIZE}}" + heartbeatMsg

	while True:
		try:
			slave1_heartbeat.send(bytes(heartbeatMsg, "utf-8"))
			slave2_heartbeat.send(bytes(heartbeatMsg, "utf-8"))
			slave3_heartbeat.send(bytes(heartbeatMsg, "utf-8"))
		except IOError as e:
			if e.errno != errno.EAGAIN and   e.errno != errno.EWOULDBLOCK:
				print('Reading error', str(e))
				sys.exit()
			continue

		except Exception as e:
			print('General error', str(e))
			pass

		time.sleep(0.05) #para evitar bug, no alcanzaba a recibir mensaje del server cuando ya estaba pidiendo otra peticion
		try:
			f = open('heartbeat_server.txt', 'w')
			f.close()
			#Seccion de escucha, Recibir mensajes
			heartbeat1_message_header = slave1_heartbeat.recv(HEADERSIZE)
			if not len(heartbeat1_message_header):
				print("Conexion perdida con el slave 1")
				f = open('heartbeat_server.txt', 'a')
				f.write("Slave 1: Muerto\n")
				f.close()
			else:
				print("Slave 1 vivo")
				f = open('heartbeat_server.txt', 'a')
				f.write("Slave 1: Vivo\n")
				f.close()
				heartbeat1_message_length = int(heartbeat1_message_header.decode('utf-8').strip())
				heartbeat1_message = slave1_heartbeat.recv(heartbeat1_message_length).decode('utf-8')

			heartbeat2_message_header = slave2_heartbeat.recv(HEADERSIZE)
			if not len(heartbeat2_message_header):
				print("Conexion perdida con el slave 2")
				f = open('heartbeat_server.txt', 'a')
				f.write("Slave 2: Muerto\n")
				f.close()
			else:
				print("Slave 2 vivo")
				f = open('heartbeat_server.txt', 'a')
				f.write("Slave 2: Vivo\n")
				f.close()
				heartbeat2_message_length = int(heartbeat2_message_header.decode('utf-8').strip())
				heartbeat2_message = slave2_heartbeat.recv(heartbeat2_message_length).decode('utf-8')

			heartbeat3_message_header = slave3_heartbeat.recv(HEADERSIZE)
			if not len(heartbeat3_message_header):
				print("Conexion perdida con el slave 3")
				f = open('heartbeat_server.txt', 'a')
				f.write("Slave 3: Muerto\n")
				f.close()
			else:
				print("Slave 3 vivo")
				f = open('heartbeat_server.txt', 'a')
				f.write("Slave 3: Vivo\n")
				f.close()
				heartbeat3_message_length = int(heartbeat3_message_header.decode('utf-8').strip())
				heartbeat3_message = slave3_heartbeat.recv(heartbeat3_message_length).decode('utf-8')

		except IOError as e:
			if e.errno != errno.EAGAIN and   e.errno != errno.EWOULDBLOCK:
				print('Reading error', str(e))
				sys.exit()
			continue

		except Exception as e:
			print('General error', str(e))
			pass
		time.sleep(DELAY)





thread1 = threadClienteServidor(1, "Thread Cliente-Servidor", 1)
thread2 = threadHeartbeat(2, "Thread Heartbeat", 2)

thread1.start()
thread2.start()

