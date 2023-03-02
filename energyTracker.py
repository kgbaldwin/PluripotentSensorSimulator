# Junior Independent Work - Katie Baldwin
# Pluripotent Sensor Energy Simulator

# https://stackoverflow.com/questions/474528/how-to-repeatedly-execute-a-function-every-x-seconds
from twisted.internet import task, reactor
import random
import numpy as np

import processing


class Variable:
    def __init__(self, rangeMin, rangeMax, energy, func, histlen: int):
        self.energyUsage = energy  # how much energy taking a measurement of this variable consumes
        self.func = func   # the processing function for this data
        self.rng = rangeMax - rangeMin  # range of possible output values for a measurement
        self.rangeMin = rangeMin   # min of possible output values for a measurement
        self.histlen = histlen   # number of prior values to keep

    def get_measurement(self):
        return random.random() * self.rng + self.rangeMin



# numbers are just filler right now
class SensorNode:
    '''
    energy: initial energy capacity of sensor
    variables: dictionary {"variableName": variable}
    '''
    def __init__(self, energy, variables):
        self.energy_level = energy

        # create sensors for each of the variables sensable by this node
        self.variables = variables

        # maps variable name to list storing current cache of data and the next index to be filled
        self.data = {}
        for item in self.variables:
            self.data[item] = [np.zeros(self.variables[item].histlen), 0]

        self.timer1 = task.LoopingCall(self._sleep)
        self.timer1.start(1)

        # this should execute as often as the sensor is to be woken up
        self.timer2 = task.LoopingCall(self.wakeup)
        self.timer2.start(5)

        reactor.run()


    # causes the sensor's power to drain slowly in sleep mode
    def _sleep(self):
        print(self.energy_level)
        self.energy_level -= 0.5


    # enacts sensor node wakeup mode - performs all necessary tasks
    def wakeup(self):
        print("waking up")
        self.timer1.stop()

        self.energy_level -= 3

        data = ''
        for item in self.variables:
            raw_value = self.variables[item].get_measurement()
            data_r = self.data[item]
            data_r[0][data_r[1]] = raw_value
            data_r[1] = (data_r[1] + 1) % self.variables[item].histlen

            self.energy_level -= self.variables[item].energyUsage

            computed = self.variables[item].func(data_r[0])

            data += str(item) + '\n'
            data += str(computed) + '\n\n'

        self._send_data(data)

        self.timer1.start(1)  # re-enters sleep mode


    def _send_data(self, data):
        self.energy_level -= 5 # turning radio on/off (not tcp)

        #  but I should do this over time b/c it's not sleeping for that time
        self.energy_level -= len(data) * 0.4


    def curr_energy(self):
        return self.energy_level


var1 = Variable(-20, 100, 2, processing.dummy, 8)
var2 = Variable(0, 5, 3, processing.avg, 8)
variables = {"temp": var1, "light": var2}
sensor1 = SensorNode(100, variables)
