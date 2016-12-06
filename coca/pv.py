import pcaspy
from pcaspy import cas
import interface
import time
import threading
import multiprocessing

# The basic data object
class BasePV(object):
	def __init__(self,name):
		self.name = name

# This is the python data object
class PV(BasePV):
	def __init__(self, name, meta={}, value=None, onUpdate=None):
		super(PV,self).__init__(name)
		self._value = meta.get("value",value)
		self.meta = meta
		self.onUpdate = onUpdate

	def __getstate__(self):
		censored = dict(self.__dict__)
		censored.pop("onUpdate",None)
		return censored

	def update(self):
		while True:
			try:
				interface.interface.wait_event(self.name)
				self._value = interface.interface.get_pv_value(self.name)
				if self.onUpdate:
					self.onUpdate(self)
				interface.interface.clear_event(self.name)
			except:
				# We will get here if the manager process exits during the wait
				# This often happens when the program exits
				print "PV {} has been disconected".format(self.name)
				break

	def watch(self):
		t = threading.Thread(target=self.update)
		t.daemon = True
		t.start()		

	@property
	def pvdb(self):
		return {self.name : self.meta}

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, newval):
		self._value = newval
		interface.interface.set_event(self.name)

def broadcast_pv(pv):
	interface.interface.broadcast_pv(pv)
	pv.watch()