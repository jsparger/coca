from pv import PV
import interface
import ast

cxx_pvs = {}
coca_pvs = {}

def broadcast_cxx_pv(pv):
	global cxx_pvs, pvs
	cxx_pvs[pv.name] = pv
	dict_string = pv.asDict();
	meta = ast.literal_eval(dict_string)[pv.name]
	coca_pv = PV(name=pv.name, meta=meta, value=pv.getValue(), onread=pv.onread, onwrite=pv.onwrite)
	coca_pvs[pv.name] = coca_pv
	interface.broadcast_pv(coca_pv)

def update_cxx_pv(pv):
	coca_pv = coca_pvs[pv.name]
	coca_pv.value = pv.getValue()
	interface.interface.update_pv(coca_pv)
	

