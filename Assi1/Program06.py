
import heapq


def find_cycle(graph, remaining):
    """Find one cycle using iterative depth-first search."""
    color = {}
    parent = {}

    for start in remaining:
        if color.get(start, 0) != 0:
            continue

        color[start] = 1
        stack = [(start, 0)]

        while stack:
            node, index = stack[-1]

            if index == len(graph[node]):
                color[node] = 2
                stack.pop()
                continue

            neighbor = graph[node][index]
            stack[-1] = (node, index + 1)

            if neighbor not in remaining:
                continue

            state = color.get(neighbor, 0)

            if state == 0:
                parent[neighbor] = node
                color[neighbor] = 1
                stack.append((neighbor, 0))

            elif state == 1:
                # A back edge identifies a cycle.
                cycle = [node]
                while cycle[-1] != neighbor:
                    cycle.append(parent[cycle[-1]])

                cycle.reverse()
                cycle.append(neighbor)
                return cycle

    return []


def resolve_modules(modules, imports):
    # module_a imports module_b means module_b loads first.
    graph = {module: [] for module in modules}
    indegree = {module: 0 for module in modules}
    edges = set()

    for module_a, module_b in imports:
        if module_a not in graph or module_b not in graph:
            raise ValueError("Unknown module name")

        edge = (module_b, module_a)

        if edge not in edges:
            edges.add(edge)
            graph[module_b].append(module_a)
            indegree[module_a] += 1

    for module in graph:
        graph[module].sort()

    # Choose the lexicographically smallest available module.
    heap = [
        module for module in modules
        if indegree[module] == 0
    ]
    heapq.heapify(heap)

    order = []

    while heap:
        module = heapq.heappop(heap)
        order.append(module)

        for dependent in graph[module]:
            indegree[dependent] -= 1

            if indegree[dependent] == 0:
                heapq.heappush(heap, dependent)

    if len(order) == len(modules):
        print(" ".join(order))
    else:
        remaining = {
            module for module in modules
            if indegree[module] > 0
        }
        cycle = find_cycle(graph, remaining)

        print("CYCLE")
        if cycle:
            print(" ".join(cycle))


def main():
    try:
        n, e = map(int, input().split())

        if not (1 <= n <= 200000 and 0 <= e <= 500000):
            print("INVALID")
            return

        modules = [input().strip() for _ in range(n)]

        if (
            any(not name or len(name) > 50 for name in modules)
            or len(set(modules)) != n
        ):
            print("INVALID")
            return

        imports = []

        for _ in range(e):
            module_a, module_b = input().split()
            imports.append((module_a, module_b))

        resolve_modules(modules, imports)

    except (ValueError, EOFError):
        print("INVALID")


if __name__ == "__main__":
    main()
