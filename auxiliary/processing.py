# https://stackoverflow.com/questions/30841738/run-lua-script-from-python (3/23/23)
import subprocess
import numpy as np

def occupancy(inputs):
    print(f'''calculating occupancy using temp input \n{inputs['temp']}
      and light input \n{inputs['light']}''')

def tempAvg(inputs):
    output = np.average(inputs["temp"])
    print("Average: " + str(output))
    return output