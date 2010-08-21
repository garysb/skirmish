# vim: set ts=8 sw=8 sts=8 list nu:

# Import required modules
import sys
import time
import protocol
import threading
import queue
from lib.user import User

class Client(threading.Thread):
	""" For  each client connection, we create a thread to handle any commands.
		Note that the client socket is closed internally.
	"""
	def __init__(self, socket, address, bind):
		threading.Thread.__init__(self, None)
		self.socket				= socket
		self.address				= address
		self.bind				= bind
		self.version				= '1.00'
		self.block				= False
		self.wait				= 1
		self.more				= True

		# Object types
		self.user				= None

		# Start running the thread
		self.start()

	def run(self):
		""" The run method is called once threading starts. It begins by making
			a stack queue to read any data created by external libraries that
			needs to send data to clients. Then it adds the message telling the
			client they need to authenticate before they can continue. Only when
			the user has authenticated, the system runs into the read/write loop
			and finally closes the connection to the client and cleans up.
		"""

		# Add the client to the queueing stack
		stack.add('clients',self.ident)

		try:
			message = 'client thread {0} started'.format(self.ident)
			logger.queue.put({'type':'notice', 'source':'client', 'message':message})
		except ZeroDivisionError:
			pass
		else:
			#self.user			= user.User(self.ident)

			# Begin our main loop
			self.process()
		finally:
			# The client has disconnected, shut down the socket and close the thread
			self.socket.shutdown(2)
			self.socket.close()
			stack.remove('clients',self.ident)
			message = 'socket control quit from {0}'.format(self.address[0])
			logger.queue.put({'type':'notice', 'source':'client', 'message':message})
			return

	def put(self, data):
		""" When we send data to the client, we need to first calculate the size of the information
			we want to send. We then tack this into the first 32 bytes of information.
			
			The client must check this value to ensure that they fetch all the information from the
			servers buffer.
		"""
		message = 'send: {0}'.format(data)
		logger.queue.put({'type':'notice', 'source':'control', 'message':message})
		self.socket.send(protocol.encryption.encrypt(data))

	def get(self):
		""" Read information from the socket.
			Start by reading the first 32 bytes to get the message length. Once
			we have the length, we loop through the socket reads to fetch all
			the information and push it onto our output stack.
		"""

		# Fetch the packet size from the first 32 bytes of data.
		data_length				= int(self.socket.recv(32))
		output					= ''

		# Loop through sockets reads until we have all the data.
		while data_length >= 1:
			data				= self.socket.recv(8192)
			data_length			= data_length - int(data.__len__())
			output				= output + data

		# return the data to the calling method
		message = 'read: {0}'.format(output)
		logger.queue.put({'type':'notice', 'source':'control', 'message':message})
		return protocol.encryption.decrypt(output)

	def process(self, data):
		""" The process method starts by reading in any information the client is
			sending and stores it on the incomming queue. It then checks the
			outgoing queue for this connection to see if the server has any info
			to send to the client. If so, it sends it and waits for another call.
		"""
		while self.more:
			# Read any data we can from the client
			try:
				data			= self.get()
			except:
				continue
			else:
				if data['type'] == '0x000':
					# Local data handler for information and actions for the server
					self.respond(data)
					#elif data['type'] == '0x100':
					# User control actions
					#stack['users'][self.user.ident].put(5,data)
				else:
					# Protocol error
					stack['clients'][self.ident].put(1,{'api':'0x000','status':'0x001'})

			# Check if there is a packet to be sent to the client
			try:
				data			= stack['clients'][self.ident].get(self.block,self.wait)
			except queue.Empty:
				data			= {'type':'0x000','action':'0x00','status':'0x000'}
			finally:
				self.put(data)
				self.block		= False
				self.wait		= 1

	def respond(self,data):
		""" The respond method is for actions targeted at the handler itself. It
			is used to send server information, close the connection, and respond
			to ping rate requests.
		"""
		if data['action'] == '0x00':
			# Empty packet sent to request next data block
			pass
		elif data['action'] == '0x20':
			# Get server information (ip address, protocol, version, time)
			stack['clients'][self.ident].put(5,{'type':'0x000','action':'0x20','status':'0x000','version':self.version,'address':self.bind,'time':time.asctime()})
		elif data['action'] == '0x30':
			# Close the connection to the client and quit the thread
			self.more			= False
		elif data['action'] == '0x40':
			# Respond to the client with the ping packet
			stack['clients'][self.ident].put(1,{'type':'0x000','status':'0x000','action':'0x40','hash':data['hash']})
		else:
			# Protocol error
			stack['clients'][self.ident].put(1,{'type':'0x000','status':'0x001'})
