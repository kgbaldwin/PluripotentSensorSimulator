import random

lines = [1,2,4]
lengths = [3,6,12]
fnames = []

for line in lines:
    for length in lengths:
        fname = "lua"+str(line)+"_"+str(length)+".txt"
        fnames.append(fname)
        file = open(fname, 'w')
        for i in range(line):
            for j in range(length):
                file.write(chr(random.randint(48, 57)))
                if j != length-1:
                    file.write(", ")
            file.write('\n')

        file.close()

print(fnames)
print("done!")