run-websocket:
	watchmedo auto-restart --patterns='*.py' --recursive ./websocket/src/main.py