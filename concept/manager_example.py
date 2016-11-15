from multiprocessing import Manager, Process, Condition, Lock, current_process
from multiprocessing.managers import BaseManager 

class CocaMPInterface(object):
	broadcast = {}

	def broadcast_pv(self,pv):
		self.broadcast[pv.name] = pv
		pass

	def update_pv(self,pv):
		self.broadcast[pv.name].setValue(pv.getValue())
		pass

	def get_pv(self,name):
		return self.broadcast[name]


class Data(object):
	def __init__(self,name):
		self.name = name
		self.value = 0

	def getValue(self):
		return self.value

	def setValue(self,value):
		self.value = value

class CocaMPManager(BaseManager):
	pass
CocaMPManager.register('CocaMPInterface',CocaMPInterface)

def check(iface):
	pv = iface.get_pv("dog")
	print "check pv.name = {}, pv.val = {}".format(pv.name, pv.getValue())


manager = CocaMPManager()
manager.start()
iface = manager.CocaMPInterface()
pv = Data("dog")
pv.setValue(7)
iface.broadcast_pv(pv)

p = Process(target=check, args=(iface,)); p.start(); p.join()
pv.setValue(77)
iface.update_pv(pv)
p = Process(target=check, args=(iface,)); p.start(); p.join()

print "check from main pv.name = {}, pv.val = {}".format(pv.name, pv.getValue())

