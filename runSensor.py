import sys
from twisted.internet import task, reactor
import numpy as np

from sensor import SensorNode, Variable
import processing

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
        variables[info[1]] = Variable(values[0], values[1], values[2], int(values[3]))

    elif info[0] == "Energy":
        energy = float(info[1])     ####### or int?
    elif info[0] == "Bandwidth":
        bandwidth = float(info[1])

file.close()

### function reference : variables to be inputted ###
functions = {processing.tempAvg: ["temp"], processing.occupancy: ["temp", "light"]}

sensor1 = SensorNode(energy, variables, functions, bandwidth)

curr_energy = energy

def append_energy():
    global curr_energy
    num = curr_energy - sensor1.energy_level
    print(num)
    curr_energy = sensor1.energy_level

timer = task.LoopingCall(append_energy) # raw_data_
timer.start(1)

reactor.run()