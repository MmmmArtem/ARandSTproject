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


class Kirpichi(pygame.sprite.Sprite):
    image = load_image("kirpich.png")
    image1 = load_image("kirpich1.jpg")
    image2 = load_image("kirpich2.jpg")

    def __init__(self):
        super().__init__(kirpichs, all_sprites)
        if game_level == 1:
            self.image = Kirpichi.image
        if game_level == 2:
            self.image = Kirpichi.image1
        if game_level == 3:
            self.image = Kirpichi.image2
        self.rect = self.image.get_rect()
        self.rect.x = kx
        self.rect.y = ky
        self.kontakt = 0


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
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_pausa = not game_pausa
                if game_pausa:
                    shar_1.vx = 0
                    shar_1.vy = 0
                else:
                    game_start = time.time()
                    shar_1.vx = game_speed_x0 * game_speed
                    shar_1.vy = game_speed_y0 * game_speed
            if event.key == pygame.K_UP:
                pygame.mixer.music.unpause()
                pygame.mixer.music.set_volume(10)
            if event.key == pygame.K_DOWN:
                pygame.mixer.music.unpause()
                pygame.mixer.music.set_volume(0.3)
            if event.key == pygame.K_g:
                god_mode = not god_mode
            if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                game_speed = 1
                shar_1.vx = game_speed_x0 * game_speed
                shar_1.vy = game_speed_y0 * game_speed
            if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                game_speed = 2
                shar_1.vx = game_speed_x0 * game_speed
                shar_1.vy = game_speed_y0 * game_speed
            if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                game_speed = 3
                shar_1.vx = game_speed_x0 * game_speed
                shar_1.vy = game_speed_y0 * game_speed
            if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                game_speed = 4
                shar_1.vx = game_speed_x0 * game_speed
                shar_1.vy = game_speed_y0 * game_speed
            if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                game_speed = 5
                shar_1.vx = game_speed_x0 * game_speed
                shar_1.vy = game_speed_y0 * game_speed
    screen.blit(background_image, (0, 0))
    f1 = pygame.font.Font(None, 30)
    text1 = f1.render('{}'.format('время игры: ' + str(int(game_time / 60))
                                  + ':' + str(int(game_time % 60))), 1, (255, 100, 0))
    text2 = f1.render('{}'.format('Счёт: ' + str(shar_1.razbit_kirp * 50)), 1, (255, 100, 0))
    text3 = f1.render('{}'.format(str(game_live) + 'x'), 1, (255, 100, 0))
    screen.blit(text1, (0, 500))
    screen.blit(text2, (0, 540))
    screen.blit(text3, (790, 570))
    if god_mode:
        text4 = f1.render('God-mode', 1, (255, 100, 0))
        screen.blit(text4, (0, 580))
    if game_live <= 2 and game_time <= 3:
        game_live += 1
    if game_level == 1:
        if shar_1.razbit_kirp == 16:
            game_level += 1
            next_level = True
    if game_level == 2:
        if shar_1.razbit_kirp == 64:
            game_level += 1
            next_level = True
    if game_level == 3:
        if shar_1.razbit_kirp == 160:
            game_level += 1
            next_level = True
    if game_level == 4:
        Vin = True
    if next_live or next_level:
        kx = 2
        ky = 2
        if game_level == 1:
            if next_level:
                for k in kirpichs:
                    k.kill()
                for i in range(16):
                    Kirpichi()
                    kx += 105
                    if kx > 800:
                        kx = 2
                        ky += 45
                next_level = False
                game_live = 3
                game_speed = 1
            shar_1.reset()
            platform_1.rect.y = 550
            platform_1.rect.x = (width - platform_1.rect.width) // 2
            next_live = False
        elif game_level == 2:
            if next_level:
                for k in kirpichs:
                    k.kill()
                for i in range(24):
                    Kirpichi()
                    kx += 105
                    if kx > 800:
                        kx = 2
                        ky += 45
                next_level = False
                game_live += 1
                game_speed = 2
            shar_1.reset()
            platform_1.rect.y = 525
            platform_1.rect.x = (width - platform_1.rect.width) // 2
            next_live = False
        elif game_level == 3:
            if next_level:
                for k in kirpichs:
                    k.kill()
                for i in range(32):
                    Kirpichi()
                    kx += 105
                    if kx > 800:
                        kx = 2
                        ky += 45
                next_level = False
                game_live += 1
                game_speed = 3
            shar_1.reset()
            platform_1.rect.y = 500
            platform_1.rect.x = (width - platform_1.rect.width) // 2
            next_live = False

    all_sprites.update(clock_dt)
    all_sprites.draw(screen)
    if Vin:
        screen.blit(vin_image, (0, 0))
        f1 = pygame.font.Font(None, 30)
        text1 = f1.render('{}'.format('время игры: ' + str(int(game_time / 60))
                                      + ':' + str(int(game_time % 60))), 1, (0, 180, 0))
        text2 = f1.render('{}'.format('Счёт: ' + str(shar_1.razbit_kirp * 50)), 1, (0, 180, 0))
        screen.blit(text1, (500, 340))
        screen.blit(text2, (500, 380))
    if lose:
        screen.blit(lose_image, (0, 0))
        f1 = pygame.font.Font(None, 30)
        text1 = f1.render('{}'.format('время игры: ' + str(int(game_time / 60))
                                      + ':' + str(int(game_time % 60))), 1, (180, 0, 0))
        text2 = f1.render('{}'.format('Счёт: ' + str(shar_1.razbit_kirp * 50)), 1, (180, 0, 0))
        screen.blit(text1, (340, 400))
        screen.blit(text2, (340, 440))
    pygame.display.flip()
    clock_dt = clock.tick(fps)
    if not game_pausa and not lose and not Vin:
        tt = time.time()
        game_time += tt - game_start
        game_start = tt
        screen.blit(lose_image, (0, 0))
pygame.quit()
