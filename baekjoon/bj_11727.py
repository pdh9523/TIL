test_list = [1,3]

t = int(input())

for idx in range(2,t) :
    test_list.append(test_list[idx-1] + 2 * test_list[idx-2])

print(test_list[t-1]%10007)