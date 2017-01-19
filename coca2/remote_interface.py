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
		self.lock = threading.Lock()
		# self.launch_epics_server()

	def launch_epics_server(self):
		m = get_manager(Manager)
		p = Process(target=run, args=(m.get_interface(),m)); p.daemon=True; p.start()
		self.epics_process = p

	def __getstate__(self):
		censored = dict(self.__dict__)
		censored.pop("lock",None)
		censored.pop("manager",None)
		censored.pop("epics_process",None)
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
		# danger
		return self.pvs[name].read()

	def write(self, name, value):
		# danger
		self.pvs[name].write(value)

interface = None

Manager.register("Interface", CocaInterface)

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