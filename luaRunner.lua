local lib = require('processing1')
local arrs = lib.lines_from('lua_test_files/lua4_12.txt')
-------------------
lib.covariance(arrs[1], arrs[2])