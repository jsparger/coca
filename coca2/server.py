from remote_pv import RemotePV
from proxy import StableEventProxy, StableLockProxy
import multiprocessing
import threading
import Queue
from multiprocessing.managers import SyncManager
import socket

# A synchronized queue to hold new pvs.
new_pv_queue = Queue.Queue()

# A class which allows the coca clients to talk to the IOC
class CocaInterface(object):
	def __init__(self):
		self.pvs = {}
		self.lock = threading.Lock()

	def __getstate__(self):
		censored = dict(self.__dict__)
		censored.pop("lock",None)
		return censored

	def broadcast_pv(self, pv):
		if pv.name in self.pvs:
			return False
		with self.lock:
			self.pvs[pv.name] = pv
			new_pv_queue.put(pv)
		return True

	def get_pv(name):
		if name not in self.pvs:
			return False
		return self.pvs[name]

	def read(self, name):
		# danger
		return self.pvs[name].read()

	def write(self, name, value):
		# danger
		self.pvs[name].write()

interface = CocaInterface()

coca_address = ('localhost',5050)

def get_manager(klass):
	manager = klass(('localhost',5050))
	try:
		# check to see if there is a server running already
		s = socket.socket()
		s.bind(coca_address)
		s.close()
	except socket.error as e:
		# server already running, so just connect
		manager.connect()
	else:
		# server not running, so start
		manager.start()

	return manager

class Manager(SyncManager):
	pass

Manager.register("StableEvent", threading.Event, StableEventProxy)
Manager.register("StableLock", threading.Lock, StableLockProxy)
Manager.register("RemotePV", RemotePV)
Manager.register("get_interface", lambda: interface)
Manager.register("get_new_pv_queue", lambda: new_pv_queue)

manager = get_manager(Manager)

