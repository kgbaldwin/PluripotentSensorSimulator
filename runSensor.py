import sys
#from twisted.internet import task, reactor
from sensor import SensorNode, Variable

# Usage: python runSensor.py configsFilename.txt
# Function names must be entered directly into this file

file = open(sys.argv[1], 'r')
lines = file.readlines()

variables = {}
parameters = {}

for line in lines:
    info = line.split(":")

    if info[0] == "Variable":
        values = info[2].split(",")
        for i in range(len(values)):
            values[i] = float(values[i])
        variables[info[1].strip()] = Variable(values[0], values[1], values[2])

    elif info[0] == "Bufferlen":
        parameters["Bufferlen"] = int(info[1])

    else:
        parameters[info[0]] = float(info[1])

file.close()

### function name : variables to be inputted ###
functions = {"mean": ["temp"]}

############ fill this automatically?
############ what about loops?
function_instr_lens = {"mean": 20}


if sys.argv[2] == "raw":
    raw = True
else:   # by convention, will be "compute"
    raw = False

sensor1 = SensorNode(variables, functions, parameters, raw)
