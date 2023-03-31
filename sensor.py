# Junior Independent Work - Katie Baldwin
# Advised by Professor Amit Levy
# Pluripotent Sensor Energy Simulator

import numpy as np
import subprocess
import datetime
import random
import math


class Variable:
    def __init__(self, rangeMin, rangeMax, energy, frequency):
        self.energyUsage = energy  # energy consumption of taking one measurement of this variable

        self.rng = rangeMax - rangeMin  # range of possible output values for a measurement
        self.rangeMin = rangeMin   # min of possible output values for a measurement

        self.freq = frequency   # frequency at which this variable is measured

    def get_measurement(self):
        return random.random() * self.rng + self.rangeMin


# numbers are just filler right now
class SensorNode:
    '''
    energy: initial energy capacity of sensor
    variables: dictionary {"variableName": variable}
    '''
    def __init__(self, variables: dict, functions: dict, parameters: dict, raw):
        self.energy_level = parameters["Energy"]
        self.parameters = parameters  ## units for bandwidth??

        self.variables = variables
        self.functions = functions

        # maps variable name to list storing current cache of data and the next index to be filled
        self.data = {}
        cycle_max = 1
        min_freq = np.inf
        #self.send_freq = np.inf
        for name, item in self.variables.items():
            self.data[name] = [np.zeros(parameters["Bufferlen"]), 0]
            if min_freq > item.freq:
                min_freq = item.freq
                # undetermined behavior when frequencies aren't a multiple of wakeup_freq

            num = int(item.freq // parameters["Wakeup_Fr"])
            if cycle_max % num != 0:
                cycle_max = math.lcm(cycle_max, num)

        self.cycle = 0
        self.cycle_max = cycle_max

        self.send_freq = int((min_freq/parameters["Wakeup_Fr"])*parameters["Bufferlen"])
        self.since_last_sent = 0

        self.start_loop(raw)


    def start_loop(self, raw):

        p = self.parameters
        prev_energy = self.energy_level

        while self.energy_level > 0:
            start = datetime.datetime.now()
            if raw:
                self.raw_data_wakeup()
            else:
                self.compute_wakeup()   ## encode the frequencies for computations

            time_to_sleep = p["Wakeup_Fr"] - (datetime.datetime.now()-start).seconds
            self.energy_level -= time_to_sleep * p["Sleep_E"]

            print(prev_energy - self.energy_level)
            prev_energy = self.energy_level


    # enacts sensor node wakeup mode - performs all necessary tasks
    def compute_wakeup(self):

        self.energy_level -= self.parameters["Wakeup_E"]
        if self.energy_level < 0:
            return
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
                #### comma if there are multiple

            func_str = func_str + ")"

            # https://stackoverflow.com/questions/30841738/run-lua-script-from-python
            result = subprocess.check_output(['lua', '-l', 'processing1', '-e', func_str])

            ## subtract function energy!!
            # 0.2 A per instruction (roughly)
            # from Instruction level + OS profiling for energy exposed software

            # self.energy_level -= 0.2*

            data += str(func) + '\n'   ### find a way to name the functions
            data += result.strip().decode('ascii') + '\n\n'

        self._send_data(data)


    def raw_data_wakeup(self):

        self.energy_level -= self.parameters["Wakeup_E"]
        if self.energy_level < 0:
            return
        self.get_measurements()

        # check if it's time to send data
        self.since_last_sent += 1
        if self.since_last_sent == self.send_freq-1:
            self.since_last_sent = 0

            # accumulate message containing all data
            data = ''
            for item in self.variables:
                data += item + '\n'
                data_arr = self.data[item][0]
                self.data[item][1] = 0
                for i in range(len(data_arr)):
                    data += str(data_arr[i]) + '\n'
                    data_arr[i] = 0
                data += '\n'

            self._send_data(data)


    def get_measurements(self):

        b = self.parameters["Bufferlen"]
        f = self.parameters["Wakeup_Fr"]

        for name, var in self.variables.items():

            if self.cycle%(var.freq // f) == 0:

                raw_value = var.get_measurement()
                data_r = self.data[name]

                # data_r[0] is data array; data_r[1] is its next index to be filled
                data_r[0][data_r[1]] = raw_value
                data_r[1] = (data_r[1] + 1) % b

                self.energy_level -= var.energyUsage

        #print(self.cycle)
        #for var in self.data:
        #    print(var, self.data[var])
        #print()

        self.cycle = (self.cycle + 1) % self.cycle_max


    def _send_data(self, data):

        p = self.parameters

        self.energy_level -= p["Radio_E"] # turning radio on/off (not tcp)

        if self.energy_level < 0:  ## location isn't consistent
            return

        #print("\nSENDING DATA")
        #print(data)

        self.energy_level -= p["Packet_E"] * 2 * (len(data) / p["Bandwidth"])  #### math - use packet_f instead of 2
