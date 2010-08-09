# Change scene to our connecting scene
def change(c):
	""" When the client first starts, this method initialises all of the needed
		modules we need, then initialises the client by loading the login scene.
	"""
	print('client.scene.change')
	# Link to our object
	o = c.owner

	# Enable the actuator
	s = c.actuators['set_scene']
	s.scene = o.get('scene')
	c.activate(s)

def overlay(c):
	""" Overlay a scene over our current scene.
	"""
	print('client.scene.overlay')
	# Link to our object
	o = c.owner

	# Enable the actuator
	s = c.actuators['set_overlay']
	s.scene = o.get('overlay')
	c.activate(s)

def restart(c):
	""" Restart the current scene.
	"""
	print('client.scene.restart')
	# Link to the object
	o = c.owner

	# Enable the actuator
	s = c.actuators['set_scene']
	s.scene = o.get('scene')
	s.useRestart = True
	c.activate(s)
