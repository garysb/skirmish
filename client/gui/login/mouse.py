# Initialize the login scene
import Rasterizer

def enable(c):
	""" Enable the mouse pointer """
	print('client.mouse.enable')
	Rasterizer.showMouse(True)

def disable(c):
	""" Disable the mouse pointer """
	print('client.mouse.disable')
	Rasterizer.showMouse(False)
