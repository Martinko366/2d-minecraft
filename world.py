# world.py
import random
from config import *

def generate_world():
    """
    Generate the world grid (a 2D list) and a corresponding terrain heightmap.
    Blocks above the surface are AIR; the surface is GRASS; just below are DIRT,
    and deeper levels are filled with STONE, with occasional caves and ores.
    """
    world = [[AIR for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]
    terrain_heights = []
    height = WORLD_HEIGHT // 2
    for x in range(WORLD_WIDTH):
        height += random.choice([-1, 0, 1])
        height = max(WORLD_HEIGHT // 4, min(WORLD_HEIGHT - 10, height))
        terrain_heights.append(height)
        for y in range(WORLD_HEIGHT):
            if y < height:
                world[x][y] = AIR
            elif y == height:
                world[x][y] = GRASS
            elif y <= height + 3:
                world[x][y] = DIRT
            else:
                if random.random() < 0.05:
                    world[x][y] = AIR  # carve a cave
                else:
                    chance = random.random()
                    if chance < CHANCE_COAL:
                        world[x][y] = COAL
                    elif chance < CHANCE_IRON:
                        world[x][y] = IRON
                    elif chance < CHANCE_GOLD:
                        world[x][y] = GOLD
                    elif chance < CHANCE_DIAMOND:
                        world[x][y] = DIAMOND
                    else:
                        world[x][y] = STONE
    return world, terrain_heights

def place_house(world, terrain_heights, x):
    """
    Place a simple house structure (5 blocks wide x 4 blocks tall) on the surface.
    The walls are built with STONE and the interior is left AIR.
    """
    house_width = 5
    house_height = 4
    if x < 0 or x + house_width >= WORLD_WIDTH:
        return
    ground = min(terrain_heights[x : x + house_width])
    floor_y = ground - 1
    for i in range(house_width):
        for j in range(house_height):
            wx = x + i
            wy = floor_y - house_height + 1 + j
            if 0 <= wy < WORLD_HEIGHT:
                if i == 0 or i == house_width - 1 or j == 0 or j == house_height - 1:
                    world[wx][wy] = STONE
                else:
                    world[wx][wy] = AIR

def place_well(world, terrain_heights, x):
    """
    Place a small 3x3 well on the surface (with a hollow center).
    """
    well_width = 3
    well_height = 3
    if x < 0 or x + well_width >= WORLD_WIDTH:
        return
    ground = min(terrain_heights[x : x + well_width])
    floor_y = ground - 1
    for i in range(well_width):
        for j in range(well_height):
            wx = x + i
            wy = floor_y - well_height + 1 + j
            if 0 <= wy < WORLD_HEIGHT:
                if i == 1 and j == 1:
                    world[wx][wy] = AIR
                else:
                    world[wx][wy] = STONE

def generate_structures(world, terrain_heights):
    """
    Randomly place structures (houses or wells) along the surface.
    """
    x = 0
    while x < WORLD_WIDTH - 5:
        if random.random() < STRUCTURE_SPAWN_CHANCE:
            if random.random() < HOUSE_PROBABILITY:
                place_house(world, terrain_heights, x)
            else:
                place_well(world, terrain_heights, x)
            x += 6  # skip a few columns to avoid overlapping structures
        else:
            x += 1
