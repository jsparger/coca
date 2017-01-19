class RemotePV(object):
	def __init__(self):
		pass

	def setup(self,name,meta):
		self.name = name
		self.meta = meta
		self.value = None
		# self.lock = ns.lock
		# self.disconnect_notify = ns.disconnect_notify
		# self.read_request = ns.read_request
		# self.read_complete = ns.read_complete
		# self.write_request = ns.write_request
		# self.write_complete = ns.write_complete
		# self.push_request = ns.push_request
		# self.push_complete = ns.push_complete

	def set_value(self,value):
		self.value = value

	def get_value(self):
		return self.value

