class RemotePV(object):
	def __init__(self):
		pass

	def setup(self,name,meta,ns):
		self.name = name
		self.meta = meta
		self.value = None
		self.lock = ns.lock
		self.disconnect_notify = ns.disconnect_notify
		self.read_request = ns.read_request
		self.read_complete = ns.read_complete
		self.write_request = ns.write_request
		self.write_complete = ns.write_complete
		self.push_request = ns.push_request
		self.push_complete = ns.push_complete

	def set_value(self,value):
		self.value = value

	def get_value(self):
		return self.value

	def disconnect(self):
		self.disconnect_notify.set()

	def read(self):
		with self.lock:
			self.read_request.set()
			try:
				self.read_complete.wait(timeout=1.0)
			except RuntimeError as e:
				self.disconnect()
			return self.value

	def write(self,value):
		with self.lock:
			self.value = value
			self.write_request.set()
			try:
				self.write_complete.wait(timeout=1.0)
			except RuntimeError as e:
				self.disconnect()

	def push(self,value):
		with self.lock:
			self.value = value
			self.push_request.set()
			try:
				self.push_complete.wait(timeout=1.0)
			except RuntimeError as e:
				raise e

