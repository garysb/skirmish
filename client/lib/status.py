# User status actions
import Rasterizer
import time

# Change the users status
def display(c):
	""" When the client first starts, this method initialises all of the needed
		modules we need, then initialises the client by loading the login scene.
	"""
	print('client.status.display')
	# Link to our object
	o = c.owner

	# Get the message status sensor to retrieve the message body
	m = c.sensors['status_sensor']

	for i in m.bodies:
		o['Text'] = i

	# Set the new position of the text
	o.worldPosition = [-(o['Text'].__len__()/4)+0.5,0,0]
	o.visible = True

	# After the duration, hide the status message
	i = c.actuators['set_ipo']
	i.frameStart = 1
	i.frameEnd = 120
	c.activate(i)
	#o.visible = False
