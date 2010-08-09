# Game initialization (store values)
import GameLogic

# Load the config parser (try except to support python v2 and v3)
try:
	import ConfigParser as configparser
except:
	import configparser as configparser

def load():
	""" Try load the config file. If we cant load it, create the file and store
		our default values. No information relating to the avatars are stored,
		only default username, system settings, and default avatar information.
	"""
	print('client.config.load')
	config = configparser.RawConfigParser()
	config.read('defaults.cfg')

	# Make sure we had a config file. If not, build the default one
	if not config.has_section('user'):
		# Create our sections
		config.add_section('user')
		config.add_section('display')

		# Create our default user values
		config.set('user','username','guest@example.tld')
		config.set('user','password','')

		# Create our default display settings
		config.set('display','opengl','on')
		config.set('display','width','800')
		config.set('display','height','600')

		# Load all the values into their respective dictionaries
		GameLogic.data = {}
		GameLogic.data['config'] = config
		save()
	else:
		# Load all the values into their respective dictionaries
		GameLogic.data = {}
		GameLogic.data['config'] = config

def save():
	""" Save our config option back to the file. This is done whenever we make
		a change to one of these variables.
	"""
	print('client.config.save')
	# Get the configuration options to be saved
	try:
		config = GameLogic.data['config']
		# Writing our configuration file to 'defaults.cfg'
		with open('defaults.cfg', 'w') as configfile:
			config.write(configfile)
	except:
		pass
