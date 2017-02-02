from pv import PV as CocaPV
import threading
import subprocess

lock = threading.Lock()

class Route(object):
	def __init__(self, ip, version, mib, community):
		self.ip = ip
		self.version = version
		self.mib = mib
		self.community = community

snmp_dtypes = {
	
	'i' : int,
	'u' : int,
	's' : str,
	'F' : float,
	'D' : float,
}

def snmp_read(pv):
	r = pv.route
	template = "snmpget -Oqv -v {v} -m {mib} -c {c} {ip} {name}"
	command = template.format(v=r.version, mib=r.mib, c=r.community, ip=r.ip, name=pv.snmpname)
	with lock:
		try:
			output = subprocess.check_output(command.split())
			pv.value = pv.dtype(output)
		except subprocess.CalledProcessError, e:
			print output
			raise e

def snmp_write(pv):
	r = pv.route
	template = "snmpset -v {v} -m {mib} -c {c} {ip} {name} {f} {value}"
	command.format(v=r.version, mib=r.mib, c=r.community, ip=r.ip, name=pv.snmpname, f=pv.format, value=pv.value)
	with lock:
		try:
			output = subprocess.check_output(command.split())
		except subprocess.CalledProcessError, e:
			print output
			raise e

class PV(CocaPV):
	def __init__(self, name, route, format, snmpname, meta={}):
		self.route = route
		self.snmpname = snmpname
		self.format = format
		self.dtype = snmp_dtypes[format]
		value = snmp_read(pv)
		super(PV,self).__init__(name,meta,value,onRead=tcread,onWrite=tcwrite)
