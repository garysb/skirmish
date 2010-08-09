#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 nowrap:
import sys
sys.path.append('../')
import time
import datetime
import threading
import Queue as queue
from lib.stack import stack
from lib import storage
from lib import loggers

class User(threading.Thread):
	""" The user object is used to keep track of user connection information.
		It is placed in the global user dictionary and holds queues to send and
		receive data from the client connections.
	"""

	# Object data generated, set, or passed in from parent
	db														= None
	block													= False
	wait													= 1
	more													= True
	client_ident											= None
	authenticated											= False

	# User data retrieved from the database
	u_id													= None
	username												= None
	password												= None
	forename												= None
	surname													= None
	expired													= False
	disabled												= False
	banned													= False

	def __init__(self, client_ident):
		""" Initialise the object by creating a new thread. We also store the
			parent objects ident value to allow us to add messages to the queue
			used to send data to the client.
		"""
		threading.Thread.__init__(self, None)
		self.client_ident									= client_ident
		self.start()

	def run(self):
		""" The run method is called when the thread starts. It begins by adding
			a local connection to the database to enable us to lookup user data.
			Then we create our input queue that all information is passed into
			so we can prioritise messages. Then we run our main queue loop to
			process data we recieve in the queue.
		"""
		loggers.log_queue.put({'type':'notice','source':'user','message':'User thread %s started' % str(self.ident)})
		self.db												= storage.db
		stack.add('users',self.ident)

		# Run our main loop to process messages in the message queue
		while self.more:
			# Check if there is a packet to process
			try:
				data										= stack['users'][self.ident].get(self.block,self.wait)
			except queue.Empty:
				pass
			else:
				self.process(data)
			finally:
				# Reset our queue parser to its default values
				self.block									= False
				self.wait									= 1

		# When the run loop is broken, clean up any queues and data we have
		stack.remove('users',self.ident)

	def process(self, data):
		""" Once we recieve a queue entry try decide what we do with it by reading
			the API and TYPE values in the data packet.
		"""
		if data['action'] == '0x40':
			self.authenticate(data)
		else:
			# Protocol error
			stack['clients'][self.client_ident].put(1,{'type':'0x000','status':'0x001'})

	def authenticate(self, data):
		# Authenticate the user
		try:
			# Get the results from the database and store them in the user object
			result											= self.db.login(data['username'], data['password'])

			# Sort out the expiry date to check if the user has expired
			expires											= self.db.get_datetime(result['u_expiry'])
			now												= datetime.datetime.now()
		except:
			self.authenticated								= False
		else:
			self.u_id										= result['u_id']
			self.username									= result['u_username']
			self.password									= result['u_password']
			self.forename									= result['u_forename']
			self.surname									= result['u_surname']
			self.disabled									= result['u_disabled']
			self.banned										= result['u_banned']
			self.expired									= True if now < expires else False
			self.authenticated								= True
		finally:
			# Check we have a valid user
			if not self.authenticated:
				stack['clients'][self.client_ident].put(1,{'type':'0x100','action':'0x40','status':'0x140'})

			# Check the user hasnt expired
			if self.expired:
				stack['clients'][self.client_ident].put(1,{'type':'0x100','action':'0x40','status':'0x141'})

			# Check the users isnt disabled
			if self.disabled:
				stack['clients'][self.client_ident].put(1,{'type':'0x100','action':'0x40','status':'0x142'})

			# Check the user isnt banned
			if self.banned:
				stack['clients'][self.client_ident].put(1,{'type':'0x100','action':'0x40','status':'0x143'})
