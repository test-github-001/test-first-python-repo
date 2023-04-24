###################
#
#  INITIALIZATION
#
###################

# pyinstaller --onefile --name MyGame --icon=icon.ico -F --noconsole main_4.py

# additional library for quit game
import sys

# import random integer
from random import randint

# init pygame and creating aliases
import pygame as PG
PG.init()
CLOCK = PG.time.Clock()
SPRITE = PG.sprite.Sprite

# set game screen
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN = PG.display.set_mode(SCREEN_SIZE)
# set screen caption
PG.display.set_caption("LABERINT 2")
# set screen icon
ICON = PG.image.load('./src/icon.png').convert_alpha()
PG.display.set_icon(ICON)
# set game loop speed
FPS = 60

frame = 0

# set game status
#'start' - start screen with text,
# 'game' - update game events,
# 'lose' or 'win' or 'next' - show corresponding screen with text
GAME_STATUS = 'start'

PLAYER_SHUTS_PER_SECOND = 1
ENEMY_SHUTS_PER_SECOND = 0.5

####################
#
#   UPLOAD FONTS
#
####################

# set font colors
C_WHITE = (255, 255, 255)
C_BLUE  = (  0, 255, 255)
# set fonts and font sizes
FONT_LIGHT = PG.font.Font('./src/Jura-Light.ttf', 64)
FONT_BOLD = PG.font.Font('./src/Jura-Bold.ttf', 128)

START_TITLE_TEXT = FONT_BOLD.render(f'SPACE WAR', True, C_WHITE)
START_TITLE_TEXT_POSITION = START_TITLE_TEXT.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT/ 2 - 60))

START_DESCRIPTION_TEXT = FONT_LIGHT.render(f'Press any button', True, C_BLUE)
START_DESCRIPTION_TEXT_POSITION = START_DESCRIPTION_TEXT.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT/ 2 + 30))

WIN_TITLE_TEXT = FONT_BOLD.render(f'WIN', True, C_WHITE)
WIN_TITLE_TEXT_POSITION = WIN_TITLE_TEXT.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT/ 2 - 60))

LOSE_TITLE_TEXT = FONT_BOLD.render(f'LOSE', True, C_WHITE)
LOSE_TITLE_TEXT_POSITION = LOSE_TITLE_TEXT.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT/ 2 - 60))

EXIT_DESCRIPTION_TEXT = FONT_LIGHT.render(f'Thanks for play', True, C_BLUE)
EXIT_DESCRIPTION_TEXT_POSITION = EXIT_DESCRIPTION_TEXT.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT/ 2 + 30))

##########################
#
#  CREATE SPRITE GROUPS
#
##########################

SPRITES_TO_DRAW = PG.sprite.Group() # use for drawing sprites
SPRITES_TO_UPDATE = PG.sprite.Group() # use for moving sprites
SOLID_SPRITES = PG.sprite.Group() # use for test collisions
ENEMY_BULLET_SPRITES = PG.sprite.Group() # use for test collisions player with enemy bullets
PLAYER_BULLET_SPRITES = PG.sprite.Group() # use for test collisions enemies with player bullets
ROCK_SPRITES = PG.sprite.Group() # use for test collisions with all bullets

###################
#
#   UPLOAD IMAGES
#
###################

def image_load(img):
    return PG.image.load(img).convert()

def image_load_alpha(img):
    return PG.image.load(img).convert_alpha()

BG_MENU_IMAGE = image_load('./src/bg-1200x800px.jpg')
BG_MENU_IMAGE_RECT = BG_MENU_IMAGE.get_rect()

BG_GAME_IMAGE = image_load('./src/bg-1-1920x1200px.jpg')

class Background():
    def __init__(self, target):
        self.target = target
        self.image = BG_GAME_IMAGE
        self.rect = BG_GAME_IMAGE.get_rect()
        self.dx = -(self.rect.width - SCREEN_WIDTH) / SCREEN_WIDTH
        self.dy = -(self.rect.height - SCREEN_HEIGHT) / SCREEN_HEIGHT
        self.update()

    def update(self):
        self.rect.x = self.target.rect.x * self.dx
        self.rect.y = self.target.rect.y * self.dy

    def draw(self):
        SCREEN.blit(self.image, self.rect)

ROCK_0_IMAGE = image_load_alpha('./src/rock-0-100x100px.png')
ROCK_1_IMAGE = image_load_alpha('./src/rock-1-100x100px.png')
ROCK_2_IMAGE = image_load_alpha('./src/rock-2-100x100px.png')
ROCK_3_IMAGE = image_load_alpha('./src/rock-3-100x100px.png')
ROCK_4_IMAGE = image_load_alpha('./src/rock-4-100x100px.png')

ROCK_IMAGES_LIST = [ROCK_0_IMAGE, ROCK_1_IMAGE, ROCK_2_IMAGE, ROCK_3_IMAGE, ROCK_4_IMAGE]

PORTAL_IMAGE = image_load_alpha('./src/portal-100x100px.png')

UNIT_MASK_IMAGE = image_load_alpha('./src/mask-80x80px.png')

PLAYER_IMAGE = image_load_alpha('./src/player-80x80px.png')
PLAYER_BULLET_IMAGE = image_load_alpha('./src/player-bullet-20x20px.png')

ENEMY_IMAGE = image_load_alpha('./src/enemy-80x80px.png')
ENEMY_BULLET_IMAGE = image_load_alpha('./src/enemy-bullet-20x20px.png')

###################
#
#   UNITS CLASSES
#
###################

class Sprite(SPRITE):
    def __init__(self, image, x, y, mask_image = None):
        SPRITE.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = PG.mask.from_surface(mask_image) if mask_image else PG.mask.from_surface(self.image) 

class Player(Sprite):
    def __init__(self, image, mask, x, y):
        Sprite.__init__(self, image, x, y, mask)
        self.speed = 2
        self.direction = 'U' # 'U'-up; 'D'-down; 'L'-left; 'R'-right.
        self.add_shut_frame = PLAYER_SHUTS_PER_SECOND * FPS
        self.frame_shut_ready = self.add_shut_frame

    def update(self):
        global GAME_STATUS

        for bullet in ENEMY_BULLET_SPRITES:
            if PG.sprite.collide_mask(self, bullet):
                GAME_STATUS = 'lose'
                return None

        speed_x = 0
        speed_y = 0
        # get pressed keys
        key = PG.key.get_pressed()
        if key[PG.K_LEFT]:
            speed_x = -self.speed
            self.direction = 'L'
        elif key[PG.K_RIGHT]:
            speed_x = self.speed
            self.direction = 'R'
        elif key[PG.K_UP]:
            speed_y = -self.speed
            self.direction = 'U'
        elif key[PG.K_DOWN]:
            speed_y = self.speed
            self.direction = 'D'

        self.rect.x += speed_x
        self.rect.y += speed_y

        if PG.sprite.collide_mask(self, portal):
            GAME_STATUS = 'win'

        # check to collide with someone other than self
        for solid in SOLID_SPRITES:
            if solid != self and  PG.sprite.collide_mask(self, solid):
                self.rect.x -= speed_x
                self.rect.y -= speed_y

        BG.update()

        if self.frame_shut_ready < frame and key[PG.K_SPACE]:
            self.frame_shut_ready = frame + self.add_shut_frame
            bullet = Bullet(PLAYER_BULLET_IMAGE, self.rect.x + 30, self.rect.y + 30, self.direction)
            SPRITES_TO_DRAW.add(bullet)
            SPRITES_TO_UPDATE.add(bullet)
            PLAYER_BULLET_SPRITES.add(bullet)
            
class Enemy(Sprite):
    def __init__(self, image, mask, x, y):
        Sprite.__init__(self, image, x, y, mask)
        self.speed = 2
        self.directions_list = ['U', 'D', 'L', 'R']
        self.direction = 'U'
        self.get_direction()
        self.add_shut_frame = ENEMY_SHUTS_PER_SECOND * FPS
        self.frame_shut_ready = self.add_shut_frame + randint(0, int(self.add_shut_frame))

    def get_direction(self):
        self.direction = self.directions_list[ randint( 0, 3 )]

    def update(self):
        global GAME_STATUS

        for bullet in PLAYER_BULLET_SPRITES:
            if PG.sprite.collide_mask(self, bullet):
                bullet.kill()
                return  self.kill()

        speed_x = 0
        speed_y = 0
        if self.direction == 'L':
            speed_x = -self.speed
        elif self.direction == 'R':
            speed_x = self.speed
        elif self.direction == 'U':
            speed_y = -self.speed
        elif self.direction == 'D':
            speed_y = self.speed

        self.rect.x += speed_x
        self.rect.y += speed_y

        # check to collide with someone other than self
        for solid in SOLID_SPRITES:
            if solid != self and PG.sprite.collide_mask(self, solid):
                self.rect.x -= speed_x
                self.rect.y -= speed_y
                self.get_direction()

        if self.frame_shut_ready < frame:
            self.frame_shut_ready = frame + self.add_shut_frame + randint(0, int(self.add_shut_frame))
            bullet = Bullet(ENEMY_BULLET_IMAGE, self.rect.x + 30, self.rect.y + 30, self.direction)
            SPRITES_TO_DRAW.add(bullet)
            SPRITES_TO_UPDATE.add(bullet)
            ENEMY_BULLET_SPRITES.add(bullet)

class Bullet(Sprite):
    def __init__(self, image, x, y, direction):
        Sprite.__init__(self, image, x, y)
        self.speed = 5
        self.speed_x = 0
        self.speed_y = 0
        if direction == 'U':
            self.speed_y = -self.speed
        if direction == 'D':
            self.speed_y = self.speed
        if direction == 'L':
            self.speed_x = -self.speed
        if direction == 'R':
            self.speed_x = self.speed

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        for rock in ROCK_SPRITES:
            if PG.sprite.collide_mask(self, rock):
                self.kill()
  
###################
#
#    GENERATE MAP
#
###################

# *** NEW ***
BG = None
portal = None
# *** NEW ***
MAP_LIST = []

'''
'#' - random rock
'E' - enemy
'P' - player
'Q' - portal
'''
# *** NEW ***
MAP1 = [
    ['#','#','#','#','#','#','#','#','#','#','#','#','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','Q','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#','P',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#','#','#','#','#','#','#','#','#','#','#','#','#'],
]
MAP_LIST.append(MAP1)

# *** NEW ***
MAP2 = [
    ['#','#','#','#','#','#','#','#','#','#','#','#','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ','E',' ',' ','Q','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ','E',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','E',' ','#'],
    ['#','P',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#','#','#','#','#','#','#','#','#','#','#','#','#'],
]
MAP_LIST.append(MAP2);

# *** NEW ***
MAP3 = [
    ['#','#','#','#','#','#','#','#','#','#','#','#','#'],
    ['#',' ','E',' ',' ',' ','E',' ',' ',' ','#','Q','#'],
    ['#',' ','#','#','#','#','#','#',' ',' ','#','E','#'],
    ['#',' ',' ',' ',' ',' ',' ','#',' ','E','#','E','#'],
    ['#','#','#','#','#',' ','E','#',' ',' ','#',' ','#'],
    ['#',' ',' ',' ','#',' ',' ','#','E',' ','#','E','#'],
    ['#',' ','#',' ','#','E',' ','#',' ',' ',' ',' ','#'],
    ['#','P','#',' ',' ',' ',' ','#',' ','E',' ',' ','#'],
    ['#','#','#','#','#','#','#','#','#','#','#','#','#'],
]
MAP_LIST.append(MAP3);

# *** NEW ***
def get_map( MAP ):
    global BG, portal
    # clear all sprite groups
    SPRITES_TO_DRAW.empty()
    SPRITES_TO_UPDATE.empty()
    SOLID_SPRITES.empty()
    # *** NEW ***
    ENEMY_BULLET_SPRITES.empty()
    PLAYER_BULLET_SPRITES.empty()
    ROCK_SPRITES.empty()

    map_step_x = 100
    map_step_y = 100
    map_y = -50
    for yy in MAP:
        map_x = -50
        for xx in yy:
            if xx == '#':
                n = randint(0, len(ROCK_IMAGES_LIST) - 1)
                rock = Sprite(ROCK_IMAGES_LIST[n], map_x, map_y)
                SPRITES_TO_DRAW.add(rock)
                SOLID_SPRITES.add(rock)
                ROCK_SPRITES.add(rock)
            elif xx == 'E':
                enemy = Enemy(ENEMY_IMAGE, UNIT_MASK_IMAGE, map_x + 10, map_y + 10)
                SPRITES_TO_DRAW.add(enemy)
                SPRITES_TO_UPDATE.add(enemy)
                SOLID_SPRITES.add(enemy)
            elif xx == 'P':
                player = Player(PLAYER_IMAGE, UNIT_MASK_IMAGE, map_x + 10, map_y + 10)
                SPRITES_TO_DRAW.add(player)
                SPRITES_TO_UPDATE.add(player)
                SOLID_SPRITES.add(player)
                BG = Background(player)
                print('bg ready')
            elif xx == 'Q':
                portal = Sprite(PORTAL_IMAGE, map_x, map_y)
                SPRITES_TO_DRAW.add(portal)
            
            map_x += map_step_x
        
        map_y += map_step_y

###################
#
#    GAME LOOP
#
###################

game_loop_is = True
# *** NEW ***
level = 0
get_map(MAP_LIST[level])

while game_loop_is:
    CLOCK.tick(FPS)
    for event in PG.event.get():
        # test game quit events
        if event.type == PG.QUIT or (event.type == PG.KEYDOWN and event.key == PG.K_ESCAPE):
            game_loop_is = False
    
    # START MENU
    if GAME_STATUS == 'start' or GAME_STATUS == 'lose' or  GAME_STATUS == 'win':
        SCREEN.blit(BG_MENU_IMAGE, BG_MENU_IMAGE_RECT)
        if GAME_STATUS == 'start':
            SCREEN.blit(START_TITLE_TEXT, START_TITLE_TEXT_POSITION)
            SCREEN.blit(START_DESCRIPTION_TEXT, START_DESCRIPTION_TEXT_POSITION)
            keys = PG.key.get_pressed()
            if True in keys:
                GAME_STATUS = 'game'
                
        elif GAME_STATUS == 'lose':
            SCREEN.blit(LOSE_TITLE_TEXT, LOSE_TITLE_TEXT_POSITION)
            SCREEN.blit(EXIT_DESCRIPTION_TEXT, EXIT_DESCRIPTION_TEXT_POSITION)
            keys = PG.key.get_pressed()
            if True in keys:
                # *** NEW ***
                level = 0
                get_map(MAP_LIST[level])
                GAME_STATUS = 'game'
        else:
            
            SCREEN.blit(WIN_TITLE_TEXT, WIN_TITLE_TEXT_POSITION)
            SCREEN.blit(EXIT_DESCRIPTION_TEXT, EXIT_DESCRIPTION_TEXT_POSITION)
            keys = PG.key.get_pressed()
            if True in keys:
                # *** NEW ***
                level += 1
                if level < len(MAP_LIST):
                    get_map(MAP_LIST[level])
                    GAME_STATUS = 'game'
                else:
                    pass

    # GAME PLAY
    else:
        # Fill the window background, draw and update sprites
        #SCREEN.blit(BG_IMAGE, BG_IMG_RECT)
        BG.draw()

        SPRITES_TO_DRAW.draw(SCREEN)
        SPRITES_TO_UPDATE.update()

    # update frame number
    frame += 1
    # Flip the display
    PG.display.flip()

# To quit
PG.quit()
sys.exit()