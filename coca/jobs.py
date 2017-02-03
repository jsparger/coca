import threading
import Queue

class Jobs(object):
	def __init__(self):
		self.queue = Queue.Queue()
		self.event = threading.Event()
		self.event.set()

	def request_stop(self):
		# print "requesting stop"
		self.event.clear()

	def start(self):
		# print "requesting start"
		self.event.set()

	def wait_for_completion(self):
		# print "waiting for queue join"
		self.queue.join()
		# print "queue join complete"


	def task(self):
		return Jobs.Task(self)

	def halt(self):
		return Jobs.Halt(self)

	class Halt(object):
		def __init__(self, jobs):
			self.jobs = jobs

		def __enter__(self):
			self.jobs.request_stop()
			self.jobs.wait_for_completion()

		def __exit__(self, exc_type, exc_val, exc_tb):
			self.jobs.start()

	class Task(object):
		def __init__(self, jobs):
			self.jobs = jobs

		def __enter__(self):
			# print "starting to enter: queue.count = {}".format(self.jobs.queue.qsize())
			self.jobs.event.wait()
			self.jobs.queue.put(0) # insert meaningless value. use queue as counter
			# print "starting task: queue.count = {}".format(self.jobs.queue.qsize())

		def __exit__(self, exc_type, exc_val, exc_tb):
			# print "starting to exit. queue.count = {}".format(self.jobs.queue.qsize())
			token = self.jobs.queue.get()
			self.jobs.queue.task_done()
			# print "finished with task: queue.count = {}".format(self.jobs.queue.qsize())



