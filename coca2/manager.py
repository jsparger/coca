from multiprocessing.managers import SyncManager
from remote_pv import RemotePV
from proxy import StableEventProxy, StableLockProxy
import threading
import socket

coca_address = ('localhost',5050)

def get_manager(klass):
	manager = klass(coca_address)
	try:
		# check to see if there is a server running already
		s = socket.create_connection(coca_address, timeout=3)
		s.close()
	except socket.error as e:
		# server not running, so start
		manager.start()
	else:
		# server already running, so just connect
		manager.connect()

	return manager

class Manager(SyncManager):
	pass

Manager.register("StableEvent", threading.Event, StableEventProxy)
Manager.register("StableLock", threading.Lock, StableLockProxy)
Manager.register("RemotePV", RemotePV)