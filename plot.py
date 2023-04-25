import sys
import numpy as np
import matplotlib.pyplot as plt

# arguments: filename of data, volt/diff

file = open(sys.argv[1])
setting = sys.argv[2]

lines = file.readlines()

final_energy = lines[-2]
battery_life = lines[-1]
lines = lines[:-3]

print(final_energy)
print(battery_life)

values = []
for i, f in enumerate(lines):
    if i % 2 == 1:
        values.append(round(float(f), 2))  # convert back to hours

diff = [round(values[x]-values[x+1], 2) for x in range(len(values)-1)]
print(diff)

x = np.arange(0, len(values))

if setting == "volt":
    plt.plot(x, values)
    plt.ylabel("Battery voltage remaining (mAh)")
    plt.title("Battery voltage remaining")

elif setting == "diff":
    plt.plot(x[:-1], diff)
    plt.ylabel("Energy used (mAh)")
    plt.title("Sensor's Current Usage")
else:
    print("Please enter either 'volt' or 'diff' as the second command-line argument")
    sys.exit()

plt.xlabel("Num actions executed")
plt.ticklabel_format(useOffset=False)
plt.show()