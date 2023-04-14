import sys
from sensor import SensorNode, Variable, ComputeFunction

# Usage: python runSensor.py configsFilename.txt raw/compute

file = open(sys.argv[1], 'r')
lines = file.readlines()

variables = {}   # variableName: variable object
functions = {}   # functionName: function object
parameters = {}  # parameterName: value

for line in lines:
    info = line.split(":")

    if info[0] == "Variable":
        values = info[2].split(",")
        for i in range(len(values)-1):
            values[i] = float(values[i])
        variables[info[1].strip()] = Variable(values[0], values[1], values[2], int(values[3]))

    elif info[0] == "Function":
        values = info[2].split(",")
        inputs = values[1].split()
        functions[info[1].strip()] = ComputeFunction(inputs, int(values[0]))

    elif info[0] == "Bufferlen":
        parameters["Bufferlen"] = int(info[1])

    else:
        parameters[info[0]] = float(info[1])

file.close()

raw = (sys.argv[2]=="raw")

sensor1 = SensorNode(variables, functions, parameters, raw)
