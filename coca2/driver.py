import pcaspy
from pcaspy import cas
import threading
import time
import sys
from datetime import datetime
from pytz import timezone

# The pcaspy module already takes care of a lot of the things we want to be able to do, but has
# some limitations and design choices we would like to change. The tag @monkeypatch will be used 
# here to indicate code that will be monkeypatched into pcaspy. The pcaspy module already uses a
# bunch of global variables so we will follow suit here.

# @monkeypatch
# A replacement for the pcaspy manager. 
# It will protect access to the driver with a mutex.
# This is used to allow us to reconfigure or replace the driver without stopping the server.
# One example is adding new PVs after starting the server. The original pcaspy code
# does not allow this, but coca will.
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

# A global instance of the coca manager
cocamanager = CocaManager()

# @monkeypatch
# A replacement for pcaspy's registerDriver. 
# This version knows to access the _driver array of cocamanager which is not protected by mutex
# This function will only be called after we have already acquired the mutex.
def registerDriver(driver_init_func):
    def wrap(*args, **kargs):
        driver_instance = args[0]
        port = driver_instance.port
        driver_init_func(*args, **kargs)
        cocamanager._driver[port] = driver_instance # this is the only changed line
    return wrap

# Generates an EPICS time stamp
# The start of the EPICS epoch.
epics_epoch_start = datetime(1990,1,1,tzinfo=timezone('UTC'))
def get_time():
	seconds = (datetime.now(timezone('UTC')) - epics_epoch_start).total_seconds();
	time = cas.epicsTimeStamp()
	time.secPastEpoch = int(seconds)
	time.nsec = int((seconds % 1) * 1e9)
	return time

# @monkeypatch
# A replacement for pcaspy's SimplePV.scan.
# This version sets the timestamp manually because the epics timestamp function seems to break
# when using multiprocessing.
# This is sort of broken conceptually though. What are we scanning?
def scan(self):
	while True:
		if self.name not in cocamanager.pvf:
			break
		driver = cocamanager.driver.get(self.info.port)
		if driver:
			gddValue = cas.gdd()
			self.getValue(gddValue)
			gddValue.setTimeStamp(get_time()) # this is the important line
			self.updateValue(gddValue)
		time.sleep(self.info.scan)


# Monkeypatch the pcaspy module
pcaspy.driver.manager = cocamanager
pcaspy.driver.registerDriver = registerDriver
pcaspy.SimplePV.scan = scan

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# A global interface which will be set when the server is started.
interface = None
remote_manager = None

# Our driver
class CocaDriver(pcaspy.Driver):
	def __init__(self, old_driver=None):
		self.pvDB    = {}
		if self.port not in cocamanager.pvs:
			return
		for reason, pv in cocamanager.pvs[self.port].items():
			data = pcaspy.driver.Data()
			check = (old_driver) and (reason in old_driver.pvDB)
			data.value = old_driver.pvDB[reason].value if check else pv.info.value 
			self.pvDB[reason] = data

	def update_status(self, reason, val):
		if reason not in cocamanager.pvs:
			return
		time = get_time() # replaces cas.epicsTimeStamp()
		alarm, severity = self._checkAlarm(reason, val)
		driver.setParamStatus(reason, alarm, severity)

	def read(self, reason):
		# read the value from the interface
		value = interface.read(reason)
		self.setParam(reason,value)
		return self.getParam(reason)

	def write(self, reason, value):
		# set the value through the interface
		interface.write(reason,value)
		value = interface.read(reason)
		self.setParam(reason,value)
		return True

# A global instance of the server
server = pcaspy.SimpleServer()

# A global instance of the driver
driver = CocaDriver()

# A thread to run the server
update_period_seconds = 0.1
def process_events():
	while True:
		server.process(update_period_seconds)

t = threading.Thread(target=process_events)
t.daemon = True
t.start()

# A thread to check for new PVs
def check_for_new_pvs():
	while (not remote_manager) or (not interface):
		time.sleep(1)
	queue = remote_manager.get_new_pv_queue()
	while True:
		pv = queue.get()
		broadcast_python_pv(pv.get_name(),pv.get_meta())

tnpv = threading.Thread(target=check_for_new_pvs)
tnpv.daemon = True
tnpv.start()


def check_for_disconnected_pvs():
	while (not remote_manager) or (not interface):
		time.sleep(1)
	queue = remote_manager.get_disconnected_pv_queue()
	while True:
		name = queue.get()
		disconnect_pv(name)

tdpv = threading.Thread(target=check_for_disconnected_pvs)
tdpv.daemon = True
tdpv.start()

# A method to refresh the driver when new PVs are available
def broadcast_python_pv(name, meta):
	with cocamanager.mutex:
		global driver
		del cocamanager._driver[driver.port]
		# TODO: there is a bug here because we don't take the initial value
		server.createPV(prefix="",pvdb={name: meta})
		# refresh the driver
		driver = CocaDriver(old_driver=driver)

def disconnect_pv(name):
	with cocamanager.mutex:
		global driver
		del cocamanager._driver[driver.port]
		pv = cocamanager.pvf.pop(name,None)
		cocamanager.pvs[driver.port].pop(name,None)
		# refresh the driver
		driver = CocaDriver(old_driver=driver)
		print "DISCONNECTED {}".format(name)

