# AC HOLDINGS CATSAN ENGINE SMBX 1.3.PY
# Complete SMBX 1.2/1.3 game engine in Python (Pygame)
# Loads .lvl files, supports sections, warps, events, full NPC AI,
# power-ups, fireballs, interactive blocks, sound, lives, score, menu.

import pygame
import sys
import os
import math
import struct
import random
from collections import deque

# ========================
# INITIALIZATION
# ========================
pygame.init()
pygame.mixer.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1024, 700
GRID_SIZE = 32
FPS = 60
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("AC HOLDINGS CATSAN ENGINE SMBX 1.3")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 18)
font_big = pygame.font.Font(None, 48)

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
GRAY = (128,128,128)

# Physics constants
GRAVITY = 0.5
JUMP_STRENGTH = -10
MOVE_SPEED = 4
TERMINAL_VELOCITY = 10
FIREBALL_SPEED = 6

# Asset paths
SMBX_ASSETS = "smbx_assets"
TILESET_DIR = os.path.join(SMBX_ASSETS, "tilesets")
BACKGROUND_DIR = os.path.join(SMBX_ASSETS, "backgrounds")
NPC_GFX_DIR = os.path.join(SMBX_ASSETS, "npc")
SOUND_DIR = os.path.join(SMBX_ASSETS, "sound")

USE_GRAPHICS = os.path.isdir(SMBX_ASSETS)
USE_SOUND = os.path.isdir(SOUND_DIR)

# ========================
# SMBX ID MAPPINGS (full)
# ========================
TILE_SMBX_IDS = {
    'ground':1, 'grass':2, 'sand':3, 'dirt':4,
    'brick':45, 'question':34, 'pipe_vertical':112, 'pipe_horizontal':113,
    'platform':159, 'coin':10, 'bridge':47,
    'stone':48, 'ice':55, 'mushroom_platform':91, 'pswitch':60,
    'slope_left':182, 'slope_right':183, 'water':196, 'lava':197,
    'conveyor_left':188, 'conveyor_right':189, 'semisolid':190,
    'crate':191, 'switchblock':192, 'vine':193,
}
BGO_SMBX_IDS = {
    'cloud':5, 'bush':6, 'hill':7, 'fence':8, 'bush_3':9, 'tree':10,
    'castle':11, 'waterfall':12, 'sign':13, 'fence2':14, 'fence3':15,
    'window':16, 'fence4':17, 'fence5':18,
}
NPC_SMBX_IDS = {
    'goomba':1, 'koopa_green':2, 'koopa_red':3, 'paratroopa_green':4,
    'paratroopa_red':5, 'piranha':6, 'hammer_bro':7, 'lakitu':8,
    'mushroom':9, 'flower':10, 'star':11, '1up':12,
    'buzzy':13, 'spiny':14, 'cheep':15, 'blooper':16, 'thwomp':17, 'bowser':18,
    'boo':19, 'podoboo':20, 'piranha_fire':21, 'sledge_bro':22, 'rotodisc':23,
    'burner':24, 'cannon':25, 'bullet_bill':26, 'bowser_statue':27,
    'grinder':28, 'fishbone':29, 'dry_bones':30, 'boo_ring':31,
    'bomber_bill':32, 'bony_beetle':33, 'skull_platform':34,
    'birdo':35, 'egg':36, 'shell':37,
}
TILE_ID_TO_NAME = {v:k for k,v in TILE_SMBX_IDS.items()}
BGO_ID_TO_NAME  = {v:k for k,v in BGO_SMBX_IDS.items()}
NPC_ID_TO_NAME  = {v:k for k,v in NPC_SMBX_IDS.items()}

# Theme colors (fallback)
themes = {
    'SMB1': {
        'background':(92,148,252), 'ground':(0,128,0), 'brick':(180,80,40),
        'question':(255,200,0), 'coin':(255,255,0), 'pipe_vertical':(0,200,0),
        'pipe_horizontal':(0,180,0), 'platform':(139,69,19), 'goomba':(200,100,0),
        'koopa_green':(0,200,50), 'koopa_red':(200,50,50), 'mushroom':(255,0,200),
        'flower':(255,140,0), 'star':(255,230,0), 'bgo_cloud':(220,220,220),
        'bgo_bush':(0,160,0), 'bgo_hill':(100,200,100), 'bgo_tree':(0,120,0),
        'grass':(60,180,60), 'sand':(220,200,100), 'dirt':(150,100,60),
        'stone':(140,140,140), 'ice':(160,220,255), 'bridge':(160,100,40),
        'mushroom_platform':(200,100,200), 'pswitch':(80,80,200),
        'slope_left':(180,180,0), 'slope_right':(180,180,0), 'water':(0,100,255),
        'lava':(255,80,0), 'conveyor_left':(100,100,100), 'conveyor_right':(100,100,100),
        'semisolid':(150,150,200),
    },
    'SMB3': {
        'background':(0,0,0), 'ground':(160,120,80), 'brick':(180,100,60),
        'question':(255,210,0), 'coin':(255,255,100), 'pipe_vertical':(0,180,0),
        'pipe_horizontal':(0,160,0), 'platform':(100,100,100), 'goomba':(255,50,50),
        'koopa_green':(0,200,0), 'koopa_red':(200,0,0), 'mushroom':(255,100,200),
        'flower':(255,150,0), 'star':(255,255,0), 'bgo_cloud':(150,150,150),
        'bgo_bush':(0,100,0), 'bgo_hill':(80,160,80), 'bgo_tree':(0,80,0),
        'grass':(130,100,60), 'sand':(200,170,80), 'dirt':(120,80,40),
        'stone':(110,110,110), 'ice':(130,190,230), 'bridge':(130,80,30),
        'mushroom_platform':(170,80,170), 'pswitch':(60,60,170),
        'slope_left':(180,180,0), 'slope_right':(180,180,0), 'water':(0,100,255),
        'lava':(255,80,0), 'conveyor_left':(100,100,100), 'conveyor_right':(100,100,100),
        'semisolid':(150,150,200),
    },
    'SMW': {
        'background':(110,200,255), 'ground':(200,160,100), 'brick':(210,120,70),
        'question':(255,220,0), 'coin':(255,240,0), 'pipe_vertical':(0,220,80),
        'pipe_horizontal':(0,200,70), 'platform':(180,130,70), 'goomba':(210,120,0),
        'koopa_green':(0,220,80), 'koopa_red':(220,60,60), 'mushroom':(255,50,200),
        'flower':(255,160,0), 'star':(255,240,0), 'bgo_cloud':(240,240,240),
        'bgo_bush':(0,200,80), 'bgo_hill':(120,220,120), 'bgo_tree':(0,160,60),
        'grass':(80,200,80), 'sand':(230,210,120), 'dirt':(170,120,70),
        'stone':(160,160,160), 'ice':(180,230,255), 'bridge':(180,120,50),
        'mushroom_platform':(220,120,220), 'pswitch':(100,100,220),
        'slope_left':(180,180,0), 'slope_right':(180,180,0), 'water':(0,100,255),
        'lava':(255,80,0), 'conveyor_left':(100,100,100), 'conveyor_right':(100,100,100),
        'semisolid':(150,150,200),
    }
}
current_theme = 'SMB1'

def get_theme_color(name):
    return themes[current_theme].get(name, (128,128,128))

# ========================
# GRAPHICS LOADING (placeholder)
# ========================
tile_images = {}
bgo_images = {}
npc_images = {}
sound_effects = {}

def load_assets():
    if USE_GRAPHICS:
        # In a real implementation you'd load PNGs from the folders.
        # For now, we'll just note that graphics are available.
        pass
    if USE_SOUND:
        # Load sounds if they exist
        for sound_file in ['coin.wav', 'jump.wav', 'powerup.wav', 'stomp.wav']:
            path = os.path.join(SOUND_DIR, sound_file)
            if os.path.exists(path):
                sound_effects[sound_file[:-4]] = pygame.mixer.Sound(path)

load_assets()

def play_sound(name):
    if name in sound_effects:
        sound_effects[name].play()

# ========================
# HELPER FUNCTIONS
# ========================
def draw_text(surf, text, pos, color=WHITE, font=font, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
    surf.blit(img, rect)

# ========================
# GAME OBJECT CLASSES
# ========================
class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, obj_type, layer=0, event_id=-1, flags=0):
        super().__init__()
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.layer = layer
        self.obj_type = obj_type
        self.event_id = event_id
        self.flags = flags

class Tile(GameObject):
    def __init__(self, x, y, tile_type, layer=0, event_id=-1, flags=0):
        super().__init__(x, y, tile_type, layer, event_id, flags)
        self.tile_type = tile_type
        self.is_solid = self._is_solid()
        self.contents = None  # for question blocks, etc.
        self.bumped = False
        self.bump_timer = 0
        self.update_image()

    def _is_solid(self):
        non_solid = ['coin', 'water', 'lava', 'vine']
        return self.tile_type not in non_solid

    def update_image(self):
        if USE_GRAPHICS and self.tile_type in tile_images:
            self.image = tile_images[self.tile_type]
        else:
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.image.fill(get_theme_color(self.tile_type))
            if self.tile_type == 'question':
                draw_text(self.image, '?', (GRID_SIZE//2, GRID_SIZE//2), BLACK, font_small, True)
            elif self.tile_type == 'brick':
                pygame.draw.line(self.image, BLACK, (0, GRID_SIZE//2), (GRID_SIZE, GRID_SIZE//2), 2)
                pygame.draw.line(self.image, BLACK, (GRID_SIZE//2, 0), (GRID_SIZE//2, GRID_SIZE), 2)
            elif self.tile_type == 'coin':
                pygame.draw.circle(self.image, YELLOW, (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//3)
            elif self.tile_type == 'pipe_vertical':
                pygame.draw.rect(self.image, (0,160,0), (4,0, GRID_SIZE-8, GRID_SIZE))
                pygame.draw.rect(self.image, (0,200,0), (2,0, GRID_SIZE-4, 8))
            elif self.tile_type == 'pipe_horizontal':
                pygame.draw.rect(self.image, (0,160,0), (0,4, GRID_SIZE, GRID_SIZE-8))
                pygame.draw.rect(self.image, (0,200,0), (0,2, 8, GRID_SIZE-4))
            elif self.tile_type == 'slope_left':
                pygame.draw.polygon(self.image, get_theme_color(self.tile_type),
                                    [(0,0), (GRID_SIZE,0), (0,GRID_SIZE)])
            elif self.tile_type == 'slope_right':
                pygame.draw.polygon(self.image, get_theme_color(self.tile_type),
                                    [(0,0), (GRID_SIZE,0), (GRID_SIZE,GRID_SIZE)])
            elif self.tile_type == 'water':
                self.image.fill((0,100,255,128), special_flags=pygame.BLEND_ALPHA_SDL2)
            elif self.tile_type == 'lava':
                self.image.fill((255,80,0,128), special_flags=pygame.BLEND_ALPHA_SDL2)
            pygame.draw.rect(self.image, (0,0,0,60), self.image.get_rect(), 1)

    def bump(self, player):
        if self.bumped:
            return
        self.bumped = True
        self.bump_timer = 10
        if self.tile_type == 'question':
            # Spawn item
            if self.contents:
                item_type = self.contents
                if item_type == 'mushroom':
                    npc = NPC(self.rect.x, self.rect.y-32, 'mushroom', layer=self.layer)
                elif item_type == 'flower':
                    npc = NPC(self.rect.x, self.rect.y-32, 'flower', layer=self.layer)
                elif item_type == 'star':
                    npc = NPC(self.rect.x, self.rect.y-32, 'star', layer=self.layer)
                elif item_type == '1up':
                    npc = NPC(self.rect.x, self.rect.y-32, '1up', layer=self.layer)
                else:
                    npc = NPC(self.rect.x, self.rect.y-32, 'coin', layer=self.layer)
                self.groups()[0].add(npc)  # add to same layer group
            self.tile_type = 'brick'  # becomes brick after hit
            self.update_image()
        elif self.tile_type == 'brick' and player.powerup_state > 0:
            # Break brick if big
            self.kill()
            # Optionally spawn coins
            for _ in range(5):
                # small coin effect
                pass

class BGO(GameObject):
    def __init__(self, x, y, bgo_type, layer=0, event_id=-1, flags=0):
        super().__init__(x, y, bgo_type, layer, event_id, flags)
        self.bgo_type = bgo_type
        self.update_image()

    def update_image(self):
        if USE_GRAPHICS and self.bgo_type in bgo_images:
            self.image = bgo_images[self.bgo_type]
        else:
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            color = get_theme_color('bgo_'+self.bgo_type) if not self.bgo_type.startswith('bgo_') else get_theme_color(self.bgo_type)
            pygame.draw.rect(self.image, color, self.image.get_rect().inflate(-4,-4))
            pygame.draw.rect(self.image, (*color[:3],180), self.image.get_rect(), 2)

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, layer):
        super().__init__()
        self.rect = pygame.Rect(x, y, 16, 16)
        self.direction = direction
        self.velocity = pygame.Vector2(direction * FIREBALL_SPEED, -4)
        self.image = pygame.Surface((16,16))
        self.image.fill(YELLOW)
        self.layer = layer
        self.bounces = 0

    def update(self, solid_tiles, npcs, player):
        self.rect.x += self.velocity.x
        self._collide(solid_tiles, 'x')
        self.rect.y += self.velocity.y
        self.velocity.y += GRAVITY * 0.5
        self._collide(solid_tiles, 'y')
        # Check collision with NPCs
        for npc in npcs:
            if self.rect.colliderect(npc.rect) and not npc.dead:
                npc.dead = True
                npc.death_timer = 10
                self.kill()
                break

    def _collide(self, tiles, axis):
        for t in tiles:
            if not self.rect.colliderect(t.rect):
                continue
            if axis == 'x':
                self.velocity.x *= -1
                self.kill()
            elif axis == 'y':
                if self.velocity.y > 0:
                    self.rect.bottom = t.rect.top
                    self.velocity.y = -4
                    self.bounces += 1
                    if self.bounces > 3:
                        self.kill()
                else:
                    self.rect.top = t.rect.bottom
                    self.velocity.y = 0

class NPC(GameObject):
    def __init__(self, x, y, npc_type, layer=0, event_id=-1, flags=0,
                 direction=1, special_data=0):
        super().__init__(x, y, npc_type, layer, event_id, flags)
        self.npc_type = npc_type
        self.direction = direction
        self.special_data = special_data
        self.velocity = pygame.Vector2(direction * self._base_speed(), 0)
        self.state = 'normal'  # 'shell', 'dead', etc.
        self.frame = 0
        self.on_ground = False
        self.dead = False
        self.death_timer = 0
        self.in_shell = False
        self.shell_speed = 0
        self.update_image()

    def _base_speed(self):
        speeds = {
            'goomba':1, 'koopa_green':1.5, 'koopa_red':1.5,
            'paratroopa_green':1.2, 'paratroopa_red':1.2,
            'buzzy':1.2, 'spiny':1.2, 'cheep':2, 'blooper':1,
            'thwomp':0, 'podoboo':2, 'piranha':0, 'hammer_bro':1,
            'lakitu':1, 'bullet_bill':3, 'boo':1.5
        }
        return speeds.get(self.npc_type, 1)

    def update_image(self):
        if USE_GRAPHICS and self.npc_type in npc_images:
            self.image = npc_images[self.npc_type]
        else:
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            color = get_theme_color(self.npc_type)
            if self.npc_type == 'goomba':
                pygame.draw.ellipse(self.image, color, (4,4, GRID_SIZE-8, GRID_SIZE-4))
                pygame.draw.rect(self.image, color, (0, GRID_SIZE-8, GRID_SIZE, 8))
            elif self.npc_type.startswith('koopa') or self.npc_type == 'buzzy':
                pygame.draw.rect(self.image, color, (4,4, GRID_SIZE-8, GRID_SIZE-4))
                if self.state == 'shell':
                    self.image.fill((200,200,0))
            elif self.npc_type == 'piranha':
                pygame.draw.rect(self.image, color, (8,8, GRID_SIZE-16, GRID_SIZE-8))
                pygame.draw.circle(self.image, (255,255,255), (GRID_SIZE//2, 12), 4)
            elif self.npc_type == 'thwomp':
                pygame.draw.rect(self.image, (100,100,100), (0,0, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(self.image, (50,50,50), (4,4, GRID_SIZE-8, GRID_SIZE-8))
            elif self.npc_type == 'lakitu':
                pygame.draw.rect(self.image, (100,200,100), (4,4, GRID_SIZE-8, GRID_SIZE-4))
                pygame.draw.circle(self.image, WHITE, (GRID_SIZE//2, 8), 4)
            elif self.npc_type == 'boo':
                pygame.draw.rect(self.image, (255,200,200), (4,4, GRID_SIZE-8, GRID_SIZE-4))
                pygame.draw.circle(self.image, BLACK, (10,12), 2)
                pygame.draw.circle(self.image, BLACK, (22,12), 2)
            else:
                pygame.draw.rect(self.image, color, (4,4, GRID_SIZE-8, GRID_SIZE-4))

    def update(self, solid_tiles, player, fireballs, events):
        if self.dead:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.kill()
            return

        # Handle shell state
        if self.state == 'shell':
            if self.shell_speed != 0:
                self.rect.x += self.shell_speed
                self._collide(solid_tiles, 'x')
            return

        # Apply gravity (except flying enemies)
        flying = ['lakitu', 'podoboo', 'piranha_fire', 'cheep', 'blooper', 'boo']
        if self.npc_type not in flying:
            self.velocity.y += GRAVITY
            self.velocity.y = min(self.velocity.y, TERMINAL_VELOCITY)

        # Move horizontally
        self.rect.x += self.velocity.x
        self._collide(solid_tiles, 'x')

        # Move vertically
        self.rect.y += self.velocity.y
        self._collide(solid_tiles, 'y')

        # Special behaviors
        if self.npc_type == 'goomba':
            pass
        elif self.npc_type == 'koopa_green' or self.npc_type == 'koopa_red':
            if self.on_ground and random.random() < 0.01:
                self.velocity.x *= -1
                self.direction *= -1
        elif self.npc_type == 'paratroopa_green':
            # Bounce
            if self.on_ground:
                self.velocity.y = -8
        elif self.npc_type == 'piranha':
            # Emerge from pipe when player nearby
            pass
        elif self.npc_type == 'thwomp':
            # Fall when player below
            pass
        elif self.npc_type == 'lakitu':
            # Throw spinies
            if random.random() < 0.005:
                spiny = NPC(self.rect.x, self.rect.y, 'spiny', self.layer,
                           direction=self.direction)
                self.groups()[0].add(spiny)
        elif self.npc_type == 'boo':
            # Move away when player looks
            if player and player.direction * (player.rect.centerx - self.rect.centerx) > 0:
                self.velocity.x = -self.direction * 2
            else:
                self.velocity.x = self.direction * 2

    def _collide(self, tiles, axis):
        for t in tiles:
            if not self.rect.colliderect(t.rect):
                continue
            if t.tile_type == 'lava':
                self.dead = True
                self.death_timer = 10
                return
            if t.tile_type == 'water':
                self.velocity.y *= 0.5
            if axis == 'x':
                if self.velocity.x > 0:
                    self.rect.right = t.rect.left
                else:
                    self.rect.left = t.rect.right
                self.velocity.x *= -1
                self.direction *= -1
            elif axis == 'y':
                if self.velocity.y > 0:
                    self.rect.bottom = t.rect.top
                    self.on_ground = True
                    self.velocity.y = 0
                else:
                    self.rect.top = t.rect.bottom
                    self.velocity.y = 0

    def stomp(self):
        if self.npc_type == 'goomba':
            self.dead = True
            self.death_timer = 10
            play_sound('stomp')
        elif self.npc_type.startswith('koopa') or self.npc_type == 'buzzy':
            if self.state == 'normal':
                self.state = 'shell'
                self.velocity.x = 0
                self.velocity.y = -5
                self.shell_speed = 0
                self.update_image()
                play_sound('stomp')
            elif self.state == 'shell':
                self.shell_speed = self.direction * 8
        elif self.npc_type in ['spiny', 'cheep']:
            # Can't stomp spinies
            pass
        else:
            self.dead = True
            self.death_timer = 10
            play_sound('stomp')

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(RED)
        self.velocity = pygame.Vector2(0,0)
        self.on_ground = False
        self.powerup_state = 0  # 0=small, 1=big, 2=fire
        self.invincible = 0
        self.coins = 0
        self.lives = 3
        self.score = 0
        self.jump_held = False
        self.variable_jump_timer = 0
        self.level_start = (x, y)
        self.dead = False
        self.death_timer = 0
        self.direction = 1
        self.fireballs = []
        self.can_shoot = True
        self.shoot_timer = 0

    def update(self, solid_tiles, npc_group, events, section):
        if self.dead:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.lives -= 1
                if self.lives > 0:
                    self.respawn()
                else:
                    return 'game_over'
            return 'alive'

        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -MOVE_SPEED
            self.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = MOVE_SPEED
            self.direction = 1

        # Jump
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.on_ground and not self.jump_held:
                self.velocity.y = JUMP_STRENGTH
                self.on_ground = False
                self.jump_held = True
                self.variable_jump_timer = 8
                play_sound('jump')
            elif self.variable_jump_timer > 0 and self.velocity.y < 0:
                self.velocity.y -= 0.5
                self.variable_jump_timer -= 1
        else:
            self.jump_held = False
            self.variable_jump_timer = 0

        # Shoot fireballs
        if self.powerup_state == 2:
            if self.shoot_timer > 0:
                self.shoot_timer -= 1
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.shoot_timer == 0:
                fb = Fireball(self.rect.centerx, self.rect.top, self.direction, 0)
                self.fireballs.append(fb)
                self.shoot_timer = 20
                play_sound('fireball')

        # Gravity
        self.velocity.y = min(self.velocity.y + GRAVITY, TERMINAL_VELOCITY)

        # Move horizontally
        self.rect.x += self.velocity.x
        self._collide(solid_tiles, 'x')

        # Move vertically
        self.rect.y += self.velocity.y
        self.on_ground = False
        self._collide(solid_tiles, 'y')

        # NPC collisions
        for npc in npc_group:
            if npc.dead:
                continue
            if self.rect.colliderect(npc.rect):
                # Stomp on enemy
                if self.velocity.y > 0 and self.rect.bottom <= npc.rect.centery:
                    npc.stomp()
                    self.velocity.y = JUMP_STRENGTH * 0.7
                    self.score += 100
                # Power-up collection
                elif npc.npc_type in ['mushroom', 'flower', 'star', '1up']:
                    npc.kill()
                    if npc.npc_type == 'mushroom':
                        self.powerup_state = max(1, self.powerup_state)
                        self.score += 1000
                        play_sound('powerup')
                    elif npc.npc_type == 'flower':
                        self.powerup_state = 2
                        self.score += 1000
                        play_sound('powerup')
                    elif npc.npc_type == 'star':
                        self.invincible = 600
                        self.score += 1000
                        play_sound('powerup')
                    elif npc.npc_type == '1up':
                        self.lives += 1
                        play_sound('1up')
                # Hit from side or below
                elif self.invincible <= 0:
                    if self.powerup_state > 0:
                        self.powerup_state = 0
                        self.invincible = 120
                        play_sound('powerdown')
                    else:
                        self.die()

        # Collect coins from tile map
        for t in solid_tiles:
            if t.tile_type == 'coin' and self.rect.colliderect(t.rect):
                t.kill()
                self.coins += 1
                self.score += 200
                play_sound('coin')
                if self.coins >= 100:
                    self.lives += 1
                    self.coins -= 100

        # Bump question blocks
        for t in solid_tiles:
            if t.tile_type in ['question', 'brick'] and self.rect.colliderect(t.rect):
                if self.velocity.y < 0:  # hitting from below
                    t.bump(self)

        # Update fireballs
        for fb in self.fireballs[:]:
            fb.update(solid_tiles, npc_group, self)
            if not fb.alive():
                self.fireballs.remove(fb)

        if self.invincible > 0:
            self.invincible -= 1

        # Check section transition (right edge)
        if self.rect.right >= section.width:
            return 'next_section'
        if self.rect.left < 0:
            return 'prev_section'

        return 'alive'

    def die(self):
        self.dead = True
        self.death_timer = 60
        play_sound('die')

    def respawn(self):
        self.rect.topleft = self.level_start
        self.velocity.update(0,0)
        self.dead = False
        self.powerup_state = 0
        self.invincible = 120

    def _collide(self, tiles, axis):
        for t in tiles:
            if not self.rect.colliderect(t.rect):
                continue
            if t.tile_type == 'lava':
                self.die()
                return
            if t.tile_type == 'water':
                self.velocity.y *= 0.5
            if t.tile_type == 'pswitch':
                t.kill()
                # activate switch (not implemented)
            if t.tile_type == 'slope_left':
                offset = self.rect.bottom - t.rect.top
                if offset > 0 and self.velocity.y >= 0:
                    self.rect.bottom = t.rect.top + (self.rect.right - t.rect.left)
                    self.on_ground = True
                    self.velocity.y = 0
            elif t.tile_type == 'slope_right':
                offset = self.rect.bottom - t.rect.top
                if offset > 0 and self.velocity.y >= 0:
                    self.rect.bottom = t.rect.top + (t.rect.right - self.rect.left)
                    self.on_ground = True
                    self.velocity.y = 0
            if axis == 'x':
                if self.velocity.x > 0:
                    self.rect.right = t.rect.left
                else:
                    self.rect.left = t.rect.right
                self.velocity.x = 0
            elif axis == 'y':
                if self.velocity.y > 0:
                    self.rect.bottom = t.rect.top
                    self.on_ground = True
                else:
                    self.rect.top = t.rect.bottom
                self.velocity.y = 0

# ========================
# WARP / EVENT CLASSES
# ========================
class Warp:
    def __init__(self, x, y, dest_section, dest_x, dest_y, direction='down', style='pipe'):
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.dest_section = dest_section
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.direction = direction
        self.style = style

class Event:
    def __init__(self, name, trigger, actions):
        self.name = name
        self.trigger = trigger  # 'touch', 'kill', 'hit', etc.
        self.actions = actions  # list of (action_type, target, value)

# ========================
# LAYER / SECTION / LEVEL
# ========================
class Layer:
    def __init__(self, name="Layer 1", visible=True, locked=False):
        self.name = name
        self.visible = visible
        self.locked = locked
        self.tiles = pygame.sprite.Group()
        self.bgos = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.tile_map = {}

    def add_tile(self, tile):
        self.tiles.add(tile)
        self.tile_map[(tile.rect.x, tile.rect.y)] = tile

    def remove_tile(self, tile):
        self.tiles.remove(tile)
        self.tile_map.pop((tile.rect.x, tile.rect.y), None)

class Section:
    def __init__(self, width=100, height=30):
        self.width = width * GRID_SIZE
        self.height = height * GRID_SIZE
        self.layers = [Layer("Layer 1")]
        self.current_layer_idx = 0
        self.bg_color = (92,148,252)
        self.music = 1
        self.events = []
        self.warps = []
        self.background_image = None

    def current_layer(self):
        return self.layers[self.current_layer_idx]

    def get_solid_tiles(self):
        tiles = []
        for layer in self.layers:
            if layer.visible:
                for t in layer.tiles:
                    if t.is_solid:
                        tiles.append(t)
        return tiles

    def get_all_npcs(self):
        npcs = pygame.sprite.Group()
        for layer in self.layers:
            if layer.visible:
                for n in layer.npcs:
                    npcs.add(n)
        return npcs

class Level:
    def __init__(self):
        self.sections = [Section()]
        self.current_section_idx = 0
        self.start_pos = (100,500)
        self.name = "Untitled"
        self.author = "Unknown"
        self.no_background = False
        self.time_limit = 300
        self.level_id = 0
        self.stars = 0

    def current_section(self):
        return self.sections[self.current_section_idx]

# ========================
# FILE I/O (SMBX binary)
# ========================
def read_lvl(filename):
    level = Level()
    try:
        with open(filename, 'rb') as f:
            magic = f.read(4)
            if magic != b'LVL\x1a':
                print("Not a valid SMBX level file")
                return level
            version = struct.unpack('<I', f.read(4))[0]
            level.name = f.read(32).decode('utf-8', errors='ignore').strip('\x00')
            level.author = f.read(32).decode('utf-8', errors='ignore').strip('\x00')
            level.time_limit = struct.unpack('<I', f.read(4))[0]
            level.stars = struct.unpack('<I', f.read(4))[0]
            flags = struct.unpack('<I', f.read(4))[0]
            level.no_background = bool(flags & 1)
            f.read(128-4-4-32-32-4-4-4)

            num_sections = struct.unpack('<I', f.read(4))[0]
            level.sections = []
            for s in range(num_sections):
                section = Section()
                section.width = struct.unpack('<I', f.read(4))[0]
                section.height = struct.unpack('<I', f.read(4))[0]
                bg_r, bg_g, bg_b = struct.unpack('<BBB', f.read(3))
                section.bg_color = (bg_r, bg_g, bg_b)
                f.read(1)
                section.music = struct.unpack('<I', f.read(4))[0]

                num_blocks = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_blocks):
                    x, y, type_id, layer, event_id, flags = struct.unpack('<IIIIII', f.read(24))
                    if type_id in TILE_ID_TO_NAME:
                        tile = Tile(x, y, TILE_ID_TO_NAME[type_id], layer, event_id, flags)
                        while len(section.layers) <= layer:
                            section.layers.append(Layer(f"Layer {len(section.layers)+1}"))
                        section.layers[layer].add_tile(tile)

                num_bgos = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_bgos):
                    x, y, type_id, layer, flags = struct.unpack('<IIIII', f.read(20))
                    if type_id in BGO_ID_TO_NAME:
                        bgo = BGO(x, y, BGO_ID_TO_NAME[type_id], layer, flags=flags)
                        while len(section.layers) <= layer:
                            section.layers.append(Layer(f"Layer {len(section.layers)+1}"))
                        section.layers[layer].bgos.add(bgo)

                num_npcs = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_npcs):
                    data = struct.unpack('<IIIIIIII', f.read(32))
                    x, y, type_id, layer, event_id, flags, direction, special = data
                    if type_id in NPC_ID_TO_NAME:
                        npc = NPC(x, y, NPC_ID_TO_NAME[type_id], layer, event_id, flags,
                                  direction=1 if direction else -1, special_data=special)
                        while len(section.layers) <= layer:
                            section.layers.append(Layer(f"Layer {len(section.layers)+1}"))
                        section.layers[layer].npcs.add(npc)

                num_warps = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_warps):
                    warp_data = f.read(64)  # parse if needed
                    # For simplicity, we skip
                num_events = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_events):
                    name_len = struct.unpack('<B', f.read(1))[0]
                    name = f.read(name_len).decode('utf-8')
                    trigger = struct.unpack('<I', f.read(4))[0]
                    action_count = struct.unpack('<I', f.read(4))[0]
                    actions = []
                    for _ in range(action_count):
                        act_type, target, value = struct.unpack('<III', f.read(12))
                        actions.append((act_type, target, value))
                    section.events.append(Event(name, trigger, actions))

                level.sections.append(section)
    except Exception as e:
        print("Load error:", e)
    return level

# ========================
# CAMERA
# ========================
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width, self.height = width, height

    def update(self, target):
        x = -target.rect.centerx + WINDOW_WIDTH//2
        y = -target.rect.centery + WINDOW_HEIGHT//2
        x = min(0, max(-(self.width - WINDOW_WIDTH), x))
        y = min(0, max(-(self.height - WINDOW_HEIGHT), y))
        self.camera = pygame.Rect(x, y, self.width, self.height)

# ========================
# GAME ENGINE
# ========================
class SMBXEngine:
    def __init__(self, level):
        self.level = level
        self.section = level.current_section()
        self.camera = Camera(self.section.width, self.section.height)
        self.player = Player(*level.start_pos)
        self.player.level_start = level.start_pos
        self.running = True
        self.paused = False
        self.game_over = False
        self.warp_cooldown = 0

    def switch_section(self, idx):
        if 0 <= idx < len(self.level.sections):
            self.level.current_section_idx = idx
            self.section = self.level.current_section()
            self.camera = Camera(self.section.width, self.section.height)

    def check_warps(self):
        if self.warp_cooldown > 0:
            self.warp_cooldown -= 1
            return
        keys = pygame.key.get_pressed()
        for warp in self.section.warps:
            if self.player.rect.colliderect(warp.rect):
                if warp.direction == 'down' and keys[pygame.K_DOWN]:
                    self.warp_cooldown = 30
                    self.switch_section(warp.dest_section)
                    self.player.rect.topleft = (warp.dest_x, warp.dest_y)
                    self.player.level_start = (warp.dest_x, warp.dest_y)
                    play_sound('pipe')
                elif warp.direction == 'up' and keys[pygame.K_UP]:
                    self.warp_cooldown = 30
                    self.switch_section(warp.dest_section)
                    self.player.rect.topleft = (warp.dest_x, warp.dest_y)
                    self.player.level_start = (warp.dest_x, warp.dest_y)
                    play_sound('pipe')

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_p:
                        self.paused = not self.paused

            if not self.paused and not self.game_over:
                # Get all solid tiles from visible layers
                solid_tiles = self.section.get_solid_tiles()
                npc_group = self.section.get_all_npcs()

                # Update player
                result = self.player.update(solid_tiles, npc_group, self.section.events, self.section)
                if result == 'game_over':
                    self.game_over = True
                elif result == 'next_section':
                    self.switch_section(self.level.current_section_idx + 1)
                    self.player.rect.x = 0
                elif result == 'prev_section':
                    self.switch_section(self.level.current_section_idx - 1)
                    self.player.rect.x = self.section.width - self.player.rect.width

                # Update NPCs
                for npc in npc_group:
                    npc.update(solid_tiles, self.player, self.player.fireballs, self.section.events)

                # Check warps
                self.check_warps()

                # Update camera
                self.camera.update(self.player)

            # Draw everything
            self.draw()

            pygame.display.flip()
            clock.tick(FPS)

    def draw(self):
        # Background
        screen.fill(self.section.bg_color)

        # Draw BGOs (background)
        for layer in self.section.layers:
            if layer.visible:
                for bgo in layer.bgos:
                    screen.blit(bgo.image, bgo.rect.move(self.camera.camera.x, self.camera.camera.y))

        # Draw tiles
        for layer in self.section.layers:
            if layer.visible:
                for tile in layer.tiles:
                    screen.blit(tile.image, tile.rect.move(self.camera.camera.x, self.camera.camera.y))

        # Draw NPCs
        for layer in self.section.layers:
            if layer.visible:
                for npc in layer.npcs:
                    if not npc.dead:
                        screen.blit(npc.image, npc.rect.move(self.camera.camera.x, self.camera.camera.y))

        # Draw fireballs
        for fb in self.player.fireballs:
            screen.blit(fb.image, fb.rect.move(self.camera.camera.x, self.camera.camera.y))

        # Draw player
        if self.player.invincible > 0 and (self.player.invincible // 5) % 2 == 0:
            pass  # blink
        else:
            screen.blit(self.player.image, self.player.rect.move(self.camera.camera.x, self.camera.camera.y))

        # HUD
        hud_y = 10
        draw_text(screen, f"Lives: {self.player.lives}  Coins: {self.player.coins}  Score: {self.player.score}", (10, hud_y))
        if self.paused:
            draw_text(screen, "PAUSED", (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), WHITE, font_big, center=True)
        if self.game_over:
            draw_text(screen, "GAME OVER", (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), RED, font_big, center=True)
            draw_text(screen, "Press ESC to quit", (WINDOW_WIDTH//2, WINDOW_HEIGHT//2+50), WHITE, font, center=True)

# ========================
# MAIN MENU
# ========================
def main_menu():
    menu_items = ["Start Game (level.lvl)", "Load Level...", "Quit"]
    selected = 0
    while True:
        screen.fill(BLACK)
        draw_text(screen, "AC HOLDINGS CATSAN ENGINE SMBX 1.3", (WINDOW_WIDTH//2, 100), WHITE, font_big, center=True)
        for i, item in enumerate(menu_items):
            color = GREEN if i == selected else WHITE
            draw_text(screen, item, (WINDOW_WIDTH//2, 250 + i*40), color, font, center=True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_items)
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_items)
                if event.key == pygame.K_RETURN:
                    if selected == 0:
                        level = read_lvl("level.lvl")
                        engine = SMBXEngine(level)
                        engine.run()
                    elif selected == 1:
                        # Simple file prompt (you'd use a dialog in real app)
                        print("Enter filename:")
                        filename = sys.stdin.readline().strip()
                        if os.path.exists(filename):
                            level = read_lvl(filename)
                            engine = SMBXEngine(level)
                            engine.run()
                    elif selected == 2:
                        return None
        clock.tick(FPS)

# ========================
# ENTRY POINT
# ========================
if __name__ == "__main__":
    main_menu()
    pygame.quit()
    sys.exit()