import multiprocessing
from multiprocessing.managers import SyncManager
from archiver import Archiver, ArchiverProxy
import socket

class Manager(SyncManager):
	pass

class ArchiverInterface(object):
	def set_archiver(self, x):
		print type(x)
		self.archiver = x

	def get_archiver(self):
		return self.archiver


interface = None

def get_interface():
	global interface
	if not interface:
		interface = ArchiverInterface()
		interface.__reduce__ = reduce
	return interface

Manager.register("get_interface", get_interface)
Manager.register("Archiver", Archiver, ArchiverProxy)


# there is a "bug" that requires this to be set to the same value for every process using the manager.
# http://stackoverflow.com/questions/28318502/pythonusing-multiprocessing-manager-in-process-pool
# http://bugs.python.org/issue7503
multiprocessing.current_process().authkey = 'xxxxx'
influx_archiver_address = ('localhost',5053)

def get_manager(klass):
	_manager = klass(influx_archiver_address)
	print _manager._registry['Archiver']
	try:
		# check to see if there is a server running already
		s = socket.create_connection(influx_archiver_address, timeout=3)
		s.close()
	except socket.error as e:
		# server not running, so start
		print "starting"
		_manager.start()
	else:
		print "connecting"
		# server already running, so just connect
		_manager.connect()

	return _manager

manager = get_manager(Manager)
interface = manager.get_interface()