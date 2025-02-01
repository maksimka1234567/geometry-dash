import pygame
import os
import sys

# Инициализация Pygame
pygame.init()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))  # Берем цвет из верхнего левого пикселя
        image = image.convert()  # Важно! Вызывать convert() ПЕРЕД set_colorkey()
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


FPS = 120
clock = pygame.time.Clock()
spikes = pygame.sprite.Group()
cube_portals = pygame.sprite.Group()
ufo_portals = pygame.sprite.Group()
ball_portals = pygame.sprite.Group()
platforms = pygame.sprite.Group()
trampolines = pygame.sprite.Group()
spheres = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash")
screen.fill("black")
is_jumping = False
jump_start = False


class Cube(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(players, all_sprites)
        self.image = pygame.transform.scale(load_image('Cube352.jpg'), (50, 50))
        self.rect = self.image.get_rect()
        self.vy = 0
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.is_jumping = False
        self.gravity = 0.5
        self.angle = 0
        self.original_image = self.image
        self.mask = pygame.mask.from_surface(self.image)  # Маска для кубика

    def update(self):
        global game_over
        global flag1
        # Вертикальное движение (прыжок и гравитация)
        if self.is_jumping or self.vy != 0:
            self.vy += self.gravity
            self.rect.y += self.vy
            # Вращение
            self.angle = (self.angle + 5) % 360
            self.image = pygame.transform.rotate(self.original_image, 180 - self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            # Проверка приземления в случае наличия платформ
            landing_platform = self.check_landing()
            if landing_platform:
                self.rect.bottom = landing_platform.rect.top + 5
                flag1 = True
                self.vy = 0
                self.is_jumping = False
                # Коррекция угла для приземления на сторону
                closest_angle = round(self.angle / 90) * 90
                self.angle = closest_angle
                self.image = pygame.transform.rotate(self.original_image, self.angle)
                self.rect = self.image.get_rect(center=self.rect.center)
            elif self.rect.y >= HEIGHT - 50:
                self.rect.y = HEIGHT - 50
                self.vy = 0
                self.is_jumping = False
                # Коррекция угла для приземления на сторону
                closest_angle = round(self.angle / 90) * 90
                self.angle = closest_angle
                self.image = pygame.transform.rotate(self.original_image, self.angle)
                self.rect = self.image.get_rect(center=self.rect.center)
                self.rect.y = HEIGHT - 50

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            if pygame.sprite.spritecollideany(self, trampolines, collided=pygame.sprite.collide_mask):
                self.vy = -15
            else:
                self.vy = -10

    def check_landing(self):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vy >= 0:  # Если падает вниз и касается платформы
                    return platform  # Возвращаем платформу
        return None  # Если приземляться некуда


class Ufo(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(players, all_sprites)
        self.image = pygame.transform.scale(load_image('UFO057.png'), (50, 50))
        self.rect = self.image.get_rect()
        self.vy = 0
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.is_jumping = False
        self.mask = pygame.mask.from_surface(self.image)  # Маска для кубика
        self.original_image = self.image

    def update(self):
        global game_over
        global flag1
        # Вертикальное движение (прыжок и гравитация)
        if self.is_jumping or self.vy != 0:
            self.vy += 0.3
            self.rect.y += self.vy
            # Проверка приземления в случае наличия платформ
            landing_platform = self.check_landing()
            if landing_platform:
                self.rect.bottom = landing_platform.rect.top + 5
                flag1 = True
                self.vy = 0
                self.is_jumping = False
            elif self.rect.y >= HEIGHT - 50:
                self.rect.y = HEIGHT - 50
                self.vy = 0
                self.is_jumping = False
            elif self.rect.y <= 0:
                self.rect.y = 0
                self.vy = 0.2

    def jump(self):
        # if not self.is_jumping:
        self.is_jumping = True
        if pygame.sprite.spritecollideany(self, trampolines, collided=pygame.sprite.collide_mask):
            self.vy = -10
        else:
            self.vy = -7

    def check_landing(self):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vy >= 0:  # Если падает вниз и касается платформы
                    return platform  # Возвращаем платформу
        return None  # Если приземляться некуда


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(players, all_sprites)
        self.image = pygame.transform.scale(load_image('Ball33.jpg'), (50, 50))
        self.rect = self.image.get_rect()
        self.vy = 0
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.is_jumping = False
        self.mask = pygame.mask.from_surface(self.image)  # Маска для шарика
        self.original_image = self.image
        self.angle = 0

    def update(self):
        global game_over
        global flag1
        global down
        # Вращение
        self.angle = (self.angle + 3) % 360
        self.image = pygame.transform.rotate(self.original_image, 180 - self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += self.vy
        if self.is_jumping or self.vy != 0:
            flag1 = False
            if self.is_jumping:
                if down:
                    self.vy = -5
                else:
                    self.vy = 5
            # Проверка приземления в случае наличия платформ
            landing_platform = self.check_landing()
            if landing_platform and self.vy != 0:
                if not down:
                    self.rect.y = landing_platform.rect.y - 50
                    flag1 = True
                    down = True
                else:
                    self.rect.y = landing_platform.rect.y + 40
                    flag1 = True
                    down = False
                self.vy = 0
                self.is_jumping = False
            if self.rect.y <= -15:
                down = False
                flag1 = False
                self.is_jumping = False
                self.vy = 0
                self.rect.y = -5
            elif self.rect.y >= HEIGHT - 40:
                flag1 = False
                self.is_jumping = False
                self.vy = 0
                self.rect.y = HEIGHT - 50
                down = True

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True

    def check_landing(self):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vy >= 0 and self.rect.y < platform.rect.y and not down and not flag1:  # Если падает вниз и касается платформы


                    return platform  # Возвращаем платформу
                elif self.vy <= 0 and self.rect.y > platform.rect.y and down and not flag1:  # Если падает вниз и касается платформы

                    return platform  # Возвращаем платформу
        return None  # Если приземляться некуда


class Backgrounds(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('backgrounds1.png'), (WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0


class Trampoline(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(trampolines, all_sprites)
        self.image = pygame.transform.scale(load_image('YellowPad.png'), (50, 20))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y + 30)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


class Sphere(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(spheres, all_sprites)
        self.image = pygame.transform.scale(load_image('YellowSphere.png'), (50, 50))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


flag = False
down = True


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Spike(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(spikes, all_sprites)
        self.image = pygame.transform.scale(load_image('RegularSpike03.png'), (50, 50))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


class CubePortal(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(cube_portals, all_sprites)
        self.image = pygame.transform.scale(load_image('CubePortalLabelled.png'), (75, 150))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y - 100)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


class UfoPortal(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(ufo_portals, all_sprites)
        self.image = pygame.transform.scale(load_image('UFOPortalLabelled.png'), (75, 150))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y - 100)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx

class BallPortal(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(ball_portals, all_sprites)
        self.image = pygame.transform.scale(load_image('BallPortalLabelled.png'), (75, 150))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y - 100)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


class Platform(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(platforms, all_sprites)
        self.image = pygame.transform.scale(load_image('RegularBlock01.png'), (50, 50))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '^':
                Spike(x, y)
            elif level[y][x] == '-':
                Platform(x, y)
            elif level[y][x] == '_':
                Trampoline(x, y)
            elif level[y][x] == '*':
                Sphere(x, y)
            elif level[y][x] == '0':
                CubePortal(x, y)
            elif level[y][x] == '1':
                UfoPortal(x, y)
            elif level[y][x] == '2':
                BallPortal(x, y)
    # вернем игрока, а также размер поля в клетках
    return x, y


game_over = False
flag1 = False
menu = False


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pressed = False # Флаг, указывающий, нажата ли кнопка

    def draw(self, screen):
        screen.blit(self.image, self.rect)


button1 = Button(15, 15, pygame.transform.scale(load_image("easy.png"), (380, 95)))
button2 = Button(400, 15, pygame.transform.scale(load_image("normal.png"), (380, 95)))

button3 = Button(15, 235, pygame.transform.scale(load_image("hard.png"), (380, 95)))
button4 = Button(400, 235, pygame.transform.scale(load_image("harder.png"), (380, 95)))
button5 = Button(15, 450, pygame.transform.scale(load_image("insane.png"), (380, 95)))
button6 = Button(400, 450, pygame.transform.scale(load_image("demon.png"), (380, 95)))


def start_screen():
    global flag
    global flag1
    global game_over
    global down
    global menu
    player = None
    fon = pygame.transform.scale(load_image('maxresdefault.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu and not flag:
                    if 15 <= event.pos[0] <= 395 and 15 <= event.pos[1] <= 110:
                        Backgrounds()
                        flag = True
                        player = Ball(200, HEIGHT - 95)
                        generate_level(load_level('level1.txt'))
                        flag1 = True
                    elif 400 <= event.pos[0] <= 780 and 15 <= event.pos[1] <= 110:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 95)
                        generate_level(load_level('level2.txt'))
                        flag1 = True
                    elif 15 <= event.pos[0] <= 395 and 235 <= event.pos[1] <= 330:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 95)
                        generate_level(load_level('level3.txt'))
                        flag1 = True
                    elif 400 <= event.pos[0] <= 780 and 235 <= event.pos[1] <= 330:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 95)
                        generate_level(load_level('level4.txt'))
                        flag1 = True
                    elif 15 <= event.pos[0] <= 395 and 450 <= event.pos[1] <= 545:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 95)
                        generate_level(load_level('level5.txt'))
                        flag1 = True
                    elif 400 <= event.pos[0] <= 780 and 450 <= event.pos[1] <= 545:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 95)
                        generate_level(load_level('level6.txt'))
                        flag1 = True

                elif not menu:
                    menu = True
                # начинаем игру
                if game_over:
                    flag = False
                    game_over = False
                    to_remove = list(players)[0]
                    players.remove(to_remove)
                    all_sprites.remove(to_remove)
                    for sprite in all_sprites:
                        sprite.rect.x = 0
                        sprite.rect.y = 0
            if event.type == pygame.KEYDOWN and flag:
                if event.key == pygame.K_UP:
                    player.jump()
                    flag1 = False
        if menu:
            if menu and not flag:
                screen.fill("blue")
                button1.draw(screen)
                button2.draw(screen)
                button3.draw(screen)
                button4.draw(screen)
                button5.draw(screen)
                button6.draw(screen)
            if not game_over and flag:

                all_sprites.update()
                if player is not None and pygame.sprite.spritecollideany(player, cube_portals,
                                                                         collided=pygame.sprite.collide_mask):
                    player = Cube(200, player.rect.y)
                    to_remove = list(players)[0]
                    players.remove(to_remove)
                    all_sprites.remove(to_remove)
                    player.vy = 1

                if player is not None and pygame.sprite.spritecollideany(player, ufo_portals,
                                                                         collided=pygame.sprite.collide_mask):
                    player = Ufo(200, player.rect.y)
                    to_remove = list(players)[0]
                    players.remove(to_remove)
                    all_sprites.remove(to_remove)
                    player.vy = 1

                if player is not None and pygame.sprite.spritecollideany(player, ball_portals,
                                                                         collided=pygame.sprite.collide_mask):
                    player = Ball(200, player.rect.y)
                    to_remove = list(players)[0]
                    players.remove(to_remove)
                    all_sprites.remove(to_remove)
                    player.vy = 5
                    down = False
                    player.is_jumping = True

                if type(player) is Cube:
                    if pygame.sprite.spritecollideany(player, spikes, collided=pygame.sprite.collide_mask):
                        game_over = True
                        # Столкновение!
                    elif pygame.sprite.spritecollideany(player, platforms, collided=pygame.sprite.collide_mask):
                        flag1 = True
                        platform = \
                            pygame.sprite.spritecollide(player, platforms, False, collided=pygame.sprite.collide_mask)[
                                0]
                        if platform.rect.x - 45 == player.rect.x:
                            game_over = True
                        elif platform.rect.y < player.rect.y:
                            game_over = True

                    elif flag1 and not pygame.sprite.spritecollideany(player, platforms,
                                                                      collided=pygame.sprite.collide_mask):
                        flag1 = False
                        player.vy = 0.2

                    if flag1 and pygame.sprite.spritecollideany(player, trampolines, collided=pygame.sprite.collide_mask):
                        player.jump()
                        flag1 = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and pygame.sprite.spritecollideany(player,
                                                                                                                    spheres,
                                                                                                                    collided=pygame.sprite.collide_mask):
                        player.is_jumping = False
                        player.jump()
                        flag1 = False
                elif type(player) is Ufo:
                    if pygame.sprite.spritecollideany(player, spikes, collided=pygame.sprite.collide_mask):
                        game_over = True
                        # Столкновение!
                    elif pygame.sprite.spritecollideany(player, platforms, collided=pygame.sprite.collide_mask):
                        flag1 = True
                        platform = \
                            pygame.sprite.spritecollide(player, platforms, False, collided=pygame.sprite.collide_mask)[
                                0]
                        if platform.rect.x - 45 == player.rect.x:
                            game_over = True
                        elif platform.rect.y < player.rect.y:
                            player.vy = 0.1
                            player.rect.top = platform.rect.bottom

                    elif flag1 and not pygame.sprite.spritecollideany(player, platforms,
                                                                      collided=pygame.sprite.collide_mask):
                        flag1 = False
                        player.vy = 0.5

                    if flag1 and pygame.sprite.spritecollideany(player, trampolines, collided=pygame.sprite.collide_mask):
                        player.jump()
                        flag1 = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and pygame.sprite.spritecollideany(player,
                                                                                                                    spheres,
                                                                                                                    collided=pygame.sprite.collide_mask):
                        player.is_jumping = False
                        player.jump()
                        flag1 = False
                elif type(player) is Ball:
                    player.update()
                    if not pygame.sprite.spritecollideany(player, platforms) and flag1 and player.vy == 0:
                        if down:
                            player.vy = 5
                        else:
                            player.vy = -5
                        flag1 = False
                    if pygame.sprite.spritecollideany(player, spikes, collided=pygame.sprite.collide_mask):
                        game_over = True
                        # Столкновение!
                    for platform in platforms:
                        if player.rect.colliderect(platform.rect) and abs(player.rect.top - platform.rect.top) < 20 and abs(player.rect.bottom - platform.rect.bottom) < 20:
                            game_over = True

            elif game_over:
                screen.blit(load_image("GAMEOVER.png"), (120, 270))
        pygame.display.flip()
        all_sprites.draw(screen)
        clock.tick(FPS)


running = True
while running:
    start_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            game_over = False
            start_screen()
pygame.quit()


