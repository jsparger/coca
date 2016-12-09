import pyads
from pv import PV as CocaPV
import interface
import threading
import time

lock = threading.Lock()

class Route(object):
	def __init__(self, ip, netid, port):
		with lock:
			pyads.open_port()
			self.addr = pyads.AmsAddr(netid,port)
			self.ip = str(ip)
			pyads.add_route(self.addr,self.ip)

tc_dtypes = {
	'bool'  : 	pyads.PLCTYPE_BOOL,
	'byte'  : 	pyads.PLCTYPE_BYTE,
	'date'  : 	pyads.PLCTYPE_DATE,
	'dint'  : 	pyads.PLCTYPE_DINT,
	'dt'    : 	pyads.PLCTYPE_DT,
	'dword' : 	pyads.PLCTYPE_DWORD,
	'int'   : 	pyads.PLCTYPE_INT,
	'lreal' : 	pyads.PLCTYPE_LREAL,
	'real'  : 	pyads.PLCTYPE_REAL,
	'sint'  : 	pyads.PLCTYPE_SINT,
	'string': 	pyads.PLCTYPE_STRING,
	'time'  : 	pyads.PLCTYPE_TIME,
	'tod'   : 	pyads.PLCTYPE_TOD,
	'udint' : 	pyads.PLCTYPE_UDINT,
	'uint'  : 	pyads.PLCTYPE_UINT,
	'usint' : 	pyads.PLCTYPE_USINT,
	'word'  : 	pyads.PLCTYPE_WORD,
}

class PV(CocaPV):
	def __init__(self, name, tcname, dtype, route, meta={}):
		super(PV,self).__init__(name,meta,None)
		self.tcname = tcname
		self.addr = route.addr
		self.dtype = tc_dtypes[dtype.lower()]
		self.onUpdate = self._onUpdate
		self._value = self.tcread()
		self._update_period = self.meta['scan']


	def __getstate__(self):
		censored = super(PV,self).__getstate__()
		censored.pop("addr",None)
		censored.pop("dtype",None)
		censored.pop("onUpdate",None)
		return censored

	def tcwrite(self,value):
		with lock:
			pyads.write_by_name(self.addr, self.tcname, value, self.dtype)

	def tcread(self):
		with lock:
			return pyads.read_by_name(self.addr, self.tcname, self.dtype)

	@property
	def value(self):
		self._value = self.tcread()
		return self._value

	@value.setter
	def value(self,value):
		self._value = value
		interface.interface.set_pv_value(self.name,self._value)

	def _onUpdate(self,pv):
		self.tcwrite(self._value)

	def _readUpdate(self):
		while True:
			self.value = self.tcread()
			# print "updating value for {} to {}".format(self.name, self._value)
			time.sleep(self._update_period)

	def watch(self):
		super(PV,self).watch()
		t = threading.Thread(target=self._readUpdate)
		t.daemon = True
		t.start()



