# config.py
import pygame

# Screen settings
WIDTH = 800
HEIGHT = 600

# Video resolution options (for settings)
RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1920, 1080)
]

# World and tile settings
TILE_SIZE = 40             # Size (in pixels) of each block
WORLD_WIDTH = 200          # in blocks
WORLD_HEIGHT = 100         # in blocks

NUM_SAVE_SLOTS = 5         # Number of save slots available

# Block type IDs
AIR     = 0
GRASS   = 1
DIRT    = 2
STONE   = 3
COAL    = 4
IRON    = 5
GOLD    = 6
DIAMOND = 7
WOOD    = 8
LEAVES  = 9

# Colors for blocks (RGB)
colors = {
    AIR:     (135, 206, 235),  # sky blue
    GRASS:   (0, 155, 0),
    DIRT:    (120, 72, 0),
    STONE:   (100, 100, 100),
    COAL:    (20, 20, 20),
    IRON:    (180, 180, 180),
    GOLD:    (255, 215, 0),
    DIAMOND: (0, 255, 255),
    WOOD:    (101, 67, 33),
    LEAVES:  (34, 139, 34)
}

# Inventory settings
inventory_order = [DIRT, GRASS, STONE, COAL, IRON, GOLD, DIAMOND, WOOD, LEAVES]
default_inventory = {
    GRASS: 0,
    DIRT: 10,
    STONE: 0,
    COAL: 0,
    IRON: 0,
    GOLD: 0,
    DIAMOND: 0,
    WOOD: 0,
    LEAVES: 0
}

# Player settings
MOVE_SPEED = 200         # pixels per second
JUMP_VELOCITY = -500     # negative = upward
GRAVITY = 1000           # pixels per second^2

# Fall damage settings
FALL_SAFE_HEIGHT = 3     # in blocks (falling less than this is safe)
FALL_DAMAGE_PER_BLOCK = 1

# Health settings
MAX_HEALTH = 10          # hearts
REGEN_TIME = 10          # seconds to regenerate 1 heart

# Collision helper
COLLISION_EPSILON = 0.1

# Generation parameters
TREE_CHANCE = 0.05  # chance per column to generate a tree
