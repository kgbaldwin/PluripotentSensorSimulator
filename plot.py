import sys
import numpy as np
import matplotlib.pyplot as plt

# arguments: filename of data, min wakeup frequency

file = open(sys.argv[1])
freq = int(sys.argv[2])

values = [round(float(f), 2) for f in file.readlines()]

diff = [round(values[x+1]-values[x], 2) for x in range(len(values)-1)]
print(diff)

x = freq*np.arange(0, len(values))

plt.plot(x, values)
plt.title("Sensor's Current Draw over time")
plt.ylabel("Energy draw (mAh)")
plt.xlabel("Minutes") # only works if matches with with freq command line argument units
plt.show()