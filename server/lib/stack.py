#!/usr/bin/env python
# vim: set ts=8 sw=8 sts=8 list nu:

# Import the PriorityQueue
from queue import PriorityQueue

class Stack(dict):
	def __init__(self):
		""" When the stack is initialised, report this to the logger """
		message = 'initialized stack controller'
		logger.queue.put({'type':'notice', 'source':'stack', 'message':message})

	def __missing__(self, k):
		""" When we try access a missing item in the stack, report the problem
			to the logger, then raise a KeyError.
		"""
		message = 'missing stack queue {0}'.format(k)
		logger.queue.put({'type':'warning', 'source':'stack', 'message':message})
		self.create(k)

	def create(self, key):
		""" Create a stack type to be used. This creates a dictionary entry on
			the top most level with the key defined by 'key'. Once created, the
			stack will be used to store multiple entries, one for each type of
			item we define. eg. user, avatar, scene, ...
		"""
		message = 'creating stack queue {0}'.format(key)
		logger.queue.put({'type':'notice', 'source':'stack', 'message':message})
		if key not in self:
			self[key] = {}

	def destroy(self, key):
		""" This destroys a stack type. To do this, we first make sure that the
			stack is empty by checking the stack count. If not empty, we raise
			an exception to get reported to the client.
		"""
		message = 'destroying stack queue {0}'.format(key)
		logger.queue.put({'type':'notice', 'source':'stack', 'message':message})
		if key in self:
			# FIXME: Need to check if its empty first
			self.__delitem__(key)

	def add(self, key, identity, maximum=100):
		""" Add a new item to the system. This creates a new priority queue for
			that item to read off. Note that we dont create stacks to be used
			as output stacks, only input stacks.
		"""
		message = 'adding stack {0} to {1}'.format(identity, key)
		logger.queue.put({'type':'notice', 'source':'stack', 'message':message})
		self[key].__setitem__(str(identity), PriorityQueue(maximum))

	def remove(self, key, identity):
		""" Remove an item from the stack. This happens when a client closes a
			connection to the server, or changes their avatar.
		"""
		message = 'removing stack queue {0} from {1}'.format(identity, key)
		logger.queue.put({'type':'notice', 'source':'stack', 'message':message})
		self[key].__delitem__(str(identity))

