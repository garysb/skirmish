#!/usr/bin/env python3
# vim: set ts=8 sw=8 sts=8 list nu:

# Set the system path to include the parent directory
import sys
sys.path.append('..')

# Import the libraries we require to run the server
import ctypes
import builtins
from lib.stack import Stack
from lib.daemon import Daemon
from lib.logger import Logger
from lib.control import Control
from lib.storage import Storage
from optparse import OptionParser
from configparser import RawConfigParser

# If we are running this as a main thread, set name and parse cli options
if __name__ == "__main__":
	# Try set the name of the application so we can see it in ps
	if sys.platform == 'linux2':
		try:
			libc = ctypes.CDLL('libc.so.6')
			libc.prctl(15, 'skirmish', 0, 0, 0)
		except:
			pass

	# TODO: Migrate this to use argparse when ubuntu catches up in 3.1
	parser = OptionParser()

	# Add our command line options
	parser.add_option("-v", "--verbose",
		action="store_true", dest="verbose", default=False,
		help="display additional information [default]")

	parser.add_option("-d", "--daemon",
		action="store_true", dest="daemonize", default=False,
		help="Run in the background [default]")

	parser.add_option("-c", "--config",
		dest="config", default="skirmish.conf",
		metavar="FILE", help="load configuration from FILE")

	parser.add_option("-l", "--log",
		dest="log", default="skirmish.log",
		metavar="FILE", help="log actions to FILE")

	# Process the command line options
	(options, args) = parser.parse_args()

	# Check if the server should be run in daemon mode
	if options.daemonize:
		result = Daemon()

	# Process any configuration options
	builtins.config = RawConfigParser()
	config.read(options.config)

	# TODO: Overwrite the logfile option in the configuration

	# Start our logging system and add a message
	builtins.logger = Logger()
	logger.start()

	message = 'skirmish server started on a '+sys.platform+' system'
	logger.queue.put({'type':'notice','source':'system','message':message})

	# Create the stack manager
	builtins.stack = Stack()

	# Import our data storage and connect to the storage system
	builtins.storage = Storage()

	# Start our connection controller system
	control = Control()
	control.start()

	# Join our child threads to the main thread
	logger.join()
	control.join()
