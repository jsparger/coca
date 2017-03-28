import time

def start_archiver(manager):
	import archiver
	archiver.manager = manager
	interface = manager.get_interface()
	interface.set_archiver(manager.Archiver())
	while (True):
		time.sleep(1)