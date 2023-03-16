# Junior Independent Work - Katie Baldwin
# Pluripotent Sensor Energy Simulator

# https://stackoverflow.com/questions/474528/how-to-repeatedly-execute-a-function-every-x-seconds
from twisted.internet import task, reactor
import random
import numpy as np


# constants (move to separate file? include in configs?)
SLEEP_FREQ = .5
WAKEUP_FREQ = 3

SLEEP_ENERGY = 0.01
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
    def __init__(self, energy, variables: dict, functions: dict, bandwidth):
        self.energy_level = energy
        self.bandwidth = bandwidth  ## units??

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
        self.sending_data = False  # whether sensor is currently sending data to computer

        # periodically calls sleep energy drainage function
        self.timer1 = task.LoopingCall(self._sleep)
        self.timer1.start(SLEEP_FREQ)

        # periodically calls wakeup function
        self.timer2 = task.LoopingCall(self.raw_data_wakeup) # raw_data_
        self.timer2.start(WAKEUP_FREQ)

        reactor.run()


    # decreases sensor's power by amount corresponding to sleep mode
    def _sleep(self):
        self.energy_level -= SLEEP_ENERGY


    # enacts sensor node wakeup mode - performs all necessary tasks
    def wakeup(self):
        print("[compute] waking up")
        self.timer1.stop()

        if self.energy_level < 0:
            self.timer2.stop()
            reactor.stop()
            return

        self.energy_level -= WAKEUP_ENERGY
        self.get_measurements()

        # perform and record computations
        data = ''
        for func in self.functions:

            # compile inputs to function
            input_vars = self.functions[func]
            input_dict = {}
            for var in input_vars:
                input_dict[var] = self.data[var][0]

            computed = func(input_dict)

            ## subtract function energy!!

            data += str(func) + '\n'   ### find a way to name the functions
            data += str(computed) + '\n\n'

        self._send_data(data)

        if not self.sending_data:
            self.timer1.start(SLEEP_FREQ)  # re-enters sleep mode


    def raw_data_wakeup(self):
        print("[raw] waking up: " + str(self.energy_level))
        self.timer1.stop()

        if self.energy_level < 0:
            self.timer2.stop()
            reactor.stop()
            return

        self.energy_level -= WAKEUP_ENERGY
        self.get_measurements()

        # check if it's time to send data
        self.since_last_sent += 1
        if self.since_last_sent == self.min_interval:
            self.timer2.stop()

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
            self.timer1.start(SLEEP_FREQ)  # re-enters sleep mode


    def get_measurements(self):

        for item in self.variables:
            raw_value = self.variables[item].get_measurement()
            data_r = self.data[item]

            # data_r[0] is data array; data_r[1] is its next index to be filled
            data_r[0][data_r[1]] = raw_value
            data_r[1] = (data_r[1] + 1) % self.variables[item].histlen

            self.energy_level -= self.variables[item].energyUsage


    def _send_data(self, data):

        self.sending_data = True
        self.since_last_sent = 0

        self.energy_level -= RADIO_ENERGY # turning radio on/off (not tcp)

        if self.energy_level < 0:  ## location isn't consistent
            reactor.stop()
            return

        print("\nSENDING DATA")
        print(data)

        self.sending = task.LoopingCall(self.packet_energy)
        self.sending.start(0.5)

        self.stop_sending = task.LoopingCall(self.data_sent)
        print("Stop interval: " + str(len(data) / self.bandwidth))
        self.stop_sending.start(len(data) / self.bandwidth, now=False)


    def packet_energy(self):
        print("sending packet")
        self.energy_level -= PACKET_ENERGY


    def data_sent(self):
        self.sending.stop()
        self.stop_sending.stop()
        self.sending_data = False
        self.timer1.start(SLEEP_FREQ)
        if not self.timer2.running:
            self.timer2.start(WAKEUP_FREQ, now=False)


