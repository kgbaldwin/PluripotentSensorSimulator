
import numpy as np

def occupancy(inputs):
    print(f"calculating occupancy using temp input \n{inputs['temp']}\n and light input \n{inputs['light']}")

def tempAvg(inputs):
    output = np.average(input[0])
    print("Average: " + str(output))
    return output