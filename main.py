# main.py
import pygame, sys, math, os, time, random
from config import *  # Assumes WIDTH, HEIGHT, TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT, default_inventory, etc.
from world import generate_world, generate_structures
from collision import horizontal_collision, vertical_collision

# ==================================================
# New Item/Block IDs for Crafting & Chests
# ==================================================
# (If not already defined in config.py, define here.)
try:
    CHEST
except NameError:
    CHEST = 10  # New block type: chest
try:
    STICK
except NameError:
    STICK = 11  # Crafted item: stick
try:
    WOOD_PLANK
except NameError:
    WOOD_PLANK = 12  # Crafted item: wood plank

# Define a sample crafting recipe dictionary.
# Keys are output IDs; values are dicts of required {item_id: quantity}.
crafting_recipes = {
    STICK: {WOOD: 2},
    WOOD_PLANK: {WOOD: 1},
    CHEST: {WOOD_PLANK: 8}  # Craft a chest from 8 wood planks.
}

# ==================================================
# World Save/Load Helpers
# ==================================================
def get_save_filename(slot):
    if not os.path.exists("saves"):
        os.makedirs("saves")
    return os.path.join("saves", f"slot{slot+1}.txt")

def load_world_save(slot):
    filename = get_save_filename(slot)
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        lines = f.read().splitlines()
    if len(lines) < 5:
        return None
    world_name = lines[0]
    seed = lines[1]
    gamemode = lines[2]
    world_data_flat = list(map(int, lines[3].split(",")))
    terrain_data = list(map(int, lines[4].split(",")))
    world_data = []
    idx = 0
    for x in range(WORLD_WIDTH):
        col = []
        for y in range(WORLD_HEIGHT):
            col.append(world_data_flat[idx])
            idx += 1
        world_data.append(col)
    return {"name": world_name, "seed": seed, "gamemode": gamemode, "world": world_data, "terrain_heights": terrain_data[:WORLD_WIDTH]}

def save_world_save(slot, world_data, terrain_heights, world_name, seed, gamemode):
    filename = get_save_filename(slot)
    flat = []
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            flat.append(str(world_data[x][y]))
    flat_str = ",".join(flat)
    terrain_str = ",".join(map(str, terrain_heights))
    with open(filename, "w") as f:
        f.write(world_name + "\n")
        f.write(seed + "\n")
        f.write(gamemode + "\n")
        f.write(flat_str + "\n")
        f.write(terrain_str + "\n")

# ==================================================
# World Generation Helpers
# ==================================================
def reset_world_world(seed=""):
    w, th = generate_world(seed)
    generate_structures(w, th)
    spawn_x = (WORLD_WIDTH // 2) * TILE_SIZE
    surface_y = th[WORLD_WIDTH // 2]
    # Ensure spawn is free.
    x_mid = WORLD_WIDTH // 2
    y_pos = surface_y - 1
    while y_pos >= 0 and w[x_mid][y_pos] != AIR:
        y_pos -= 1
    if y_pos < 0:
        y_pos = surface_y - 1
    spawn_y = y_pos * TILE_SIZE
    inv = default_inventory.copy()
    return w, th, spawn_x, spawn_y, inv

def reset_world():
    """
    Create a new world (for respawn without seed input).
    """
    w, th = generate_world()
    generate_structures(w, th)
    spawn_x = (WORLD_WIDTH // 2) * TILE_SIZE
    surface_y = th[WORLD_WIDTH // 2]
    spawn_y = (surface_y - 1) * TILE_SIZE
    inv = default_inventory.copy()
    return w, th, spawn_x, spawn_y, inv

# ==================================================
# Menu State Variables & Settings
# ==================================================
state = "menu"  # possible states: "menu", "settings", "world_selection", "new_world", "credits", "in_game", "inventory", "chest"
current_resolution = (WIDTH, HEIGHT)
selected_save_slot = 0

# For new world creation:
new_world_name = ""
new_seed = ""
new_gamemode = "survival"  # or "creative"
active_field = None  # "name" or "seed"

# For settings: new resolution inputs
new_width = str(WIDTH)
new_height = str(HEIGHT)

# ==================================================
# In-Game Variables
# ==================================================
world_data, terrain_heights = None, None
player_x = 0
player_y = 0
inventory = None
game_mode = "survival"
player_vel_y = 0
on_ground = False
fall_start_y = None
player_health = MAX_HEALTH
regen_timer = 0
selected_slot = 0  # inventory selection (for in-game items)
player_color = (255, 0, 0)
player_width = TILE_SIZE // 2
player_height = TILE_SIZE
camera_x = 0
camera_y = 0
CAMERA_SMOOTHING = 0.1

# Debug toggles.
show_stats = False  # F1 toggles stats display
show_fps = False    # F2 toggles FPS display

# Additional toggles:
inventory_open = False
interact_message = ""
interact_message_time = 0

# Chest mechanic:
# For simplicity, when the player interacts (F) on a chest block, we open a chest UI.
chest_inventory = {item: 0 for item in default_inventory}  #  simple chest inventory

# ==================================================
# Pygame Initialization
# ==================================================
pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 24)
screen = pygame.display.set_mode(current_resolution)
pygame.display.set_caption("2DCraft")
clock = pygame.time.Clock()

# ==================================================
# Menu Drawing Functions
# ==================================================
def draw_main_menu():
    screen.fill((0,0,0))
    title = font.render("2DCraft", True, (255,255,255))
    screen.blit(title, (current_resolution[0]//2 - title.get_width()//2, 30))
    # Version in upper right
    version = font.render("v0.2-alpha", True, (200,200,200))
    screen.blit(version, (current_resolution[0] - version.get_width() - 10, 10))
    buttons = [
        ("Play", pygame.Rect(current_resolution[0]//2 - 100, 100, 200, 50)),
        ("World Selection", pygame.Rect(current_resolution[0]//2 - 100, 170, 200, 50)),
        ("Settings", pygame.Rect(current_resolution[0]//2 - 100, 240, 200, 50)),
        ("Credits", pygame.Rect(current_resolution[0]//2 - 100, 310, 200, 50)),
        ("Quit", pygame.Rect(current_resolution[0]//2 - 100, 380, 200, 50))
    ]
    for text, rect in buttons:
        pygame.draw.rect(screen, (100,100,100), rect)
        pygame.draw.rect(screen, (255,255,255), rect, 2)
        t = font.render(text, True, (255,255,255))
        screen.blit(t, (rect.x + (rect.width - t.get_width())//2, rect.y + (rect.height - t.get_height())//2))
    return buttons

def draw_settings_menu():
    screen.fill((0,0,0))
    title = font.render("Settings", True, (255,255,255))
    screen.blit(title, (current_resolution[0]//2 - title.get_width()//2, 30))
    # Two input fields for width and height.
    width_rect = pygame.Rect(current_resolution[0]//2 - 100, 100, 200, 40)
    height_rect = pygame.Rect(current_resolution[0]//2 - 100, 150, 200, 40)
    save_rect = pygame.Rect(current_resolution[0]//2 - 100, 210, 200, 50)
    back_rect = pygame.Rect(current_resolution[0]//2 - 100, 280, 200, 50)
    pygame.draw.rect(screen, (50,50,50), width_rect)
    pygame.draw.rect(screen, (255,255,255), width_rect, 2)
    pygame.draw.rect(screen, (50,50,50), height_rect)
    pygame.draw.rect(screen, (255,255,255), height_rect, 2)
    width_text = font.render("Width: " + new_width, True, (255,255,255))
    height_text = font.render("Height: " + new_height, True, (255,255,255))
    screen.blit(width_text, (width_rect.x+10, width_rect.y+10))
    screen.blit(height_text, (height_rect.x+10, height_rect.y+10))
    pygame.draw.rect(screen, (100,100,100), save_rect)
    pygame.draw.rect(screen, (255,255,255), save_rect, 2)
    save_text = font.render("Save", True, (255,255,255))
    screen.blit(save_text, (save_rect.x + (save_rect.width - save_text.get_width())//2, save_rect.y + (save_rect.height - save_text.get_height())//2))
    pygame.draw.rect(screen, (100,100,100), back_rect)
    pygame.draw.rect(screen, (255,255,255), back_rect, 2)
    back_text = font.render("Back", True, (255,255,255))
    screen.blit(back_text, (back_rect.x + (back_rect.width - back_text.get_width())//2, back_rect.y + (back_rect.height - back_text.get_height())//2))
    return (width_rect, height_rect), ("save", save_rect), ("back", back_rect)

def draw_credits_menu():
    screen.fill((0,0,0))
    title = font.render("Credits", True, (255,255,255))
    screen.blit(title, (current_resolution[0]//2 - title.get_width()//2, 30))
    credits = ["Created by ChatGPT", "Inspired by Minecraft", "v0.2-alpha"]
    y = 100
    for line in credits:
        t = font.render(line, True, (255,255,255))
        screen.blit(t, (current_resolution[0]//2 - t.get_width()//2, y))
        y += 40
    back_rect = pygame.Rect(current_resolution[0]//2 - 100, y+20, 200, 50)
    pygame.draw.rect(screen, (100,100,100), back_rect)
    pygame.draw.rect(screen, (255,255,255), back_rect, 2)
    bt = font.render("Back", True, (255,255,255))
    screen.blit(bt, (back_rect.x + (back_rect.width - bt.get_width())//2, back_rect.y + (back_rect.height - bt.get_height())//2))
    return [("back", back_rect)]

def draw_world_selection_menu():
    screen.fill((0,0,0))
    title = font.render("World Selection", True, (255,255,255))
    screen.blit(title, (current_resolution[0]//2 - title.get_width()//2, 30))
    slots = []
    y = 100
    for i in range(NUM_SAVE_SLOTS):
        rect = pygame.Rect(current_resolution[0]//2 - 150, y, 300, 40)
        save = load_world_save(i)
        if save is None:
            text = f"Slot {i+1}: [Empty]"
        else:
            text = f"Slot {i+1}: {save['name']} ({save['gamemode']})"
        slots.append((i, rect, text))
        y += 50
    back_rect = pygame.Rect(current_resolution[0]//2 - 150, y+20, 300, 50)
    pygame.draw.rect(screen, (100,100,100), back_rect)
    pygame.draw.rect(screen, (255,255,255), back_rect, 2)
    back_text = font.render("Back", True, (255,255,255))
    screen.blit(back_text, (back_rect.x + (back_rect.width - back_text.get_width())//2, back_rect.y + (back_rect.height - back_text.get_height())//2))
    return slots, ("back", back_rect)

def draw_new_world_menu():
    screen.fill((0,0,0))
    title = font.render("New World Settings", True, (255,255,255))
    screen.blit(title, (current_resolution[0]//2 - title.get_width()//2, 30))
    wn_rect = pygame.Rect(current_resolution[0]//2 - 150, 100, 300, 40)
    seed_rect = pygame.Rect(current_resolution[0]//2 - 150, 160, 300, 40)
    mode_rect = pygame.Rect(current_resolution[0]//2 - 150, 220, 300, 40)
    create_rect = pygame.Rect(current_resolution[0]//2 - 150, 280, 300, 50)
    back_rect = pygame.Rect(current_resolution[0]//2 - 150, 350, 300, 50)
    pygame.draw.rect(screen, (50,50,50), wn_rect)
    pygame.draw.rect(screen, (255,255,255), wn_rect, 2)
    pygame.draw.rect(screen, (50,50,50), seed_rect)
    pygame.draw.rect(screen, (255,255,255), seed_rect, 2)
    pygame.draw.rect(screen, (50,50,50), mode_rect)
    pygame.draw.rect(screen, (255,255,255), mode_rect, 2)
    wn_text = font.render("Name: " + new_world_name, True, (255,255,255))
    seed_text = font.render("Seed: " + new_seed, True, (255,255,255))
    mode_text = font.render("Mode: " + new_gamemode, True, (255,255,255))
    screen.blit(wn_text, (wn_rect.x+10, wn_rect.y+10))
    screen.blit(seed_text, (seed_rect.x+10, seed_rect.y+10))
    screen.blit(mode_text, (mode_rect.x+10, mode_rect.y+10))
    pygame.draw.rect(screen, (100,100,100), create_rect)
    pygame.draw.rect(screen, (255,255,255), create_rect, 2)
    create_text = font.render("Create", True, (255,255,255))
    screen.blit(create_text, (create_rect.x + (create_rect.width - create_text.get_width())//2, create_rect.y + (create_rect.height - create_text.get_height())//2))
    pygame.draw.rect(screen, (100,100,100), back_rect)
    pygame.draw.rect(screen, (255,255,255), back_rect, 2)
    back_text = font.render("Back", True, (255,255,255))
    screen.blit(back_text, (back_rect.x + (back_rect.width - back_text.get_width())//2, back_rect.y + (back_rect.height - back_text.get_height())//2))
    return wn_rect, seed_rect, mode_rect, ("create", create_rect), ("back", back_rect)

def draw_inventory_ui():
    """
    Draw the inventory and crafting panels.
    Left panel: player's inventory.
    Right panel: available crafting recipes (only those you can craft).
    """
    inv_panel = pygame.Rect(50, 50, current_resolution[0]//2 - 100, current_resolution[1] - 100)
    craft_panel = pygame.Rect(current_resolution[0]//2 + 50, 50, current_resolution[0]//2 - 100, current_resolution[1] - 100)
    pygame.draw.rect(screen, (30,30,30), inv_panel)
    pygame.draw.rect(screen, (255,255,255), inv_panel, 2)
    pygame.draw.rect(screen, (30,30,30), craft_panel)
    pygame.draw.rect(screen, (255,255,255), craft_panel, 2)
    inv_title = font.render("Inventory", True, (255,255,255))
    screen.blit(inv_title, (inv_panel.x + 10, inv_panel.y + 10))
    craft_title = font.render("Crafting", True, (255,255,255))
    screen.blit(craft_title, (craft_panel.x + 10, craft_panel.y + 10))
    # Draw player's inventory items in a grid.
    cols = 5
    slot_size = 50
    gap = 5
    for idx, item in enumerate(inventory_order):
        row = idx // cols
        col = idx % cols
        slot_rect = pygame.Rect(inv_panel.x + 10 + col*(slot_size+gap),
                                inv_panel.y + 50 + row*(slot_size+gap),
                                slot_size, slot_size)
        pygame.draw.rect(screen, (100,100,100), slot_rect)
        pygame.draw.rect(screen, (255,255,255), slot_rect, 2)
        count = inventory.get(item, 0)
        t = font.render(str(count), True, (255,255,255))
        screen.blit(t, (slot_rect.x+2, slot_rect.y+2))
    # Draw available crafting recipes.
    available_recipes = []
    for output, req in crafting_recipes.items():
        can_craft = True
        for r_item, amount in req.items():
            if inventory.get(r_item, 0) < amount:
                can_craft = False
                break
        if can_craft:
            available_recipes.append((output, req))
    # List recipes vertically.
    y_offset = craft_panel.y + 50
    for (output, req) in available_recipes:
        req_text = ", ".join([f"{r}:{req[r]}" for r in req])
        recipe_str = f"Craft {output}  ({req_text})"
        t = font.render(recipe_str, True, (255,255,255))
        screen.blit(t, (craft_panel.x + 10, y_offset))
        y_offset += 30
    return inv_panel, craft_panel

def draw_chest_ui():
    """
    Draw a simple chest UI.
    Chest inventory is a 3x3 grid.
    """
    chest_panel = pygame.Rect(current_resolution[0]//2 - 150, current_resolution[1]//2 - 150, 300, 300)
    pygame.draw.rect(screen, (50,50,50), chest_panel)
    pygame.draw.rect(screen, (255,255,255), chest_panel, 2)
    title = font.render("Chest", True, (255,255,255))
    screen.blit(title, (chest_panel.x + 10, chest_panel.y + 10))
    # Draw chest grid (3x3)
    slot_size = 50
    gap = 10
    grid = []
    for row in range(3):
        for col in range(3):
            rect = pygame.Rect(chest_panel.x + 20 + col*(slot_size+gap),
                               chest_panel.y + 50 + row*(slot_size+gap),
                               slot_size, slot_size)
            pygame.draw.rect(screen, (100,100,100), rect)
            pygame.draw.rect(screen, (255,255,255), rect, 2)
            grid.append(rect)
    return chest_panel, grid

# ============================
# In-Game World Reset (with seed)
# ============================
def reset_world_using_seed(seed=""):
    return reset_world_world(seed)

# ==================================================
# Main Loop
# ==================================================
running = True
while running:
    dt = clock.tick(60) / 1000.0  # delta time (seconds)
    
    # ------------------------------
    # Event Handling
    # ------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Global: F11 toggles fullscreen.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode(current_resolution, pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode(current_resolution)
        
        # State-specific event handling.
        if state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                buttons = draw_main_menu()
                mx, my = pygame.mouse.get_pos()
                for text, rect in buttons:
                    if rect.collidepoint(mx, my):
                        if text == "Play":
                            state = "world_selection"
                        elif text == "World Creation":
                            state = "world_selection"
                        elif text == "Settings":
                            state = "settings"
                        elif text == "Credits":
                            state = "credits"
                        elif text == "Quit":
                            running = False
        
        elif state == "settings":
            if event.type == pygame.MOUSEBUTTONDOWN:
                inputs, save_btn, back_btn = draw_settings_menu()
                mx, my = pygame.mouse.get_pos()
                # Check inputs (for simplicity, we treat them as non-editable; you can extend with text input handling)
                if save_btn[1].collidepoint(mx, my):
                    try:
                        w_new = int(new_width)
                        h_new = int(new_height)
                        current_resolution = (w_new, h_new)
                        screen = pygame.display.set_mode(current_resolution)
                    except:
                        pass
                if back_btn[1].collidepoint(mx, my):
                    state = "menu"
            if event.type == pygame.KEYDOWN:
                # For simplicity, allow typing numbers for width and height.
                if active_field == "width":
                    if event.key == pygame.K_BACKSPACE:
                        new_width = new_width[:-1]
                    else:
                        new_width += event.unicode
                elif active_field == "height":
                    if event.key == pygame.K_BACKSPACE:
                        new_height = new_height[:-1]
                    else:
                        new_height += event.unicode
                if event.key == pygame.K_TAB:
                    # Toggle active field.
                    active_field = "height" if active_field == "width" else "width"
        
        elif state == "world_selection":
            if event.type == pygame.MOUSEBUTTONDOWN:
                slots, back_btn = draw_world_selection_menu()
                mx, my = pygame.mouse.get_pos()
                for slot, rect, text in slots:
                    if rect.collidepoint(mx, my):
                        selected_save_slot = slot
                        save_data = load_world_save(slot)
                        if save_data is None:
                            state = "new_world"
                        else:
                            world_data = save_data["world"]
                            terrain_heights = save_data["terrain_heights"]
                            game_mode = save_data["gamemode"]
                            player_x = (WORLD_WIDTH // 2) * TILE_SIZE
                            surface_y = terrain_heights[WORLD_WIDTH // 2]
                            player_y = (surface_y - 1) * TILE_SIZE
                            inventory = default_inventory.copy()
                            state = "in_game"
                if back_btn[1].collidepoint(mx, my):
                    state = "menu"
        
        elif state == "new_world":
            if event.type == pygame.MOUSEBUTTONDOWN:
                wn_rect, seed_rect, mode_rect, create_btn, back_btn = draw_new_world_menu()
                mx, my = pygame.mouse.get_pos()
                if wn_rect.collidepoint(mx, my):
                    active_field = "name"
                elif seed_rect.collidepoint(mx, my):
                    active_field = "seed"
                elif mode_rect.collidepoint(mx, my):
                    new_gamemode = "creative" if new_gamemode == "survival" else "survival"
                elif create_btn[1].collidepoint(mx, my):
                    game_mode = new_gamemode
                    world_data, terrain_heights, player_x, player_y, inventory = reset_world_using_seed(new_seed)
                    save_world_save(selected_save_slot, world_data, terrain_heights, new_world_name, new_seed, new_gamemode)
                    state = "in_game"
                elif back_btn[1].collidepoint(mx, my):
                    state = "world_selection"
            if event.type == pygame.KEYDOWN:
                if active_field == "name":
                    if event.key == pygame.K_BACKSPACE:
                        new_world_name = new_world_name[:-1]
                    else:
                        new_world_name += event.unicode
                elif active_field == "seed":
                    if event.key == pygame.K_BACKSPACE:
                        new_seed = new_seed[:-1]
                    else:
                        new_seed += event.unicode
        
        elif state == "in_game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    show_stats = not show_stats
                elif event.key == pygame.K_F2:
                    show_fps = not show_fps
                elif event.key == pygame.K_1:
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
                elif event.key == pygame.K_ESCAPE:
                    state = "menu"
                elif event.key == pygame.K_e:
                    state = "inventory"
                elif event.key == pygame.K_f:
                    # Interact: if the block at player's feet is a chest, open chest UI.
                    foot_x = int((player_x + player_width//2) // TILE_SIZE)
                    foot_y = int((player_y + player_height) // TILE_SIZE)
                    if 0 <= foot_x < WORLD_WIDTH and 0 <= foot_y < WORLD_HEIGHT:
                        if world_data[foot_x][foot_y] == CHEST:
                            state = "chest"
                    else:
                        interact_message = "Nothing to interact with!"
                        interact_message_time = time.time()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = int((mouse_x + camera_x) // TILE_SIZE)
                world_y = int((mouse_y + camera_y) // TILE_SIZE)
                player_center_x = player_x + player_width/2
                player_center_y = player_y + player_height/2
                block_center_x = world_x * TILE_SIZE + TILE_SIZE/2
                block_center_y = world_y * TILE_SIZE + TILE_SIZE/2
                if math.hypot(player_center_x - block_center_x, player_center_y - block_center_y) <= 5 * TILE_SIZE:
                    if 0 <= world_x < WORLD_WIDTH and 0 <= world_y < WORLD_HEIGHT:
                        if event.button == 1:
                            if world_data[world_x][world_y] != AIR:
                                block_type = world_data[world_x][world_y]
                                inventory[block_type] = inventory.get(block_type, 0) + 1
                                world_data[world_x][world_y] = AIR
                        elif event.button == 3:
                            block_to_place = inventory_order[selected_slot]
                            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
                            block_rect = pygame.Rect(world_x * TILE_SIZE, world_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            if not player_rect.colliderect(block_rect):
                                if game_mode == "creative":
                                    world_data[world_x][world_y] = block_to_place
                                else:
                                    if inventory.get(block_to_place, 0) > 0 and world_data[world_x][world_y] == AIR:
                                        world_data[world_x][world_y] = block_to_place
                                        inventory[block_to_place] -= 1
        
        elif state == "inventory":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_e:
                    state = "in_game"
            if event.type == pygame.MOUSEBUTTONDOWN:
                # In inventory UI, check if a crafting recipe is clicked.
                mx, my = pygame.mouse.get_pos()
                # For simplicity, assume recipes are listed in a column on the right.
                recipe_y = current_resolution[1]//2
                idx = 0
                for output, req in crafting_recipes.items():
                    rect = pygame.Rect(current_resolution[0] - 250, recipe_y + idx*30, 240, 25)
                    if rect.collidepoint(mx, my):
                        # Craft this recipe: subtract required resources, add the output.
                        can_craft = True
                        for r_item, amt in req.items():
                            if inventory.get(r_item, 0) < amt:
                                can_craft = False
                                break
                        if can_craft:
                            for r_item, amt in req.items():
                                inventory[r_item] -= amt
                            inventory[output] = inventory.get(output, 0) + 1
                    idx += 1

        elif state == "chest":
            # In chest UI, allow transferring items.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "in_game"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # We'll draw chest UI grid; detect clicks.
                chest_panel, grid = draw_chest_ui()
                for rect in grid:
                    if rect.collidepoint(mx, my):
                        # For simplicity, if the player has an item selected from inventory (selected_slot),
                        # transfer one unit from player's inventory to chest (if available).
                        item = inventory_order[selected_slot]
                        if inventory.get(item, 0) > 0:
                            inventory[item] -= 1
                            chest_inventory[item] = chest_inventory.get(item, 0) + 1
            # Pressing 'C' will transfer one unit from chest back to player's inventory.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    # For simplicity, transfer from first nonzero chest slot.
                    for item, amt in chest_inventory.items():
                        if amt > 0:
                            chest_inventory[item] -= 1
                            inventory[item] = inventory.get(item, 0) + 1
                            break

    # ============================
    # State-Based Updates & Drawing
    # ============================
    if state == "menu":
        draw_main_menu()
        pygame.display.flip()
    elif state == "settings":
        draw_settings_menu()
        pygame.display.flip()
    elif state == "credits":
        draw_credits_menu()
        pygame.display.flip()
    elif state == "world_selection":
        draw_world_selection_menu()
        pygame.display.flip()
    elif state == "new_world":
        draw_new_world_menu()
        pygame.display.flip()
    elif state == "in_game":
        # Game movement & collision.
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -MOVE_SPEED * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = MOVE_SPEED * dt
        new_px = horizontal_collision(player_x, player_y, dx, player_width, player_height, world_data)
        if new_px == player_x:
            dx = 0
        player_x = new_px
        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and on_ground:
            player_vel_y = JUMP_VELOCITY
            on_ground = False
            fall_start_y = None
        player_vel_y += GRAVITY * dt
        if not on_ground and player_vel_y > 0 and fall_start_y is None:
            fall_start_y = player_y
        new_py, landed = vertical_collision(player_x, player_y, player_vel_y * dt, player_width, player_height, world_data)
        if landed:
            if fall_start_y is not None:
                fall_distance = new_py - fall_start_y
                fall_distance_blocks = fall_distance / TILE_SIZE
                if fall_distance_blocks > FALL_SAFE_HEIGHT:
                    damage = int((fall_distance_blocks - FALL_SAFE_HEIGHT) * FALL_DAMAGE_PER_BLOCK)
                    player_health -= damage
                fall_start_y = None
            player_vel_y = 0
            on_ground = True
        else:
            on_ground = False
        player_y = new_py
        if player_y > WORLD_HEIGHT * TILE_SIZE:
            player_health = 0
        if player_health < MAX_HEALTH:
            regen_timer += dt
            if regen_timer >= REGEN_TIME:
                player_health += 1
                if player_health > MAX_HEALTH:
                    player_health = MAX_HEALTH
                regen_timer = 0
        if player_health <= 0:
            world_data, terrain_heights, player_x, player_y, inventory = reset_world()
            player_vel_y = 0
            on_ground = False
            player_health = MAX_HEALTH
            fall_start_y = None
            regen_timer = 0

        # Smooth camera movement.
        target_camera_x = player_x - current_resolution[0] // 2 + player_width // 2
        target_camera_y = player_y - current_resolution[1] // 2 + player_height // 2
        camera_x += (target_camera_x - camera_x) * CAMERA_SMOOTHING
        camera_y += (target_camera_y - camera_y) * CAMERA_SMOOTHING

        # Draw the game world.
        screen.fill(colors[AIR])
        for x in range(WORLD_WIDTH):
            for y in range(WORLD_HEIGHT):
                block_type = world_data[x][y]
                if block_type != AIR:
                    rect = pygame.Rect(x * TILE_SIZE - int(camera_x),
                                       y * TILE_SIZE - int(camera_y),
                                       TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, colors[block_type], rect)
                    pygame.draw.rect(screen, (0,0,0), rect, 1)
        player_rect = pygame.Rect(int(player_x - camera_x), int(player_y - camera_y), player_width, player_height)
        pygame.draw.rect(screen, player_color, player_rect)
        # Draw Inventory Bar (at bottom center).
        inv_slot_size = 50
        pad = 10
        total_slots = len(inventory_order)
        bar_width = total_slots * (inv_slot_size + pad) + pad
        bar_height = inv_slot_size + 2 * pad
        bar_x = (current_resolution[0] - bar_width) // 2
        bar_y = current_resolution[1] - bar_height - 10
        pygame.draw.rect(screen, (50,50,50), (bar_x, bar_y, bar_width, bar_height))
        for i, btype in enumerate(inventory_order):
            sx = bar_x + pad + i * (inv_slot_size + pad)
            sy = bar_y + pad
            srect = pygame.Rect(sx, sy, inv_slot_size, inv_slot_size)
            pygame.draw.rect(screen, (100,100,100), srect)
            if i == selected_slot:
                pygame.draw.rect(screen, (255,255,0), srect, 3)
            inner = srect.inflate(-10, -10)
            pygame.draw.rect(screen, colors[btype], inner)
            ct = font.render(str(inventory.get(btype, 0)), True, (255,255,255))
            screen.blit(ct, (sx+5, sy+5))
        # Draw Health (Hearts) at top left.
        hsize = 20
        hpad = 5
        for i in range(MAX_HEALTH):
            hx = 10 + i * (hsize + hpad)
            hy = 10
            hrect = pygame.Rect(hx, hy, hsize, hsize)
            if i < player_health:
                pygame.draw.rect(screen, (255,0,0), hrect)
            else:
                pygame.draw.rect(screen, (50,50,50), hrect)
            pygame.draw.rect(screen, (0,0,0), hrect, 2)
        if show_stats:
            debug_lines = [
                f"X: {int(player_x)}",
                f"Y: {int(player_y)}",
                f"On Ground: {on_ground}",
                f"Health: {player_health}",
                f"Velocity Y: {int(player_vel_y)}",
                f"Seed: {new_seed if new_seed != '' else 'N/A'}",
                f"Gamemode: {game_mode}"
            ]
            for i, line in enumerate(debug_lines):
                dtext = font.render(line, True, (255,255,255))
                screen.blit(dtext, (10, 40 + i*20))
        if show_fps:
            fps = int(clock.get_fps())
            fps_text = font.render(f"FPS: {fps}", True, (255,255,255))
            fps_rect = fps_text.get_rect(topright=(current_resolution[0] - 10, 10))
            screen.blit(fps_text, fps_rect)
        if inventory_open:
            inv_panel, craft_panel = draw_inventory_ui()
        if interact_message and time.time() - interact_message_time < 1:
            im_text = font.render(interact_message, True, (255,255,0))
            screen.blit(im_text, (current_resolution[0]//2 - im_text.get_width()//2, current_resolution[1]//2))
        pygame.display.flip()
    
    elif state == "inventory":
        # Draw full-screen inventory/crafting UI.
        screen.fill((0,0,0))
        inv_panel, craft_panel = draw_inventory_ui()
        # Allow closing with ESC or E.
        pygame.display.flip()
    
    elif state == "chest":
        # Draw chest UI.
        screen.fill((0,0,0))
        chest_panel, chest_grid = draw_chest_ui()
        # (For simplicity, chest transfers are handled in event loop.)
        pygame.display.flip()

pygame.quit()
sys.exit()
