from collections import deque

def find_path(start, goal, is_walkable_fn):
    """
    Finds the shortest path from 'start' to 'goal'.
    is_walkable_fn is a function that checks if tile (x, y) is walkable.
    """
    queue = deque([start])  # Frontier queue (tiles to explore)
    came_from = {start: None}  # Breadcrumbs dictionary to reconstruct path

    while queue:
        current = queue.popleft()  # Get next tile to inspect
        if current == goal:  # Goal reached, stop search
            break

        cx, cy = current
        # Check neighbors: up, down, left, right
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = (cx + dx, cy + dy)
            
            # Ensure within grid boundaries
            if 0 <= nx < 20 and 0 <= ny < 20:
                neighbor = (nx, ny)
                # If neighbor hasn't been visited and is walkable
                if neighbor not in came_from and is_walkable_fn(nx, ny):
                    queue.append(neighbor)
                    came_from[neighbor] = current

    # Return empty list if no path was found
    if goal not in came_from:
        return []

    # Reconstruct path from goal back to start
    path = []
    curr = goal
    while curr != start:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    
    return path