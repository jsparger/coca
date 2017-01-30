from multiprocessing import Process
from interface import interface
from pv import PV
import time
import os
import sys

def info(title):
    print title
    print 'module name:', __name__
    print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def run(interface):
	# set up logging
	procname = 'cocadriver'
	sys.stdout = open(procname + ".out", "w", buffering=0)
	sys.stderr = open(procname + ".err", "w", buffering=0)
	info(procname)

	# start the coca server
	import driver
	driver.interface = interface
	# create a status pv
	# pvA = driver.Data("coca:running", value=1, meta={'scan': 1})
	# driver.broadcast_python_pv(pvA)
	# let server continue to run
	driver.t.join()

# start the coca process
p = Process(target=run, args=(interface,)); p.daemon=True; p.start()


def wait():
	while True:
		time.sleep(1)