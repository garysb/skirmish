# User module
import hashlib
import GameLogic
import client
from protocol import errors

def authenticate(c):
	""" Authenticate the user on the server. If there is an error, we set the
		flash in GameLogic.data['flash'] to the error message and restart the
		current scene. If success, we set the scene variable to the avatar scene
		to let the user choose or create their avatar.
	"""
	print('client.user.authenticate')
	# Link to the object
	o = c.owner

	# Import the username and password from the config file
	u = GameLogic.data['config'].get('user','username')
	p = hashlib.md5(('{0}'.format(GameLogic.data['config'].get('user','password'))).encode('utf-8')).hexdigest()

	# Try to create the connection to the server
	GameLogic.data['server'] = client.Connection('205.186.153.242', 30405)
	s = GameLogic.data['server']
	s.connect()
	if s.output['api'] == '0x100' and s.output['status'] == '0x02':
		# An error occured, report it to the user
		print('0x%X: %s\n' % (int(s.output['status'],16), errors.ERRORS[int(s.output['status'],16)]))
		o.sendMessage('status', errors.ERRORS[int(s.output['status'],16)])
		o.sendMessage('authenticated', '0')
		return

	# Send the username and password to the server and wait for a response
	s.send({'api':'0x100','username':u, 'password':p})
	s.read()

	if s.output['status'] != '0x00':
		# An error occured, report it to the user
		print('0x%X: %s\n' % (int(s.output['status'],16), errors.ERRORS[int(s.output['status'],16)]))
		o.sendMessage('status', errors.ERRORS[int(s.output,16)])
		o.sendMessage('authenticated', '0')
	else:
		# Go the the avatar scene
		o.sendMessage('authenticated', '1')

def disconnect(c):
	""" Disconnect the user from the server. This is called when the user tries
		to exit the game. It tidies up all the connection data and sends a QUIT
		signal.
	"""
	print('client.user.disconnect')
	GameLogic.data['server'].close()

def status(c):
	""" Depending on the status, we need to run diferent actions on this scene.
	"""
	print('client.user.status')

	# Link to the object and the scene selector
	o = c.owner
	s = c.actuators['set_scene']

	# Get the message sensor that triggered this
	m = c.sensors['message_sensor']

	# Decide what to do depending on the state
	for i in m.bodies:
		authenticated = i

	if int(authenticated):
		# Create the user dictionary and redirect to the avatar_select scene
		GameLogic.data['user'] = {}
		GameLogic.data['user']['authenticated'] = True
		s.scene = 'avatar_select'
	else:
		# Restart the login scene
		s.scene = 'login'
		s.useRestart = True

	c.activate(s)
