#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 nowrap:
import os
import sys
import socket
import threading
import ConfigParser
from lib import loggers
from lib import client

class Controller(threading.Thread):
	""" The create_listerner class/thread creates a socket server to handle our
		connections from a client system. The sockets interact with the other
		threads to execute commands on the system. To do this, it calls the
		global method list defined within our daemon to decide which thread has
		the method we are trying to call.
	"""
	dismiss													= threading.Event()

	def __init__(self):
		""" Load the threading initiator, then setup some port information for
			the network server. By default, we listen on port 30405 for our
			socket connections.
		"""
		threading.Thread.__init__(self, None)
		Controller.dismiss.set()

		# Parse our configuration options
		config												= ConfigParser.ConfigParser()
		config.read(['skirmish.conf', os.path.expanduser('~/.skirmish.conf')])

		# Socket server setup
		try:
			# Fetch the port we need to listen on
			if config.has_option('global', 'port'):
				self.port									= int(config.get('global','port'))
			else:
				self.port									= 30405

			# Fetch the hostname to bind to
			if config.has_option('global', 'host'):
				self.bind_addr								= config.get('global','host')
			else:
				self.bind_addr								= ''

			# Socket server setup
			self.listen										= 5
			self.timeout									= 1
		except:
			loggers.log_queue.put({'type':'error','source':'control','message':'Error starting server'})
			print('Error starting connection controller system')
			sys.exit(1)

	def run(self):
		""" The run method is called when we start the thread. We first bind
			the server to socket 30405, then we wait for a connection from a
			client and create a new thread to handle the connection.
		"""
		# Bind the server to our socket
		server_socket										= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((self.bind_addr, self.port))
		server_socket.listen(self.listen)
		server_socket.settimeout(self.timeout)
		loggers.log_queue.put({'type':'notice','source':'control','message':'Connection controller started'})
		# Wait for a connection to be established
		while Controller.dismiss.isSet():
			try:
				# Wait for a connection from a client
				client_socket, address						= server_socket.accept()
				client.Client(client_socket, address, self.bind_addr)
				loggers.log_queue.put({'type':'notice','source':'control','message':'Socket control started from '+address[0]})
			except socket.timeout:
				pass

if __name__ == '__main__':
	# Run some unit tests to check we have a working socket server
	control													= Controller()
	control.start()
	control.join()
