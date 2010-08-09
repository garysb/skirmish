#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 nowrap:
import Queue as queue
from lib import loggers

class Stack(dict):
	def __init__(self):
		""" When the stack is initialised, report this to the logger """
		loggers.log_queue.put({'type':'notice','source':'stack','message':"Initialised stack controller"})

	def __missing__(self, k):
		""" When we try access a missing item in the stack, report the problem
			to the logger, then raise a KeyError.
		"""
		loggers.log_queue.put({'type':'warning','source':'stack','message':"Missing stack queue %s" % k})
		self.create(k)

	def create(self, key):
		""" Create a stack type to be used. This creates a dictionary entry on
			the top most level with the key defined by 'key'. Once created, the
			stack will be used to store multiple entries, one for each type of
			item we define. eg. user, avatar, scene, ...
		"""
		loggers.log_queue.put({'type':'notice','source':'stack','message':"Creating stack queue %s" % key})
		if key not in self:
			self[key] = {}

	def destroy(self, key):
		""" This destroys a stack type. To do this, we first make sure that the
			stack is empty by checking the stack count. If not empty, we raise
			an exception to get reported to the client.
		"""
		loggers.log_queue.put({'type':'notice','source':'stack','message':"Destroying stack queue %s" % key})
		if key in self:
			# FIXME: Need to check if its empty first
			self.__delitem__(key)

	def add(self, key, identity, maximum=100):
		""" Add a new item to the system. This creates a new priority queue for
			that item to read off. Note that we dont create stacks to be used
			as output stacks, only input stacks.
		"""
		loggers.log_queue.put({'type':'notice','source':'stack','message':"Adding stack queue %s to %s" % (identity,key)})
		self[key].__setitem__(str(identity),queue.PriorityQueue(maximum))

	def remove(self, key, identity):
		""" Remove an item from the stack. This happens when a client closes a
			connection to the server, or changes their avatar.
		"""
		loggers.log_queue.put({'type':'notice','source':'stack','message':"Removing stack queue %s from %s" % (identity,key)})
		self[key].__delitem__(str(identity))

stack = Stack()
