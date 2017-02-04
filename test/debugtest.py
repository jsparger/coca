import coca
from coca.pv import PV as CocaPV
import time
import random
import threading
import Queue
import functools
from coca.jobs import QLock

# lock = threading.Lock()
qlock = QLock()

# Meta data for the temperature variables (e.g. TE1)
meta = {
	'scan' : 1,
	'prec' : 3,
	'unit' : 'K',
	'lolim': 0,
	'hilim': 1,
	'hihi' : 0.9,
	'high' : 0.8,
	'low'  : 0.2,
	'lolo' : 0.1,
}

def qLockRead(pv):
	with qlock:
		# time.sleep(0.5)
		pv.value = pv.value + 0.1*(random.random() - 0.5)
		# print "{} updated".format(pv.name)

def qLockWrite(pv):
	with qlock:
		print "{} = {}".format(pv.name, pv.value)


print "creating pvs"
pvs = [coca.PV(name="debug:{}".format(i),meta=meta,value=0.0,onRead=qLockRead,onWrite=qLockWrite) for i in range(100)]

for pv in pvs:
	print "broacasting pv {}".format(pv.name)
	coca.broadcast_pv(pv)
	time.sleep(0.1)

coca.wait()

