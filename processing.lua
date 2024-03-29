local M = {}

function M.lines_from(file)
    local lines = {}
    for line in io.lines(file) do

        arr = {}
        for num in string.gmatch(line, "[%d.]+") do
            arr[#arr + 1] = tonumber(num)
        end
        lines[#lines + 1] = arr
    end

    return lines
end


function M.mean(arr)
    for i=0, 1000 do
        sum = 0
        for i=1, #arr do
            sum = sum + arr[i]
        end
    end
    return (sum/(#arr))
end


function M.covariance(arr1, arr2)
    for i=0, 1000 do
        mean1 = M.mean(arr1)
        mean2 = M.mean(arr2)

        sum = 0
        for i=1, #arr1 do
            sum = sum + (arr1[i]-mean1)*(arr2[i]-mean2)
        end
    end

    return (sum/(#arr1-1))
end


return M
