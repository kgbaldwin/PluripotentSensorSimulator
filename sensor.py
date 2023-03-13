# Junior Independent Work - Katie Baldwin
# Pluripotent Sensor Energy Simulator

# https://stackoverflow.com/questions/474528/how-to-repeatedly-execute-a-function-every-x-seconds
from twisted.internet import task, reactor
import random
import numpy as np

import processing


class Variable:
    def __init__(self, rangeMin, rangeMax, energy, histlen: int):
        self.energyUsage = energy  # how much energy taking a measurement of this variable consumes

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
    def __init__(self, energy, variables, functions, bandwidth):
        self.energy_level = energy

        self.variables = variables
        self.functions = functions   # inputs must be enclosed in a dictionary

        # maps variable name to list storing current cache of data and the next index to be filled
        self.data = {}
        self.min_interval = np.inf
        for item in self.variables:
            self.data[item] = [np.zeros(self.variables[item].histlen), 0]
            if self.variables[item].histlen < self.min_interval:
                self.min_interval = self.variables[item].histlen

        self.since_last_sent = 0
        self.sending_data = False
        self.bandwidth = bandwidth  ## units??

        self.timer1 = task.LoopingCall(self._sleep)
        self.timer1.start(1)

        # this should execute as often as the sensor is to be woken up
        self.timer2 = task.LoopingCall(self.raw_data_wakeup)
        self.timer2.start(3)

        reactor.run()


    # causes the sensor's power to drain slowly in sleep mode
    def _sleep(self):
        print("sleep: " + str(self.energy_level))
        self.energy_level -= 0.5


    # enacts sensor node wakeup mode - performs all necessary tasks
    def wakeup(self):
        print("[compute] waking up")
        if self.timer1.running:
            self.timer1.stop()

        if self.energy_level < 0:
            self.timer2.stop()
            reactor.stop()
            return

        self.energy_level -= 3

        data = ''

        self.get_measurements()


        for func in self.functions:

            # compile inputs to function
            input_vars = self.functions[func]
            input_dict = {}
            for var in input_vars:
                input_dict[var] = self.data[var][0]

            computed = func(input_dict)

            data += str(func) + '\n'
            data += str(computed) + '\n\n'

        self._send_data(data)

        self.timer1.start(1)  # re-enters sleep mode


    def raw_data_wakeup(self):
        print("[raw] waking up")
        self.timer1.stop()

        if self.energy_level < 0:
            self.timer2.stop()
            reactor.stop()
            return

        self.energy_level -= 3

        # take measurements
        self.get_measurements()

        # check if it's time to send data
        self.since_last_sent += 1
        if self.since_last_sent == self.min_interval:
            self.timer2.stop()

            self.since_last_sent = 0

            # accumulate message containing all data
            data = ''
            for item in self.variables:
                data += item + '\n'
                data_arr = self.data[item][0]
                for value in data_arr:
                    data += str(value) + '\n'
                data += '\n'

            self._send_data(data)

        if not self.sending_data:
            self.timer1.start(1)  # re-enters sleep mode


    def get_measurements(self):
        for item in self.variables:
            raw_value = self.variables[item].get_measurement()
            data_r = self.data[item]
            data_r[0][data_r[1]] = raw_value
            data_r[1] = (data_r[1] + 1) % self.variables[item].histlen

            self.energy_level -= self.variables[item].energyUsage


    def _send_data(self, data):
        self.sending_data = True

        self.energy_level -= 5 # turning radio on/off (not tcp)

        print("\nSENDING DATA")
        print(data)

        self.sending = task.LoopingCall(self.packet_energy)
        self.sending.start(0.4)

        self.stop_sending = task.LoopingCall(self.data_sent)
        print("Stop interval: " + str(len(data) / self.bandwidth))
        self.stop_sending.start(len(data) / self.bandwidth, now=False)


    def packet_energy(self):
        print("packet energy")
        self.energy_level -= 2


    def data_sent(self):
        self.sending.stop()
        self.stop_sending.stop()
        self.sending_data = False
        self.timer1.start(1)
        self.timer2.start(3, now=False)



var1 = Variable(-20, 100, 2, 5)
var2 = Variable(0, 5, 3, 5)
variables = {"temp": var1, "light": var2}

# function reference : variables to be inputted
functions = {processing.tempAvg: ["temp"], processing.occupancy: ["temp", "light"]}

sensor1 = SensorNode(100, variables, functions, 50)
