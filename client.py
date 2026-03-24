import pygame
import socket
import json
import math
import threading
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pistol Combat 2D")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

HOST = '127.0.0.1'      # Change en ton IP seulement si tu joues sur deux PC
PORT = 5555

# ==================== SOCKET AVEC TIMEOUT ====================
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(1.0)          # Timeout court = connexion plus rapide
# ============================================================

try:
    client_socket.connect((HOST, PORT))
except socket.timeout:
    print("Erreur : Le serveur n'est pas lancé ou ne répond pas.")
    input("Appuie sur Entrée pour quitter...")
    sys.exit()
except ConnectionRefusedError:
    print("Erreur : Connexion refusée. Assure-toi que le serveur tourne.")
    input("Appuie sur Entrée pour quitter...")
    sys.exit()
# ============================================================

my_id = None
players = {}
bullets = []
running = True
shoot_cooldown = 0

def receive_data():
    global my_id, players, bullets
    while running:
        try:
            data = client_socket.recv(8192)
            if not data:
                break
            msg = json.loads(data.decode())
            if msg["type"] == "connected":
                my_id = msg["id"]
            elif msg["type"] == "state":
                players = msg.get("players", {})
                bullets = msg.get("bullets", [])
        except:
            break

threading.Thread(target=receive_data, daemon=True).start()

def play_shoot_sound():
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        sound = pygame.sndarray.make_sound((pygame.sndarray.samples(pygame.mixer.Sound(buffer=b'\x00\x7F'*20)) * 4000))
        sound.play()
    except:
        pass

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    input_data = {
        "type": "input",
        "keys": {
            "left":  keys[pygame.K_a] or keys[pygame.K_LEFT],
            "right": keys[pygame.K_d] or keys[pygame.K_RIGHT],
            "up":    keys[pygame.K_w] or keys[pygame.K_UP],
            "down":  keys[pygame.K_s] or keys[pygame.K_DOWN],
        },
        "angle": 0,
        "shoot": False
    }

    if my_id is not None:
        my_str = str(my_id)
        if my_str in players:
            p = players[my_str]
            mx, my = pygame.mouse.get_pos()
            input_data["angle"] = math.degrees(math.atan2(my - p["y"], mx - p["x"]))

            if pygame.mouse.get_pressed()[0] and shoot_cooldown <= 0:
                input_data["shoot"] = True
                shoot_cooldown = 12
                play_shoot_sound()

    try:
        client_socket.send(json.dumps(input_data).encode())
    except:
        running = False

    # Dessin
    screen.fill((8, 8, 40))

    for i in range(-5, 15):
        pygame.draw.line(screen, (18, 18, 55), (i*70, 0), (i*70 - 120, HEIGHT), 2)

    for pid, p in players.items():
        color = (0, 255, 255) if int(pid) == my_id else (255, 80, 80)
        pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), 20)
        pygame.draw.circle(screen, (255, 255, 255), (int(p["x"]), int(p["y"])), 20, 3)

        rad = math.radians(p.get("angle", 0))
        gx = p["x"] + 28 * math.cos(rad)
        gy = p["y"] + 28 * math.sin(rad)
        pygame.draw.line(screen, (230, 230, 230), (p["x"], p["y"]), (gx, gy), 7)

        if "health" in p:
            hr = max(0, p["health"] / 100)
            pygame.draw.rect(screen, (180, 0, 0), (p["x"]-23, p["y"]-38, 46, 7))
            pygame.draw.rect(screen, (0, 220, 0), (p["x"]-23, p["y"]-38, 46 * hr, 7))

    for b in bullets:
        pygame.draw.circle(screen, (255, 230, 80), (int(b["x"]), int(b["y"])), 7)
        pygame.draw.circle(screen, (255, 255, 255), (int(b["x"]), int(b["y"])), 7, 2)

    if my_id is not None:
        my_str = str(my_id)
        if my_str in players:
            score = players[my_str].get("score", 0)
            screen.blit(font.render(f"Kills : {score}", True, (255, 255, 255)), (15, 15))

    pygame.display.flip()

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    clock.tick(60)

client_socket.close()
pygame.quit()
sys.exit()