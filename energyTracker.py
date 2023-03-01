# Junior Independent Work - Katie Baldwin
# Pluripotent Sensor Energy Simulator

# https://stackoverflow.com/questions/474528/how-to-repeatedly-execute-a-function-every-x-seconds
from twisted.internet import task, reactor
import random

# numbers are just filler right now
class SensorNode:
    '''
    energy: initial energy capacity of sensor
    variables: dictionary {"variableName": [int energyUsage, (float rangeMin, float rangeMax)] for one measurement}
    '''
    def __init__(self, energy, variables):
        self.energy_level = energy

        self.variables = variables
        self.variableSensors = {}
        for item in self.variables:
            range = self.variables[item][1]
            self.variableSensors[item] = Sensor(range)

        self.timer = task.LoopingCall(self._sleep)
        self.timer.start(1)

        reactor.run()

    def _sleep(self):
        #if not self.timer.running:
        #    self.timer.start(1)

        print(self.energy_level)
        self.energy_level -= 0.5

    # call other methods from here? yes
    def wakeup(self):
        self.timer.stop()
        self.energy_level -= 3

        data = ''
        for item in self.variables:
            value = self._measure(item)
            # do computation
            data += item + '\n'
            data += value + '\n\n'

        self._connect()
        self._send_data(data)

        self.timer.start(1)  # re-enters sleep mode

    def _measure(self, variable):
        self.energy_level -= self.variables[variable]

    def _connect(self):  # turning radio on/off (not tcp)
        self.energy_level -= 5

    def _send_data(self, data):
        # wait but I should do this over time b/c not sleeping
        self.energy_level -= len(data)*2

    def _curr_energy(self):
        return self.energy_level


class Sensor:
    def __init__(self, range):
        self.min = range[0]
        self.rng = range[1]-range[0]

    def get_measurement(self):
        return random.random() * self.rng + self.min



variables = {"temperature": [2, (-20, 100)], "light": [3, (0, 5)]}
sensor1 = SensorNode(100, variables)