# collision.py
import pygame
from config import TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT, COLLISION_EPSILON, AIR

def horizontal_collision(px, py, dx, player_width, player_height, world):
    """
    Adjust horizontal movement by dx so that the player does not penetrate solid blocks.
    Instead of making tiny adjustments, we "snap" the player directly to the nearest safe tile boundary.
    """
    new_x = px + dx
    # Create the player's new rectangle
    player_rect = pygame.Rect(new_x, py, player_width, player_height)
    
    # Determine the range of tiles to check
    x_start = max(0, int(new_x // TILE_SIZE))
    x_end = min(WORLD_WIDTH, int((new_x + player_width) // TILE_SIZE) + 1)
    y_start = max(0, int(py // TILE_SIZE))
    y_end = min(WORLD_HEIGHT, int((py + player_height) // TILE_SIZE) + 1)
    
    # For each potentially colliding block...
    for bx in range(x_start, x_end):
        for by in range(y_start, y_end):
            if world[bx][by] != AIR:
                block_rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player_rect.colliderect(block_rect):
                    if dx > 0:
                        # Moving right; snap the player's right side to the block's left side.
                        new_x = bx * TILE_SIZE - player_width - COLLISION_EPSILON
                    elif dx < 0:
                        # Moving left; snap the player's left side to the block's right side.
                        new_x = (bx + 1) * TILE_SIZE + COLLISION_EPSILON
                    # Update the player's rectangle after snapping.
                    player_rect.x = new_x
    return new_x

def vertical_collision(px, py, dy, player_width, player_height, world):
    """
    Adjust vertical movement by dy so that the player does not penetrate solid blocks.
    We snap the player to the nearest safe tile boundary on collision.
    Returns the new y–position and a boolean 'landed' indicating a collision when falling.
    """
    new_y = py + dy
    player_rect = pygame.Rect(px, new_y, player_width, player_height)
    landed = False
    
    x_start = max(0, int(px // TILE_SIZE))
    x_end = min(WORLD_WIDTH, int((px + player_width) // TILE_SIZE) + 1)
    y_start = max(0, int(new_y // TILE_SIZE))
    y_end = min(WORLD_HEIGHT, int((new_y + player_height) // TILE_SIZE) + 1)
    
    for bx in range(x_start, x_end):
        for by in range(y_start, y_end):
            if world[bx][by] != AIR:
                block_rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player_rect.colliderect(block_rect):
                    if dy > 0:
                        # Falling; snap the player's bottom to the top of the block.
                        new_y = by * TILE_SIZE - player_height - COLLISION_EPSILON
                        landed = True
                    elif dy < 0:
                        # Jumping upward; snap the player's top to the bottom of the block.
                        new_y = (by + 1) * TILE_SIZE + COLLISION_EPSILON
                    player_rect.y = new_y
    return new_y, landed
