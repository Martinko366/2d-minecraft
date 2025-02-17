# server.py
import socket
import threading
import random
from world import generate_world, generate_structures
from config import TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT, default_inventory

HOST = "0.0.0.0"
PORT = 25515

# Generate a permanent world for the server.
world, terrain_heights = generate_world()
generate_structures(world, terrain_heights)

# Dictionary to hold connected players (using their connection as key).
players = {}

def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    # Assign spawn position (center of the world)
    spawn_x = (WORLD_WIDTH // 2) * TILE_SIZE
    surface_y = terrain_heights[WORLD_WIDTH // 2]
    spawn_y = (surface_y - 1) * TILE_SIZE
    player_state = {
        "x": spawn_x,
        "y": spawn_y,
        "inventory": default_inventory.copy(),
        "health": 10
    }
    players[conn] = player_state
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode("utf-8")
            print(f"Received from {addr}: {command}")
            if command == "die":
                # Reset the player's state.
                player_state["inventory"] = default_inventory.copy()
                player_state["health"] = 10
                player_state["x"] = spawn_x
                player_state["y"] = spawn_y
                conn.sendall("reset".encode("utf-8"))
            else:
                conn.sendall("ack".encode("utf-8"))
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        conn.close()
        del players[conn]
        print(f"Client disconnected: {addr}")

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        s.close()

if __name__ == "__main__":
    start_server()
