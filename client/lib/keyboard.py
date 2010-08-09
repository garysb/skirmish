# Control the login pages keyboard
import GameKeys

max_length = 10

cont = GameLogic.getCurrentController()
own = cont.owner

# Process the key presses and run actions on them
keySensor = cont.sensors["keyboard"]
keys = keySensor.events
for key in keys:
	keycode=key[0]

    if key[1] == GameLogic.KX_INPUT_ACTIVE: