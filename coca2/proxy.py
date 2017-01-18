import multiprocessing
from multiprocessing import current_process
from multiprocessing.forking import Popen

def RebuildProxy(func, token, serializer, kwds):
	incref = (
		kwds.pop('incref', True) and
		not getattr(current_process(), '_inheriting', False)
		)
	return func(token, serializer, incref=incref, **kwds)

class StableEventProxy(multiprocessing.managers.EventProxy):
	def __reduce__(self):
	    kwds = {}
	    if Popen.thread_is_spawning():
	        kwds['authkey'] = self._authkey

	    if getattr(self, '_isauto', False):
	        kwds['exposed'] = self._exposed_
	        return (RebuildProxy,
	                (AutoProxy, self._token, self._serializer, kwds))
	    else:
	        return (RebuildProxy,
	                (type(self), self._token, self._serializer, kwds))


class StableConditionProxy(multiprocessing.managers.ConditionProxy):
	def __reduce__(self):
	    kwds = {}
	    if Popen.thread_is_spawning():
	        kwds['authkey'] = self._authkey

	    if getattr(self, '_isauto', False):
	        kwds['exposed'] = self._exposed_
	        return (RebuildProxy,
	                (AutoProxy, self._token, self._serializer, kwds))
	    else:
	        return (RebuildProxy,
	                (type(self), self._token, self._serializer, kwds))

class StableNamespaceProxy(multiprocessing.managers.NamespaceProxy):
	def __reduce__(self):
	    kwds = {}
	    if Popen.thread_is_spawning():
	        kwds['authkey'] = self._authkey

	    if getattr(self, '_isauto', False):
	        kwds['exposed'] = self._exposed_
	        return (RebuildProxy,
	                (AutoProxy, self._token, self._serializer, kwds))
	    else:
	        return (RebuildProxy,
	                (type(self), self._token, self._serializer, kwds))

class StableLock(multiprocessing.managers.AcquirerProxy):
	def __reduce__(self):
	    kwds = {}
	    if Popen.thread_is_spawning():
	        kwds['authkey'] = self._authkey

	    if getattr(self, '_isauto', False):
	        kwds['exposed'] = self._exposed_
	        return (RebuildProxy,
	                (AutoProxy, self._token, self._serializer, kwds))
	    else:
	        return (RebuildProxy,
	                (type(self), self._token, self._serializer, kwds))
