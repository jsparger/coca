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

		self.remote = manager.RemotePV()
		self.remote.setup(self.name,self.meta)

	def _run(self):
		# launch read thread
		t = threading.Thread(target=self._read); t.daemon = True; t.start()
		# launch write thread
		t = threading.Thread(target=self._write); t.daemon = True; t.start()

	def _read(self):
		while True:
			try:
				interface.wait_event(self.name,'read_request')
				with self.lock:
					print "self.value = {}".format(self.value)
					if self.onRead:
						self.onRead(self)
					self.remote.set_value(self.value)
					interface.clear_event(self.name,'read_request')
					interface.set_event(self.name, 'read_complete')
					print "read complete"
			except Exception as e:
				# We will get here if the manager process exits during the wait
				# This often happens when the program exits
				print str(e)
				print "PV {} has been disconected".format(self.name)
				sys.exit(1)

	def _write(self):
		while True:
			try:
				interface.wait_event(self.name, 'write_request')
				self.value = self.remote.get_value()
				with self.lock:
					if self.onWrite:
						self.onWrite(self)
					interface.clear_event(self.name, 'write_request')
					interface.set_event(self.name, 'write_complete')
			except Exception as e:
				# We will get here if the manager process exits during the wait
				# This often happens when the program exits
				print str(e)
				print "PV {} has been disconected".format(self.name)
				sys.exit(1)

	def push(self,value):
		pass

def broadcast_pv(pv):
	interface.create_pv_events(pv.name)
	pv._run()
	interface.broadcast_pv(pv.remote)








