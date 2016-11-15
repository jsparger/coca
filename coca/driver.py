import ast
import pcaspy
from pcaspy import cas
import threading
import time
import sys
import multiprocessing

# A companion to the pcaspy manager
class CocaManager(pcaspy.driver.Manager):
	proxies = {}
	mutex = threading.Lock()

	def __getattribute__(self, name):
		if name == "_driver":
			return object.__getattribute__(self,"driver")
		elif name == "driver":
			mutex = object.__getattribute__(self,"mutex")
			with mutex:
				return object.__getattribute__(self,name)
		else:
			return object.__getattribute__(self,name)

# A global instance of the companion manager
cocamanager = CocaManager()

def registerDriver(driver_init_func):
    def wrap(*args, **kargs):
        driver_instance = args[0]
        port = driver_instance.port
        driver_init_func(*args, **kargs)
        cocamanager._driver[port] = driver_instance
    return wrap

# Monkeypatch the pcaspy module
pcaspy.driver.manager = cocamanager
pcaspy.driver.registerDriver = registerDriver

# The basic data object
class BaseData(object):
	def __init__(self,name):
		self.name = name
		self.flag  = False
		self.severity  = pcaspy.Severity.INVALID_ALARM
		self.alarm = pcaspy.Alarm.UDF_ALARM
		self.udf = True
		self.mask = 0
		self.time  = cas.epicsTimeStamp()

	def update_status(self, val):
		if self.name not in cocamanager.proxies:
			return
		self.flag = True
		self.mask = (cas.DBE_VALUE | cas.DBE_LOG)
		self.time = cas.epicsTimeStamp()
		alarm, severity = driver._checkAlarm(self.name, val)
		driver.setParamStatus(self.name, alarm, severity)

# This class will be the interface to our monitored c++ objects.
class ProxyData(BaseData):
	def __init__(self,proxy):
		super(ProxyData,self).__init__(proxy.name)
		self.proxy = proxy

	@property
	def value(self):
		val = self.proxy.getValue()
		self.update_status(val)
		return val

	@value.setter
	def value(self, newval):
		self.proxy.setValue(newval)
		self.update_status(newval)

# This is the python data object
class Data(BaseData):
	def __init__(self, name, meta={}, value=None):
		super(Data,self).__init__(name)
		self._value = meta.get("value",value)
		self.meta = meta

	@property
	def pvdb(self):
		return {self.name : self.meta}

	@property
	def value(self):
		self.update_status(self._value)
		return self._value

	@value.setter
	def value(self, newval):
		self._value = newval
		self.update_status(newval)


# This class will maintain the default driver behavior but
# replace data with proxies where available.
class ProxyDriver(pcaspy.Driver):
	def __init__(self, old_driver=None):
		self.pvDB = {}
		if self.port not in cocamanager.pvs:
			return
		for reason, pv in cocamanager.pvs[self.port].items():
			if reason in cocamanager.proxies:
				x = cocamanager.proxies[reason]
				data = x if isinstance(x,Data) else ProxyData(x)
			else:
				data = pcaspy.driver.Data()
				check = (old_driver) and (reason in old_driver.pvDB)
				data.value = old_driver.pvDB[reason].value if check else pv.info.value 
			self.pvDB[reason] = data

# A global instance of the server
server = pcaspy.SimpleServer()

# A global instance of the driver
driver = ProxyDriver()

# A thread to run the server
update_period_seconds = 0.1
def process_events():
	while True:
		server.process(update_period_seconds)

t = threading.Thread(target=process_events)
t.daemon = True
t.start()

def print_pv(pv):
	print pv
	print pv.name
	print pv.value

def broadcast_pv(pv):
	if any(s in str(type(pv)) for s in ["coca::PV", "coca::iPV"]):
		broadcast_proxy_pv(pv)
	elif isinstance(pv, Data):
		broadcast_python_pv(pv)
	else:
		raise TypeError("The type {} is not supported".format(type(pv)))

def create_pv(prefix,pvdb):
	with cocamanager.mutex:
		global driver
		del cocamanager._driver[driver.port]
		server.createPV(prefix="",pvdb=pvdb)
		# refresh the driver
		driver = ProxyDriver(old_driver=driver)

def broadcast_python_pv(pv):
	with cocamanager.mutex:
		global driver
		del cocamanager._driver[driver.port]
		cocamanager.proxies[pv.name] = pv
		server.createPV(prefix="",pvdb=pv.pvdb)
		# refresh the driver
		driver = ProxyDriver(old_driver=driver)

# A function to create a pv
def broadcast_proxy_pv(pv):
	# delete the existing driver from the manager to prevent
	# scan threads from accessing driver while we update
	# TODO: this is still a race condition unless we protect with a mutex.
	
	with cocamanager.mutex:
		global driver
		del cocamanager._driver[driver.port]
		# add pv to cocamanager
		cocamanager.proxies[pv.name] = pv
		# create the pv using the server
		dict_string = pv.asDict();
		pvdb = ast.literal_eval(dict_string)
		print pvdb
		server.createPV(prefix="",pvdb=pvdb)
		# refresh the driver
		driver = ProxyDriver(old_driver=driver)
