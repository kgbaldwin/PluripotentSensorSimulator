function test (a, b)
    print(a .. ', ' .. b)
end

function test2(a)
    print(a)
end

function mean(arr)
    sum = 0
    for i=1, #arr do
        sum = sum + arr[i]
    end
    print(sum/(#arr))
end


print(#{1,5,8,3,3})

mean({1,5,8,3,3})


