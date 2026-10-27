class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy, world, rock_pos):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if the destination tile is walkable
        if world.is_walkable(new_x, new_y):
            # Check that the rock is not occupying the tile
            if [new_x, new_y] != rock_pos:
                self.x = new_x
                self.y = new_y

import pygame
from settings import *
from pathfinding import find_path

# --- Timo's FSM States ---
STATE_INSPECTING = "INSPECTING"
STATE_GATHERING_WOOD = "GATHERING_WOOD"
STATE_GOING_TO_REPAIR = "GOING_TO_REPAIR"
STATE_REPAIRING = "REPAIRING"
STATE_SUSPENDED = "SUSPENDED"
STATE_DONE = "DONE"

class Agent:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.path = []
        self.last_move_time = 0
        self.move_delay = 300  # Delay between steps in milliseconds

        # --- Internal memory / state ---
        self.state = STATE_INSPECTING
        self.previous_state = None          # State to return to after suspension
        self.inventory = {"wood": 0}
        self.required_materials = {"wood": BRIDGE_REPAIR_WOOD_REQUIRED}
        self.broken_tiles = []              # Bridge tiles needing repair

        # --- Points of interest ---
        self.inspect_position = (8, 9)      # Vantage point to inspect the bridge
        self.repair_position = (9, 10)      # Tile adjacent to the broken bridge

        # --- Resource gathering ---
        self.harvest_delay = 800            # Time to chop a tree in milliseconds
        self.last_harvest_time = 0

        # --- Repair timing (GDD Section 4.6 & Appendix A) ---
        self.repair_start_time = 0
        self.repair_duration = BRIDGE_REPAIR_TIME_MS

        # --- Replanning & blockages (GDD Section 17 & Appendix A) ---
        self.last_replan_time = 0
        self.replan_interval = AGENT_REPLAN_INTERVAL_MS
        self.blocked_since = None           # Timestamp when blockage was first detected
        self.blocked_timeout = 2000         # Time blocked before suspending goal (ms)
        self.suspend_duration = 3000        # How long the goal remains suspended (ms)
        self.suspended_until = 0

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _step_towards(self, target, walkable_fn, current_time):
        """Calculates path towards target and takes a step when ready. Returns True if reached or path exists."""
        if (self.x, self.y) == target:
            self.path = []
            return True

        # Replan route periodically or if path is empty
        if not self.path or (current_time - self.last_replan_time > self.replan_interval):
            self.path = find_path((self.x, self.y), target, walkable_fn)
            self.last_replan_time = current_time

        if not self.path:
            return False

        if current_time - self.last_move_time > self.move_delay:
            self.x, self.y = self.path[0]
            self.path.pop(0)
            self.last_move_time = current_time
        return True

    def _suspend(self, current_time):
        """Temporarily suspends the current goal."""
        self.previous_state = self.state
        self.state = STATE_SUSPENDED
        self.suspended_until = current_time + self.suspend_duration
        self.blocked_since = None
        self.path = []

    def _register_blocked(self, current_time):
        """Tracks blocked time and transitions to suspended if threshold is exceeded."""
        if self.blocked_since is None:
            self.blocked_since = current_time
        elif current_time - self.blocked_since > self.blocked_timeout:
            self._suspend(current_time)

    def _adjacent_tiles(self, pos):
        x, y = pos
        return [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]

    # ------------------------------------------------------------------
    # Main update loop
    # ------------------------------------------------------------------
    def update(self, world, rock_pos):
        current_time = pygame.time.get_ticks()

        # Perception: tiles Timo can walk on (world obstacles + current rock position)
        def walkable(x, y):
            return world.is_walkable(x, y) and [x, y] != rock_pos

        if self.state == STATE_INSPECTING:
            self._do_inspecting(world, walkable, current_time)
        elif self.state == STATE_GATHERING_WOOD:
            self._do_gathering(world, walkable, current_time)
        elif self.state == STATE_GOING_TO_REPAIR:
            self._do_going_to_repair(world, walkable, current_time)
        elif self.state == STATE_REPAIRING:
            self._do_repairing(world, current_time)
        elif self.state == STATE_SUSPENDED:
            if current_time >= self.suspended_until:
                self.state = self.previous_state

    # ------------------------------------------------------------------
    # State Behaviors
    # ------------------------------------------------------------------
    def _do_inspecting(self, world, walkable, current_time):
        if not self._step_towards(self.inspect_position, walkable, current_time):
            self._register_blocked(current_time)
            return
        self.blocked_since = None
        if (self.x, self.y) == self.inspect_position:
            # Inspection: detect bridge needs maintenance and determine materials (GDD Section 5)
            self.broken_tiles = list(world.bridge_tiles)
            self.required_materials["wood"] = BRIDGE_REPAIR_WOOD_REQUIRED
            if self.inventory["wood"] >= self.required_materials["wood"]:
                self.state = STATE_GOING_TO_REPAIR
            else:
                self.state = STATE_GATHERING_WOOD

    def _do_gathering(self, world, walkable, current_time):
        if self.inventory["wood"] >= self.required_materials["wood"]:
            self.state = STATE_GOING_TO_REPAIR
            return

        trees = world.get_trees()

        # Already next to a tree? -> harvest with delay
        for tree in trees:
            if (self.x, self.y) in self._adjacent_tiles(tree):
                self.path = []
                if current_time - self.last_harvest_time > self.harvest_delay:
                    self.inventory["wood"] += world.harvest_tree(*tree)
                    self.last_harvest_time = current_time
                return

        # Find the shortest path to an accessible tile adjacent to any tree
        best_path = None
        for tree in trees:
            for adj in self._adjacent_tiles(tree):
                if walkable(*adj):
                    path = find_path((self.x, self.y), adj, walkable)
                    if path and (best_path is None or len(path) < len(best_path)):
                        best_path = path

        if best_path is None:
            self._register_blocked(current_time)  # No reachable trees
            return

        self.blocked_since = None
        self.path = best_path
        if current_time - self.last_move_time > self.move_delay:
            self.x, self.y = self.path[0]
            self.path.pop(0)
            self.last_move_time = current_time

    def _do_going_to_repair(self, world, walkable, current_time):
        if not self._step_towards(self.repair_position, walkable, current_time):
            # Path blocked (e.g. by the rock): retry and eventually suspend
            self._register_blocked(current_time)
            return
        self.blocked_since = None
        if (self.x, self.y) == self.repair_position:
            needed = self.required_materials["wood"]
            if self.inventory["wood"] >= needed:
                # GDD 24.1: Timo consumes required wood only when repair begins
                self.inventory["wood"] -= needed
                self.state = STATE_REPAIRING
                self.repair_start_time = current_time
                world.set_bridge_state("repairing")
                self.path = []
            else:
                self.state = STATE_GATHERING_WOOD

    def _do_repairing(self, world, current_time):
        # GDD Section 4.6 & Appendix A: Repair state with construction duration
        if current_time - self.repair_start_time >= self.repair_duration:
            world.set_bridge_state("repaired")
            self.state = STATE_DONE
            self.path = []


