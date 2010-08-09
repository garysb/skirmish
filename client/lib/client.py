#!/usr/bin/env python3.1
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 nowrap:
import sys
import socket

# Add a new module path for our protocol
# FIXME: Need to remove void references
sys.path.append('../../../')
sys.path.append('../../')
sys.path.append('../')
from protocol import errors
from protocol import encryption

class Connection:
	""" Create a client connection with authentication.
	"""

	def __init__(self, host, port):
		"""
		Instantiate the connection object and create the connection to the server. Requires a hostname and a port
		"""
		self.host											= host
		self.port											= port
		self.sock											= None
		self.output											= None

		self.connect()

	def connect(self):
		"""
		Connect to a host. Don't try to reopen an already connected instance.
		"""

		# Ensure we dont already have an open socket
		if self.sock:
			return

		# Create the socket connection to the server
		for res in socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM):
			af, socktype, proto, canonname, sa				= res
			try:
				# Create the connection
				self.sock									= socket.socket(af, socktype, proto)
				self.sock.connect(sa)

				# Read and display the welcome message
				self.read()
				print(self.output)
				self.output									= {'api':'0x100','status':'0x00'}
			except socket.error:
				if self.sock:
					self.sock.close()
				self.sock									= None
				continue
			break

		# Make sure the connection is active
		if not self.sock:
			self.output										= {'api':'0x100','status':'0x02'}

	def __del__(self):
		"""Destructor -- close the connection."""
		self.close()

	def close(self):
		"""Close the connection."""
		if self.sock:
			self.sock.close()
		self.sock											= 0

	def send(self, data):
		""" When we send data to the server, we need to first calculate the size of the information
			we want to send. We then tack this into the first 32 bytes of information.

			The server must check this value to ensure that they fetch all the information from the
			clients buffer.
		"""
		self.sock.send(encryption.encrypt(data).encode())

	def read(self):
		""" Read information from the socket.
			Start by reading the first 32 bytes to get the message length. Once
			we have the length, we loop through the socket reads to fetch all
			the information and pushing it onto our output stack.
		"""

		# Fetch the packet size from the first 32 bytes of data.
		try:
			data_length										= int(self.sock.recv(32))
			self.output										= b''
		except ValueError:
			sys.exit(0)

		# Loop through sockets reads until we have all the data.
		while data_length >= 1:
			data											= self.sock.recv(8192)
			data_length										= data_length - int(data.__len__())
			self.output										= self.output + data

		self.output											= encryption.decrypt(self.output.decode())
