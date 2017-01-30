# SNMP

from pysnmp.hlapi import *

errorIndication, errorStatus, errorIndex, varBinds = next(
    getCmd(SnmpEngine(),
           CommunityData('guru', mpModel=1),
           UdpTransportTarget(('192.168.0.22',161)),
           ContextData(),
           # ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
           ObjectType(ObjectIdentity('./WIENER-CRATE-MIB', 'outputVoltage', 0))
           )
)

if errorIndication:
    print(errorIndication)
elif errorStatus:
    print('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
else:
    for varBind in varBinds:
        print(' = '.join([x.prettyPrint() for x in varBind]))