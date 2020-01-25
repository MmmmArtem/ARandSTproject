import pygame
import os
import time

pygame.init()
size = width, height = 840, 600
screen = pygame.display.set_mode(size)
fps = 0
clock = pygame.time.Clock()
clock_dt = 0
platforms = pygame.sprite.Group()
kirpichs = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
lose = False
god_mode = False
game_pausa = False
game_speed = 1
game_speed_x0 = 0.100
game_speed_y0 = 0.150
game_start = time.time()
game_time = 0
game_live = 3
next_live = False
game_level = 0
next_level = False
Vin = False


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
    return image