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
t_vals = []
for i, f in enumerate(lines):
    if i % 2 == 1:
        if len(f.split()) == 1:
            values.append(round(float(f), 2))
        else:
            t_vals.append(round(float(f.split()[1])/60, 2))
            if setting=="volt":
                values.append(round(float(f.split()[0])/3600, 2))
            else:
                values.append(round(float(f.split()[0]), 2))

diff = [round(values[x]-values[x+1], 2) for x in range(len(values)-1)]
print(t_vals)
print(diff)

x = np.arange(0, len(values))

if not (setting == "volt" or setting == "diff"):
    print("Please enter either 'volt' or 'diff' as the second command-line argument")
    sys.exit()


if setting == "volt":
    if len(t_vals) == 0:
        plt.plot(x, values)
    else:
        plt.plot(t_vals, values)
    plt.ylabel("Battery voltage remaining (mAh)")
    plt.title("Battery voltage remaining")
    plt.tight_layout(pad=2)

else:   # setting == "diff"
    if len(t_vals) == 0:
        plt.plot(x, diff, 'o')
    else:
        plt.plot(t_vals[1:], diff, 'o')
    plt.ylabel("Energy used (mAh)")
    plt.title("Sensor's Current Usage")


if len(t_vals) == 0:
    plt.xlabel("Num actions executed")
else:
    plt.xlabel("Minutes")


plt.grid(True)
plt.ticklabel_format(useOffset=False)
plt.show()