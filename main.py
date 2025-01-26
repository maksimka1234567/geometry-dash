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
    # вернем игрока, а также размер поля в клетках
    return x, y


game_over = False
flag1 = False


def start_screen():
    global flag
    global flag1
    global game_over
    player = None
    fon = pygame.transform.scale(load_image('maxresdefault.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and not flag:
                Backgrounds()
                player = Ufo(200, HEIGHT - 95)
                flag = True
                generate_level(load_level('level1.txt'))
                # начинаем игру
            if event.type == pygame.KEYDOWN and flag:
                if event.key == pygame.K_UP:
                    player.jump()
                    flag1 = False
        if not game_over and flag:
            all_sprites.update()
            if player is not None and pygame.sprite.spritecollideany(player, cube_portals,
                                                                     collided=pygame.sprite.collide_mask):
                player = Cube(200, player.rect.y)
                to_remove = list(players)[0]
                players.remove(to_remove)
                all_sprites.remove(to_remove)
                player.vy = 1

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
        all_sprites.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


running = True
while running:
    start_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
pygame.quit()
