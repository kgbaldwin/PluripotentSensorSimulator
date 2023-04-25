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
            r_min = var["range_min"]
            r_max = var["range_max"]
            m_energy = var["measure_E"]
            m_freq = var["measure_freq"]

            m_unit = var["measure_unit"]
            # convert to seconds
            if m_unit == "m":
                m_freq *= 60
            if m_unit == "h":
                m_freq *= 3600

            variables[var["name"]] = Variable(r_min, r_max, m_energy, m_freq)

    elif label=="functions":
        for func in item:
            inputs = func["inputs"]
            m_freq = func["measure_freq"]
            cache_len = func["cache_len"]

            m_unit = func["measure_unit"]
            # convert to seconds
            if m_unit == "m":
                m_freq *= 60
            if m_unit == "h":
                m_freq *= 3600

            functions[func["name"]] = ComputeFunction(inputs, m_freq, cache_len)

    else:
        parameters[label] = item

if parameters["Wakeup_unit"] == "m":
    parameters["Wakeup_freq"] *= 60
elif parameters["Wakeup_unit"] == "h":
    parameters["Wakeup_freq"] *= 3600

# energy level converted to seconds in sensor

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
