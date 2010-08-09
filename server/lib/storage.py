#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 nowrap:
import sys
import re
import datetime
import MySQLdb
from lib import loggers

class Database(object):
	"""The database object controls all the pure database commands.
		All other information partaining to a spicific table or column
		are contained within there own respective object.
	"""
	#-------------------------------------------------------------------------------
	# General database connection actions
	#-------------------------------------------------------------------------------
	def __init__(self):
		try:
			self.conn = MySQLdb.connect (host = 'localhost',
										user = 'skirmish',
										passwd = 'CHANGEME',
										db = 'skirmish',
										client_flag = 131072|65536)
		except MySQLdb.Error, e:
			loggers.log_queue.put({'type':'error','source':'storage','message':"%d: %s" % (e.args[0], e.args[1])})
			sys.exit(1)

		loggers.log_queue.put({'type':'notice','source':'storage','message':"MySQL version %s" % self.version()})

	def version(self):
		self.cursor = self.conn.cursor()
		self.cursor.execute("SELECT VERSION()")
		row = self.cursor.fetchone()
		return row[0]

	def close(self):
		self.conn.close()

	def close_cursor(self):
		self.cursor.close()

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
		query						= """SELECT * FROM `Users` WHERE
											`Users`.`u_password`='%s'
											AND `Users`.`u_username`='%s'
											LIMIT 1;""" % (password, username)

		self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
		self.cursor.execute(query)
		result_set = self.cursor.fetchall()
		return result_set[0]

	def search(self, num=0, txt="", company="", location=""):
		# Search through our database and return the results
		query                       = "SELECT * FROM contacts"
		if len(company) > 0:
			query                   += " WHERE c_company LIKE '%%%s%%'" % company
		query                       += " LIMIT %s, 10" % num
		self.cursor = self.conn.cursor (MySQLdb.cursors.DictCursor)
		self.cursor.execute (query)
		result_set = self.cursor.fetchall ()
		return result_set

	def totalRowCount(self, txt="", company="", location=""):
		# Search through our database and return the results
		query                       = "SELECT * FROM contacts"
		if len(company) > 0:
			query                   += " WHERE c_company LIKE '%%%s%%'" % company
		self.cursor = self.conn.cursor (MySQLdb.cursors.DictCursor)
		self.cursor.execute (query)
		return self.cursor.rowcount

	def rowCount(self):
		return self.cursor.rowcount

	#-------------------------------------------------------------------------------
	# User management (Add new user, fetch user information, ...)
	#-------------------------------------------------------------------------------
	def subscribe(self, username, password1, password2, company, category, url, forname, surname, phone, enum, sip, description):
		# Check user detail was entered corectly
		# Add user to the database
		self.cursor = self.conn.cursor ()
		insert_user                 = "INSERT INTO users (u_name, u_passwd)\
									VALUES ('%s', '%s')" % (username, password1)
		self.cursor.execute (insert_user)
		user_id                     = self.conn.insert_id()
		# Add contact to the database
		insert_contact              = "INSERT INTO contacts\
									(c_company, c_enum, c_sip, c_phone, c_forname, c_surname, c_url, c_description)\
									VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" % (company,enum,sip,phone,forname,surname,url,description)
		self.cursor.execute (insert_contact)
		contact_id                  = self.conn.insert_id()
		# Link the contact to the user
		contact_user                = "INSERT INTO propagation\
										(parent_table, parent_id, child_table, child_id)\
										VALUES ('users','%s','contacts','%s')" % (user_id, contact_id)
		self.cursor.execute (contact_user)
		# Link the contact to the category
		tags_contacts                   = "INSERT INTO propagation\
										(parent_table, parent_id, child_table, child_id)\
										VALUES ('tags','%s','contacts','%s')" % (category, contact_id)
		self.cursor.execute (tags_contacts)

db = Database()
