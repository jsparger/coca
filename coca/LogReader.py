import driver
import sh
import csv

class LogReader(object):
	def __init__(self,pvs,file):
		self.filename = file
		self.pvs = pvs
		self.num_pvs = len(pvs)
		self.first_time = True
		self.tail_process = sh.tail(["-f","-n0"], self.filename, _out=self.process_line, _bg=True)
		# TODO: bug: this process does not die when python exits.

	def start_pv_broadcast(self, value_strings):
		for pv in self.pvs:
			driver.broadcast_pv(pv)

	def process_line(self,line):
		value_strings = list(csv.reader([line]))[0]
		n = len(value_strings)
		if n != self.num_pvs:
			# TODO: error
			print "WRONG NUMBER OF VALUES"

		for pv,value_string in zip(self.pvs,value_strings):
			# TODO: try catch
			pv.value = type(pv.value)(value_string)

		if self.first_time:
			self.first_time = False
			self.start_pv_broadcast(value_strings)
			return 

		


