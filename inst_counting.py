import subprocess
import os

fnames = ['lua1_3.txt', 'lua1_6.txt', 'lua1_12.txt', 'lua2_3.txt',
          'lua2_6.txt', 'lua2_12.txt', 'lua4_3.txt', 'lua4_6.txt', 'lua4_12.txt']

executable = os.getcwd() + '/mylua'

for file in fnames:
    luaRunner = open("luaRunner.lua", "w")
    luaRunner.write("local lib = require('processing1')\n")
    luaRunner.write("l = lib.lines_from('lua_test_files/"+file+"')")
    luaRunner.close()

    output = subprocess.run([executable, 'luaRunner.lua'], capture_output=True)
    result = output.stdout.decode()
    print(file, result, end='')
