-- https://stackoverflow.com/questions/40928887/how-to-use-multiple-files-in-lua
local M = {}

-- https://stackoverflow.com/questions/11201262/how-to-read-data-from-a-file-in-lua
function M.lines_from(file)
    local lines = {}
    for line in io.lines(file) do

        arr = {}
        -- https://www.ibm.com/docs/en/db2-warehouse?topic=manipulation-stringgmatch-s-pattern
        for num in string.gmatch(line, "[%d.]+") do
            arr[#arr + 1] = tonumber(num)
        end
        lines[#lines + 1] = arr
    end

    return lines
end


-- first 5 avg values are wrong because dividing by 5 ????
function M.mean(arr)
    sum = 0
    for i=1, #arr do
        sum = sum + arr[i]
    end
    return (sum/(#arr))
end


function M.covariance(arr1, arr2)
    mean1 = M.mean(arr1)
    mean2 = M.mean(arr2)
    -- assert arrays are same length
    sum = 0
    for i=1, #arr1 do
        sum = sum + (arr1[i]-mean1)*(arr2[i]-mean2)
    end
    return (sum/(#arr1-1))

end


return M

-- some for running "require" (4)
-- one to open, one for creating/returning M, 2 per function
-- with one function: 8

-- without calc_ functions: 12 total to require