import multiprocessing
from multiprocessing.managers import BaseManager
import threading

manager = None

# need some locks here
class CocaMPInterface(object):
	pvs = {}
	new_pvs = []
	events = {}

	def get_pv_dict(self):
		return self.pvs

	def get_new(self):
		return self.new_pvs

	def clear_new(self):
		if self.new_pvs:
			self.new_pvs = []

	def broadcast_pv(self,pv):
		self.new_pvs.append(pv.name)
		self.events[pv.name] = multiprocessing.Event()
		self.update_pv(pv)

	def clear_event(self,name):
		self.events[name].clear()

	def wait_event(self,name):
		self.events[name].wait()

	def update_pv(self,pv):
		self.pvs[pv.name] = pv

	def get_pv(self,name):
		return self.pvs[name]

	def get_pv_value(self,name):
		return self.pvs[name]._value

	def set_pv_value(self,name,value):
		self.pvs[name]._value = value
		self.events[name].set()

class CocaMPManager(BaseManager):
	pass

CocaMPManager.register('CocaMPInterface',CocaMPInterface)
CocaMPManager.register('Event', multiprocessing.Event)

manager = CocaMPManager()
manager.start()
interface = manager.CocaMPInterface()