import sys
from sensor import SensorNode, Variable

# Usage: python runSensor.py configsFilename.txt raw/compute
# Function names must be entered directly into this file (why?)

file = open(sys.argv[1], 'r')
lines = file.readlines()

variables = {}   # variableName: variable object
functions = {}   # functionName: variables to be inputted
parameters = {}  # parameterName: value

for line in lines:
    info = line.split(":")

    if info[0] == "Variable":
        values = info[2].split(",")
        for i in range(len(values)-1):
            values[i] = float(values[i])
        variables[info[1].strip()] = Variable(values[0], values[1], values[2], int(values[3]))

    elif info[0] == "Function":
        functions[info[1].strip()] = [var.strip() for var in info[2].split()]

    elif info[0] == "Bufferlen":
        parameters["Bufferlen"] = int(info[1])

    else:
        parameters[info[0]] = float(info[1])

file.close()

raw = (sys.argv[2]=="raw")

sensor1 = SensorNode(variables, functions, parameters, raw)
