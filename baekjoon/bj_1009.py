test_rot = int(input())
rot = [[0,0,0,0],[1,1,1,1],[2,4,8,6],[3,9,7,1],[4,6,4,6],[5,5,5,5],[6,6,6,6],[7,9,3,1],[8,4,2,6],[9,1,9,1]]

for i in range(test_rot) :
    a,b = map(int,input().split())
    a %= 10
    b %= 4
    if a == 0 :
        print(10)
    else :
        print(rot[a][b-1])