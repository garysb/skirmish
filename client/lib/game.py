# Game control
import GameLogic
def quit(c):
	""" exit the game """
	print('client.game.quit')

	# Get the game_actuator and set the mode to quit. The enable the actuator
	g = c.actuators['set_game']
	g.mode = GameLogic.KX_GAME_QUIT
	c.activate(g)

def restart(c):
	""" Restart the game """
	print('client.game.restart')

	# Get the game_actuator and set the mode to restart. The enable the actuator
	g = c.actuators['set_game']
	g.mode = GameLogic.KX_GAME_RESTART
	c.activate(g)
