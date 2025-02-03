# main.py
import pygame
import sys
import math
from config import *
from world import generate_world, generate_structures
from collision import horizontal_collision, vertical_collision

def reset_world():
    """
    Generate a new world and reset player and inventory.
    """
    world, terrain_heights = generate_world()
    generate_structures(world, terrain_heights)
    spawn_x = (WORLD_WIDTH // 2) * TILE_SIZE
    surface_y = terrain_heights[WORLD_WIDTH // 2]
    spawn_y = (surface_y - 1) * TILE_SIZE
    inventory = default_inventory.copy()
    return world, terrain_heights, spawn_x, spawn_y, inventory

pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Minecraft Clone - 2D Enhanced")
clock = pygame.time.Clock()

# Initial world and player setup.
world, terrain_heights, player_x, player_y, inventory = reset_world()
player_width = TILE_SIZE // 2
player_height = TILE_SIZE
player_color = (255, 0, 0)
player_vel_y = 0
on_ground = False
fall_start_y = None  # used to track the beginning of a fall
player_health = MAX_HEALTH
regen_timer = 0
selected_slot = 0
camera_x = 0
camera_y = 0

# Debug toggles.
show_stats = False  # F1 toggles stats display
show_fps = False    # F2 toggles FPS display

running = True
while running:
    dt = clock.tick(60) / 1000.0  # delta time in seconds

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Inventory slot selection.
            if event.key == pygame.K_1:
                selected_slot = 0
            elif event.key == pygame.K_2:
                selected_slot = 1
            elif event.key == pygame.K_3:
                selected_slot = 2
            elif event.key == pygame.K_4:
                selected_slot = 3
            elif event.key == pygame.K_5:
                selected_slot = 4
            elif event.key == pygame.K_6:
                selected_slot = 5
            elif event.key == pygame.K_7:
                selected_slot = 6
            # Toggle stats display with F1.
            elif event.key == pygame.K_F1:
                show_stats = not show_stats
            # Toggle FPS display with F2.
            elif event.key == pygame.K_F2:
                show_fps = not show_fps

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x = int((mouse_x + camera_x) // TILE_SIZE)
            world_y = int((mouse_y + camera_y) // TILE_SIZE)
            # Only allow mining/placing within a 5-block radius.
            player_center_x = player_x + player_width / 2
            player_center_y = player_y + player_height / 2
            block_center_x = world_x * TILE_SIZE + TILE_SIZE / 2
            block_center_y = world_y * TILE_SIZE + TILE_SIZE / 2
            dist = math.hypot(player_center_x - block_center_x, player_center_y - block_center_y)
            if dist <= 5 * TILE_SIZE:
                if 0 <= world_x < WORLD_WIDTH and 0 <= world_y < WORLD_HEIGHT:
                    if event.button == 1:  # left-click: mine block
                        if world[world_x][world_y] != AIR:
                            block_type = world[world_x][world_y]
                            inventory[block_type] = inventory.get(block_type, 0) + 1
                            world[world_x][world_y] = AIR
                    elif event.button == 3:  # right-click: place block
                        block_to_place = inventory_order[selected_slot]
                        if inventory.get(block_to_place, 0) > 0 and world[world_x][world_y] == AIR:
                            world[world_x][world_y] = block_to_place
                            inventory[block_to_place] -= 1

    # --- Player Movement ---
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx = -MOVE_SPEED * dt
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx = MOVE_SPEED * dt

    # Horizontal collision resolution.
    player_x = horizontal_collision(player_x, player_y, dx, player_width, player_height, world)

    # Jumping: only when on ground.
    if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and on_ground:
        player_vel_y = JUMP_VELOCITY
        on_ground = False
        fall_start_y = None

    # Apply gravity.
    player_vel_y += GRAVITY * dt
    if not on_ground and player_vel_y > 0 and fall_start_y is None:
        fall_start_y = player_y

    dy = player_vel_y * dt
    new_player_y, landed = vertical_collision(player_x, player_y, dy, player_width, player_height, world)
    if landed:
        if fall_start_y is not None:
            fall_distance = new_player_y - fall_start_y
            fall_distance_blocks = fall_distance / TILE_SIZE
            if fall_distance_blocks > FALL_SAFE_HEIGHT:
                damage = int((fall_distance_blocks - FALL_SAFE_HEIGHT) * FALL_DAMAGE_PER_BLOCK)
                player_health -= damage
            fall_start_y = None
        player_vel_y = 0
        on_ground = True
    else:
        on_ground = False

    player_y = new_player_y

    # If the player falls out of the world.
    if player_y > WORLD_HEIGHT * TILE_SIZE:
        player_health = 0

    # Health regeneration.
    if player_health < MAX_HEALTH:
        regen_timer += dt
        if regen_timer >= REGEN_TIME:
            player_health += 1
            if player_health > MAX_HEALTH:
                player_health = MAX_HEALTH
            regen_timer = 0

    # If the player dies, generate a new world.
    if player_health <= 0:
        world, terrain_heights, player_x, player_y, inventory = reset_world()
        player_vel_y = 0
        on_ground = False
        player_health = MAX_HEALTH
        fall_start_y = None
        regen_timer = 0

    # --- Update Camera ---
    camera_x = player_x - WIDTH // 2 + player_width // 2
    camera_y = player_y - HEIGHT // 2 + player_height // 2

    # --- Drawing ---
    screen.fill(colors[AIR])
    # Draw world blocks.
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            block_type = world[x][y]
            if block_type != AIR:
                rect = pygame.Rect(x * TILE_SIZE - camera_x,
                                   y * TILE_SIZE - camera_y,
                                   TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, colors[block_type], rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
    # Draw the player.
    player_rect = pygame.Rect(player_x - camera_x, player_y - camera_y, player_width, player_height)
    pygame.draw.rect(screen, player_color, player_rect)

    # Draw the inventory bar.
    inventory_slot_size = 50
    padding = 10
    total_slots = len(inventory_order)
    bar_width = total_slots * (inventory_slot_size + padding) + padding
    bar_height = inventory_slot_size + 2 * padding
    bar_x = (WIDTH - bar_width) // 2
    bar_y = HEIGHT - bar_height - 10
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    for i, block_type in enumerate(inventory_order):
        slot_x = bar_x + padding + i * (inventory_slot_size + padding)
        slot_y = bar_y + padding
        slot_rect = pygame.Rect(slot_x, slot_y, inventory_slot_size, inventory_slot_size)
        pygame.draw.rect(screen, (100, 100, 100), slot_rect)
        if i == selected_slot:
            pygame.draw.rect(screen, (255, 255, 0), slot_rect, 3)
        inner_rect = slot_rect.inflate(-10, -10)
        pygame.draw.rect(screen, colors[block_type], inner_rect)
        count_text = font.render(str(inventory.get(block_type, 0)), True, (255, 255, 255))
        screen.blit(count_text, (slot_x + 5, slot_y + 5))

    # Draw player health (hearts) at top left.
    heart_size = 20
    heart_padding = 5
    for i in range(MAX_HEALTH):
        heart_x = 10 + i * (heart_size + heart_padding)
        heart_y = 10
        heart_rect = pygame.Rect(heart_x, heart_y, heart_size, heart_size)
        if i < player_health:
            pygame.draw.rect(screen, (255, 0, 0), heart_rect)
        else:
            pygame.draw.rect(screen, (50, 50, 50), heart_rect)
        pygame.draw.rect(screen, (0, 0, 0), heart_rect, 2)

    # --- Debug Information ---
    if show_stats:
        # Display player stats on the upper left.
        stats_lines = [
            f"X: {int(player_x)}",
            f"Y: {int(player_y)}",
            f"On Ground: {on_ground}",
            f"Health: {player_health}",
            f"Velocity Y: {int(player_vel_y)}"
        ]
        for i, line in enumerate(stats_lines):
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, 40 + i * 20))
    if show_fps:
        # Display FPS in the upper right.
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
        text_rect = fps_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(fps_text, text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
