import pyads
from pv import PV as CocaPV
from coca.jobs import QLock

lock = QLock()

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

def tcread(pv):
	with lock:
		value = pyads.read_by_name(pv.addr, pv.tcname, pv.dtype)
		pv.value = value

def tcwrite(pv):
	with lock:
		pyads.write_by_name(pv.addr, pv.tcname, pv.value, pv.dtype)

class PV(CocaPV):
	def __init__(self, name, tcname, dtype, route, meta={}):
		self.name = name
		self.tcname = tcname
		self.addr = route.addr
		self.dtype = tc_dtypes[dtype.lower()]
		tcread(self)
		super(PV,self).__init__(name,meta,self.value,onRead=tcread,onWrite=tcwrite)
