import sys
import numpy as np
import matplotlib.pyplot as plt

file = open(sys.argv[1])

values = [round(float(f), 2) for f in file.readlines()]

diff = [round(values[x+1]-values[x], 2) for x in range(len(values)-1)]
print(diff)

x = np.arange(0, len(values))

plt.plot(x, values)
plt.title("Sensor's Current Draw over time")
plt.ylabel("Energy draw (mAh)")
plt.show()