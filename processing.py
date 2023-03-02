
import numpy as np

def dummy(input):
    print(f"~~ doing stuff with input {input} ~~")

def avg(input):
    output = np.average(input)
    print("Average: " + str(output))
    return output