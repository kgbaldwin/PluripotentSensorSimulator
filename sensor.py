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

        self.freq = frequency   # frequency at which this variable is measured (seconds)

    def get_measurement(self):
        return random.random() * self.rng + self.rangeMin


class ComputeFunction:
    def __init__(self, inputs, freq):
        self.inputs = inputs
        self.load_inst = -1
        self.freq = freq


class SensorNode:

    def __init__(self, variables: dict, functions: dict, parameters: dict, raw: bool, cycles: int):
        self.energy_level = parameters["Energy"]   # given in "mAs"
        print("inital energy level")
        print(self.energy_level, "0")
        self.curr_t = 0

        self.parameters = parameters
        self.variables = variables
        self.functions = functions

        # maps variable name to list storing current cache of data and
        # the next index to be filled
        self.raw_data = {}
        self.computed_data = {}

        self.num_cycles = cycles
        cycle_max = 1
        min_freq = np.inf

        # frequencies of variables
        for name, item in self.variables.items():
            self.raw_data[name] = [np.zeros(parameters["Raw_cache"]), 0]
            if min_freq > item.freq:
                min_freq = item.freq

            # undetermined behavior when frequencies aren't a multiple of Wakeup_freq
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


    # Simulates lifetime-loop of sensor, calling other functions in
    # their appropriate sequence
    def run_loop(self, raw):

        p = self.parameters

        # loop enough times such that data is sent num_cycles number of times
        for _ in range(self.num_cycles * self.send_freq):

            # terminate if sensor's battery has been depleted
            if self.energy_level < 0:
                return

            # estimating that wakeup takes ~1/6 s
            self.energy_level -= p["Wakeup_E"]/6
            self.curr_t += 1/6

            print("after waking up")
            print(round(self.energy_level, 4), round(self.curr_t, 3))

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

            # record energy draw during this sleep cycle
            print("after sleeping")
            print(round(self.energy_level, 4), round(self.curr_t, 3))

        # after simulation has completed, print lifetime stats
        self.lifetime_stats()



    # Measures all variables to be measured at current timestep
    def get_measurements(self):

        b = self.parameters["Raw_cache"]
        f = self.parameters["Wakeup_freq"]

        for name, var in self.variables.items():

            # if variable is to be measured this cycle
            if self.cycle%(var.freq // f) == 0:

                raw_value = var.get_measurement()
                data_r = self.raw_data[name]

                # data_r[0] is data array; data_r[1] is its next index to be filled
                data_r[0][data_r[1]] = raw_value
                data_r[1] = (data_r[1] + 1) % b

                self.energy_level -= var.energyUsage

        self.cycle = (self.cycle + 1) % self.cycle_max

        # increment time by 1 second per variable measured
        self.curr_t += len(self.variables)

        print("after getting measurements")
        print(round(self.energy_level, 4), round(self.curr_t, 3))



    # Simulates sensor wakeup where it only collects raw data and sends
    # back to access point if necessary
    def raw_data_wakeup(self):

        # check if it's time to send data
        self.since_last_sent += 1
        if self.since_last_sent == self.send_freq:
            self.since_last_sent = 0

            # count total number of bytes to be sent
            num_bytes = 0
            for item in self.variables:
                num_bytes += 1    # variable identifier byte

                data_arr = self.raw_data[item][0]
                # number of raw values that cache contains
                num_values = self.raw_data[item][1] + 1
                num_bytes += 4 * num_values   # 4 bytes per float

                # reset array
                for i in range(num_values):
                    data_arr[i] = 0
                self.raw_data[item][1] = 0  # reset current index

            self.send_data(num_bytes)


    # Simulates sensor wakeup where it performs computations
    def compute_wakeup(self):

        for func in self.functions:
            funcObj = self.functions[func]

            if self.cycle%(funcObj.freq // self.parameters["Wakeup_freq"]) == 0:

                self.write_files(func)

                # count number of instructions for line-retrieving for function
                if funcObj.load_inst == -1:
                    self.count_load_instructions(func)

                # run function
                executable = os.getcwd() + '/mylua'
                output = subprocess.run([executable, 'luaRunner.lua'], capture_output=True)
                result = output.stdout.decode()

                # subtract data loading instructions
                instructions = int(result.split()[3]) - funcObj.load_inst

                # subtract function energy
                ips = self.parameters["MIPS"] * 1000000
                self.energy_level -= self.parameters["Processor_E"] * instructions / ips
                self.curr_t += 1   ## assume 1 second for function execution
                print("after executing function")
                print(round(self.energy_level, 4), round(self.curr_t, 3))

                # data_c[0] is data array; data_c[1] is its next index to be filled
                data_c = self.computed_data[func]
                data_c[0][data_c[1]] = float(result.split()[0])
                data_c[1] = (data_c[1] + 1) % len(data_c[0])


        self.since_last_sent += 1
        if self.since_last_sent == self.send_freq:
            self.since_last_sent = 0

            # estimate number of bytes to be sent
            num_bytes = 0
            for item in self.functions:
                num_bytes += 1    # function identifier byte

                data_arr = self.computed_data[item][0]
                # number of computed values that function has; 4 bytes per float
                num_values = self.computed_data[item][1] + 1
                num_bytes += 4 * num_values

                # reset array
                for i in range(num_values):
                    data_arr[i] = 0
                self.computed_data[item][1] = 0  # reset current index

            self.send_data(num_bytes)



    # writes lua runner file and data transfer file, given a function
    def write_files(self, func):

        # write data to file to send to lua
        file = open("input.txt", "w")

        # write compution instructions to luaRunner.lua
        luaRunner = open("luaRunner.lua", "w")
        luaRunner.write("local lib = require('processing')\n")
        luaRunner.write("local arrs = lib.lines_from('input.txt')\n")
        luaRunner.write("-------------------\n")  # recorded at this point
        luaRunner.write("print(lib." + func + "(")

        # input_vars: vars to be inputted to function
        input_vars = self.functions[func].inputs
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



    # Simulates energy of sending data back to access point
    def send_data(self, num_bytes):

        p = self.parameters
        self.energy_level -= p["Radio_E"]/6  # turning radio on
        self.curr_t += 1/6    # time to turn radio on (s)

        time = 1 + 0.04*num_bytes
        self.curr_t += time

        self.energy_level -= p["Sending_E"] * time

        print("after sending packet")
        print(round(self.energy_level, 4), round(self.curr_t, 3))



    # After simulation stops, calculates energy used during simulation
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

