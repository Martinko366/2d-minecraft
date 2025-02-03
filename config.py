# config.py
import pygame

# Screen settings
WIDTH = 800
HEIGHT = 600

# Tile and world settings
TILE_SIZE = 40  # size (in pixels) of each block
WORLD_WIDTH = 400  # in blocks
WORLD_HEIGHT = 100  # in blocks

# Block type IDs
AIR     = 0
GRASS   = 1
DIRT    = 2
STONE   = 3
COAL    = 4
IRON    = 5
GOLD    = 6
DIAMOND = 7

# Colors for blocks (RGB)
colors = {
    AIR:     (135, 206, 235),  # sky
    GRASS:   (0, 155, 0),
    DIRT:    (120, 72, 0),
    STONE:   (100, 100, 100),
    COAL:    (20, 20, 20),
    IRON:    (180, 180, 180),
    GOLD:    (255, 215, 0),
    DIAMOND: (0, 255, 255)
}

# Inventory settings
inventory_order = [DIRT, GRASS, STONE, COAL, IRON, GOLD, DIAMOND]
default_inventory = {
    GRASS: 0,
    DIRT: 10,
    STONE: 0,
    COAL: 0,
    IRON: 0,
    GOLD: 0,
    DIAMOND: 0
}

# Player settings
MOVE_SPEED = 200                # pixels per second
JUMP_VELOCITY = -400            # pixels per second (negative = upward)
GRAVITY = 1000                  # pixels per second^2

# Fall damage settings
FALL_SAFE_HEIGHT = 4            # in blocks; falling less than this is safe
FALL_DAMAGE_PER_BLOCK = 1       # hearts lost per extra block fallen

# Health settings
MAX_HEALTH = 10                 # hearts
REGEN_TIME = 10                 # seconds to regenerate 1 heart

# Collision helper
COLLISION_EPSILON = 0.1         # small offset to reduce jitter in collision resolution

# Structure generation settings
STRUCTURE_SPAWN_CHANCE = 0.02   # chance per column to spawn a structure
HOUSE_PROBABILITY = 0.5         # chance to spawn a house versus a well

# Ore generation chances
CHANCE_COAL    = 0.01
CHANCE_IRON    = 0.015
CHANCE_GOLD    = 0.017
CHANCE_DIAMOND = 0.019
