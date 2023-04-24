import sys
import json
from sensor import SensorNode, Variable, ComputeFunction

# Usage: python runSensor.py configsFilename.json raw/compute

file = open(sys.argv[1], 'r')
settings = json.load(file)

variables = {}   # variableName: variable object
functions = {}   # functionName: function object
parameters = {}  # parameterName: value

for label, item in settings.items():
    if label=="variables":
        for var in item:
            r_min = var["rangeMin"]
            r_max = var["rangeMax"]
            m_energy = var["measureEnergy"]
            m_freq = var["measureFrequency"]
            m_unit = var["measureUnit"]  ########

            variables[var["name"]] = Variable(r_min, r_max, m_energy, m_freq)

    elif label=="functions":
        for func in item:
            inputs = func["inputs"]
            m_freq = func["measureFrequency"]
            cache_len = func["cacheLen"]

            functions[func["name"]] = ComputeFunction(inputs, m_freq, cache_len)

    else:
        parameters[label] = item

raw = (sys.argv[2]=="raw")

sensor1 = SensorNode(variables, functions, parameters, raw)



'''
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
        inputs = values[2].split()
        functions[info[1].strip()] = ComputeFunction(inputs, int(values[0]), int(values[1]))

    elif info[0] == "Bufferlen":
        parameters["Bufferlen"] = int(info[1])

    else:
        parameters[info[0]] = float(info[1])

file.close()'''
