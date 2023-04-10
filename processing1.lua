-- https://stackoverflow.com/questions/11201262/how-to-read-data-from-a-file-in-lua
-- seems 80 instructions, +5 for each line past first one
-- amount of processing depends on length of input...
function lines_from(file)
    local lines = {}
    for line in io.lines(file) do
      lines[#lines + 1] = line
    end
    return lines
  end


function mean(arr)
    sum = 0
    for i=1, #arr do
        sum = sum + arr[i]
    end
    return (sum/(#arr))
end

-- first 5 avg values are wrong because dividing by 5
function calc_mean()
    line = lines_from("input.txt")
    -- if len != 1, error

    -- LUA IS 1-INDEXED
    arr = {}
    -- https://www.ibm.com/docs/en/db2-warehouse?topic=manipulation-stringgmatch-s-pattern
    for w in string.gmatch(line[1], "[%d.]+") do
        arr[#arr + 1] = tonumber(w)
    end

    ------------------ (5 more instructions if you do it inside?)

    print(mean(arr))    -- print result
end


function covariance(arr1, arr2)
    mean1 = mean(arr1)
    mean2 = mean(arr2)
    -- assert arrays are same length
    sum = 0
    for i=1, #arr1 do
        sum = sum + (arr1[i]-mean1)*(arr2[i]-mean2)
    end
    return sum/(#arr1-1)

end


function calc_cov()
    line = lines_from("input.txt")
    -- if len != 1, error

    -- LUA IS 1-INDEXED
    arr1 = {}
    -- https://www.ibm.com/docs/en/db2-warehouse?topic=manipulation-stringgmatch-s-pattern
    for w in string.gmatch(line[1], "[%d.]+") do
        arr1[#arr1 + 1] = tonumber(w)
    end

    arr2 = {}
    for w in string.gmatch(line[2], "[%d.]+") do
        arr2[#arr2 + 1] = tonumber(w)
    end

    ------------------ (5 more instructions if you do it inside?)

    print(covariance(arr1, arr2))    -- print result
end


calc_cov()
