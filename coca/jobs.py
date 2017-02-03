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


class QLock(object):
	def __init__(self):
		self.events = Queue.Queue()
		self.release_queue = Queue.Queue()
		self.t = threading.Thread(target=self.sync_thread)
		self.t.daemon = True
		self.t.start()

	def sync_thread(self):
		while True:
			# get the next event,lock pair from the queue.
			event,lock = self.events.get()

			# the lock always comes to us acquired. 
			# Put it in the queue of locks waiting to be released.
			self.release_queue.put(lock)

			# Set the event. This will let the acquisition of the QLock to complete.
			event.set()

			# try to acquire the lock. We will not be able to do this until it has been released by 
			# the current owner of the QLock. This will also cause subsequent calls to acquire to 
			# block as they wait for their event.
			lock.acquire()

	def acquire(self):
		# create an event and a lock. 
		event = threading.Event()
		lock = threading.Lock(); 
	
		# acquire the lock before putting it in the queue
		lock.acquire()
		self.events.put((event,lock))

		# wait for the event to be set before returning
		event.wait()

	def release(self):
		# get our original lock back. It has been transferred to this
		# queue by our update thread.
		lock = self.release_queue.get()

		# Release the lock
		lock.release()

	def __enter__(self):
		self.acquire()

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.release()


