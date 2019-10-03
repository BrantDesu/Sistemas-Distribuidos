import socket
import errno
import sys
import time
import threading 

HEADERSIZE = 10

IP_MASTER = socket.gethostname()
PUERTO = 5002
PUERTO_HEARTBEAT = 5005

class threadMasterSlave (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		print ("Starting " + self.name)
		masterSlave()
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

def handshake(socket):
	slave_message = "Slave 2 reportandose"
	slave_message = slave_message.encode('utf-8')
	slave_message_header = f"{len(slave_message):<{HEADERSIZE}}".encode('utf-8')
	socket.send(slave_message_header + slave_message)
	flag = True
	while flag:
		master_message_header = socket.recv(HEADERSIZE)
		if not len(master_message_header):
			print("Conexion perdida/cerrada por el servidor")
			sys.exit()
		master_message_length = int(master_message_header.decode('utf-8').strip())
		master_message = socket.recv(master_message_length).decode('utf-8')
		if master_message:
			print(master_message)
			#f = open('respuestas.txt', 'a')
			#f.write(f"Server: {server_message}\n")
			#f.close()
			flag = False
	return True


def masterSlave():
	slave_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	slave_socket.connect((IP_MASTER, PUERTO))


	handshake(slave_socket)

	slave_socket.setblocking(False)

	while True:
		try:
			while True:
				#Seccion de escucha, Recibir mensajes
				master_message_header = slave_socket.recv(HEADERSIZE)
				if not len(master_message_header):
					print("Conexion perdida/cerrada por el servidor")
					sys.exit()
				master_message_length = int(master_message_header.decode('utf-8').strip())
				master_message = slave_socket.recv(master_message_length).decode('utf-8')

				print(master_message)
				f = open('data.txt', 'a')
				f.write(f"{master_message}\n")
				f.close()

				messageConfirmacionRegistro = "Mensaje registrado exitosamente".encode('utf-8')
				messageConfirmacionRegistro_header = f"{len(messageConfirmacionRegistro):<{HEADERSIZE}}".encode('utf-8')

				slave_socket.send(messageConfirmacionRegistro_header + messageConfirmacionRegistro)

		except IOError as e:
			if e.errno != errno.EAGAIN and   e.errno != errno.EWOULDBLOCK:
				print('Reading error', str(e))
				sys.exit()
			continue

		except Exception as e:
			print('General error', str(e))
			pass

def heartbeat():
	heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	heartbeat_socket.connect((IP_MASTER, PUERTO_HEARTBEAT))
	heartbeat_socket.setblocking(False)

	while True:
		try:
			while True:
				# Seccion de escucha, Recibir mensajes
				heartbeat_message_header = heartbeat_socket.recv(HEADERSIZE)
				if not len(heartbeat_message_header):
					print("Conexion perdida con el master")
					sys.exit()
				heartbeat_message_length = int(heartbeat_message_header.decode('utf-8').strip())
				heartbeat_message = heartbeat_socket.recv(heartbeat_message_length).decode('utf-8')


				heartbeat_message2 = "Hello".encode('utf-8')
				heartbeat_message2_header = f"{len(heartbeat_message2):<{HEADERSIZE}}".encode('utf-8')

				heartbeat_socket.send(heartbeat_message2_header + heartbeat_message2)

		except IOError as e:
			if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
				print('Reading error', str(e))
				sys.exit()
			continue

		except Exception as e:
			print('General error', str(e))
			pass

thread1 = threadMasterSlave(1, "Thread Master-Slave", 1)
thread2 = threadHeartbeat(2, "Thread Heartbeat", 2)

thread1.start()
thread2.start()