import subprocess
import os

# 'lua1_3.txt', 'lua1_6.txt', 'lua1_12.txt',
fnames = ['lua2_3.txt',
          'lua2_6.txt', 'lua2_12.txt', 'lua4_3.txt', 'lua4_6.txt', 'lua4_12.txt']

executable = os.getcwd() + '/mylua'

for file in fnames:
    luaRunner = open("luaRunner.lua", "w")
    luaRunner.write("local lib = require('processing1')\n")
    luaRunner.write("local arrs = lib.lines_from('lua_test_files/"+file+"')\n")
    luaRunner.write("-------------------\n")  # recorded at this point
    luaRunner.write("lib.covariance(arrs[1], arrs[2])")
    luaRunner.close()

    output = subprocess.run([executable, 'luaRunner.lua'], capture_output=True)
    result = output.stdout.decode()
    print(file, result, end='')
