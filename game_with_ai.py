import pygame
import sys
import random
import math
import copy
from collections import deque

pygame.init()

# -----------------------------------------------------------------------------
# PLEASE READ BEFORE YOU EDIT!
# This code has been written for a course in AI. Try not to change anything
# except for the parameters listed below. If you know what you're doing, then
# feel free to change the rest of the code!
# -----------------------------------------------------------------------------
CONFIG = {
    # Movement / timing
    "FPS": 60,
    "PLAYER_SPEED": 3.0,          # Tiles per second
    "PLAYER_BOX_SCALE": 0.6,      # Fraction of TILE_SIZE used for player's bounding box
    "BULLET_SPEED": 6.0,          # Tiles per second
    "BULLET_LIFETIME": 2.0,       # In seconds
    
    # Enemy speeds
    "WANDER_MOVE_INTERVAL": 60,   # frames between steps when wandering (IDLE/SEARCH)
    "CHASE_MOVE_INTERVAL": 10,    # frames between steps when chasing
    "ENEMY_PATH_UPDATE_INTERVAL": 60,  # BFS path refresh
    "DETECTION_RADIUS": 6,        # Enemies detect player within this Manhattan distance
    
    # Time & ammo
    "TIME_LIMIT": 60,             # Seconds to collect all coins
    "MAX_AMMO": 6,
    
    # Map / tiles
    "TILE_SIZE": 40,
    
    # Enemy spawn
    "INITIAL_ENEMY_COUNT": 3,
    "ENEMY_SPAWN_INTERVAL": 300,  # frames between spawns
    "SPAWN_MIN_DISTANCE": 8,      # min Manhattan distance from player when spawning
    
    # Explosion (particle) effect
    "PARTICLE_COUNT": 15,
    "PARTICLE_LIFETIME": 0.5,     # seconds
    "PARTICLE_SPEED_MIN": 50,     # px/s
    "PARTICLE_SPEED_MAX": 150,    # px/s
}

CUSTOM_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,3,1],
    [1,0,0,0,0,0,0,1,1,1,1,1,0,0,2,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,1,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,1,0,1,0,1,0,0,1,0,0,0,2,1],
    [1,0,1,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,1,0,0,1,0,0,0,0,1],
    [1,0,2,0,0,1,0,1,1,1,1,1,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,1,2,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,1],
    [1,0,2,0,0,1,0,0,0,1,0,1,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,1,3,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1,0,2,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,2,0,0,1,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,1,0,1,0,1,0,1,0,0,0,0,0,1],
    [1,0,0,0,0,3,0,0,0,1,0,0,0,0,0,0,0,0,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

try:
    shoot_sound = pygame.mixer.Sound("./assets/shoot.mp3")
    empty_sound = pygame.mixer.Sound("./assets/empty.mp3")
    coin_sound = pygame.mixer.Sound("./assets/coin.mp3")
    ammo_sound = pygame.mixer.Sound("./assets/ammo.mp3")
    win_sound = pygame.mixer.Sound("./assets/win.mp3")
    lose_sound = pygame.mixer.Sound("./assets/lose.mp3")
    start_sound = pygame.mixer.Sound("./assets/preparation.mp3")
    explosion_sound = pygame.mixer.Sound("./assets/explosion.mp3")
except:
    shoot_sound = pygame.mixer.Sound(file=None)
    empty_sound = pygame.mixer.Sound(file=None)
    coin_sound = pygame.mixer.Sound(file=None)
    ammo_sound = pygame.mixer.Sound(file=None)
    win_sound = pygame.mixer.Sound(file=None)
    lose_sound = pygame.mixer.Sound(file=None)
    start_sound = pygame.mixer.Sound(file=None)
    explosion_sound = pygame.mixer.Sound(file=None)

TILE_SIZE = CONFIG["TILE_SIZE"]
GRID_ROWS = len(CUSTOM_MAP)
GRID_COLS = len(CUSTOM_MAP[0])
MAP_WIDTH = GRID_COLS * TILE_SIZE
MAP_HEIGHT = GRID_ROWS * TILE_SIZE

WINDOW_WIDTH = MAP_WIDTH
WINDOW_HEIGHT = MAP_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Game With AI Demonstration")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 20, bold=True)
big_font = pygame.font.SysFont("arial", 40, bold=True)

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
GREEN = (60, 255, 60)
BLUE = (60, 60, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

def copy_map():
    """Return a fresh, deep-copied version of CUSTOM_MAP."""
    return copy.deepcopy(CUSTOM_MAP)

def in_bounds(r, c):
    return 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS

def get_tile_from_xy(x, y):
    return int(y // TILE_SIZE), int(x // TILE_SIZE)

def tile_rect(r, c):
    return pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def tile_center(r, c):
    return (c*TILE_SIZE + TILE_SIZE/2, r*TILE_SIZE + TILE_SIZE/2)

def will_collide_with_wall(new_x, new_y, grid, half_size):
    """
    Check if the bounding box around (new_x, new_y) with 'half_size'
    overlaps any wall tile (1).
    """
    rect_player = pygame.Rect(new_x - half_size, new_y - half_size,
                              half_size*2, half_size*2)
    
    r0, c0 = get_tile_from_xy(new_x, new_y)
    for rr in range(r0-2, r0+3):
        for cc in range(c0-2, c0+3):
            if in_bounds(rr, cc) and grid[rr][cc] == 1:
                rect_wall = tile_rect(rr, cc)
                if rect_player.colliderect(rect_wall):
                    return True
    return False

def bfs_pathfinding(grid, start, goal):
    """
    BFS ignoring bullet logic, just walls.
    Returns list of tiles from start->goal inclusive if found, else [].
    """
    if start == goal:
        return [start]
    
    visited = set([start])
    queue = deque([(start, [])])
    
    while queue:
        (cr, cc), path = queue.popleft()
        for (nr, nc) in [(cr-1,cc),(cr+1,cc),(cr,cc-1),(cr,cc+1)]:
            if in_bounds(nr, nc) and grid[nr][nc] != 1:
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    new_path = path + [(cr, cc)]
                    if (nr, nc) == goal:
                        return new_path + [(nr, nc)]
                    queue.append(((nr, nc), new_
class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

    def __init__(self, r, c):
        self.x = c * TILE_SIZE + TILE_SIZE/2
        self.y = r * TILE_SIZE + TILE_SIZE/2
        self.speed_px = CONFIG["PLAYER_SPEED"] * TILE_SIZE  # px/second
        self.box_half = (CONFIG["PLAYER_BOX_SCALE"] * TILE_SIZE) / 2
        self.dir_r = 1
        self.dir_c = 0
        
        self.ammo = CONFIG["MAX_AMMO"]

    def get_tile_pos(self):
        return get_tile_from_xy(self.x, self.y)
    
    def update(self, dt, keys, grid):
        dist = self.speed_px * dt
        vx, vy = 0, 0
        
        up    = keys[pygame.K_w] or keys[pygame.K_UP]
        down  = keys[pygame.K_s] or keys[pygame.K_DOWN]
        left  = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        
        if up:    vy -= dist
        if down:  vy += dist
        if left:  vx -= dist
        if right: vx += dist
        
        # Facing direction if net movement
        if up and not down:
            self.dir_r, self.dir_c = -1, 0
        elif down and not up:
            self.dir_r, self.dir_c = 1, 0
        if left and not right:
            self.dir_r, self.dir_c = 0, -1
        elif right and not left:
            self.dir_r, self.dir_c = 0, 1
        
        # Move (X then Y) with collision checks
        new_x = self.x + vx
        if not will_collide_with_wall(new_x, self.y, grid, self.box_half):
            self.x = new_x
        
        new_y = self.y + vy
        if not will_collide_with_wall(self.x, new_y, grid, self.box_half):
            self.y = new_y

    def draw(self, surface):
        rect = pygame.Rect(0,0, self.box_half*2, self.box_half*2)
        rect.center = (self.x, self.y)
        pygame.draw.rect(surface, BLUE, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)

class Bullet:
    def __init__(self, x, y, dir_r, dir_c):
        self.x = x
        self.y = y
        self.dir_r = dir_r
        self.dir_c = dir_c
        self.speed_px = CONFIG["BULLET_SPEED"] * TILE_SIZE  # px/second
        self.lifetime = CONFIG["BULLET_LIFETIME"]
        self.alive = True

        self.old_x = x
        self.old_y = y

    def update(self, dt, enemies, explosions, grid):
        # store old position
        self.old_x, self.old_y = self.x, self.y
        
        dist = self.speed_px * dt
        self.x += self.dir_c * dist
        self.y += self.dir_r * dist

        # Check collision with walls
        if self.will_collide_with_wall(grid):
            self.alive = False
            return
        
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return

        # out-of-bounds?
        if (self.x < 0 or self.x > MAP_WIDTH or
            self.y < 0 or self.y > MAP_HEIGHT):
            self.alive = False
            return
        
        # Check collision with enemies
        bullet_rect = pygame.Rect(self.x-4, self.y-4, 8, 8)
        for e in enemies:
            if not e.dead:
                ex, ey = tile_center(e.r, e.c)
                enemy_rect = pygame.Rect(ex - TILE_SIZE/2, ey - TILE_SIZE/2,
                                         TILE_SIZE, TILE_SIZE)
                if bullet_rect.colliderect(enemy_rect):
                    e.dead = True
                    e.spawn_explosion(explosions)
                    explosion_sound.play()
                    self.alive = False
                    return

    def will_collide_with_wall(self, grid):
        """
        Check if the bullet collides with any wall tile.
        """
        bullet_tile_r, bullet_tile_c = get_tile_from_xy(self.x, self.y)
        if in_bounds(bullet_tile_r, bullet_tile_c) and grid[bullet_tile_r][bullet_tile_c] == 1:
            return True
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 4)

class Enemy:
    """
    States: IDLE, CHASE, SEARCH
      - IDLE: randomly wander
      - CHASE: BFS path to player, moves faster
      - SEARCH: BFS path to player's last known tile, same speed as IDLE
    """
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.state = "IDLE"
        
        self.dead = False
        self.path = []
        self.path_index = 0
        
        self.move_cooldown = 0
        self.path_update_cooldown = 0

    def see_player(self, pr, pc):
        dist = manhattan_distance((self.r, self.c), (pr, pc))
        return dist <= CONFIG["DETECTION_RADIUS"]
    
    def get_move_interval(self):
        """Return frames between moves depending on state."""
        if self.state == "CHASE":
            return CONFIG["CHASE_MOVE_INTERVAL"]
        else:
            # IDLE or SEARCH => slow move
            return CONFIG["WANDER_MOVE_INTERVAL"]

    def update(self, grid, player, dt, bullets):
        if self.dead:
            return
        
        # Check collision with player => game over
        if (self.r, self.c) == player.get_tile_pos():
            raise_player_caught()
        
        pr, pc = player.get_tile_pos()
        
        # Basic detection
        if self.see_player(pr, pc):
            # If see player, go CHASE
            if self.state != "CHASE":
                self.state = "CHASE"
        else:
            # If was chasing but lost sight => SEARCH
            if self.state == "CHASE":
                self.state = "SEARCH"
            elif self.state not in ("SEARCH", "CHASE"):
                self.state = "IDLE"
        
        # BFS path if CHASE or SEARCH
        if self.state in ("CHASE", "SEARCH"):
            if self.path_update_cooldown <= 0 or not self.path:
                goal = (pr, pc)  # chase or search last known
                self.path = bfs_pathfinding(grid, (self.r, self.c), goal)
                self.path_index = 0
                self.path_update_cooldown = CONFIG["ENEMY_PATH_UPDATE_INTERVAL"]
        
            # If we finished a SEARCH path, revert to IDLE
            if self.state == "SEARCH" and self.path_index >= len(self.path):
                self.state = "IDLE"
        
        # Movement cooldown
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return  # can't move yet
        
        # Attempt to dodge bullets if possible (for "smart" behavior)
        if self.dodge_bullets_if_possible(bullets, grid):
            self.move_cooldown = self.get_move_interval()
            return
        
        # If we have a path (CHASE/SEARCH), follow it
        if self.path and self.path_index < len(self.path):
            tr, tc = self.path[self.path_index]
            if (self.r, self.c) == (tr, tc):
                self.path_index += 1
            else:
                # step 1 tile
                if self.r < tr:
                    self.r += 1
                elif self.r > tr:
                    self.r -= 1
                elif self.c < tc:
                    self.c += 1
                elif self.c > tc:
                    self.c -= 1
            self.move_cooldown = self.get_move_interval()
        
        else:
            # IDLE => move randomly each time cooldown expires
            if self.state == "IDLE":
                neighbors = [(self.r-1, self.c),
                             (self.r+1, self.c),
                             (self.r, self.c-1),
                             (self.r, self.c+1)]
                random.shuffle(neighbors)
                for (nr, nc) in neighbors:
                    if in_bounds(nr, nc) and grid[nr][nc] != 1:
                        self.r, self.c = nr, nc
                        break
                self.move_cooldown = self.get_move_interval()
        
        if self.path_update_cooldown > 0:
            self.path_update_cooldown -= 1

    def dodge_bullets_if_possible(self, bullets, grid):
        """
        If a bullet crosses our tile, we attempt to step away.
        Return True if dodged, else False.
        """
        ex, ey = tile_center(self.r, self.c)
        enemy_rect = pygame.Rect(ex - TILE_SIZE/2, ey - TILE_SIZE/2, TILE_SIZE, TILE_SIZE)
        
        threatening = False
        bullet_paths = []
        for b in bullets:
            if not b.alive:
                continue
            if line_rect_intersect(b.old_x, b.old_y, b.x, b.y, enemy_rect):
                threatening = True
            bullet_paths.append((b.old_x, b.old_y, b.x, b.y))
        
        if not threatening:
            return False
        
        # Attempt to move to a safe adjacent tile
        neighbors = [(self.r-1,self.c),(self.r+1,self.c),
                     (self.r,self.c-1),(self.r,self.c+1)]
        random.shuffle(neighbors)
        for (nr, nc) in neighbors:
            if in_bounds(nr, nc) and grid[nr][nc] != 1:
                nx, ny = tile_center(nr, nc)
                rect2 = pygame.Rect(nx - TILE_SIZE/2, ny - TILE_SIZE/2,
                                    TILE_SIZE, TILE_SIZE)
                
                safe = True
                for (ox, oy, xx, yy) in bullet_paths:
                    if line_rect_intersect(ox, oy, xx, yy, rect2):
                        safe = False
                        break
                if safe:
                    self.r, self.c = nr, nc
                    return True
        
        return False

    def spawn_explosion(self, explosions):
        x, y = tile_center(self.r, self.c)
        for _ in range(CONFIG["PARTICLE_COUNT"]):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(CONFIG["PARTICLE_SPEED_MIN"], CONFIG["PARTICLE_SPEED_MAX"])
            vx = math.cos(angle)*speed
            vy = math.sin(angle)*speed
            particle = Particle(x, y, vx, vy, RED, CONFIG["PARTICLE_LIFETIME"])
            explosions.append(particle)

    def draw(self, surface):
        if self.dead:
            return
        ex, ey = tile_center(self.r, self.c)
        rect = pygame.Rect(ex - TILE_SIZE/2, ey - TILE_SIZE/2,
                           TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)


def orientation(px, py, qx, qy, rx, ry):
    val = (qy - py) * (rx - qx) - (qx - px) * (ry - qy)
    if abs(val) < 1e-9:
        return 0
    return 1 if val > 0 else 2

def lines_intersect(p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y):
    o1 = orientation(p1x, p1y, p2x, p2y, p3x, p3y)
    o2 = orientation(p1x, p1y, p2x, p2y, p4x, p4y)
    o3 = orientation(p3x, p3y, p4x, p4y, p1x, p1y)
    o4 = orientation(p3x, p3y, p4x, p4y, p2x, p2y)
    if o1 != o2 and o3 != o4:
        return True
    return False

def line_rect_intersect(x1, y1, x2, y2, rect):
    edges = [
        (rect.topleft, rect.topright),
        (rect.topright, rect.bottomright),
        (rect.bottomright, rect.bottomleft),
        (rect.bottomleft, rect.topleft)
    ]
    for edge_start, edge_end in edges:
        if lines_intersect(
            x1, y1, x2, y2,
            edge_start[0], edge_start[1], edge_end[0], edge_end[1]
        ):
            return True
    return False

game_over_flag = False
def raise_player_caught():
    global game_over_flag
    game_over_flag = True


def main():
    global game_over_flag
    game_over_flag = False
    
    grid = copy_map()
    
    # Collect coins & free spots
    coins = []
    free_spots = []
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid[r][c] == 2:
                coins.append((r,c))
            if grid[r][c] in (0,2,3):
                free_spots.append((r,c))
    
    # Create player in random free spot
    pr, pc = random.choice(free_spots)
    player = Player(pr, pc)
    
    # Create enemies far from player
    enemies = []
    for _ in range(CONFIG["INITIAL_ENEMY_COUNT"]):
        spawn_enemy_far_from_player(grid, player, enemies, free_spots)

    spawn_timer = 0
    bullets = []
    explosions = []
    
    game_state = "MENU"
    start_time = 0
    time_left = CONFIG["TIME_LIMIT"]
    
    running = True
    while running:
        dt_ms = clock.tick(CONFIG["FPS"])
        dt = dt_ms / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    game_state = "PLAY"
                    start_time = pygame.time.get_ticks() // 1000
                    start_sound.play()
            
            elif game_state == "PLAY":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Attempt to shoot
                        if player.ammo > 0:
                            player.ammo -= 1
                            bx, by = player.x, player.y
                            bullet = Bullet(bx, by, player.dir_r, player.dir_c)
                            bullets.append(bullet)
                            shoot_sound.play()
                        else:
                            empty_sound.play()
            
            elif game_state in ("GAMEOVER", "WIN"):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    main()  # fully restart
                    return

        
        if game_state == "PLAY":
            current_time = pygame.time.get_ticks() // 1000
            elapsed = current_time - start_time
            time_left = CONFIG["TIME_LIMIT"] - elapsed
            if time_left <= 0:
                game_state = "GAMEOVER"
                lose_sound.play()
            
            # Player
            keys = pygame.key.get_pressed()
            player.update(dt, keys, grid)
            
            # Bullets
            for b in bullets:
                b.update(dt, enemies, explosions, grid)
            bullets = [b for b in bullets if b.alive]
            
            # Enemies
            try:
                for e in enemies:
                    e.update(grid, player, dt, bullets)
            except:
                pass
            
            if game_over_flag:
                game_state = "GAMEOVER"
                lose_sound.play()
            
            # Remove dead enemies
            enemies = [e for e in enemies if not e.dead]
            
            # Update explosions
            new_explosions = []
            for p in explosions:
                p.update(dt)
                if p.lifetime > 0:
                    new_explosions.append(p)
            explosions = new_explosions
            
            # Coin pickup
            rr, cc = player.get_tile_pos()
            if (rr, cc) in coins:
                coins.remove((rr, cc))
                grid[rr][cc] = 0
                coin_sound.play()
            
            # Ammo refill
            if in_bounds(rr, cc) and grid[rr][cc] == 3:
                if player.ammo < CONFIG["MAX_AMMO"]:
                    player.ammo = CONFIG["MAX_AMMO"]
                    ammo_sound.play()
            
            # Win condition
            if len(coins) == 0 and not game_over_flag:
                game_state = "WIN"
                win_sound.play()
            
            # Enemy spawn
            spawn_timer += 1
            if spawn_timer >= CONFIG["ENEMY_SPAWN_INTERVAL"]:
                spawn_timer = 0
                spawn_enemy_far_from_player(grid, player, enemies, free_spots)
        
        screen.fill(BLACK)
        
        if game_state == "MENU":
            text = big_font.render("Press ENTER to Start", True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(text, rect)
        
        elif game_state == "PLAY":
            draw_map(screen, grid, coins)
            
            for b in bullets:
                b.draw(screen)
            
            player.draw(screen)
            
            for e in enemies:
                e.draw(screen)
            
            for p in explosions:
                p.draw(screen)
            
            info_text = f"Time: {int(time_left)}s  Ammo: {player.ammo}/{CONFIG['MAX_AMMO']}  Coins: {len(coins)}"
            surf = font.render(info_text, True, WHITE)
            screen.blit(surf, (10, 10))
        
        elif game_state == "GAMEOVER":
            screen.fill(BLACK)
            text = big_font.render("GAME OVER! Press ENTER to Restart", True, RED)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(text, rect)
        
        elif game_state == "WIN":
            screen.fill(BLACK)
            text = big_font.render("YOU WIN! Press ENTER to Restart", True, GREEN)
            rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(text, rect)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

def spawn_enemy_far_from_player(grid, player, enemies, free_spots):
    """Pick a random free spot >= SPAWN_MIN_DISTANCE from player."""
    pr, pc = player.get_tile_pos()
    candidates = []
    for (r,c) in free_spots:
        dist = manhattan_distance((r,c), (pr,pc))
        if dist >= CONFIG["SPAWN_MIN_DISTANCE"]:
            candidates.append((r,c))
    if not candidates:
        candidates = free_spots[:]
    r, c = random.choice(candidates)
    enemies.append(Enemy(r, c))

def draw_map(surface, grid, coins):
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            val = grid[r][c]
            rect = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if val == 1:
                pygame.draw.rect(surface, BROWN, rect)  # wall
            elif val == 3:
                pygame.draw.rect(surface, (70,70,200), rect)  # ammo tile
            else:
                pygame.draw.rect(surface, (40,40,40), rect)   # floor
            
            pygame.draw.rect(surface, GRAY, rect, 1)
    
    # Draw coins
    for (rr, cc) in coins:
        x = cc * TILE_SIZE + TILE_SIZE//4
        y = rr * TILE_SIZE + TILE_SIZE//4
        w = TILE_SIZE//2
        coin_rect = pygame.Rect(x, y, w, w)
        pygame.draw.ellipse(surface, GOLD, coin_rect)
        pygame.draw.ellipse(surface, WHITE, coin_rect, 2)


game_over_flag = False

def raise_player_caught():
    global game_over_flag
    game_over_flag = True


if __name__ == "__main__":
    main()
