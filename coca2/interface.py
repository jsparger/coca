from multiprocessing.managers import BaseManager 

# need some locks here
class CocaMPInterface(object):
	pvs = {}
	new_pvs = []

	def get_pv_dict(self):
		return self.pvs

	def get_new(self):
		return self.new_pvs

	def clear_new(self):
		if self.new_pvs:
			self.new_pvs = []

	def broadcast_pv(self,pv):
		self.new_pvs.append(pv.name)
		self.update_pv(pv)

	def update_pv(self,pv):
		self.pvs[pv.name] = pv

	def get_pv(self,name):
		return self.pvs[name]

	def get_pv_value(self,name):
		return self.pvs[name]._value

	def set_pv_value(self,name,value):
		self.pvs[name]._value = value

	def update(self):
		pass

class CocaMPManager(BaseManager):
	pass

CocaMPManager.register('CocaMPInterface',CocaMPInterface)

manager = CocaMPManager()
manager.start()
interface = manager.CocaMPInterface()

def broadcast_pv(pv):
	global interface
	interface.broadcast_pv(pv)