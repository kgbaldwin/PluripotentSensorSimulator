import sys
import json
from sensor import SensorNode, Variable, ComputeFunction

# Usage: python runSensor.py configsFilename.json raw/compute num_cycles

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

            m_unit = func["measure_unit"]
            # convert to seconds
            if m_unit == "m":
                m_freq *= 60
            if m_unit == "h":
                m_freq *= 3600

            functions[func["name"]] = ComputeFunction(inputs, m_freq)

    else:
        parameters[label] = item

if parameters["Wakeup_unit"] == "m":
    parameters["Wakeup_freq"] *= 60
elif parameters["Wakeup_unit"] == "h":
    parameters["Wakeup_freq"] *= 3600

# convert energy level to seconds
parameters["Energy"] *= 3600

raw = (sys.argv[2]=="raw")

cycles = int(sys.argv[3])
if cycles < 1:
    print("Please enter a value for cycles greater than or equal to 1!")
    sys.exit()

sensor1 = SensorNode(variables, functions, parameters, raw, cycles)

