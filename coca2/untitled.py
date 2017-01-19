# RUN IN INTERPRETER 1

import multiprocessing
from multiprocessing.managers import SyncManager
import threading
from proxy import StableLockProxy

class Dog(object):
	def __init__(self):
		self.name = "Rolf"

	def set_name(self,name):
		self.name = name

	def get_name(self):
		try:
			m = SyncManager(('localhost',5050),authkey='abracadabra')
			m.register("StableLock")
			m.connect()
			print "worked fine"
			l = m.StableLock()
			print l
		except Exception as e:
			print e
			print "wtf"
		return self.name

dog = Dog()
sync = SyncManager()

class Manager(SyncManager):
	pass

Manager.register("Dog",lambda: dog)
Manager.register("Sync",lambda: sync)
Manager.register("StableLock", threading.Lock, StableLockProxy)


m = Manager(('localhost',5050),authkey='abracadabra')
m.start()
l = m.StableLock()
print l
dogproxy = m.Dog()
print dogproxy.get_name()
dogproxy.set_name("Spike")





# RUN IN INTERPRETER 2

import multiprocessing
from multiprocessing.managers import SyncManager

class Dog(object):
	def __init__(self):
		self.name = "Rolf"

	def set_name(self,name):
		self.name = name

	def get_name(self):
		return self.name

class Manager(SyncManager):
	pass

Manager.register("Dog")
Manager.register("Sync")

m = Manager(('localhost',5050),authkey='abracadabra')
m.connect()
dog = m.Dog()
print dog.get_name()