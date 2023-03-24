import sys
import numpy as np
import matplotlib.pyplot as plt

file = open(sys.argv[1])

values = [round(float(f), 2) for f in file.readlines()]

diff = [round(values[x+1]-values[x], 2) for x in range(len(values)-1)]
print(diff)

x = np.arange(0, len(values))
print()
print(values)

plt.plot(x, values)
plt.title("Sensor's Current Draw over time")
plt.xlabel("Seconds")
plt.ylabel("Energy draw (mAh)")
plt.show()