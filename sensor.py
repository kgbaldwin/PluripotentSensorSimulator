# Junior Independent Work - Katie Baldwin
# Pluripotent Sensor Energy Simulator

import subprocess
import random
import numpy as np
import datetime


class Variable:
    def __init__(self, rangeMin, rangeMax, energy):
        self.energyUsage = energy  # how much energy taking a measurement of this variable consumes

        self.rng = rangeMax - rangeMin  # range of possible output values for a measurement
        self.rangeMin = rangeMin   # min of possible output values for a measurement

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
        for item in self.variables:
            self.data[item] = [np.zeros(parameters["Bufferlen"]), 0]

        self.since_last_sent = 0

        self.prev_energy = self.energy_level
        self.start_loop(raw)


    def start_loop(self, raw):

        p = self.parameters

        while self.energy_level > 0:
            start = datetime.datetime.now()
            if raw:
                self.raw_data_wakeup()
            else:
                self.wakeup()

            time_to_sleep = p["Wakeup_Fr"] - (datetime.datetime.now()-start).seconds
            self.energy_level -= time_to_sleep * p["Sleep_E"]

            self.record_energy()


    def record_energy(self):
        print(self.prev_energy - self.energy_level)
        self.prev_energy = self.energy_level


    # enacts sensor node wakeup mode - performs all necessary tasks
    def wakeup(self):
        #print("[compute] waking up")

        if self.energy_level < 0:
            return

        self.energy_level -= self.parameters["Wakeup_E"]
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
            result = subprocess.check_output(['lua', '-l', 'processing1', '-e', func_str])

            ## subtract function energy!!
            # 0.2 A per instruction (roughly)
            # from Instruction level + OS profiling for energy exposed software

            # self.energy_level -= 0.2*

            data += str(func) + '\n'   ### find a way to name the functions
            data += result.strip().decode('ascii') + '\n\n'

        self._send_data(data)


    def raw_data_wakeup(self):
        #print("[raw] waking up: " + str(self.energy_level))

        if self.energy_level < 0:
            return

        self.energy_level -= self.parameters["Wakeup_E"]
        self.get_measurements()

        # check if it's time to send data
        self.since_last_sent += 1
        if self.since_last_sent == self.parameters["Bufferlen"]:

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
            data_r[1] = (data_r[1] + 1) % self.parameters["Bufferlen"]

            self.energy_level -= self.variables[item].energyUsage


    def _send_data(self, data):

        self.since_last_sent = 0
        p = self.parameters

        self.energy_level -= p["Radio_E"] # turning radio on/off (not tcp)

        if self.energy_level < 0:  ## location isn't consistent
            return

        #print("\nSENDING DATA")
        #print(data)

        self.energy_level -= p["Packet_E"] * 2 * (len(data) / p["Bandwidth"])  #### math - use packet_f instead of 2
