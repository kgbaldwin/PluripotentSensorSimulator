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
    def __init__(self, inputs, freq):
        self.inputs = inputs
        self.load_inst = -1
        self.freq = freq


class SensorNode:

    def __init__(self, variables: dict, functions: dict, parameters: dict, raw: bool, cycles: int):
        self.energy_level = parameters["Energy"] # given in "mAs"
        print("inital energy level")
        print(self.energy_level)
        self.curr_t = 0

        self.parameters = parameters  ## units for bandwidth??
        self.variables = variables
        self.functions = functions

        # maps variable name to list storing current cache of data and
        # the next index to be filled
        self.raw_data = {}
        self.computed_data = {}

        self.num_cycles = cycles
        cycle_max = 1
        min_freq = np.inf

        # freqencies of variables
        for name, item in self.variables.items():
            self.raw_data[name] = [np.zeros(parameters["Raw_cache"]), 0]
            if min_freq > item.freq:
                min_freq = item.freq

            # undetermined behavior when frequencies aren't a multiple of wakeup_freq
            num = int(item.freq // parameters["Wakeup_freq"])
            if cycle_max % num != 0:
                cycle_max = math.lcm(cycle_max, num)

        if raw:
            self.send_freq = int((min_freq/parameters["Wakeup_freq"])*parameters["Raw_cache"])
        else:
            # frequencies of functions
            for name, item in self.functions.items():
                self.computed_data[name] = [np.zeros(parameters["Compute_cache"]), 0]

                if min_freq > item.freq:
                    min_freq = item.freq

                num = int(item.freq // parameters["Wakeup_freq"])
                if cycle_max % num != 0:
                    cycle_max = math.lcm(cycle_max, num)

            self.send_freq = int((min_freq/parameters["Wakeup_freq"])*parameters["Compute_cache"])

        self.cycle = 0
        self.cycle_max = cycle_max
        self.since_last_sent = 0

        self.run_loop(raw)


    # Simulates lifetime-loop of sensor, calling other functions in the
    # appropriate sequence
    def run_loop(self, raw):

        p = self.parameters

        for _ in range(self.num_cycles * self.send_freq):

            if self.energy_level < 0:
                return

            # estimating each of these actions take ~1/6 s
            self.energy_level -= p["Wakeup_E"]/6
            self.curr_t += 1/6

            print("after waking up")
            print(round(self.energy_level, 4), round(self.curr_t, 2))

            self.get_measurements()

            # call proper wakeup function
            if raw:
                self.raw_data_wakeup()
            else:
                self.compute_wakeup()

            # subtract sleeping energy
            time_to_sleep = p["Wakeup_freq"] - p["Wakeup_len"]
            self.energy_level -= time_to_sleep * p["Sleep_E"]

            self.curr_t += time_to_sleep

            # record energy draw during this cycle
            print("after sleeping")
            # print(round(self.energy_level, 4))
            print(round(self.energy_level, 4), round(self.curr_t, 2))

        self.lifetime_stats()


    # Simulates sensor wakeup where it performs computations
    def compute_wakeup(self):

        for func in self.functions:
            funcObj = self.functions[func]

            if self.cycle%(funcObj.freq // self.parameters["Wakeup_freq"]) == 0:

                self.write_files(func)

                # first, count how many instructions line-retrieving for function takes
                if funcObj.load_inst == -1:
                    self.count_load_instructions(func)

                executable = os.getcwd() + '/mylua'
                output = subprocess.run([executable, 'luaRunner.lua'], capture_output=True)
                result = output.stdout.decode()

                # subtract data loading instructions
                instructions = int(result.split()[3]) - funcObj.load_inst

                # subtract function energy
                self.energy_level -= self.parameters["Processor_E"] * instructions / 10000
                self.curr_t += 1   ## assume 1 second for function execution
                print("after executing function")
                print(round(self.energy_level, 4), round(self.curr_t, 2))

                data_c = self.computed_data[func]

                # data_c[0] is data array; data_c[1] is its next index to be filled
                data_c[0][data_c[1]] = float(result.split()[0])
                data_c[1] = (data_c[1] + 1) % len(data_c[0])

        self.since_last_sent += 1
        if self.since_last_sent == self.send_freq:
            self.since_last_sent = 0

            # accumulate message containing all computed data
            data = ''
            for item in self.functions:
                data += item + '\n'
                data_arr = self.computed_data[item][0]
                self.computed_data[item][1] = 0  # reset current index
                for i in range(len(data_arr)):
                    data += str(round(data_arr[i], 2)) + '\n'
                    data_arr[i] = 0
                data += '\n'

            self._send_data(data)



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
        luaRunner.write("print(lib." + func + "(")

        # input_vars: vars to be inputted to function
        for counter, var in enumerate(input_vars):
            datapoints = self.raw_data[var][0]

            for i in range(len(datapoints)):
                file.write(str(datapoints[i]))
                if i != len(datapoints)-1:
                    file.write(", ")
            file.write("\n")

            luaRunner.write("arrs[" + str(counter+1) + "]")
            if counter != len(input_vars) - 1:
                luaRunner.write(", ")

        file.close()
        luaRunner.write("))")
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
                data_arr = self.raw_data[item][0]
                self.raw_data[item][1] = 0  # reset current index
                for i in range(len(data_arr)):
                    data += str(round(data_arr[i], 2)) + '\n'
                    data_arr[i] = 0
                data += '\n'

            self._send_data(data)


    # Measures all variables to be measured at current timestep
    def get_measurements(self):

        b = self.parameters["Raw_cache"]
        f = self.parameters["Wakeup_freq"]

        for name, var in self.variables.items():

            if self.cycle%(var.freq // f) == 0:

                raw_value = var.get_measurement()
                data_r = self.raw_data[name]

                # data_r[0] is data array; data_r[1] is its next index to be filled
                data_r[0][data_r[1]] = raw_value
                data_r[1] = (data_r[1] + 1) % b

                self.energy_level -= var.energyUsage

        self.cycle = (self.cycle + 1) % self.cycle_max

        self.curr_t += len(self.variables)

        print("after getting measurements")
        print(round(self.energy_level, 4), round(self.curr_t, 2))


    # Simulates sending data back to access point
    def _send_data(self, data):

        p = self.parameters
        self.energy_level -= p["Radio_E"]/6  # turning radio on
        self.curr_t += 1/6

        self.energy_level -= p["Packet_E"] * math.ceil(len(data) / p["Bandwidth"])  #### ** was 2 ** math ????
        print("after sending packet")
        self.curr_t += math.ceil(len(data) / p["Bandwidth"])
        print(round(self.energy_level, 4), round(self.curr_t, 2))


    # after simulation stops, calculates energy used during simulation
    # and total expected battery life
    def lifetime_stats(self):
        p = self.parameters

        energy_used = round(float(p["Energy"])-self.energy_level, 2)
        time_elapsed = self.num_cycles * self.send_freq * p["Wakeup_freq"] / 3600

        print()
        print("Energy:", energy_used/time_elapsed, "mAh per hr")

        e_per_hr = energy_used/time_elapsed
        hrs = p["Energy"]/e_per_hr

        print("Expected battery life:", round(hrs/24/30.4), "months")

