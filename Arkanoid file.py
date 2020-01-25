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


def start_screen():
    global running, game_level, next_level
    fon = pygame.transform.scale(load_image('start_screen.png'), (840, 600))
    screen.blit(fon, (0, 0))
    pygame.mixer.music.load('1234.mp3')
    pygame.mixer.music.play(-1)
    a = True
    while a:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = True
                game_level += 1
                next_level = True
                return  # начинаем игру
            if event.type == pygame.QUIT:
                a = False
        pygame.display.flip()