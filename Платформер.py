import pygame
import time
from pygame import mixer
import pickle
import sqlite3
from os import path

all_time = []
record_time = set()
time_to_count = True
database = True

con = sqlite3.connect('record.db')
cur = con.cursor()

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
mixer.init()

cursor_img = pygame.image.load("ass.png")

pygame.mouse.set_visible(False)
cursor_img_rect = cursor_img.get_rect()

clock = pygame.time.Clock()
fps = 45

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Dungeon Master')

tile_size = 40  # основные игровые переменные
game_over = 0
main_menu = 1
level = 10
max_levels = 10
score = 0
result = True

font_score = pygame.font.SysFont('Bauhaus', 30)
font = pygame.font.SysFont('Bauhaus', 70)
instruction_text = pygame.font.SysFont('Arial', 30)
blue = (100, 100, 255)
white = (255, 255, 255)
game_over_text = pygame.font.SysFont('Bauhaus', 50)

icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)
Background = pygame.image.load('dungeon1.png')  # загрузка картинок
restart = pygame.image.load('restart.jpg')
start = pygame.image.load('start.jpg')
exit = pygame.image.load('exit.jpg')
ach = pygame.image.load('achievements.png')
instruction = pygame.image.load('instructions.jpg')
edit = pygame.image.load('edit.jpg')
back = pygame.image.load('back.jpg')
records = pygame.image.load('records.png')
min_back = pygame.image.load('min_back.jpg')
delete = pygame.image.load('delete.png')

kaneki = False  # далее ачивки
lava_is_death = False
beginning = False
time_is_illusion = False
rich = False

count_death = 0
count_lava_death = 0

pygame.mixer.music.load('music_game.mp3')  # загрузка МуЗыКи
coin_fx = pygame.mixer.Sound('coin.mp3')
coin_fx.set_volume(0.05)
jump_fx = pygame.mixer.Sound('jump1.mp3')
jump_fx.set_volume(0.05)
game_over_fx = pygame.mixer.Sound('game_over.mp3')
game_over_fx.set_volume(0.05)
portal_fx = pygame.mixer.Sound('teleport.mp3')
portal_fx.set_volume(0.05)
win_fx = pygame.mixer.Sound('win.mp3')
win_fx.set_volume(0.05)


def load_image(name, colorkey=None):
    image = pygame.image.load(name)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def write_text(text, font, text_color, x, y):  # функция для создания текстовых "вставок"
    image_of_text = font.render(text, True, text_color)
    screen.blit(image_of_text, (x, y))


def reset_level(level):  # функция для перезапуска уровня
    player.reset(80, screen_height - 104)
    ghost_group.empty()
    platform_group.empty()
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()
    pumpkin_group.empty()
    checkpoint_group.empty()

    if path.exists(f'level{level}_data.txt'):  # отрисовка
        pickle_in = open(f'level{level}_data.txt', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    return world


class Button(object):
    def __init__(self, x_button, y_button, img):
        self.image = pygame.transform.scale(img, (tile_size * 5, tile_size * 3))
        self.rect = self.image.get_rect()
        self.rect.x = x_button
        self.rect.y = y_button
        self.clicked = False

    def draw(self):
        action = False
        mouse_position = pygame.mouse.get_pos()  # отслеживание движение мышки
        if self.rect.collidepoint(mouse_position):  # проверка на клик
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)  # отрисовка кнопки
        return action


class Button_1(object):
    def __init__(self, x_button, y_button, img):
        self.image = pygame.transform.scale(img, (tile_size * 3, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x_button
        self.rect.y = y_button
        self.clicked = False

    def draw(self):
        action = False
        mouse_position = pygame.mouse.get_pos()  # отслеживание движение мышки
        if self.rect.collidepoint(mouse_position):  # проверка на клик
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)  # отрисовка кнопки
        return action


class Player(object):
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        delta_x = 0
        delta_y = 0
        walk_recharge = 5
        collision = 20

        if game_over == 0:  # нажатие кнопок
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                jump_fx.play()
                self.shift_y = -15
                self.jumped = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_LEFT]:
                delta_x -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                delta_x += 5
                self.counter += 1
                self.direction = 1
            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image_player = self.images_right[self.index]
                if self.direction == -1:
                    self.image_player = self.images_left[self.index]

            if self.counter > walk_recharge:  # анимация движения
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image_player = self.images_right[self.index]
                if self.direction == -1:
                    self.image_player = self.images_left[self.index]

            self.shift_y += 1  # что-то типо гравитации
            if self.shift_y > 10:
                self.shift_y = 10
            delta_y += self.shift_y

            self.in_air = True  # проверка на столкновения
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.width,
                                       self.height):  # проверка на столкновения по горизонтали
                    delta_x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.width,
                                       self.height):  # проверка на столкновения по вертикали
                    if self.shift_y < 0:  # прыжооооок
                        delta_y = tile[1].bottom - self.rect.top
                        self.shift_y = 0  # падеееение
                    elif self.shift_y >= 0:
                        delta_y = tile[1].top - self.rect.bottom
                        self.shift_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, ghost_group, False):  # проверка на столкновение с противниками (призраки)
                game_over = -1
                game_over_fx.play()

            if pygame.sprite.spritecollide(self, lava_group, False):  # проверка на столкновение с лавой
                game_over = 5
                game_over_fx.play()

            if pygame.sprite.spritecollide(self, exit_group, False):  # проверка на столкновение с выходом
                game_over = 1
                if level < 10:
                    portal_fx.play()
                    pass

            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + delta_x, self.rect.y, self.width,
                                             self.height):
                    delta_x = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + delta_y, self.width,
                                             self.height):
                    # if abs((self.rect.top + delta_y) - platform.rect.bottom) < collision:  # проверка столкновения ПОД платформой
                    #     self.shift_y = 0
                    #     delta_y = platform.rect.bottom - self.rect.top
                    if abs((self.rect.bottom + delta_y) - platform.rect.top) < collision:  # проверка столкновения НАД платформой
                        self.rect.bottom = platform.rect.top - 1  # считерил :3
                        self.in_air = False
                        delta_y = 0
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            self.rect.x += delta_x  # обновление координат игрока
            self.rect.y += delta_y

        elif game_over == -1:  # полёт мёртвого игрока
            self.image_player = self.dead_image
            if self.rect.y > -100:
                self.rect.y -= 5

        screen.blit(self.image_player, self.rect)
        # pygame.draw.rect(screen, 'white', self.rect, 2) - отрисовка хитбокса персонажа
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for number in range(1, 9):
            img_right = pygame.image.load(f'R{number}.png')
            img_right = pygame.transform.scale(img_right, (35, 64))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('dead.png')
        self.image_player = self.images_right[self.index]
        self.rect = self.image_player.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image_player.get_width()
        self.height = self.image_player.get_height()
        self.shift_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World(object):
    def __init__(self, data):
        self.tile_list = []

        main_platform = pygame.image.load('stoneTry.png')
        auxiliary_platform = pygame.image.load('stoneTry2.png')
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:  # каменный блок - основание
                    img = pygame.transform.scale(main_platform, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:  # каменный блок - "подкаркас"
                    img = pygame.transform.scale(auxiliary_platform, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:  # противники - призраки
                    ghost = Enemy(col_count * tile_size, row_count * tile_size - 15)
                    ghost_group.add(ghost)
                if tile == 4:  # горизонтальная платформа
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:  # вертикальная платформа
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:  # лава
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 50))
                    lava_group.add(lava)
                if tile == 7:  # монетки
                    coins = Coin(col_count * tile_size + (tile_size // 2),
                                 row_count * tile_size + (tile_size // 2))
                    coin_group.add(coins)
                if tile == 8:  # выход
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 9:  # тыковка
                    pumpkin = Pumpkin(col_count * tile_size, row_count * tile_size + (tile_size // 6))
                    pumpkin_group.add(pumpkin)
                if tile == 10:  # стрелочка - сейвилка
                    checkpoint = Checkpoint(col_count * tile_size, row_count * tile_size)
                    checkpoint_group.add(checkpoint)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2) - отрисовка игровой сетки


class Enemy(pygame.sprite.Sprite):  # класс врагов
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('ghost1.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size + 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):  # движение призраков
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 80:
            self.move_direction *= -1
            self.move_counter *= -1


class Platform(pygame.sprite.Sprite):  # класс платформ
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('stoneHalf.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):  # проверка движения платформы (вертикаль \ горизонталь)
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 80:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):  # класс Лавы
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Lava_Animation.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):  # класс Монеток
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('coin.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):  # класс Выхода
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('portal.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Pumpkin(pygame.sprite.Sprite):  # класс Лавы
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('нравится).png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Checkpoint(pygame.sprite.Sprite):  # класс чекпоинта
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('signRight.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(80, screen_height - 104)

main_block = pygame.sprite.Group()

ghost_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
pumpkin_group = pygame.sprite.Group()
alone_coin = pygame.sprite.Group()
checkpoint_group = pygame.sprite.Group()

score_coin = Coin(15, 15)
alone_coin.add(score_coin)

if path.exists(f'level{level}_data.txt'):  # проверка на номер карты и её доступность (существование)
    pickle_in = open(f'level{level}_data.txt', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

instruction_button = Button(screen_width // 2 - 300, screen_height // 3 + 240, instruction)  # создание кнопок
restart_button = Button(screen_width // 2 - 100, screen_height // 2 + 100, restart)
start_button = Button(screen_width // 2 - 300, screen_height // 2 - 50, start)
exit_button = Button(screen_width // 2 + 100, screen_height // 3 + 240, exit)
edit_button = Button(screen_width // 2 - 300, screen_height // 4, edit)
record_button = Button(screen_width // 2 + 100, screen_height // 4, records)
back_button = Button(screen_width // 2 + 100, screen_height - 150, back)
ach_button = Button(screen_width // 2 + 100, screen_height // 2 - 50, ach)
back_button_game = Button_1(330, 0, min_back)
delete_button = Button(screen_width // 7, screen_height - 150, delete)

all_sprites = pygame.sprite.Group()

cursor = pygame.sprite.Sprite(all_sprites)
cursor.image = load_image('ass.png')
cursor.rect = cursor.image.get_rect()
pygame.mouse.set_visible(False)
Running = True
while Running:
    clock.tick(fps)
    screen.blit(Background, (0, 0))
    if main_menu == 1:  # стартовое меню
        write_text('Ω-DUNGEON MASTER-Ω', font, 'white', 115, 50)
        write_text('[{8--вышла лютая хрень--8}]', font, (64, 224, 208), 75, 740)
        if exit_button.draw():
            Running = False
        if start_button.draw():
            main_menu = -1
            pygame.mixer.music.play(-1, 0.0, 5000)
            pygame.mixer.music.set_volume(0.1)
        if instruction_button.draw():
            main_menu = 2
        if edit_button.draw():
            main_menu = 0
        if record_button.draw():
            main_menu = 3
        if ach_button.draw():
            main_menu = 7
    elif main_menu == 0:  # edit
        pygame.init()
        tile_size = 40
        columns = 20
        screen = pygame.display.set_mode((screen_width, screen_height))
        Background = pygame.image.load('dungeon1.png')
        Stone_center = pygame.image.load('stoneTry.png')
        Stone_grass = pygame.image.load('stoneTry2.png')
        ghost = pygame.image.load('ghost1.png')
        platform_x_img = pygame.image.load('stoneHalf.png')
        platform_y_img = pygame.image.load('stoneHalf1.png')
        lava_img = pygame.image.load('Lava_Animation.png')
        coin_img = pygame.image.load('coin.png')
        exit_img = pygame.image.load('portal.png')
        save_img = pygame.image.load('save.jpg')
        load_img = pygame.image.load('load.jpg')
        pumpkin_img = pygame.image.load('нравится).png')
        checkpoint_img = pygame.image.load('signRight.png')
        back_img = pygame.image.load('exit.jpg')

        clicked = False
        level = 0
        white = (255, 255, 255)  # основные цвета
        green = (144, 201, 120)
        font = pygame.font.SysFont('comicsans', 24)
        world_data = []
        for row in range(20):
            list_of_tiles = [0] * 20
            world_data.append(list_of_tiles)

        for tile in range(0, 20):
            world_data[19][tile] = 2
            world_data[0][tile] = 1
            world_data[tile][0] = 1
            world_data[tile][19] = 1


        def draw_text(text, font, text_col, x, y):
            img = font.render(text, True, text_col)
            screen.blit(img, (x, y))


        def draw_grid():  # бортики
            for c in range(21):
                pygame.draw.line(screen, white, (c * tile_size, 0),
                                 (c * tile_size, 800))  # вертикальные полосочки
                pygame.draw.line(screen, white, (0, c * tile_size),
                                 (screen_width, c * tile_size))  # горизонтальные полосочки


        def draw_world():
            for row in range(20):
                for col in range(20):
                    if world_data[row][col] > 0:
                        if world_data[row][col] == 1:  # каменные блоки
                            img = pygame.transform.scale(Stone_center, (tile_size, tile_size))
                            screen.blit(img, (col * tile_size, row * tile_size))
                        if world_data[row][col] == 2:  # каменные блоки с травкой
                            img = pygame.transform.scale(Stone_grass, (tile_size, tile_size))
                            screen.blit(img, (col * tile_size, row * tile_size))
                        if world_data[row][col] == 3:  # призраки
                            img = pygame.transform.scale(ghost, (tile_size, int(tile_size * 1.5)))
                            screen.blit(img, (col * tile_size, row * tile_size - 20))
                        if world_data[row][col] == 4:  # горизонтальные платформы
                            img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
                            screen.blit(img, (col * tile_size, row * tile_size))
                        if world_data[row][col] == 5:  # вертикальные платформы
                            img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
                            screen.blit(img, (col * tile_size, row * tile_size))
                        if world_data[row][col] == 6:  # лава
                            img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
                            screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
                        if world_data[row][col] == 7:  # монеточка
                            img = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
                            screen.blit(img,
                                        (col * tile_size + (tile_size // 4),
                                         row * tile_size + (tile_size // 4)))
                        if world_data[row][col] == 8:  # выход
                            img = pygame.transform.scale(exit_img, (tile_size, int(tile_size * 1.5)))
                            screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))
                        if world_data[row][col] == 9:  # тыковка :3
                            img = pygame.transform.scale(pumpkin_img, (tile_size, tile_size))
                            screen.blit(img, (col * tile_size, row * tile_size))
                        if world_data[row][col] == 10:  # стрелка-сейвилка
                            img = pygame.transform.scale(checkpoint_img, (tile_size, tile_size))
                            screen.blit(img, (col * tile_size, row * tile_size))


        class Button(object):
            def __init__(self, x, y, img):
                self.image = pygame.transform.scale(img, (tile_size * 3, tile_size))
                self.rect = self.image.get_rect()
                self.rect.topleft = (x, y)
                self.clicked = False

            def draw(self):
                action = False
                pos = pygame.mouse.get_pos()  # позиция мышки
                if self.rect.collidepoint(pos):  # проверка положения мышки
                    if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                        action = True
                        self.clicked = True

                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False
                screen.blit(self.image, (self.rect.x, self.rect.y))  # сама кнопочка
                return action


        save_button = Button(tile_size * 3, screen_height - 80, save_img)  # кнопка сохранения
        load_button = Button(tile_size * 8.5, screen_height - 80, load_img)  # кнопка загрузки
        back_button = Button(tile_size * 14, screen_height - 80, back_img)  # кнопка возвращения

        Running = True
        while Running:
            clock.tick(fps)
            screen.fill(green)
            screen.blit(Background, (0, 0))  # отрисовка фона
            if save_button.draw():  # кнопка сохранения -> пока что START
                pickle_out = open(f'level{level}_data.txt', 'wb')
                pickle.dump(world_data, pickle_out)
                pickle_out.close()
            if load_button.draw():  # кнопка загрузки -> пока что EXIT
                if path.exists(f'level{level}_data.txt'):
                    pickle_in = open(f'level{level}_data.txt', 'rb')
                    world_data = pickle.load(pickle_in)
            if back_button.draw():
                pygame.quit()
                main_menu = 1
            draw_grid()  # сетка
            draw_world()  # уровень

            draw_text(f'Уровень: {level}', font, white, tile_size, screen_height - 40)  # текст
            draw_text('Нажимайте ВВЕРХ и ВНИЗ для переключения уровня', font, white, tile_size,
                      screen_height - 20)
            if pygame.mouse.get_focused():
                all_sprites.draw(screen)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    cursor.rect.x = x
                    cursor.rect.y = y
                if event.type == pygame.QUIT:
                    Running = False
                if event.type == pygame.MOUSEBUTTONDOWN and not clicked:
                    clicked = True
                    pos = pygame.mouse.get_pos()
                    x = pos[0] // tile_size
                    y = pos[1] // tile_size
                    if x < 20 and y < 20:  # проверка координат мышки
                        if pygame.mouse.get_pressed()[0] == 1:
                            world_data[y][x] += 1
                            if world_data[y][x] > 10:
                                world_data[y][x] = 0
                        elif pygame.mouse.get_pressed()[2] == 1:
                            world_data[y][x] -= 1
                            if world_data[y][x] < 0:
                                world_data[y][x] = 10
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked = False
                    if event.button == 3:
                        world_data[y][x] = 0
                if event.type == pygame.KEYDOWN:  # вверх и вниз для смены уровня!!!
                    if event.key == pygame.K_UP and level < 10:
                        level += 1
                    elif event.key == pygame.K_DOWN and level >= 1:
                        level -= 1

            pygame.display.update()  # обновить окошко

    elif main_menu == 2:  # инструкция
        write_text('ИгРоВоЕ пОсОбИе', instruction_text, 'green', screen_width // 3, 50)
        write_text('1) Управление движения влево и вправо по стрелОЧКАМ (<- и ->) ', instruction_text,
                   'green', 10, 100)
        write_text('2) Прыжок на пробел', instruction_text, 'green', 10, 150)
        write_text('3) Задача игрока - дойти до портала в каждом из уровней', instruction_text, 'green',
                   10, 200)
        write_text('4) Избегайте лавы и призраков подземелья!', instruction_text, 'green', 10, 250)
        write_text('5) Желаю вам удачи и приятной игры :3', instruction_text, 'green', 10, 300)
        write_text('6) Выражаю огромную благодарность этим людям: Шайдт Никита, ', instruction_text,
                   'green', 10, 350)
        write_text('Соколов Вячеслав, Рачеев Илья, Терский Елисей и Лукша Никита.', instruction_text,
                   'green', 10, 400)
        write_text('7) ДА, Я ЧЁРТ ВОЗЬМИ ПРОСТО УДЛИНЯЮ КОД!', instruction_text, 'green', 10, 450)
        if back_button.draw():
            main_menu = 1

    elif main_menu == 3:  # рекорды
        text_record_time = cur.execute("""SELECT Time FROM record_time_coin""").fetchall()
        text_record_coin = cur.execute("""SELECT Coin FROM record_time_coin""").fetchall()
        time_count = len(text_record_time)
        coin_count = len(text_record_coin)
        all_time_coins = (len(text_record_coin) + len(text_record_time))
        write_text('Результата прохождения игры:', instruction_text, 'green', 200, 50)
        if all_time_coins == 0:
            write_text('Пока что нет никаких результатов', instruction_text, 'green', 190, 100)
        else:
            for number in range(time_count):
                write_text(
                    str(number + 1) + ') Пройдено за ' + str(text_record_time[number][0]) + ' секунд,',
                    instruction_text, 'green', 90, 100 + number * 30)
            for num in range(coin_count):
                write_text('cобрано ' + str(text_record_coin[num][0]) + ' монет', instruction_text,
                           'green', 430, 100 + num * 30)
        if back_button.draw():
            main_menu = 1
        if delete_button.draw():
            delete_all = cur.execute("""DELETE FROM record_time_coin""").fetchall()
            kaneki = False
            rich = False
            beginning = False
            lava_is_death = False
    elif main_menu == 7:
        write_text('Ваши никчёмные достижения :3', instruction_text, 'green', screen_width // 4 + 20, 50)
        if kaneki:
            write_text('Ты мертв. Поздравляю. - умереть 10 раз', instruction_text, 'green', screen_width // 40,
                       screen_height // 5)
        else:
            write_text('Достижение заблокировано - умереть 10 раз', instruction_text, 'green',
                       50, screen_height // 5)
        if rich:
            write_text('Богатый капиталист - собрать 20 монеток', instruction_text, 'green',
                       screen_width // 40 + 30, screen_height // 4)
        else:
            write_text('Достижение заблокировано - собрать 20 монеток', instruction_text, 'green',
                       screen_width // 40 + 30, screen_height // 4)
        if beginning:
            write_text('А стоило ли начинать? - начать игру :/', instruction_text, 'green',
                       screen_width // 40 + 30, screen_height // 3 - 30)
        else:
            write_text('Достижение заблокировано - начать игру :/', instruction_text, 'green',
                       screen_width // 40 + 30, screen_height // 3 - 30)
        if lava_is_death:
            write_text('Любитель джакузи - сгореть в лаве 10 раз', instruction_text, 'green',
                       screen_width // 40 + 30, screen_height // 2)
        else:
            write_text('Достижение заблокировано - сгореть в лаве 10 раз', instruction_text, 'green',
                       screen_width // 40 + 30, screen_height // 3 + 5)
        if time_is_illusion:
            write_text('Разве время что-то значит? - пройти игру', instruction_text, 'green',
                       screen_width // 40 + 30, screen_height // 3 + 40)
        else:
            write_text('Достижение заблокировано - пройти игру', instruction_text, 'green',
                       screen_width // 40 + 30, screen_height // 3 + 40)

        if back_button.draw():
            main_menu = 1

    elif main_menu == -1:
        world.draw()
        if time_to_count:
            begin_time = time.time()
            all_time.append(begin_time)
        if back_button_game.draw():
            main_menu = 1
        if game_over == 0:  # игрок жив
            ghost_group.update()
            platform_group.update()
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            write_text('    Тугриков X ' + str(score) + ' монет', font_score, 'green', 8, 8)
            write_text('Время: ' + str(round(all_time[-1] - all_time[0], 1)) + ' секунд', font_score,
                       'green', 500, 8)

        ghost_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)
        pumpkin_group.draw(screen)
        alone_coin.draw(screen)
        checkpoint_group.draw(screen)
        game_over = player.update(game_over)
        if game_over == -1:  # игрок погиб
            write_text('    Тугриков X ' + str(score) + ' монет', font_score, 'green', 8, 8)
            write_text('Время: ' + str(round(all_time[-1] - all_time[0], 1)) + ' секунд', font_score,
                       'green', 500, 8)
            write_text('ИГРА ОКОНЧЕНА.', game_over_text, blue, screen_width // 2 - 130,
                       screen_height // 2)
            count_death += 1
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        if game_over == 5:
            count_lava_death += 1
            game_over = -1

        if game_over == 1:  # игрок завершил игру (уровень)
            level += 1  # переход на след. уровень
            beginning = True
            if level <= max_levels:
                world_data = []  # перезапуск уровня
                world = reset_level(level)
                game_over = 0
            else:
                time_to_count = False
                write_text('    Тугриков X ' + str(score) + ' монет', font_score, 'green', 8, 8)
                write_text('Время: ' + str(round(all_time[-1] - all_time[0], 1)) + ' секунд', font_score,
                           'green', 500, 8)
                write_text('   ВЫ ВЫИГРАЛИ!', font, white, (screen_width // 2) - 200, screen_height // 2)
                if count_death > 10:
                    kaneki = True
                if count_lava_death > 10:
                    lava_is_death = True
                if score >= 20:
                    rich = True
                if kaneki:
                    write_text('Разблокировано достижение: В первый раз?', font_score, 'green',
                               (screen_width // 2) - 200, (screen_height // 5))
                if rich:
                    write_text('Разблокировано достижение: Да я богатый чертила', font_score, 'green',
                               (screen_width // 2) - 200, (screen_height // 5) + 50)
                if beginning:
                    write_text('Разблокировано достижение: Начало начал', font_score, 'green',
                               (screen_width // 2) - 200, (screen_height // 5) + 100)
                if lava_is_death:
                    write_text('Разблокировано достижение: Горячий парень', font_score, 'green',
                               (screen_width // 2) - 200, (screen_height // 5) + 150)
                if time_is_illusion:
                    write_text('Разблокировано достижение: Господин время', font_score, 'green',
                               (screen_width // 2) - 200, (screen_height // 5) + 200)
                count_death = 0
                win_fx.play()

                time_record_game = all_time[-1] - all_time[0]
                if time_record_game < 100:
                    time_is_illusion = True
                record_time.add(time_record_game)
                if database:
                    time_order = "INSERT INTO record_time_coin(Time, Coin)" "VALUES('{}', '{}')".format(
                        round(time_record_game, 1), score)
                    cur.execute(time_order).fetchall()
                    con.commit()
                    database = False
                if restart_button.draw():
                    level = 0  # перезапуск уровня
                    world_data = []
                    all_time = []
                    time_to_count = True
                    world = reset_level(level)
                    game_over = 0
                    score = 0
                    database = True
    for event in pygame.event.get():
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            cursor.rect.x = x
            cursor.rect.y = y
        if event.type == pygame.QUIT:
            Running = False
    if pygame.mouse.get_focused():
        all_sprites.draw(screen)
    pygame.display.update()

con.commit()
pygame.quit()