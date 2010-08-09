#!/usr/bin/env python26
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 nowrap:

import sys

# Set the system path to include the parent directory
sys.path.append('../')

import ctypes
from lib import loggers
from lib import controller

def usage():
	print('Usage: ./server [OPTION]...')
	print('Start the skirmish server\n')
	print('Options are any combination of the following:')
	print('-c, --config=FILE\t\t(NOT IMPLEMENTED)Use the configuration file specified')
	print('-d, --daemon\t\t\tRun the database in daemon mode')
	print('-h, --help\t\t\tDisplay this help page')

# If we are running this as a main thread, recreate as a daemon
if __name__ == "__main__":
	# Try set the name of the application so we can see it in ps
	if sys.platform == 'linux2':
		try:
			libc											= ctypes.CDLL('libc.so.6')
			libc.prctl(15, 'skirmish', 0, 0, 0)
		except:
			pass

	# Setup option parsing
	import getopt
	try:
		short_opts											= 'hdc:'
		long_opts											= ['help', 'daemon','config=']
		opts, args											= getopt.getopt(sys.argv[1:], short_opts, long_opts)
	except getopt.GetoptError:
		# print help information and exit:
		usage()
		sys.exit(2)

	# FIXME: Should be using a lambda function map
	for opt in opts:
		if '-h' in opt[0] or '--help' in opt[0]:
			usage()
			sys.exit(0)

	# FIXME: Should be using a lambda function map
	for opt in opts:
		if '-d' in opt[0] or '--daemon' in opt[0]:
			from lib import daemon
			ret_val											= daemon.set_daemon()
			break

	# Start our logging system
	logger													= loggers.run_logger()
	loggers.log_queue.put({'type':'notice','source':'system','message':'Skirmish Server started on a '+sys.platform+' system'})
	logger.start()

	# Start our storage system up
	from lib import storage

	# Start our controller system
	control													= controller.Controller()
	control.start()

	# Join our child threads to the main thread
	logger.join()
	control.join()
