import pyads
from pv import PV as CocaPV


class Route(object):
	def __init__(self, ip, netid, port):
		pyads.open_port()
		self.addr = pyads.AmsAddr(str(ip),port)
		self.ip = str(ip)
		pyads.add_route(adr,remote_ip)

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
	def __init__(self, name, tcname, dtype, route, meta={}, value=None):
		super(PV,self).__init__(name,meta,value)
		self.tcname = tcname
		self.addr = route.addr
		self.dtype = tc_dtypes[dtype.lower()]

	def tcwrite(self,value):
		pyads.write_by_name(self.addr, self.tcname, value, self.dtype)

	def tcread(self):
		return pyads.read_by_name(self.addr, self.tcname, self.dtype)

	@property
	def value(self):
		self._value = self.tcread()
		return self._value()

	@CocaPV.value.setter
	def value(self,value):
		self.tcwrite(value)
		self._value = self.tcread()
		interface.interface.set_event(self.name)



