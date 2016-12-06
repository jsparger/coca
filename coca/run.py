from multiprocessing import Process
from interface import interface
from pv import PV

def run(interface):
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