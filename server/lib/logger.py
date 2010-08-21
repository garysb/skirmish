#!/usr/bin/env python3
# vim: set ts=8 sw=8 sts=8 list nu:
import threading
import socket
import time
from queue import Queue
from queue import Empty as QueueEmpty

class Logger(threading.Thread):
	""" The Logger class/thread creates a socket server to handle our
		connections from a client system. The sockets interact with the other
		threads to execute commands on the system. To do this, it calls the
		global method list defined within our daemon to decide which thread has
		the method we are trying to call.
	"""
	# Create a dismisser and event locker (aka mutex)
	dismiss = threading.Event()
	client_list = []
	client_lock = threading.Lock()

	def __init__(self):
		# Initiate the threader and define the dismisser
		threading.Thread.__init__(self, None)
		Logger.dismiss.set()

		# Instantiate a module wide queue
		self.queue = Queue()

		# Logger configuration options
		try:
			# Set the configuration section name
			section = 'logger'

			# Check if the config has the section we need
			if not config.has_section(section):
				# Add a logger section and the default values for it
				config.add_section(section)
				config.set(section, 'host', 'localhost')
				config.set(section, 'port', 30406)
				config.set(section, 'listen', 5)
				config.set(section, 'timeout', 1)
				config.set(section, 'logfile', 'skirmish.log')

			# Store the configuration variables locally
			self.host = config.get(section, 'host') if (config.has_option(section, 'host')) else ''
			self.port = config.getint(section, 'port') if (config.has_option(section, 'port')) else 30406
			self.listen = config.getint(section, 'listen') if (config.has_option(section, 'listen')) else 5
			self.timeout = config.getint(section, 'timeout') if (config.has_option(section, 'timeout')) else 1
			self.logfile = config.get(section, 'logfile') if (config.has_option(section, 'logfile')) else 'skirmish.log'

		# An exception was thown
		except configparser.Error:
			# Add an entry into the logs
			message = 'error processing configuration options'
			self.queue.put({'type':'error','source':'logger','message':message})

			# Report the error to the console and exit
			print('Error starting logging system')
			sys.exit(1)

	def run(self):
		"""
		Create two different types of logging systems. The first type
		is a file logger that writes the log messages into a file
		specified in the configuration file or from the console.
		The second log type is a tcp socket that pushes log data
		to a tcp port.
		"""

		# Create our file log thread
		Logger.client_lock.acquire()
		file_client = handle_filelog(self.logfile)
		file_client.setName('fileThread')
		Logger.client_list.append(file_client)
		Logger.client_lock.release()
		file_client.start()

		# Report that the file logger has started
		message = 'file logging started'
		self.queue.put({'type':'notice', 'source':'logger', 'message':message})

		# Bind the logger tcp server to a socket
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((self.host, self.port))
		server_socket.listen(self.listen)
		server_socket.settimeout(self.timeout)

		# Wait for a tcp connection to be established
		while Logger.dismiss.isSet():
			try:
				msg = self.queue.get(block=False, timeout=False)
				for client in Logger.client_list:
					client.queue.put(msg)
			except QueueEmpty:
				pass

			try:
				# Wait for a connection from a client
				client_socket, address = server_socket.accept()
				Logger.client_lock.acquire()
				new_client = handle_connection(client_socket, address, self.host)
				Logger.client_list.append(new_client)
				Logger.client_lock.release()
				new_client.start()
				message = address[0]+' connected'
				self.queue.put({'type':'notice', 'source':'logger', 'message':message})
			except socket.timeout:
				pass

class handle_connection(threading.Thread):
	""" When a client connects to the tcp logger, start a new thread to
		handle the connection. The thread polls the log queue for any
		new values.
	"""

	def __init__(self, client_socket, address, host):
		threading.Thread.__init__(self, None)
		self.queue = Queue()
		self.client_socket = client_socket
		self.client_socket.settimeout(0.5)
		self.address = address
		self.host = host

	def run(self):
		# Send the connection welcome message to the client
		self.client_socket.send(self.set_welcome())

		# While a connection is active, loop through the log queue
		while True:

			# Try generate the output message and send it to the client
			try:
				raw = self.queue.get(True, 0.5)
				msg = '[{0}] [{1}] [{2}] {3}\n'.format(time.asctime(), raw['source'], raw['type'], raw['message'])
				self.client_socket.send(msg)

			# No new items in the queue, just continue
			except QueueEmpty:
				continue

			# An error raised due to no raw variable set
			except NameError:
				continue

		# Shutdown the client tcp connection
		self.client_socket.shutdown(2)
		self.client_socket.close()
		Logger.client_lock.acquire()
		Logger.client_list.remove(self)
		Logger.client_lock.release()

		# Report that the client has disconnected
		message = self.address[0]+' disconnected'
		logger.queue.put({'type':'notice', 'source':'logger', 'message':message})

	def set_welcome(self):
		welcome = '220 {0} Skirmish logs; {1}\n'.format(self.bind_addr, time.asctime())
		return welcome

class handle_filelog(threading.Thread):
	""" The handle_file_log object/thread generates a filesystem log that adds
		its queue messages into the filesystem.
	"""
	queue = Queue()

	def __init__(self, logfile='skirmish.log'):
		threading.Thread.__init__(self, None)
		self.logfile = logfile

	def run(self):
		while True:
			try:
				# Fetch the message from the queue
				raw = self.queue.get(True, 0.5)
				msg = '[{0}] [{1}] [{2}] {3}\n'.format(time.asctime(), raw['source'], raw['type'], raw['message'])

				# Write the new message to the log file
				log_file = open(self.logfile,'a')
				log_file.write(msg)
				log_file.close()

			except QueueEmpty:
				continue

			except NameError:
				continue

if __name__ == '__main__':
	# Run some unit tests to check we have a working socket server
	logger = Logger()
	logger.start()

	# Add some random test messages to the queue
	time.sleep(3)
	logger.queue.put({'type':'notice','source':'logger','message':'Unit test 1'})
	time.sleep(0.5)
	logger.queue.put({'type':'error','source':'logger','message':'Unit test 2'})
	logger.queue.put({'type':'notice','source':'logger','message':'Unit test 3'})
	time.sleep(2)
	logger.queue.put({'type':'warning','source':'logger','message':'Unit test 4'})
	logger.queue.put({'type':'notice','source':'logger','message':'Unit test 5'})
	time.sleep(0.1)
	logger.queue.put({'type':'warning','source':'logger','message':'Unit test 6'})
	time.sleep(0.1)
	logger.queue.put({'type':'notice','source':'logger','message':'Unit test 7'})
	time.sleep(2)
	logger.queue.put({'type':'error','source':'logger','message':'Unit test 8'})
	time.sleep(1)
	logger.queue.put({'type':'notice','source':'logger','message':'Unit test 9'})
	logger.queue.put({'type':'notice','source':'logger','message':'Unit test 10'})

	logger.join()
