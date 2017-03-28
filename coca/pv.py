import threading
import sys
import os
import remote_interface as ri
import socket
import multiprocessing

class PV(object):
	def __init__(self, name, meta={}, value=None, onRead=None, onWrite=None):
		self.lock = threading.Lock()
		self.name = name
		self.value = meta.get("value",value)
		self.meta = meta
		self.onRead = onRead
		self.onWrite = onWrite

		self.remote = ri.manager.RemotePV()
		self.remote.setup(self.name,self.meta)

	def _run(self):
		# launch read thread
		t = threading.Thread(target=self._read); t.daemon = True; t.start()
		# launch write thread
		t = threading.Thread(target=self._write); t.daemon = True; t.start()

	def _read(self):
		while True:
			try:
				ri.interface.wait_event(self.name,'read_request')
				with self.lock:
					# print self.name + " got read request"
					if self.onRead:
						self.onRead(self)
					self.remote.set_value(self.value)
					# print self.name + " set the value"
					ri.interface.clear_event(self.name,'read_request')
					# print self.name + " cleared the read request"
					ri.interface.set_event(self.name, 'read_complete')
					# print self.name + " sent read complete"
			except (socket.error, EOFError, IOError) as e:
				# We will get here if the manager process exits during the wait
				# This often happens when the program exits
				print e
				print "PV {} has been disconnected".format(self.name)
				sys.exit(1)

	def _write(self):
		while True:
			try:
				ri.interface.wait_event(self.name, 'write_request')
				self.value = self.remote.get_value()
				with self.lock:
					if self.onWrite:
						self.onWrite(self)
					ri.interface.clear_event(self.name, 'write_request')
					ri.interface.set_event(self.name, 'write_complete')
			except socket.error as e:
				# We will get here if the manager process exits during the wait
				# This often happens when the program exits
				print str(e)
				print "PV {} has been disconected".format(self.name)
				sys.exit(1)

	def push(self,value):
		pass

def broadcast_pv(pv):
	ri.interface.create_pv_events(pv.name)
	pv._run()
	ri.interface.broadcast_pv(pv.remote)








