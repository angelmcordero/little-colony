import pygame
import sys
from settings import *
from world import World
from entities import Player, Agent
from pathfinding import find_path

def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))

def draw_world(surface, world):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            tile_id = world.grid[x][y]
            rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if tile_id == TILE_WATER:
                pygame.draw.rect(surface, COLOR_WATER, rect)
            elif tile_id == TILE_TREE:
                pygame.draw.rect(surface, COLOR_TREE, rect)
            elif tile_id == TILE_BRIDGE_BROKEN:
                pygame.draw.rect(surface, COLOR_BRIDGE_BROKEN, rect)
            elif tile_id == TILE_BRIDGE_REPAIRING:
                pygame.draw.rect(surface, COLOR_BRIDGE_REPAIRING, rect)
            elif tile_id == TILE_BRIDGE_REPAIRED:
                pygame.draw.rect(surface, COLOR_BRIDGE_REPAIRED, rect)


def calculate_harmony(world, rock_pos):
    """Calculates Ecosystem Harmony following GDD Section 11.1."""
    harmony = INITIAL_HARMONY  # Base 42%
    # Builder access condition (+8%): rock is not blocking the repair position (9, 10)
    if tuple(rock_pos) != INITIAL_ROCK_POS:
        harmony += 8
    # Bridge repaired condition (+12%)
    if world.bridge_state == "repaired":
        harmony += 12
    return harmony


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Little Colony - Causal Chain")
    clock = pygame.time.Clock()

    game_world = World()
    player = Player(2, 2)
    rock_pos = list(INITIAL_ROCK_POS)
    
    # Initialize Timo (GDD Section 5)
    timo = Agent(5, 10, COLOR_TIMO)

    pygame.font.init()
    font_hud = pygame.font.SysFont("Arial", 16, bold=True)
    font_small = pygame.font.SysFont("Arial", 13)

    debug_mode = False  # Toggle with F3 (GDD Section 21.2)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player.move(-1, 0, game_world, rock_pos)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.move(1, 0, game_world, rock_pos)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    player.move(0, -1, game_world, rock_pos)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    player.move(0, 1, game_world, rock_pos)
                
                # Push rock with legal placement rules (GDD Section 6 & 15)
                elif event.key == pygame.K_e:
                    dx = rock_pos[0] - player.x
                    dy = rock_pos[1] - player.y
                    # Check if player is directly adjacent (Manhattan distance == 1)
                    if abs(dx) + abs(dy) == 1:
                        occupied = [(player.x, player.y), (timo.x, timo.y)]
                        target_x = rock_pos[0] + dx
                        target_y = rock_pos[1] + dy
                        if game_world.is_legal_rock_pos(target_x, target_y, occupied):
                            rock_pos[0] = target_x
                            rock_pos[1] = target_y
                        else:
                            # Fallback to legal adjacent tiles (e.g. North) if direct push is blocked by water
                            for alt_dx, alt_dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                                alt_x = rock_pos[0] + alt_dx
                                alt_y = rock_pos[1] + alt_dy
                                if game_world.is_legal_rock_pos(alt_x, alt_y, occupied):
                                    rock_pos[0] = alt_x
                                    rock_pos[1] = alt_y
                                    break


                # Reset rock key for testing/recovery (GDD Section 15 & 21)
                elif event.key == pygame.K_r:
                    rock_pos = list(INITIAL_ROCK_POS)

                # Toggle developer debug view (GDD Section 21.2)
                elif event.key == pygame.K_F3:
                    debug_mode = not debug_mode

        # --- SIMULATION LOGIC ---
        timo.update(game_world, rock_pos)
        harmony = calculate_harmony(game_world, rock_pos)

        # --- RENDERING ---
        screen.fill(COLOR_GRASS)
        draw_world(screen, game_world)
        draw_grid(screen)

        # Draw Timo planned path in debug mode
        if debug_mode and timo.path:
            for px, py in timo.path:
                center = (px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2)
                pygame.draw.circle(screen, (255, 230, 120), center, 4)

        # Draw Rock (Gray), Timo (Yellow), and Player (White)
        pygame.draw.rect(screen, COLOR_ROCK, (rock_pos[0] * TILE_SIZE, rock_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, timo.color, (timo.x * TILE_SIZE, timo.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, COLOR_PLAYER, (player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        # --- HUD (GDD Section 13: Minimal Interface) ---
        # Upper-left: Ecosystem Harmony: XX%
        harmony_box = pygame.Surface((220, 32), pygame.SRCALPHA)
        harmony_box.fill((20, 20, 20, 180))
        screen.blit(harmony_box, (8, 8))
        harmony_text = font_hud.render(f"Ecosystem Harmony: {harmony}%", True, (240, 240, 240))
        screen.blit(harmony_text, (16, 14))

        # Contextual prompt when adjacent to the movable rock (GDD Section 4.7)
        dist_x = abs(player.x - rock_pos[0])
        dist_y = abs(player.y - rock_pos[1])
        if dist_x + dist_y == 1:
            prompt_surf = font_small.render("[E] Move Rock", True, (255, 255, 255))
            screen.blit(prompt_surf, (rock_pos[0] * TILE_SIZE, rock_pos[1] * TILE_SIZE - 16))

        # --- DEVELOPER DEBUG OVERLAY (GDD Section 21.2) ---
        if debug_mode:
            dbg_bg = pygame.Surface((320, 120), pygame.SRCALPHA)
            dbg_bg.fill((10, 10, 25, 220))
            screen.blit(dbg_bg, (8, 48))

            curr_time = pygame.time.get_ticks()
            repair_str = ""
            if timo.state == "REPAIRING":
                pct = int(min(1.0, (curr_time - timo.repair_start_time) / timo.repair_duration) * 100)
                repair_str = f" ({pct}%)"

            dbg_lines = [
                f"[DEBUG MODE - Press F3 to Hide]",
                f"Timo: {timo.state}{repair_str} | Wood: {timo.inventory['wood']}/{timo.required_materials['wood']}",
                f"Bridge: {game_world.bridge_state.upper()}",
                f"Rock Pos: {rock_pos} | Player: ({player.x}, {player.y})",
                f"[R] Reset Rock Position"
            ]
            for i, line in enumerate(dbg_lines):
                col = (255, 220, 80) if i == 0 else (220, 220, 220)
                screen.blit(font_small.render(line, True, col), (16, 52 + i * 20))
        else:
            hint = font_small.render("F3: Debug", True, (160, 160, 160))
            screen.blit(hint, (8, SCREEN_HEIGHT - 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()