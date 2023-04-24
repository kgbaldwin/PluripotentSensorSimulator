# Junior Independent Work - Spring 2023 - Katie Baldwin
# Advised by Professor Amit Levy

# Pluripotent Sensor Energy Simulator

import numpy as np
import subprocess
import random
import math
import os


class Variable:
    def __init__(self, rangeMin, rangeMax, energy, frequency):
        self.energyUsage = energy  # energy consumption of taking one measurement of this variable

        self.rng = rangeMax - rangeMin  # range of possible output values for a measurement
        self.rangeMin = rangeMin   # min of possible output values for a measurement

        self.freq = frequency   # frequency at which this variable is measured

    def get_measurement(self):
        return random.random() * self.rng + self.rangeMin


class ComputeFunction:
    def __init__(self, inputs, freq, cache_len):
        self.inputs = inputs
        self.load_inst = -1
        self.freq = freq
        self.cache = np.zeros(cache_len)


class SensorNode:

    def __init__(self, variables: dict, functions: dict, parameters: dict, raw: bool):
        self.energy_level = parameters["Energy"]
        self.parameters = parameters  ## units for bandwidth??

        self.variables = variables
        self.functions = functions


        # maps variable name to list storing current cache of data and the next
        # index to be filled
        self.data = {}

        cycle_max = 1
        min_freq = np.inf

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

        self.run_loop(raw)


    # Simulates lifetime-loop of sensor, calling other functions in the
    # appropriate sequence
    def run_loop(self, raw):

        p = self.parameters

        #while self.energy_level > 0:
        for _ in range(2*self.cycle_max):

            self.energy_level -= p["Wakeup_E"]
            self.energy_level -= p["Radio_E"] # turning radio on

            print("after waking up")
            print(self.energy_level)

            if self.energy_level < 0:
                return
            self.get_measurements()

            # call proper wakeup function
            if raw:
                self.raw_data_wakeup()
            else:
                self.compute_wakeup()

            if self.energy_level < 0:
                return

            # subtract sleeping energy
            # one second per variable? maybe? per analysis of three
            time_to_sleep = p["Wakeup_Fr"] - 1 # ~1min to wakeup -- assuming fr is in minutes
            self.energy_level -= time_to_sleep * p["Sleep_E"] #### units????

            # record energy draw during this cycle
            print("after sleeping")
            print(self.energy_level)

        print("ENERGY:", round(float(p["Energy"])-self.energy_level, 2), "per", 2*p["Wakeup_Fr"]*self.cycle_max, "[units]")


    # Simulates sensor wakeup where it performs computations
    def compute_wakeup(self):

        data = ''
        for func in self.functions:
            funcObj = self.functions[func]
            ########
            if self.cycle%(funcObj.freq // self.parameters["Wakeup_Fr"]) == 0:

                self.write_files(func)

                # first, count how many instructions line-retrieving function takes
                if funcObj.load_inst == -1:
                    self.count_load_instructions(func)

                # https://stackoverflow.com/questions/30841738/run-lua-script-from-python
                executable = os.getcwd() + '/mylua'
                output = subprocess.run([executable, 'luaRunner.lua'], capture_output=True)
                result = output.stdout.decode()

                # subtract data loading instructions
                instructions = int(result.split()[2]) - funcObj.load_inst

                ## subtract function energy -- 0.2 A per instruction (roughly)
                # from Instruction level + OS profiling for energy exposed software
                self.energy_level -= 0.2*instructions  ###### index (whether runner prints results)
                print("after executing function")
                print(self.energy_level)

                data += str(func) + '\n'
                data += result.strip() + '\n\n'

        ######## when to send data
        self._send_data(data)   ### can I use length of input.txt file?


    # writes lua runner file and data transfer file, given a function
    def write_files(self, func):

        input_vars = self.functions[func].inputs

        # write data to file to send to lua
        file = open("input.txt", "w")

        # write compution instructions to luaRunner.lua
        luaRunner = open("luaRunner.lua", "w")
        luaRunner.write("local lib = require('processing')\n")
        luaRunner.write("local arrs = lib.lines_from('input.txt')\n")
        luaRunner.write("-------------------\n")  # recorded at this point
        luaRunner.write("lib." + func + "(")

        # input_vars: vars to be inputted to function
        for counter, var in enumerate(input_vars):
            datapoints = self.data[var][0]

            for i in range(len(datapoints)):
                file.write(str(datapoints[i]))
                if i != len(datapoints)-1:
                    file.write(", ")
            file.write("\n")

            luaRunner.write("arrs[" + str(counter+1) + "]")
            if counter != len(input_vars) - 1:
                luaRunner.write(", ")

        file.close()
        luaRunner.write(")")
        luaRunner.close()


    # Counts number of instructions used to load data into lua file.
    # Records in self.func_load_inst
    def count_load_instructions(self, func):

        luaCounter = open("luaCounter.lua", "w")
        luaCounter.write("local lib = require('processing')\n")
        luaCounter.write("local arrs = lib.lines_from('input.txt')\n")
        luaCounter.close()

        executable = os.getcwd() + '/mylua'

        instructions = subprocess.run([executable, 'luaCounter.lua'], capture_output=True)
        result = instructions.stdout.decode().split()[2]

        self.functions[func].load_inst = int(result)


    # Simulates sensor wakeup where it only collects raw data and sends
    # back to access point if necessary
    def raw_data_wakeup(self):

        # check if it's time to send data
        self.since_last_sent += 1
        if self.since_last_sent == self.send_freq:
            self.since_last_sent = 0

            # accumulate message containing all data
            data = ''
            for item in self.variables:
                data += item + '\n'
                data_arr = self.data[item][0]
                self.data[item][1] = 0  # reset current index
                for i in range(len(data_arr)):
                    data += str(round(data_arr[i],2)) + '\n'
                    data_arr[i] = 0
                data += '\n'

            self._send_data(data)


    # Measures all variables to be measured at current timestep
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

        self.cycle = (self.cycle + 1) % self.cycle_max

        print("after getting measurements")
        print(self.energy_level)


    # Simulates sending data back to access point
    def _send_data(self, data):

        p = self.parameters

        if self.energy_level < 0:  ## location isn't consistent
            return

        self.energy_level -= p["Packet_E"] * (len(data) / p["Bandwidth"])  #### ** was 2 ** math ????
        print("after sending packet")
        print(self.energy_level)

