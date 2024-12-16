arr = list(range(int(input())+1))
brr = sorted([[*map(int,input().split())] for _ in range(int(input()))], key=lambda x: (x[0], -x[1]))

start, end = -1,-1
for s,e in brr:
    if s > start and e < end:
        continue

    if end < s:
        for i in range(s,e+1):
            arr[i] = arr[s]
        start = s
        end = e
        continue

    if end < e:
        for i in range(end,e+1):
            arr[i] = arr[end]
        end = e

print(len(set(arr[1:])))