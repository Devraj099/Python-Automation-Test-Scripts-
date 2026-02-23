"""
🤖 MAZE ESCAPE - AUTO SOLVER
==============================
Watches an AI solve all 3 maze levels automatically using BFS pathfinding.
It collects every star before heading to the exit for maximum score!

Run: python maze_auto.py [--speed fast|normal|slow]
"""

import os
import sys
import time
import argparse
from collections import deque
from copy import deepcopy

# ─────────────────────────────────────────────
# ANSI COLORS
# ─────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
GRAY    = "\033[90m"
MAGENTA = "\033[95m"
BLUE    = "\033[94m"

def c(text, *codes):
    return "".join(codes) + str(text) + RESET

# ─────────────────────────────────────────────
# LEVELS  (same as original game)
# ─────────────────────────────────────────────
LEVELS = [
    {
        "name": "The Beginning",
        "grid": [
            "###########",
            "#@        #",
            "# ####### #",
            "# #     # #",
            "# # ### # #",
            "# # # * # #",
            "# # ### # #",
            "# #   * # #",
            "# ####### #",
            "#         E",
            "###########",
        ],
    },
    {
        "name": "The Winding Path",
        "grid": [
            "#############",
            "#@          #",
            "########## ##",
            "#    *     ##",
            "# ###########",
            "# #         #",
            "# # ####### #",
            "# # # *   # #",
            "# # # ### # #",
            "# #       # #",
            "# ######### #",
            "#           E",
            "#############",
        ],
    },
    {
        "name": "The Labyrinth",
        "grid": [
            "###############",
            "#@    #   *   #",
            "# ### # ##### #",
            "# # # #     # #",
            "# # # ##### # #",
            "# #   *   # # #",
            "# ####### # # #",
            "# #       # # #",
            "# # ####### # #",
            "# #   *   # # #",
            "# ####### # # #",
            "#         #   E",
            "###############",
        ],
    },
]

# ─────────────────────────────────────────────
# BFS PATHFINDER
# ─────────────────────────────────────────────
def bfs(grid, start, targets):
    """
    BFS from `start` to the nearest cell in `targets`.
    Returns list of (r, c) positions forming the path (inclusive of start & end),
    or None if unreachable.
    """
    rows = len(grid)
    cols = len(grid[0])
    queue = deque()
    queue.append((start, [start]))
    visited = {start}

    while queue:
        (r, c), path = queue.popleft()
        if (r, c) in targets:
            return path
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                cell = grid[nr][nc]
                if cell != '#':
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))
    return None  # unreachable

def solve_level(level_data):
    """
    Plan the full route:
      1. Visit every star (greedy nearest-star order)
      2. Then go to exit E
    Returns a list of (r,c) waypoints covering the complete journey.
    """
    raw_grid = level_data["grid"]
    # Build mutable grid
    grid = [list(row) for row in raw_grid]
    cols = max(len(r) for r in grid)
    for row in grid:
        while len(row) < cols:
            row.append(' ')

    # Locate key cells
    start = None
    exit_pos = None
    stars = []
    for r, row in enumerate(grid):
        for col, cell in enumerate(row):
            if cell == '@':
                start = (r, col)
            elif cell == 'E':
                exit_pos = (r, col)
            elif cell == '*':
                stars.append((r, col))

    full_path = [start]
    current = start
    remaining_stars = list(stars)

    # Greedy: always go to nearest reachable star
    while remaining_stars:
        path = bfs(grid, current, set(remaining_stars))
        if path is None:
            break  # unreachable star — skip
        # Append path (skip first node, already in full_path)
        full_path.extend(path[1:])
        current = path[-1]
        remaining_stars.remove(current)

    # Finally go to exit
    path_to_exit = bfs(grid, current, {exit_pos})
    if path_to_exit:
        full_path.extend(path_to_exit[1:])

    return full_path, grid, stars, exit_pos

# ─────────────────────────────────────────────
# RENDERER
# ─────────────────────────────────────────────
def render(grid, player, trail, stars_left, stars_total,
           moves, score, level_num, level_name, message,
           planned_path, start_time):
    os.system('cls' if os.name == 'nt' else 'clear')
    elapsed = int(time.time() - start_time)

    print(c("╔════════════════════════════════════════╗", CYAN))
    print(c(f"║  🤖 MAZE AUTO-SOLVER  — Level {level_num}/3     ║", CYAN))
    print(c(f"║  {level_name:<38}║", CYAN))
    print(c("╚════════════════════════════════════════╝", CYAN))
    print(
        f"  {c('Moves:', GRAY)} {c(moves, YELLOW)}   "
        f"{c('Stars:', GRAY)} {c(f'{stars_total-len(stars_left)}/{stars_total}', YELLOW)}   "
        f"{c('Time:', GRAY)} {c(f'{elapsed}s', YELLOW)}   "
        f"{c('Score:', GRAY)} {c(score, GREEN)}"
    )
    print()

    # Build set of trail and planned path for rendering
    trail_set   = set(trail)
    planned_set = set(planned_path)

    for r, row in enumerate(grid):
        line = ""
        for col, cell in enumerate(row):
            pos = (r, col)
            if pos == player:
                line += c("@", GREEN, BOLD)
            elif cell == '#':
                line += c("█", GRAY)
            elif cell == 'E':
                line += c("E", RED, BOLD)
            elif cell == '*':
                line += c("★", YELLOW, BOLD)
            elif pos in trail_set:
                line += c("·", BLUE)       # breadcrumb trail
            elif pos in planned_set:
                line += c("░", MAGENTA)    # planned future path
            else:
                line += " "
        print("  " + line)

    print()
    print(c("  Trail: · (visited)   Planned: ░ (upcoming)", GRAY))
    if message:
        print(c(f"\n  {message}", MAGENTA, BOLD))

# ─────────────────────────────────────────────
# ANIMATE ONE LEVEL
# ─────────────────────────────────────────────
def animate_level(level_index, delay, total_score):
    level_data = LEVELS[level_index]
    level_name = level_data["name"]
    level_num  = level_index + 1

    full_path, grid, all_stars, exit_pos = solve_level(level_data)

    stars_left   = list(all_stars)
    stars_total  = len(all_stars)
    trail        = []
    moves        = 0
    start_time   = time.time()
    message      = f"🤖 AI planning route... collecting {stars_total} star(s) first!"

    # Show initial state briefly
    render(grid, full_path[0], trail, stars_left, stars_total,
           moves, total_score, level_num, level_name, message,
           full_path[1:], start_time)
    time.sleep(delay * 4)

    for i, pos in enumerate(full_path):
        r, c_pos = pos
        cell = grid[r][c_pos]

        # Collect star
        if cell == '*':
            grid[r][c_pos] = ' '
            stars_left.remove(pos)
            message = "⭐ Star collected!"
            total_score += 50
        elif pos == exit_pos:
            message = "🎉 Exit reached!"
        elif i == 0:
            message = f"🤖 Starting level {level_num}..."
        elif not stars_left:
            message = "🚀 All stars collected — heading to exit!"
        else:
            message = f"🤖 Navigating... {len(stars_left)} star(s) remaining"

        if i > 0:
            trail.append(full_path[i-1])
            moves += 1

        # Upcoming path (everything after current position)
        planned = full_path[i+1:]

        # Calculate live score
        elapsed   = int(time.time() - start_time)
        lv_score  = (stars_total - len(stars_left)) * 50 + max(0, 200 - moves * 2 - elapsed)
        disp_score = total_score - (stars_total - len(stars_left)) * 50 + lv_score

        render(grid, pos, trail, stars_left, stars_total,
               moves, disp_score, level_num, level_name, message,
               planned, start_time)

        time.sleep(delay)

    # Pause on completed level
    elapsed   = int(time.time() - start_time)
    bonus     = max(0, 200 - moves * 2 - elapsed)
    lv_score  = stars_total * 50 + bonus
    total_score_final = total_score - (stars_total * 50) + lv_score  # recalc from base

    # Actually compute cleanly:
    base       = total_score  # score before this level
    lv_earned  = stars_total * 50 + max(0, 200 - moves * 2 - elapsed)

    time.sleep(delay * 5)
    return base + lv_earned, moves, elapsed

# ─────────────────────────────────────────────
# TITLE / WIN SCREENS
# ─────────────────────────────────────────────
def show_title(speed_label):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(c(f"""
  ╔══════════════════════════════════════════╗
  ║                                          ║
  ║     🤖  MAZE ESCAPE — AUTO SOLVER  🤖    ║
  ║                                          ║
  ║  Watch AI solve all 3 mazes using BFS    ║
  ║  pathfinding. Stars are collected        ║
  ║  greedily (nearest-first) before exit.   ║
  ║                                          ║
  ║  Trail  ·  = cells already visited       ║
  ║  Ahead  ░  = planned future path         ║
  ║                                          ║
  ║  Speed: {speed_label:<34}║
  ║                                          ║
  ║          Press ENTER to watch            ║
  ║                                          ║
  ╚══════════════════════════════════════════╝
""", CYAN))
    input("  > ")

def show_summary(level_stats, grand_total):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(c("""
  ╔══════════════════════════════════════════╗
  ║     🏆  ALL LEVELS SOLVED!  🏆           ║
  ╚══════════════════════════════════════════╝
""", GREEN, BOLD))

    for i, (score, moves, elapsed) in enumerate(level_stats):
        lvl = LEVELS[i]
        print(c(f"  Level {i+1}: {lvl['name']}", CYAN))
        print(f"    Moves: {c(moves, YELLOW)}   Time: {c(f'{elapsed}s', YELLOW)}   Score: {c(score, GREEN)}")
        print()

    print(c(f"  ══════════════════════════════════", GRAY))
    print(c(f"  Grand Total Score : {grand_total}", YELLOW, BOLD))
    print()

    # Algorithm explanation
    print(c("  How the AI works:", CYAN, BOLD))
    print(c("  ─────────────────────────────────", GRAY))
    print("  1. " + c("BFS", YELLOW) + " maps the shortest path between any two points")
    print("  2. Stars are collected in " + c("nearest-first (greedy)", YELLOW) + " order")
    print("  3. After all stars, BFS finds the " + c("shortest path to exit", YELLOW))
    print("  4. The " + c("· trail", BLUE) + " shows cells already visited")
    print("  5. The " + c("░ overlay", MAGENTA) + " shows the planned upcoming route")
    print()
    print(c("  Press ENTER to exit.", GRAY))
    input()

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Maze Auto Solver")
    parser.add_argument(
        "--speed",
        choices=["fast", "normal", "slow"],
        default="normal",
        help="Animation speed (default: normal)"
    )
    args = parser.parse_args()

    delays = {"fast": 0.05, "normal": 0.18, "slow": 0.40}
    delay  = delays[args.speed]
    speed_labels = {"fast": "Fast  ⚡", "normal": "Normal 🚶", "slow": "Slow  🐢"}

    show_title(speed_labels[args.speed])

    grand_total  = 0
    level_stats  = []

    for i in range(len(LEVELS)):
        new_total, moves, elapsed = animate_level(i, delay, grand_total)
        earned = new_total - grand_total
        level_stats.append((earned, moves, elapsed))
        grand_total = new_total

        if i < len(LEVELS) - 1:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(c(f"\n  ✅ Level {i+1} complete! Score so far: {grand_total}", GREEN, BOLD))
            print(c(f"  Loading level {i+2}...\n", GRAY))
            time.sleep(1.5)

    show_summary(level_stats, grand_total)

if __name__ == "__main__":
    main()