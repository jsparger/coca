import coca
import coca.influx
import random
import multiprocessing

# start coca
coca.init()

# a function to perform random walk betweein -10 and 10.
def walk(val):
    newval = val + random.random() - 0.5
    return newval if abs(newval) < 10 else val

# a function that will be called every time the PV is read
def my_read_callback(pv):
    # update the pv value using random walk
    pv.value = walk(pv.value)

# meta data for the PVs
metadata= {
    'scan': 0.5,    # how frequently to read the value
    'lolim': -10,   # lower limit for the PV's value
    'hilim': 10,    # upper limit for the PV's value
    'lolo': -8,     # very low value alarm threshold
    'low': -5,      # low value alarm threshold
    'high': 5,      # high value alarm threshold
    'hihi': 8,      # very high value alarm threshold
    'prec': 3,      # precision (number of decimal places)
    'unit': 'kg'    # physical units for the PV
}

# create the PVs    
pvA = coca.PV("HelloWorld:A", value=0.0, meta=metadata, onRead=my_read_callback)
pvB = coca.PV("HelloWorld:B", value=7.0, meta=metadata, onRead=my_read_callback)

# tell coca we would like to broadcast these pvs
coca.broadcast_pv(pvA)
coca.broadcast_pv(pvB)

# archive the PVs in influxdb
coca.influx.manager.interface.set_address(coca.influx.manager.interface._token.address)
influx = coca.influx.manager.interface.get_archiver()
influx.archive(pvA.name)
influx.archive(pvB.name)

# let the server run indefinitely
coca.wait()