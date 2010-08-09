# Initialize the login scene
import Rasterizer

def enable(c):
	""" Enable the mouse pointer and at the same time sets the mouse to the our
		center of the screen. Does not require any properties.
	"""
	print('client.mouse.enable')
	# Set the mouse to the default position
	try:
		Rasterizer.setMousePosition(Rasterizer.getWindowWidth()/2, Rasterizer.getWindowHeight()/2)
	except:
		pass

	# Enable the mouse
	Rasterizer.showMouse(True)

def disable(c):
	""" Disable the mouse pointer by hiding the pointer. Does not require any of
		the properties.
	"""
	print('client.mouse.disable')
	Rasterizer.showMouse(False)

def reset(c):
	""" Connect to all the mouse sensors and try reset them. """
	print('client.mouse.reset')

	# Only reset the left sensor for now
	c.sensors['mouse_left'].reset()

def set(c):
	""" Sets the mouse position using the Rasterizer library. Requires that the
		calling object has the properties: mouse_x and mouse_y set to enable the
		position setting.
	"""
	print('client.mouse.set')

	# Make sure the mouse_x and mouse_y properties are set and are int's
	o = c.owner
	try:
		# Get the coordinates
		mouse_x = o.get('mouse_x')
		mouse_y = o.get('mouse_y')

		# Set the pointer to these coords
		Rasterizer.setMousePosition(mouse_x,mouse_y)
	except:
		return
