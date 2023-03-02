# Junior Independent Work - Katie Baldwin
# Pluripotent Sensor Energy Simulator

# https://stackoverflow.com/questions/474528/how-to-repeatedly-execute-a-function-every-x-seconds
from twisted.internet import task, reactor
import random

class Variable:
    def __init__(self, rangeMin, rangeMax, energy, func):
        self.energyUsage = energy  # how much energy taking a measurement of this variable consumes
        self.func = func   # the processing function for this data
        self.rng = rangeMax - rangeMin
        self.rangeMin = rangeMin

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
            self.energy_level -= self.variables[item].energyUsage

            computed = self.variables[item].func(raw_value)

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

def dummy(input):
    print(f"~~ doing stuff with input {input} ~~")


var1 = Variable(-20, 100, 2, dummy)
var2 = Variable(0, 5, 3, dummy)
variables = {"temp": var1, "light": var2}
sensor1 = SensorNode(100, variables)
