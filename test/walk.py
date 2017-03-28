import coca
import random
import time

# start coca
coca.init()

# A function to perform random walk betweein -10 and 10.
def walk(val):
	newval = val + random.random() - 0.5
	return newval if abs(newval) < 10 else val

# create some PVs
pvA = coca.PV("test2:A", value = 7.0, meta={'lolim': -10, 'scan': 0.1, 'lolo': -8, 'prec': 3, 'high': 5, 'hilim': 10, 'low': -5, 'hihi': 8, 'unit': 'tst'})
pvB = coca.PV("test2:B", value = 7.0, meta={'lolim': -10, 'scan': 0.1, 'lolo': -8, 'prec': 3, 'high': 5, 'hilim': 10, 'low': -5, 'hihi': 8, 'unit': 'cats'})

# tell coca we would like to broadcast these pvs
coca.broadcast_pv(pvA)
coca.broadcast_pv(pvB)

# "Read from the log file' to update the PV.
a = 0
b = 0
while(True):
	a = walk(a)
	b = walk(b)
	pvA.value = a
	pvB.value = b
	time.sleep(0.1)

