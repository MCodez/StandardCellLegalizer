import shapely.geometry as sg
import shapely.affinity as affinity
import matplotlib.pyplot as plt
import numpy as np

# Given inputs
BLOCK_COORDS = [(0, 0), (1000, 0), (1000, 2000), (800, 2000), (800, 1500),
                (400, 1500), (400, 2000), (100, 2000), (100, 1000), (0, 1000), (0, 0)]
GRID_HEIGHT = 20

# Function to snap a polygon to grid
def snap_to_grid(polygon, grid_size):
    minx, miny, _, _ = polygon.bounds
    dx = round(minx / grid_size) * grid_size - minx
    dy = round(miny / grid_size) * grid_size - miny
    return affinity.translate(polygon, dx, dy)

# Function to check if a cell is completely inside the block
def is_inside_block(cell, block_boundary):
    return block_boundary.contains(cell)

# Function to check overlap with other standard cells
def has_overlap(cell, cells):
    for other in cells:
        if other != cell and cell.intersects(other):
            return True
    return False

# Function to check overlap with block boundary
def overlap_with_boundary(cell, block_boundary):
    return not block_boundary.contains(cell)

# Compute displacement required to resolve overlaps safely
def compute_displacement(cell, block_boundary, cells, grid_size):
    directions = {"left": float("inf"), "right": float("inf"), "up": float("inf"), "down": float("inf")}

    minx, miny, maxx, maxy = cell.bounds

    # Check how much we need to move in each direction to resolve overlaps
    for other in cells:
        if other != cell and cell.intersects(other):
            ox_minx, oy_miny, ox_maxx, oy_maxy = other.bounds
            directions["left"] = min(directions["left"], maxx - ox_minx + grid_size)
            directions["right"] = min(directions["right"], ox_maxx - minx + grid_size)
            directions["down"] = min(directions["down"], maxy - oy_miny + grid_size)
            directions["up"] = min(directions["up"], oy_maxy - miny + grid_size)

    # Ensure moves do not push the cell outside the block boundary
    if minx - directions["left"] < 0:
        directions["left"] = float("inf")
    if maxx + directions["right"] > 1000:
        directions["right"] = float("inf")
    if miny - directions["down"] < 0:
        directions["down"] = float("inf")
    if maxy + directions["up"] > 2000:
        directions["up"] = float("inf")

    # Find the best move with minimum displacement
    best_move = min(directions, key=directions.get)
    return best_move, directions[best_move]

# Function to resolve overlaps safely
def resolve_overlaps(cells, block_boundary, grid_size):
    updated_cells = [snap_to_grid(cell, grid_size) for cell in cells]

    for i, cell in enumerate(updated_cells):
        original_cell = cell
        seen_positions = set()

        while has_overlap(cell, updated_cells) or overlap_with_boundary(cell, block_boundary):
            best_move, displacement = compute_displacement(cell, block_boundary, updated_cells, grid_size)
            if displacement == float("inf"):
                break  # No valid move

            if (cell.bounds, best_move) in seen_positions:
                updated_cells[i] = original_cell  # Restore original position on deadlock
                break

            seen_positions.add((cell.bounds, best_move))

            if best_move == "left":
                cell = affinity.translate(cell, -displacement, 0)
            elif best_move == "right":
                cell = affinity.translate(cell, displacement, 0)
            elif best_move == "up":
                cell = affinity.translate(cell, 0, displacement)
            elif best_move == "down":
                cell = affinity.translate(cell, 0, -displacement)

            # Ensure cell is inside block after movement
            if not is_inside_block(cell, block_boundary):
                updated_cells[i] = original_cell  # Restore original position if invalid move
                break

            updated_cells[i] = cell  # Update cell position

    return updated_cells

# Function to plot initial and final positions
def plot_cells(initial_cells, final_cells, block_boundary):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    titles = ["Initial Cell Placement", "Final Cell Placement"]
    
    for i, (cells, ax) in enumerate(zip([initial_cells, final_cells], axes)):
        ax.set_title(titles[i])
        ax.set_xlim(-50, 1050)
        ax.set_ylim(-50, 2050)
        ax.set_aspect('equal')

        # Plot block boundary
        x, y = block_boundary.exterior.xy
        ax.plot(x, y, "black", linewidth=2, label="Block Boundary")

        for y_grid in range(0, 2001, GRID_HEIGHT):
            ax.axhline(y=y_grid, color='gray', linestyle='--', linewidth=0.5)

        # Plot standard cells
        for j, cell in enumerate(cells):
            x, y = cell.exterior.xy
            ax.fill(x, y, alpha=0.5, label=f"Cell {j+1}" if i == 0 else None)

        #ax.legend(loc="upper right", fontsize="small")

    plt.tight_layout()
    plt.show()

def compute_distance(original_cell, new_cell):
    """Calculate displacement magnitude between original and final cell."""
    orig_x, orig_y = original_cell.centroid.xy
    new_x, new_y = new_cell.centroid.xy
    displacement = np.sqrt((new_x[0] - orig_x[0]) ** 2 + (new_y[0] - orig_y[0]) ** 2)
    return displacement

def summarize_movements(initial_cells, final_cells):
    """Summarize how much each cell moved and find the maximum movement."""
    movements = []
    max_movement = 0
    max_cell_idx = -1

    for i, (orig, new) in enumerate(zip(initial_cells, final_cells)):
        displacement = compute_distance(orig, new)
        movements.append((i, displacement))

        if displacement > max_movement:
            max_movement = displacement
            max_cell_idx = i

    # Print summary
    print("\n Movement Summary:")
    for idx, move in movements:
        print(f"  - Cell {idx}: Moved {move:.2f} units")

    print(f"\n Maximum Movement: {max_movement:.2f} units by Cell {max_cell_idx}")


# Initialize block boundary and standard cells
block_boundary = sg.Polygon(BLOCK_COORDS)

# Standard cells before filtering
all_standard_cells = [
    sg.Polygon([(50, 50), (150, 50), (150, 90), (50, 90)]),      # No overlap
    sg.Polygon([(140, 60), (260, 60), (260, 120), (140, 120)]),  # Overlaps with Cell 1
    sg.Polygon([(250, 100), (370, 100), (370, 140), (250, 140)]), # Overlaps with Cell 2
    sg.Polygon([(350, 80), (470, 80), (470, 160), (350, 160)]),   # Overlaps with Cell 3
    sg.Polygon([(50, 300), (170, 300), (170, 360), (50, 360)]),   # No overlap
    sg.Polygon([(160, 320), (310, 320), (310, 400), (160, 400)]), # Overlaps with Cell 5
    sg.Polygon([(280, 280), (430, 280), (430, 360), (280, 360)]), # Overlaps with Cell 6
    sg.Polygon([(400, 300), (550, 300), (550, 380), (400, 380)]), # Overlaps with Cell 7
    sg.Polygon([(90, 500), (210, 500), (210, 580), (90, 580)]),   # No overlap
    sg.Polygon([(200, 540), (330, 540), (330, 600), (200, 600)]), # Overlaps with Cell 9
    sg.Polygon([(320, 520), (470, 520), (470, 600), (320, 600)]), # Overlaps with Cell 10
    sg.Polygon([(50, 700), (170, 700), (170, 760), (50, 760)]),   # No overlap
    sg.Polygon([(160, 720), (320, 720), (320, 800), (160, 800)]), # Overlaps with Cell 12
    sg.Polygon([(300, 750), (460, 750), (460, 820), (300, 820)]), # Overlaps with Cell 13
    sg.Polygon([(450, 770), (600, 770), (600, 860), (450, 860)]), # Overlaps with Cell 14
    sg.Polygon([(100, 900), (240, 900), (240, 980), (100, 980)]), # No overlap
    sg.Polygon([(220, 930), (380, 930), (380, 1000), (220, 1000)]), # Overlaps with Cell 16
    sg.Polygon([(350, 920), (500, 920), (500, 1000), (350, 1000)]), # Overlaps with Cell 17
    sg.Polygon([(50, 1100), (180, 1100), (180, 1160), (50, 1160)]), # No overlap
    sg.Polygon([(160, 1120), (300, 1120), (300, 1200), (160, 1200)]), # Overlaps with Cell 19
    sg.Polygon([(280, 1150), (420, 1150), (420, 1220), (280, 1220)]), # Overlaps with Cell 20
    sg.Polygon([(400, 1170), (550, 1170), (550, 1260), (400, 1260)]), # Overlaps with Cell 21
    sg.Polygon([(100, 1300), (250, 1300), (250, 1360), (100, 1360)]), # No overlap
    sg.Polygon([(220, 1330), (370, 1330), (370, 1400), (220, 1400)]), # Overlaps with Cell 23
    sg.Polygon([(350, 1320), (500, 1320), (500, 1400), (350, 1400)]), # Overlaps with Cell 24
    sg.Polygon([(50, 1500), (200, 1500), (200, 1580), (50, 1580)]),   # No overlap
    sg.Polygon([(160, 1520), (320, 1520), (320, 1600), (160, 1600)]), # Overlaps with Cell 26
    sg.Polygon([(300, 1550), (450, 1550), (450, 1620), (300, 1620)]), # Overlaps with Cell 27
    sg.Polygon([(450, 1570), (600, 1570), (600, 1660), (450, 1660)]), # Overlaps with Cell 28
    sg.Polygon([(100, 1700), (250, 1700), (250, 1780), (100, 1780)])  # No overlap
]

# Filter out standard cells outside block boundary
standard_cells = [cell for cell in all_standard_cells if is_inside_block(cell, block_boundary)]

print(f"Total standard cells before filtering: {len(all_standard_cells)}")
print(f"Standard cells inside block after filtering: {len(standard_cells)}")

# Run overlap resolution
resolved_cells = resolve_overlaps(standard_cells, block_boundary, GRID_HEIGHT)

# Plot initial and final placements
plot_cells(standard_cells, resolved_cells, block_boundary)

# Print resolved cell positions
for idx, cell in enumerate(resolved_cells):
    print(f"Cell {idx+1} final position: {list(cell.exterior.coords)}")
    
summarize_movements(standard_cells,resolved_cells)






