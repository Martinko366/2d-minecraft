# world.py
import random
from config import *

def generate_world(seed=None):
    """
    Generate a new world using an optional seed.
    Returns a 2D world array and a terrain height list.
    """
    if seed is not None and seed != "":
        random.seed(seed)
    else:
        random.seed()
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
                    world[x][y] = AIR  # cave
                else:
                    chance = random.random()
                    if chance < 0.01:
                        world[x][y] = COAL
                    elif chance < 0.015:
                        world[x][y] = IRON
                    elif chance < 0.017:
                        world[x][y] = GOLD
                    elif chance < 0.019:
                        world[x][y] = DIAMOND
                    else:
                        world[x][y] = STONE
    return world, terrain_heights

def generate_trees(world, terrain_heights):
    """
    Generate trees on grass: a trunk (WOOD) and a simple 3x3 canopy of LEAVES.
    """
    for x in range(1, WORLD_WIDTH - 1):
        surface_y = terrain_heights[x]
        if world[x][surface_y] == GRASS and random.random() < TREE_CHANCE:
            trunk_height = random.randint(3, 5)
            for i in range(1, trunk_height + 1):
                if surface_y - i >= 0:
                    world[x][surface_y - i] = WOOD
            canopy_y = surface_y - trunk_height
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    tx = x + dx
                    ty = canopy_y + dy
                    if 0 <= tx < WORLD_WIDTH and 0 <= ty < WORLD_HEIGHT:
                        if world[tx][ty] == AIR:
                            world[tx][ty] = LEAVES

def generate_structures(world, terrain_heights):
    """
    Generate additional structures. For now, we generate trees.
    """
    generate_trees(world, terrain_heights)

# World save/load helper functions are implemented in main.py.
