function mean(arr)
    sum = 0
    for i=1, #arr do
        sum = sum + arr[i]
    end
    print(sum/(#arr))
end