from multiprocessing import Process
import time
import os
import sys

def info(title):
    print title
    print 'module name:', __name__
    print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def run(interface,manager):
	# set up logging
	procname = 'cocadriver'
	# sys.stdout = open(procname + ".out", "w", buffering=0)
	# sys.stderr = open(procname + ".err", "w", buffering=0)
	info(procname)

	# start the coca server
	import driver
	driver.interface = interface
	driver.remote_manager = manager

	# let server continue to run
	driver.t.join()

def wait():
	while True:
		time.sleep(1)