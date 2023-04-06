    -- first 5 avg values are wrong because dividing by 5
function mean(arr)
    sum = 0
    for i=1, #arr do
        sum = sum + arr[i]*arr[i]
    end
    print(math.sqrt(sum)/(#arr))
end

a = {4,6,2,5,4,3,4}
mean(a)
