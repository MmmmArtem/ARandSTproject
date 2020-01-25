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


def sboku(plat_r, shar_r, ydir):
    st = ''
    dx1 = shar_r.x + shar_r.width - plat_r.x
    dx2 = plat_r.x + plat_r.width - shar_r.x
    if ydir == 1:
        dy1 = (shar_r.y + shar_r.height) - plat_r.y
        if 0 < dx1 < dy1:
            st = 'left'
        if 0 < dx2 < dy1:
            st = 'right'
    else:
        dy2 = (plat_r.y + plat_r.height) - shar_r.y
        if 0 < dx1 < dy2:
            st = 'left'
        if 0 < dx2 < dy2:
            st = 'right'
    return st


class Platform(pygame.sprite.Sprite):
    image = load_image('platform.png')

    def __init__(self):
        super().__init__(platforms, all_sprites)
        self.image = Platform.image
        self.rect = self.image.get_rect()
        self.rect.y = 550
        self.rect.x = (width - self.rect.width) // 2
        self.dx = 0
        self.vx = 1000 / 1000  # 1000 пикселей в секунду
        self.moveleft = False
        self.moverght = False

    def update(self, dt):
        if not game_pausa:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.moveleft = self.rect.x > 0
                self.dx -= self.vx * dt
                int_dx = int(self.dx)
                if int_dx < 0:
                    self.rect.x += int_dx
                    self.rect.x = max(0, self.rect.x)
                    self.dx = self.dx - int_dx
            else:
                self.moveleft = False
            if keys[pygame.K_RIGHT]:
                self.moverght = self.rect.x < width - self.rect.width
                self.dx += self.vx * dt
                int_dx = int(self.dx)
                if int_dx > 0:
                    self.rect.x += int_dx
                    self.rect.x = min(width - self.rect.width, self.rect.x)
                    self.dx = self.dx - int_dx
            else:
                self.moverght = False


class Shar(pygame.sprite.Sprite):
    image = load_image('shar.png')

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Shar.image
        self.rect = self.image.get_rect()
        self.dx = 0
        self.dy = 0
        self.vx = game_speed_x0 * game_speed
        self.vy = game_speed_y0 * game_speed
        self.numx = 1
        self.numy = 1
        self.razbit_kirp = 0

    def reset(self):
        self.rect.y = 300
        self.rect.x = 300
        self.dx = 0
        self.dy = 0
        self.vx = game_speed_x0 * game_speed
        self.vy = game_speed_y0 * game_speed
        self.numx = 1
        self.numy = 1

    def update(self, dt):
        global lose, game_live, next_live
        self.dx += self.vx * dt
        self.dy += self.vy * dt
        int_dx = int(self.dx)
        int_dy = int(self.dy)
        if int_dx > 0:
            self.rect.x += int_dx * self.numx
            # отскок от стен
            if self.rect.x <= 0 or self.rect.x + self.rect.width > width:
                self.numx = -self.numx
            self.dx = self.dx - int_dx
        if int_dy > 0:
            self.rect.y += int_dy * self.numy
            if self.rect.y + self.rect.height >= height:
                if god_mode:
                    self.numy = -self.numy
                    self.rect.y = height - self.rect.height
                else:
                    game_live -= 1
                    # игра проиграна
                    if game_live == 0:
                        pygame.mixer.music.stop()
                        lose = True
                    else:
                        next_live = True
            # отскок от потолка
            if self.rect.y <= 0:
                self.numy = -self.numy
                self.rect.y = 0
            self.dy = self.dy - int_dy
        # отскок от платформы
        if not lose:
            coll_p = pygame.sprite.spritecollide(self, platforms, False)
            if coll_p:
                for plat in coll_p:
                    sb = sboku(plat.rect, self.rect, self.numy)
                    if sb == 'left':
                        self.numx = -self.numx
                    elif sb == 'right':
                        self.numx = -self.numx
                    else:
                        # Подкручивание
                        if plat.moveleft and self.numx > 0:
                            self.numx = -self.numx
                        if plat.moverght and self.numx < 0:
                            self.numx = -self.numx
                        # Шар выше платформы
                        if self.numy > 0:
                            self.numy = -self.numy
                            self.rect.y = plat.rect.y - self.rect.height
                        else:
                            self.numy = -self.numy
                            self.rect.y = plat.rect.y + self.rect.height
            coll_k = pygame.sprite.spritecollide(self, kirpichs, False)
            if coll_k:
                for kirp in coll_k:
                    lk = 0
                    rk = 0
                    sb = sboku(kirp.rect, self.rect, self.numy)
                    if sb == 'left':
                        if lk == 0:
                            self.numx = -self.numx
                        lk += 1
                    elif sb == 'right':
                        if rk == 0:
                            self.numx = -self.numx
                        rk += 1
                    else:
                        self.numy = -self.numy
                    kirp.kontakt += 1
                    if kirp.kontakt == game_level:
                        self.razbit_kirp += game_level
                        kirp.kill()


running = False
if running == False:
    start_screen()
if running:
    shar_1 = Shar()
    platform_1 = Platform()
vin_image = load_image('Vin.png')
background_image = load_image('Fon.jpg')
lose_image = load_image('lose.png')
pygame.mixer.music.load('123.mp3')
pygame.mixer.music.play()
