space = [[0 for _ in range(101)] for _ in range(101)]

t = int(input())
count = 0
for _ in range(t) :
    x,y = map(int,input().split())

    for i in range(x,x+10) :
        for j in range(y,y+10) :
            space[i][j] = 1

for i in range(100) :
    for j in range(100) :
        if space[i][j] == 1 and space[i][j+1] == 0 :
            count += 1
        if space[j][i] == 1 and space[j+1][i] == 0 :
            count += 1
        if space[i][j] == 1 and space[i][j-1] == 0 :
            count += 1
        if space[j][i] == 1 and space[j-1][i] == 0 :
            count += 1
print(count)