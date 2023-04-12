import sys

file = open(sys.argv[1])
for line in file:
    elems = line.split()
    print(elems[0], "\t", int(elems[3])-12)
        # because 12 extra instructions (see google sheet)