# vim: set ts=8 sw=8 sts=8 list nu:
import sys
import re
import os
import datetime
import configparser
import sqlite3

class Storage(object):
	"""The storage object controls all the pure database commands.
		All other information partaining to a spicific table or column
		are contained within there own respective object.
	"""
	#-------------------------------------------------------------------------------
	# General database connection actions
	#-------------------------------------------------------------------------------
	def __init__(self):
		# Process storage configuration options
		try:
			# Set the configuration section name
			section = 'storage'

			# Check if the config has the section we need
			if not config.has_section(section):
				# Add a storage section and the default values for it
				config.add_section(section)
				config.set(section, 'data', 'data.db')

			# Store the configuration variables locally
			self.data = config.get(section, 'data') if (config.has_option(section, 'data')) else 'data.db'

		# An exception was thown
		except configparser.Error:
			# Add an entry into the logs
			message = 'error processing configuration options'
			logger.queue.put({'type':'error', 'source':'storage', 'message':message})

			# Report the error to the console and exit
			print('Error starting storage controller system')
			sys.exit(1)

		# Configuration options set, check database exists
		else:
			# Create the database if it doesnt exist
			if not os.path.isfile(self.data):
				print('Create')

	def close(self):
		print('close')

	def close_cursor(self):
		print('close cursor')

	def get_datetime(self, s):
		dates = str(s)
		redate = re.compile("^([0-9]{4})[-/\.]?([0-9]{1,2})[-/\.]?([0-9]{1,2})")
		match = redate.search(dates)
		if not match: return None

		year = long(match.group(1))
		month = long(match.group(2))
		day = long(match.group(3))
		return datetime.datetime(year, month, day)

	#-------------------------------------------------------------------------------
	# User storage actions
	#-------------------------------------------------------------------------------
	def login(self, username='', password=''):
		""" This method handles a user logging into the system. Once the user is
			logged in, it generates a session key for the user and updates their
			last logged in time.
		"""

	#-------------------------------------------------------------------------------
	# User management (Add new user, fetch user information, ...)
	#-------------------------------------------------------------------------------

