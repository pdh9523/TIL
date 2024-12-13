import sys; input = lambda: sys.stdin.readline().strip()


class Node:
    def __init__(self,key=""):
        self.key = key
        self.children = dict()
        self.to_save = 0
        self.is_end = False


class Trie:
    def __init__(self):
        self.root = Node()
        self.ans = 0

    def insert(self, word, is_save=False):
        now = self.root
        if is_save:
            now.to_save += 1

        for char in word:
            now = now.children.setdefault(char, Node(char))
            if is_save:
                now.to_save += 1
        if not is_save:
            now.is_end = True
    
    def clean(self, now):
        if now is self.root and now.to_save == 0:
            self.ans += 1
            return

        for char in now.children:
            if now.children[char].to_save == 0:
                self.ans += 1
                continue

            if now.children[char].is_end:
                self.ans += 1
            
            self.clean(now.children[char])


for _ in range(int(input())):
    trie = Trie()
    N = int(input())
    for _ in range(N):
        trie.insert(input())
    M = int(input())
    for _ in range(M):
        trie.insert(input(), True)
    
    trie.clean(trie.root)
    print(trie.ans)