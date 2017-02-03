import coca
from coca.pv import PV as CocaPV
import time
import random
import threading
import Queue
import functools

lock = threading.Lock()

# Meta data for the temperature variables (e.g. TE1)
meta = {
	'scan' : 0.1,
	'prec' : 3,
	'unit' : 'K',
	'lolim': 0,
	'hilim': 1,
	'hihi' : 0.9,
	'high' : 0.8,
	'low'  : 0.2,
	'lolo' : 0.1,
}

class QueuePV(CocaPV):
	def __init__(self, name, meta={}, value=None, onRead=None, onWrite=None):
		super(QueuePV,self).__init__(name,meta,value,onRead=onRead,onWrite=onWrite)
		self.read_event = threading.Event()

queue = Queue.Queue()

def slowRead(pv):
		time.sleep(0.05)
		pv.value = random.random()

def slowReadQueue(pv):
	queue.put(pv)
	pv.read_event.wait()
	pv.read_event.clear()
	# print "{} updated".format(pv.name)

def slowReadThread():
	while True:
		pv = queue.get()
		slowRead(pv)
		pv.read_event.set()

t = threading.Thread(target=slowReadThread)
t.daemon = True
t.start()

print "creating pvs"
pvs = [QueuePV(name="debug:{}".format(i),meta=meta,onRead=slowReadQueue) for i in range(1)]

for pv in pvs:
	print "broacasting pv {}".format(pv.name)
	coca.broadcast_pv(pv)
	time.sleep(0.1)

time.sleep(10)

