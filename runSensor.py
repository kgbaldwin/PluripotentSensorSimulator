import sys

from sensor import SensorNode, Variable

# Usage: python runSensor.py configsFilename.txt
# Function names must be entered directly into this file

file = open(sys.argv[1], 'r')
lines = file.readlines()

variables = {}

for line in lines:
    info = line.split(":")

    if info[0] == "Variable":
        values = info[2].split(",")
        for i in range(len(values)-1):
            values[i] = float(values[i])
        variables[info[1].strip()] = Variable(values[0], values[1], values[2], int(values[3]))

    elif info[0] == "Energy":
        energy = float(info[1])     ####### or int?
    elif info[0] == "Bandwidth":
        bandwidth = float(info[1])

file.close()

### function reference : variables to be inputted ###
functions = {"mean": ["temp"]}

sensor1 = SensorNode(energy, variables, functions, bandwidth)
