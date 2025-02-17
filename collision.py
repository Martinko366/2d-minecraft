# collision.py
import pygame
from config import TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT, COLLISION_EPSILON, AIR

def horizontal_collision(px, py, dx, player_width, player_height, world):
    """
    Attempt to move horizontally by dx. If the resulting position would collide with
    any solid block, cancel the movement (return the original px).
    """
    new_x = px + dx
    player_rect = pygame.Rect(new_x, py, player_width, player_height)
    x_start = max(0, int(new_x // TILE_SIZE))
    x_end = min(WORLD_WIDTH, int((new_x + player_width) // TILE_SIZE) + 1)
    y_start = max(0, int(py // TILE_SIZE))
    y_end = min(WORLD_HEIGHT, int((py + player_height) // TILE_SIZE) + 1)
    for bx in range(x_start, x_end):
        for by in range(y_start, y_end):
            if world[bx][by] != AIR:
                block_rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player_rect.colliderect(block_rect):
                    # Collision detected: cancel horizontal movement.
                    return px
    return new_x

def vertical_collision(px, py, dy, player_width, player_height, world):
    """
    Attempt to move vertically by dy. If moving downward and a collision is detected,
    snap the player's bottom to the top of the colliding block; if moving upward, cancel
    the movement. If a collision is detected (and cannot be resolved), return the original py.
    Returns: (new_y, landed) where landed is True if a downward collision occurred.
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
                        # If falling, place the player's bottom flush with the block's top.
                        new_y = by * TILE_SIZE - player_height
                        landed = True
                        # Re-check for collisions at the adjusted position.
                        player_rect = pygame.Rect(px, new_y, player_width, player_height)
                        for bx2 in range(x_start, x_end):
                            for by2 in range(y_start, y_end):
                                if world[bx2][by2] != AIR:
                                    block_rect2 = pygame.Rect(bx2 * TILE_SIZE, by2 * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                                    if player_rect.colliderect(block_rect2):
                                        return py, False  # Unable to resolve; cancel vertical movement.
                    else:
                        # If moving upward, cancel the movement.
                        return py, False
    return new_y, landed
