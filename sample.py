import heapq

def dijkstra(graph, start):
    # 시작 정점으로부터의 최단 거리를 저장하는 딕셔너리
    dist = {vertex: float('infinity') for vertex in graph}
    dist[start] = 0  # 시작 정점의 거리는 0으로 설정

    # 우선순위 큐를 사용하여 방문할 정점을 관리
    priority_q = [(0, start)]

    while priority_q:
        current_dist, current_vertex = heapq.heappop(priority_q)

        # 현재 정점을 방문했을 때 더 긴 경로를 이미 찾았다면 건너뜁니다.
        if current_dist > dist[current_vertex]:
            continue

        for node, weight in graph[current_vertex].items():
            dist_to_node = current_dist + weight

            # 더 짧은 경로를 발견했을 때 최단 거리를 갱신하고 우선순위 큐에 추가합니다.
            if dist_to_node < dist[node]:
                dist[node] = dist_to_node
                heapq.heappush(priority_q, (dist_to_node, node))

    return dist

# 예시 그래프
graph = {
    'A': {'B': 3, 'C': 2},
    'B': {'A': 3, 'C': 1, 'D': 5},
    'C': {'A': 2, 'B': 1, 'D': 3},
    'D': {'B': 5, 'C': 3}
}

start_vertex = 'A'
shortest_distances = dijkstra(graph, start_vertex)
print("최단 거리:", shortest_distances)

V,E = map(int,input().split())

start = int(input())

graph = {}
for _ in range(E):
    u,v,w = map(int,input().split())
    if graph[u][v] > w:
        graph[u] = graph.update({v:w})