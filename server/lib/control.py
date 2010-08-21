#!/usr/bin/env python3
# vim: set ts=8 sw=8 sts=8 list nu:
import sys
import socket
import threading
import configparser
from lib.client import Client

class Control(threading.Thread):
	""" The control class/thread creates a socket server to handle our
		connections from a client system. The sockets interact with the other
		threads to execute commands on the system. To do this, it calls the
		global method list defined within our daemon to decide which thread has
		the method we are trying to call.
	"""
	dismiss = threading.Event()

	def __init__(self):
		""" Load the threading initiator, then setup some port information for
			the network server. By default, we listen on port 30405 for our
			socket connections.
		"""

		# Setup threading and load the dismisser
		threading.Thread.__init__(self, None)
		Control.dismiss.set()

		# Process control configuration options
		try:
			# Set the configuration section name
			section = 'control'

			# Check if the config has the section we need
			if not config.has_section(section):
				# Add a control section and the default values for it
				config.add_section(section)
				config.set(section, 'host', '')
				config.set(section, 'port', 30405)
				config.set(section, 'listen', 5)
				config.set(section, 'timeout', 1)

			# Store the configuration variables locally
			self.host = config.get(section, 'host') if (config.has_option(section, 'host')) else ''
			self.port = config.getint(section, 'port') if (config.has_option(section, 'port')) else 30405
			self.listen = config.getint(section, 'listen') if (config.has_option(section, 'listen')) else 5
			self.timeout = config.getint(section, 'timeout') if (config.has_option(section, 'timeout')) else 1

		# An exception was thown
		except configparser.Error:
			# Add an entry into the logs
			message = 'error processing configuration options'
			logger.queue.put({'type':'error', 'source':'control', 'message':message})

			# Report the error to the console and exit
			print('Error starting connection controller system')
			sys.exit(1)

	def run(self):
		""" The run method is called when we start the thread. We first bind
			the server to socket 30405, then we wait for a connection from a
			client and create a new thread to handle the connection.
		"""
		# Bind the server to our socket
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((self.host, self.port))
		server_socket.listen(self.listen)
		server_socket.settimeout(self.timeout)
		message = 'connection control started'
		logger.queue.put({'type':'notice', 'source':'control', 'message':message})

		# Wait for a connection to be established
		while Control.dismiss.isSet():
			try:
				# Wait for a connection from a client
				client_socket, address	= server_socket.accept()
				Client(client_socket, address, self.host)
				message = 'socket control started from '+address[0]
				logger.queue.put({'type':'notice', 'source':'control', 'message':message})
			except socket.timeout:
				pass

if __name__ == '__main__':
	# Run some unit tests to check we have a working socket server
	control = Control()
	control.start()
	control.join()
