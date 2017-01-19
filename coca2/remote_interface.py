from multiprocessing import Process
import threading
import Queue
from manager import Manager, get_manager
from run_epics_server import run
from proxy import reduce

# A synchronized queue to hold new pvs.
new_pv_queue = Queue.Queue()

# A class which allows the coca clients to talk to the IOC
class CocaInterface(object):
	def __init__(self):
		self.pvs = {}
		self.events = {}
		self.lock = threading.Lock()
		# self.launch_epics_server()

	def launch_epics_server(self):
		self.manager = get_manager(Manager)
		self.interface = self.manager.get_interface()
		p = Process(target=run, args=(self.interface,self.manager)); p.daemon=True; p.start()
		self.epics_process = p

	def __getstate__(self):
		censored = dict(self.__dict__)
		censored.pop("lock",None)
		censored.pop("interface",None)
		censored.pop("manager",None)
		censored.pop("epics_process",None)
		censored.pop("events",None)
		censored.pop("pvs",None)
		return censored

	def broadcast_pv(self, pv):
		if pv.name in self.pvs:
			return False
		with self.lock:
			self.pvs[pv.name] = pv
			new_pv_queue.put(pv)
		return True

	def get_pv(self, name):
		if name not in self.pvs:
			return False
		return self.pvs[name]

	def get_pv_dict(self):
		return self.pvs

	def read(self, name):
		# with self.lock:
		self.events[name]['read_request'].set()
		try:
			self.events[name]['read_complete'].wait(timeout=1.0)
			self.events[name]['read_complete'].clear()
		except RuntimeError as e:
			pass
			# self.disconnect()
		return self.get_value(name)

	def write(self, name, value):
		# with self.lock:
		self.pvs[name].value = value
		self.events[name]['write_request'].set()
		try:
			self.events[name]['write_complete'].wait(timeout=1.0)
			self.events[name]['write_complete'].clear()
		except RuntimeError as e:
			pass

	def get_value(self, name):
		return self.pvs[name].value

	def create_pv_events(self,name):
		events = {}
		actions = {'read_request','read_complete','write_request','write_complete','push_request','push_complete','disconnect_notify'}
		self.events[name] = {key:threading.Event() for key in actions}

	def set_event(self, name, action):
		self.events[name][action].set()

	def wait_event(self, name, action, timeout=None):
		self.events[name][action].wait(timeout)

	def clear_event(self, name, action):
		self.events[name][action].clear()


interface = None

# Manager.register("Interface", CocaInterface)

def get_interface():
	global interface
	if not interface:
		interface = CocaInterface()
		interface.__reduce__ = reduce
	return interface

Manager.register("get_interface", get_interface)
Manager.register("get_new_pv_queue", lambda: new_pv_queue)
manager = get_manager(Manager)
interface = manager.get_interface()
interface.launch_epics_server()