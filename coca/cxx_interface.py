from pv import PV,broadcast_pv
import ast

cxx_pvs = {}
coca_pvs = {}

def broadcast_cxx_pv(pv):
	global cxx_pvs, pvs
	cxx_pvs[pv.name] = pv
	dict_string = pv.asDict();
	meta = ast.literal_eval(dict_string)[pv.name]
	coca_pv = PV(name=pv.name, meta=meta, onRead=pv.onRead, onWrite=pv.onWrite, value=pv.getValue())
	coca_pvs[pv.name] = coca_pv
	broadcast_pv(coca_pv)

# def update_cxx_pv(pv):
# 	coca_pv = coca_pvs[pv.name]
# 	coca_pv.value = pv.getValue()
# 	interface.interface.update_pv(coca_pv)
	

