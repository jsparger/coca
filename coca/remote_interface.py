from multiprocessing import Process
import threading
import Queue
from jobs import Jobs
from manager import Manager, get_manager
from run_epics_server import run
from proxy import reduce
from datetime import datetime

# A synchronized queue to hold new pvs.
new_pv_queue = Queue.Queue()
disconnected_pv_queue = Queue.Queue()

# A class which allows the coca clients to talk to the IOC
class CocaInterface(object):
	def __init__(self):
		self.new_backlog = Queue.Queue()
		self.disconnected_backlog = Queue.Queue()
		self.pvs = {}
		self.events = {}
		self.locks = {}
		self.overall_lock = threading.Lock()
		self.epics_process = None
		self.jobs = Jobs()
		# self.launch_epics_server()

	def launch_epics_server(self):
		if self.epics_process and self.epics_process.is_alive:
			return
		self.manager = get_manager(Manager)
		self.interface = self.manager.get_interface()
		p = Process(target=run, args=(self.interface,self.manager)); p.daemon=True; p.start()
		self.epics_process = p

	def __getstate__(self):
		censored = dict(self.__dict__)
		censored.pop("lock",None)
		censored.pop("locks",None)
		censored.pop("interface",None)
		censored.pop("manager",None)
		censored.pop("epics_process",None)
		censored.pop("events",None)
		censored.pop("pvs",None)
		censored.pop("jobs",None)
		return censored

	def broadcast_pv(self, pv):
		name = pv.get_name()
		if name in self.pvs:
			return False

		self.new_backlog.put(pv)
		with self.jobs.halt():
			while not self.new_backlog.empty():
				pv = self.new_backlog.get()
				self.pvs[name] = pv
				new_pv_queue.put(pv)
		return True

	def disconnect_pv(self,name):
		print "disconnect called for " + name
		if name not in self.pvs:
			return False
		self.disconnected_backlog.put(name)
		with self.jobs.halt():
			while not self.disconnected_backlog.empty():
				name = disconnected_backlog.get()
				disconnected_pv_queue.put(name)
				self.pvs.pop(name,None)

	def get_pv(self, name):
		if name not in self.pvs:
			return False
		return self.pvs[name]

	def get_pv_dict(self):
		return self.pvs

	def read(self, name):
		with self.jobs.task():
			with self.locks[name]:
				self.events[name]['read_request'].set()
				# start = datetime.now()
				result = self.events[name]['read_complete'].wait(timeout=60.0)
				# print "{} : {} end wait at {}".format(result,name,datetime.now()-start)
				if not result:
					self.disconnect_pv(name)
					return None
				self.events[name]['read_complete'].clear()
				return self.get_value(name)

	def write(self, name, value):
		with self.jobs.task():
			with self.locks[name]:
				self.pvs[name].set_value(value)
				self.events[name]['write_request'].set()
				if not self.events[name]['write_complete'].wait(timeout=60.0):
					self.disconnect_pv(name)
				self.events[name]['write_complete'].clear()

	def get_value(self, name):
		if name not in self.pvs:
			return None
		return self.pvs[name].get_value()

	def create_pv_events(self,name):
		with self.jobs.halt():
			actions = {'read_request','read_complete','write_request','write_complete','push_request','push_complete','disconnect_notify'}
			self.events[name] = {key:threading.Event() for key in actions}
			self.locks[name] = threading.Lock()

	def set_event(self, name, action):
			try:
				self.events[name][action].set()
				return True
			except:
				return False

	def wait_event(self, name, action, timeout=None):
		try:
			self.events[name][action].wait(timeout)
			return True
		except:
			return False

	def clear_event(self, name, action):
		try:
			self.events[name][action].clear()
			return True
		except:
			return False


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
Manager.register("get_disconnected_pv_queue", lambda: disconnected_pv_queue)

manager = get_manager(Manager)
interface = manager.get_interface()
interface.launch_epics_server()