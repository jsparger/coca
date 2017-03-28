
import time
import threading
from multiprocessing.managers import BaseProxy
from coca.proxy import reduce
from coca.jobs import QLock
import epics
import influxdb

class Archiver(object):
	def __init__(self):
		self.lock = QLock()
		self.pvs = {}
		self.db_name = "coca_archive"
		self.influx_client = influxdb.InfluxDBClient('localhost', 8086, '', '', self.db_name)
		self.influx_client.create_database(self.db_name)

	def archive(self,name):
		with self.lock:
			self.pvs[name] = epics.PV(name,callback=self.influx_write)

	def stop_archiving(self):
		with self.lock:
			pv = self.pvs.pop(name,None)
		if pv:
			pv.disconnect()

	def influx_write(self, pvname=None, value=None, timestamp=None, **kws):
		if not (pvname and value and timestamp):
			return
		
		json_body = [ 
			{
				"measurement": pvname,
				"time": int(1000*timestamp),
				"fields": {
					"value": value
				}
			}
		]

		self.influx_client.write_points(json_body,time_precision='ms')


class ArchiverProxy(BaseProxy):
	_exposed_ = ('archive', 'stop_archiving')
	def __reduce__(self):
		return reduce(self)
	def archive(self, name):
		return self._callmethod('archive', (name,))
	def stop_archiving(self, name):
		return self._callmethod('stop_archiving', (name,))


def process_events():
	while True:
		time.sleep(1)

t = threading.Thread(target=process_events)
t.daemon = True
t.start()


