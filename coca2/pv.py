import threading
import sys
from remote_interface import manager,interface

class PV(object):
	def __init__(self, name, meta={}, value=None, onRead=None, onWrite=None):
		self.lock = threading.Lock()
		self.name = name
		self.value = meta.get("value",value)
		self.meta = meta
		self.onRead = onRead
		self.onWrite = onWrite

		ns = manager.Namespace()
		self.lock 				= ns.lock 				= manager.StableLock()
		self.disconnect_notify 	= ns.disconnect_notify 	= manager.StableEvent()
		self.read_request 		= ns.read_request 		= manager.StableEvent()
		self.read_complete 		= ns.read_complete 		= manager.StableEvent()
		self.write_request 		= ns.write_request 		= manager.StableEvent()
		self.write_complete 	= ns.write_complete 	= manager.StableEvent()
		self.push_request 		= ns.push_request 		= manager.StableEvent()
		self.push_complete 		= ns.push_complete 		= manager.StableEvent()
		
		self.remote = manager.RemotePV()
		self.remote.setup(self.name,self.meta,ns)

	def _run(self):
		# launch read thread
		t = threading.Thread(target=self._read); t.daemon = True; t.start()
		# launch write thread
		t = threading.Thread(target=self._write); t.daemon = True; t.start()

	def _read(self):
		while True:
			try:
				self.read_request.wait()
				with self.lock:
					if self.onRead:
						self.onRead(self)
					self.remote.set_value(self.value)
					self.read_request.clear()
					self.read_complete.set()
			except Exception as e:
				# We will get here if the manager process exits during the wait
				# This often happens when the program exits
				print str(e)
				print "PV {} has been disconected".format(self.name)
				sys.exit(1)

	def _write(self):
		while True:
			try:
				self.write_request.wait()
				self.value = self.remote.get_value()
				with self.lock:
					if self.onWrite:
						self.onWrite(self)
					self.write_request.clear()
					self.write_complete.set()
			except Exception as e:
				# We will get here if the manager process exits during the wait
				# This often happens when the program exits
				print str(e)
				print "PV {} has been disconected".format(self.name)
				sys.exit(1)

	def push(self,value):
		pass

def broadcast_pv(pv):
	pv._run()
	interface.broadcast_pv(pv.remote)








