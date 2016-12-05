import pcaspy
from pcaspy import cas
import interface
import time

# The basic data object
class BasePV(object):
	def __init__(self,name):
		self.name = name

# This is the python data object
class PV(BasePV):
	def __init__(self, name, meta={}, value=None):
		super(PV,self).__init__(name)
		self._value = meta.get("value",value)
		self.meta = meta

	@property
	def pvdb(self):
		return {self.name : self.meta}

	@property
	def value(self):
		self._value = interface.interface.get_pv_value(self.name)
		return self._value

	@value.setter
	def value(self, newval):
		self._value = newval
		interface.interface.update_pv(self)