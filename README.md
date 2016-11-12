### Dependencies:

+ EPICS Base 
+ pcaspy

Download EPICS base from http://www.aps.anl.gov/epics/base/. Version 3.14 should work well.
PCASPY is available from https://github.com/paulscherrerinstitute/pcaspy. It can also be installed with pip `pip install pcaspy`. It requires the environment variables EPICS_BASE and EPICS_HOST_ARCH to be set. Here is an example of how that can be done:

# EPICS
export EPICS_BASE=/path/to/your/base-3.14.12.5
export EPICS_HOST_ARCH=`$EPICS_BASE/startup/EpicsHostArch`
export PATH=$EPICS_BASE/bin/your-arch:$PATH
