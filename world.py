from settings import *

class World:
    def __init__(self):
        # Initialize a 20x20 grid filled with zeros (0 = grass)
        self.grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.bridge_tiles = [(10, 9), (10, 10)]
        self.bridge_state = "broken"  # "broken", "repairing", "repaired"
        self.setup_environment()

    def setup_environment(self):
        # Create the river on column 10 (water = 3)
        for y in range(GRID_HEIGHT):
            self.grid[10][y] = TILE_WATER
        
        # Add the bridge tiles
        self.set_bridge_state("broken")

        # Add trees (wood sources = 4) in accessible areas
        tree_positions = [(3, 4), (4, 4), (3, 5), (2, 14), (3, 14), (3, 15)]
        for tx, ty in tree_positions:
            self.grid[tx][ty] = TILE_TREE

    def set_bridge_state(self, state):
        """Updates bridge state and tile IDs ('broken', 'repairing', 'repaired')."""
        self.bridge_state = state
        if state == "broken":
            tile_id = TILE_BRIDGE_BROKEN
        elif state == "repairing":
            tile_id = TILE_BRIDGE_REPAIRING
        elif state == "repaired":
            tile_id = TILE_BRIDGE_REPAIRED
        else:
            return

        for bx, by in self.bridge_tiles:
            self.grid[bx][by] = tile_id

    def is_walkable(self, x, y):
        # 1. Check bounds
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False
        
        # 2. Check terrain (water, broken/repairing bridge, and trees are impassable; repaired bridge is walkable)
        if self.grid[x][y] in [TILE_WATER, TILE_BRIDGE_BROKEN, TILE_BRIDGE_REPAIRING, TILE_TREE]:
            return False
            
        return True

    def is_legal_rock_pos(self, x, y, occupied_positions=None):
        """Checks if a tile is a legal destination for the movable rock (GDD Section 15)."""
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False
        # Cannot be on water, bridge, tree, or non-grass tile
        if self.grid[x][y] != TILE_GRASS:
            return False
        # Cannot occupy an agent or player tile
        if occupied_positions and (x, y) in occupied_positions:
            return False
        return True

    def get_trees(self):
        """Returns a list of (x, y) coordinates for all available trees."""
        trees = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if self.grid[x][y] == TILE_TREE:
                    trees.append((x, y))
        return trees

    def harvest_tree(self, x, y):
        """Harvests a tree at (x, y), turning it into grass and returning wood amount."""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and self.grid[x][y] == TILE_TREE:
            self.grid[x][y] = TILE_GRASS
            return 1  # Returns 1 wood unit
        return 0

