import coca
import time

route = coca.twincat.Route(ip='192.168.0.9',netid='192.168.0.9.1.1',port=801)
pv = coca.twincat.PV("IG_IN_INT",tcname=".IG_IN_INT",dtype="int",route=route,meta={'scan':1})
pv2 = coca.twincat.PV("TE1_LIMIT_LO",tcname=".TE1_LIMIT_LO",dtype="real",route=route,meta={'scan':1})
coca.broadcast_pv(pv2)

while(True):
	time.sleep(1)