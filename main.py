# main.py
import pygame
import sys
import os

# -----------------------
# Basic setup
# -----------------------
os.environ["SDL_RENDER_SCALE_QUALITY"] = "0"  # nearest-neighbor scaling
pygame.init()
pygame.display.set_caption("Undertale Fangame")

# Base logical resolution
BASE_W, BASE_H = 640, 480
game_surface = pygame.Surface((BASE_W, BASE_H))

screen = pygame.display.set_mode((BASE_W * 2, BASE_H * 2), pygame.RESIZABLE)
clock = pygame.time.Clock()
fullscreen = False

# -----------------------
# Font
# -----------------------
font_path = "assets/fonts/determination.ttf"
if os.path.isfile(font_path):
    ui_font = pygame.font.Font(font_path, 28)
    name_font = pygame.font.Font(font_path, 36)
else:
    ui_font = pygame.font.SysFont("arial", 24)
    name_font = pygame.font.SysFont("arial", 32)

# -----------------------
# Game states
# -----------------------
STATE_NAME_ENTRY = "name_entry"
STATE_OVERWORLD = "overworld"
game_state = STATE_NAME_ENTRY

player_name = ""
MAX_NAME_LEN = 12

# -----------------------
# Player setup
# -----------------------
PLAYER_SIZE = 64
PLAYER_SPEED = 200  # pixels per second logical

FACING_DOWN = "down"
FACING_UP = "up"
FACING_LEFT = "left"
FACING_RIGHT = "right"
player_facing = FACING_DOWN

# -----------------------
# Load player sprites
# -----------------------
def load_player_sprites():
    try:
        down = pygame.image.load("assets/sprites/player_down.png").convert_alpha()
        up = pygame.image.load("assets/sprites/player_up.png").convert_alpha()

        # Resize to PLAYER_SIZE
        down = pygame.transform.scale(down, (PLAYER_SIZE, PLAYER_SIZE))
        up = pygame.transform.scale(up, (PLAYER_SIZE, PLAYER_SIZE))

        # Generate sideways by rotating the down sprite 90° clockwise
        right = pygame.transform.rotate(down, -90)
        left = pygame.transform.flip(right, True, False)

        return {
            FACING_DOWN: down,
            FACING_UP: up,
            FACING_RIGHT: right,
            FACING_LEFT: left
        }

    except Exception:
        # fallback placeholder: simple colored square
        surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        surf.fill((255, 220, 60))
        pygame.draw.rect(surf, (60, 40, 0), surf.get_rect(), 2)
        right = pygame.transform.rotate(surf, -90)
        left = pygame.transform.flip(right, True, False)
        return {
            FACING_DOWN: surf,
            FACING_UP: surf,
            FACING_RIGHT: right,
            FACING_LEFT: left
        }

player_sprites = load_player_sprites()
player_rect = player_sprites[FACING_DOWN].get_rect(center=(BASE_W//2, BASE_H//2))

# -----------------------
# Room collisions
# -----------------------
walls = [
    pygame.Rect(0,0,BASE_W,16),                    # top
    pygame.Rect(0,BASE_H-16,BASE_W,16),           # bottom
    pygame.Rect(0,0,16,BASE_H),                    # left
    pygame.Rect(BASE_W-16,0,16,BASE_H),           # right
    pygame.Rect(120,120,80,16),
    pygame.Rect(120,120,16,120),
    pygame.Rect(360,200,160,16),
    pygame.Rect(480,280,16,96)
]

def move_with_collision(rect, dx, dy, obstacles):
    rect.x += int(dx)
    for w in obstacles:
        if rect.colliderect(w):
            if dx>0: rect.right=w.left
            elif dx<0: rect.left=w.right
    rect.y += int(dy)
    for w in obstacles:
        if rect.colliderect(w):
            if dy>0: rect.bottom=w.top
            elif dy<0: rect.top=w.bottom

# -----------------------
# Draw functions
# -----------------------
def draw_name_entry(surface, typed_name):
    surface.fill((0,0,0))
    title = name_font.render("Name the Fallen Human.", True, (255,255,255))
    surface.blit(title, ((BASE_W-title.get_width())//2, 80))
    hint = ui_font.render("Type a name (A-Z). Enter to confirm.", True, (200,200,200))
    surface.blit(hint, ((BASE_W-hint.get_width())//2,140))
    name_label = name_font.render(typed_name if typed_name else "_", True, (255,220,0))
    surface.blit(name_label, ((BASE_W-name_label.get_width())//2,220))
    footer = ui_font.render("(Backspace to delete)", True, (120,120,120))
    surface.blit(footer, ((BASE_W-footer.get_width())//2,300))

def draw_overworld(surface, name):
    surface.fill((12,12,20))
    tile_color = (18,18,28)
    for y in range(0, BASE_H, 32):
        for x in range(0, BASE_W, 32):
            pygame.draw.rect(surface, tile_color, (x,y,32,32),1)
    for w in walls:
        pygame.draw.rect(surface, (80,80,90), w)
    surface.blit(player_sprites[player_facing], player_rect)
    name_surf = ui_font.render(name if name else "???", True, (255,240,200))
    surface.blit(name_surf, (8,8))

# -----------------------
# Main loop
# -----------------------
last_time = pygame.time.get_ticks()/1000.0
running=True
while running:
    now = pygame.time.get_ticks()/1000.0
    dt = max(0, now-last_time)
    last_time=now

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_F4 and not (pygame.key.get_mods() & pygame.KMOD_ALT):
                fullscreen=not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((BASE_W*2,BASE_H*2),pygame.RESIZABLE)
            if game_state==STATE_NAME_ENTRY:
                if event.key==pygame.K_RETURN and player_name!="":
                    game_state=STATE_OVERWORLD
                elif event.key==pygame.K_BACKSPACE:
                    player_name=player_name[:-1]
                elif event.unicode:
                    ch=event.unicode
                    if ch.isalpha() and len(player_name)<12:
                        player_name+=ch.upper()
                    elif ch==" " and len(player_name)<12:
                        player_name+=" "

    # Overworld movement
    if game_state==STATE_OVERWORLD:
        keys=pygame.key.get_pressed()
        x_input=(keys[pygame.K_RIGHT] or keys[pygame.K_d])-(keys[pygame.K_LEFT] or keys[pygame.K_a])
        y_input=(keys[pygame.K_DOWN] or keys[pygame.K_s])-(keys[pygame.K_UP] or keys[pygame.K_w])
        vel=pygame.math.Vector2(x_input,y_input)
        if vel.length_squared()>0:
            vel=vel.normalize()*PLAYER_SPEED
            # Update facing
            if abs(x_input)>abs(y_input):
                player_facing=FACING_RIGHT if x_input>0 else FACING_LEFT
            else:
                player_facing=FACING_DOWN if y_input>0 else FACING_UP
        else:
            vel=pygame.math.Vector2(0,0)
        dx=vel.x*dt
        dy=vel.y*dt
        move_with_collision(player_rect,dx,dy,walls)

    # Draw to logical surface
    if game_state==STATE_NAME_ENTRY:
        draw_name_entry(game_surface,player_name)
    else:
        draw_overworld(game_surface,player_name)

    # Scale surface to screen
    screen_w,screen_h=screen.get_size()
    scale=max(1,min(screen_w//BASE_W,screen_h//BASE_H))
    scaled_w,scaled_h=BASE_W*scale,BASE_H*scale
    scaled_surf=pygame.transform.scale(game_surface,(scaled_w,scaled_h))
    x=(screen_w-scaled_w)//2
    y=(screen_h-scaled_h)//2
    screen.fill((0,0,0))
    screen.blit(scaled_surf,(x,y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
