import coca
import random
import time

# start coca
coca.init()

# create the log file (overwrite any existing)
file = "./test.log"
with open(file,'w') as logfile:
	logfile.write("this log file is a test".format(1.0))

# describe the log file. each entry in pvs describes a column.
meta = {'lolim': -10, 'scan': 0.1, 'lolo': -8, 'prec': 3, 'high': 5, 'hilim': 10, 'low': -5, 'hihi': 8, 'unit': 'tst'}
pvs = [ coca.PV("LogReader:test",  value=float(), meta=meta),
        coca.PV("LogReader:test2", value=float(), meta=meta) ]

# create the reader.
reader = coca.LogReader(pvs,file=file)

# write random values to the log file. The reader will broadcast these changes at the scan interval.
while(True):
	val = random.random()*20-10
	val2 = random.random()*20-10
	with open(file,'a') as logfile:
		logfile.write("{}, {}\n".format(val,val2))
	time.sleep(0.1)

