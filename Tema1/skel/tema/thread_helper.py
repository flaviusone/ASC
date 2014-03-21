import sys
import random
from threading import Event,Thread, current_thread, Lock, Semaphore, Condition
from time import sleep
from barrier import ReusableBarrierSem

class Listner(Thread):
	def __init__(self, node_id, matrix_size, datastore, nodes, thread_list):
		Thread.__init__(self, name = str(node_id))
		self.node_id = node_id
		self.matrix_size = matrix_size
		self.datastore = datastore
		self.nodes = nodes
		self.thread_list = thread_list
		self.self_node = self.nodes[self.node_id]
		self.destination_node = None
		self.element = None
		self.event_listner = Event()
		self.semafor = Semaphore(value = 1)
		self.exit = 0

	def run(self):
		while(True):
			# Astept sa primesc o cerere de la alt nod
			print "Waiting"
			self.event_listner.wait()
			if self.exit==1:
				break
			# Scot element din datastore si il trimit
			payload = self.datastore.get_A(self.self_node,self.element)
			self.destination_node.thread.payload_bay = payload
			# Notific nodul destinatie ca am trimis
			self.destination_node.thread.event_listner.set()
			# Clear si reiau bucla
			self.event_listner.clear();
			# Deblochez semafor
			self.semafor.release()
			print "Boom\n"


	def set(self,destination_node,element):
		self.semafor.acquire()
		self.destination_node = destination_node
		self.element = element
		self.event_listner.set()
		print "Sunt %s si am primit cerere pentru elementul %d de la %s\n" % (self.node_id, element,str(destination_node))


class Master(Thread):
	def __init__(self, node_id, matrix_size, datastore, nodes,thread_list):
		Thread.__init__(self, name = str(node_id))
		self.node_id = node_id
		self.matrix_size = matrix_size
		self.datastore = datastore
		self.nodes = nodes
		self.thread_list = thread_list
		self.self_node = self.nodes[self.node_id]
		self.listner_thread = self.thread_list[0]
		self.event_listner = Event()

		# Aici imi pun elemente de alte noduri
		self.payload_bay = None

		random.seed(0)

		#########################
		# Creez o bariera locala
		if self.node_id == 0:
			# initializez bariera
			self.barrier = ReusableBarrierSem(self.matrix_size)
		else:
			# setez bariera comuna
			self.barrier = self.nodes[0].thread.barrier
		#########################

		#########################
		# in valor_pivot primesc date de la celalalte noduri
		# in incomming_buffer primesc de la alt nod un rand intreg
		# in outgoing_buffer creez pachetul pe care il trimit la alt nod
		self.valori_pivot = []
		self.incomming_buffer = []
		self.outgoing_buffer = []
		# Initializez cu 0
		for i in range(self.matrix_size):
			self.valori_pivot.append(0)
			self.incomming_buffer.append(0)
			self.outgoing_buffer.append(0)
		#########################

	def run(self):
		# main for loop
		for j in range(self.matrix_size):
			rp = self.find_pivot(j)
			self.swap_rows(rp,j)
			if self.node_id > j:
				# Cerun element
				print "Inainte de set"
				self.nodes[0].listner.set(self.self_node,0)

				# Astept sa il primesc
				self.event_listner.wait()
				self.event_listner.clear()
				print "Am primit de la cine am cerut\n"
			# 	for i in range(j+1,self.matrix_size):
			# 		element = self.datastore.get_A(self.self_node,i)
			# 		element -= self.datastore
			# 		self.datastore.put_A(self.self_node,i,element)
			# 	self.datastore.put_A(self.self_node,j,0)

	def swap_rows(self,rp,j):
		"""
			Row j swapps with row rp
		"""
		if self.node_id == j:
			# Creez buffer pt trimitere
			for i in range(self.matrix_size):
				self.outgoing_buffer[i] = self.datastore.get_A(self.self_node,i)
			#Trimit
			self.nodes[rp].thread.incomming_buffer = self.outgoing_buffer

		if self.node_id == rp:
			# Creez buffer pt trimitere
			for i in range(self.matrix_size):
				self.outgoing_buffer[i] = self.datastore.get_A(self.self_node,i)
			# Trimit
			self.nodes[j].thread.incomming_buffer = self.outgoing_buffer

		self.barrier.wait()

		# Updatez linia
		if self.node_id == j:
			for i in range(self.matrix_size):
				self.datastore.put_A(self.self_node,i,self.incomming_buffer[i])

		if self.node_id == rp:
			for i in range(self.matrix_size):
				self.datastore.put_A(self.self_node,i,self.incomming_buffer[i])

		self.barrier.wait()
		return True

	def find_pivot(self,row):
		"""
			Finds pivot
			@type row: Integer
			@param row: randul pe care se cauta elementul de pe pozitia row

			@return: index-ul rowului care are pivotul
		"""
		index = -1

		if self.node_id != row:
			# Trimit element de pe coloana row la nodul row
			self.send_data_pivot(self.nodes[row],self.datastore.get_A(self.self_node,row))

		# Astept sa primesc toate elementele de la celelalte noduri
		self.barrier.wait()

		if self.node_id == row:
			# Pun si valoarea mea in vector
			self.valori_pivot[self.node_id] = self.datastore.get_A(self.self_node,row)

			# Compute local max
			maxim = -1
			index = -1
			for k in range(len(self.valori_pivot)):
				if abs(self.valori_pivot[k]) > maxim:
					maxim = self.valori_pivot[k]
					index = k
			if maxim == 0:
				print "Maxim 0 matrice nesingulara"
			print "Am calculat maxim %d pe row %d" % (maxim,index)
			# print maxim

		return index


	def send_data_pivot(self,destination_node,data):
		destination_node.thread.valori_pivot[self.node_id] = data
		# .append((data,self.node_id))










# class Slave(Thread):
# 	def __init__(self, stuff):
# 		Thread.__init__(self, name = "Slave")

# 	def run(self):
# 		print "Doing nothing"


