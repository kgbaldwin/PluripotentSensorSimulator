# Junior Independent Work - Katie Baldwin
# Pluripotent Sensor Energy Simulator

import subprocess
import random
import numpy as np
import datetime


# constants (move to separate file? include in configs?)
#SLEEP_FREQ = .5   # don't need anymore
WAKEUP_FREQ = 3

SLEEP_ENERGY = 0.02  # energy consumed in 1 second
WAKEUP_ENERGY = 60

RADIO_ENERGY = 60
PACKET_ENERGY = 45


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
    def __init__(self, energy, variables: dict, functions: dict, bandwidth, raw):
        self.energy_level = energy
        self.bandwidth = bandwidth  ## units??

        self.variables = variables
        self.functions = functions

        # maps variable name to list storing current cache of data and the next index to be filled
        self.data = {}
        self.min_interval = np.inf
        for item in self.variables:
            self.data[item] = [np.zeros(self.variables[item].histlen), 0]
            if self.variables[item].histlen < self.min_interval:
                self.min_interval = self.variables[item].histlen

        self.since_last_sent = 0
        self.sending_data = False  # whether sensor is currently sending data to computer

        self.prev_energy = self.energy_level
        self.start_loop(raw)


    def start_loop(self, raw):

        while self.energy_level > 0:

            start = datetime.datetime.now()
            if raw:
                self.raw_data_wakeup()
            else:
                self.wakeup()

            time_to_sleep = WAKEUP_FREQ - (datetime.datetime.now()-start).seconds

            self.energy_level -= time_to_sleep * SLEEP_ENERGY

            self.record_energy()



    def record_energy(self):
        print(self.prev_energy - self.energy_level)
        self.prev_energy = self.energy_level


    # enacts sensor node wakeup mode - performs all necessary tasks
    def wakeup(self):
        print("[compute] waking up")

        if self.energy_level < 0:
            return

        self.energy_level -= WAKEUP_ENERGY
        self.get_measurements()

        # perform and record computations
        data = ''
        for func in self.functions:
            func_str = func + "("

            # compile inputs to function
            input_vars = self.functions[func]

            for var in input_vars:
                func_str += "{"
                datapoints = self.data[var][0]
                for i in range(len(datapoints)):
                    func_str += str(datapoints[i])

                    if i != len(datapoints)-1:
                        func_str += ","
                func_str += "}"


            func_str = func_str + ")"

            # https://stackoverflow.com/questions/30841738/run-lua-script-from-python
            result = subprocess.check_output(['lua', '-l', 'processing', '-e', func_str])

            ## subtract function energy!!

            data += str(func) + '\n'   ### find a way to name the functions
            data += result.strip().decode('ascii') + '\n\n'

        print("DATA")
        print(data)
        self._send_data(data)


    def raw_data_wakeup(self):
        #print("[raw] waking up: " + str(self.energy_level))

        if self.energy_level < 0:
            return

        self.energy_level -= WAKEUP_ENERGY
        self.get_measurements()

        # check if it's time to send data
        self.since_last_sent += 1
        if self.since_last_sent == self.min_interval:

            # accumulate message containing all data
            data = ''
            for item in self.variables:
                data += item + '\n'
                data_arr = self.data[item][0]
                for value in data_arr:
                    data += str(value) + '\n'
                data += '\n'

            self._send_data(data)


    def get_measurements(self):

        for item in self.variables:
            raw_value = self.variables[item].get_measurement()
            data_r = self.data[item]

            # data_r[0] is data array; data_r[1] is its next index to be filled
            data_r[0][data_r[1]] = raw_value
            data_r[1] = (data_r[1] + 1) % self.variables[item].histlen

            self.energy_level -= self.variables[item].energyUsage

        #print(self.data)


    def _send_data(self, data):

        self.sending_data = True
        self.since_last_sent = 0

        self.energy_level -= RADIO_ENERGY # turning radio on/off (not tcp)

        if self.energy_level < 0:  ## location isn't consistent
            return

        #print("\nSENDING DATA")
        #print(data)

        self.energy_level -= PACKET_ENERGY * 2 * (len(data) / self.bandwidth)  #### math
