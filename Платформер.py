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

clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Dungeon Master')

tile_size = 40  # основные игровые переменные
game_over = 0
main_menu = 1
level = 0
max_levels = 10
score = 0
result = True

font_score = pygame.font.SysFont('Bauhaus', 30)
font = pygame.font.SysFont('Bauhaus', 70)
instruction_text = pygame.font.SysFont('Arial', 30)
blue = (100, 100, 255)
white = (255, 255, 255)
game_over_text = pygame.font.SysFont('Bauhaus', 50)

icon = pygame.image.load('icon.png')  # загрузка картинок
pygame.display.set_icon(icon)
Background = pygame.image.load('dungeon1.png')
restart = pygame.image.load('restart.jpg')
start = pygame.image.load('start.jpg')
exit = pygame.image.load('exit.jpg')
instruction = pygame.image.load('instructions.jpg')
edit = pygame.image.load('edit.jpg')
back = pygame.image.load('back.jpg')
records = pygame.image.load('records.png')
min_back = pygame.image.load('min_back.jpg')

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

    if path.exists(f'level{level}_data.txt'):   # отрисовка
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
        self.image = pygame.transform.scale(img, (tile_size * 3, tile_size ))
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
                if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.width, self.height):  # проверка на столкновения по горизонтали
                    delta_x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.width, self.height):  # проверка на столкновения по вертикали
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
                game_over = -1
                game_over_fx.play()

            if pygame.sprite.spritecollide(self, exit_group, False):  # проверка на столкновение с выходом
                game_over = 1
                if level < 10:
                    portal_fx.play()
                    pass

            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + delta_x, self.rect.y, self.width, self.height):
                    delta_x = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + delta_y, self.width, self.height):
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

instruction_button = Button(screen_width // 2 - 300, screen_height // 3 + 240, instruction)   # создание кнопок
restart_button = Button(screen_width // 2 - 100, screen_height // 2 + 100, restart)
start_button = Button(screen_width // 2 - 100, screen_height // 2 - 50, start)
exit_button = Button(screen_width // 2 + 100, screen_height // 3 + 240, exit)
edit_button = Button(screen_width // 2 - 300, screen_height // 4, edit)
record_button = Button(screen_width // 2 + 100, screen_height // 4, records)
back_button = Button(screen_width // 2 - 100, screen_height - 150, back)
back_button_game = Button_1(330, 0, min_back)


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
    elif main_menu == 0:  # edit
        # тут будет редактор уровня
        pass

    elif main_menu == 2:  # инструкция
        write_text('ИгРоВоЕ пОсОбИе', instruction_text, 'green', screen_width // 3, 50)
        write_text('1) Управление движения влево и вправо по стрелОЧКАМ (<- и ->) ', instruction_text, 'green', 10, 100)
        write_text('2) Прыжок на пробел', instruction_text, 'green', 10, 150)
        write_text('3) Задача игрока - дойти до портала в каждом из уровней', instruction_text, 'green', 10, 200)
        write_text('4) Избегайте лавы и призраков подземелья!', instruction_text, 'green', 10, 250)
        write_text('5) Желаю вам удачи и приятной игры :3', instruction_text, 'green', 10, 300)
        write_text('6) Выражаю огромную благодарность этим людям: Шайдт Никита, ', instruction_text, 'green', 10, 350)
        write_text('Соколов Вячеслав, Рачеев Илья, Терский Елисей и Лукша Никита.', instruction_text, 'green', 10, 400)
        write_text('7) ДА, Я ЧЁРТ ВОЗЬМИ ПРОСТО УДЛИНЯЮ КОД!', instruction_text, 'green', 10, 450)
        if back_button.draw():
            main_menu = 1

    elif main_menu == 3:  # рекорды
        pass

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
            write_text('Время: ' + str(round(all_time[-1] - all_time[0], 1)) + ' секунд', font_score, 'green', 500, 8)

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
            write_text('Время: ' + str(round(all_time[-1] - all_time[0], 1)) + ' секунд', font_score, 'green', 500, 8)
            write_text('ИГРА ОКОНЧЕНА.', game_over_text, blue, screen_width // 2 - 130, screen_height // 2)
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        if game_over == 1:  # игрок завершил игру (уровень)
            level += 1  # переход на след. уровень
            if level <= max_levels:
                world_data = []  # перезапуск уровня
                world = reset_level(level)
                game_over = 0
            else:
                time_to_count = False
                write_text('    Тугриков X ' + str(score) + ' монет', font_score, 'green', 8, 8)
                write_text('Время: ' + str(round(all_time[-1] - all_time[0], 1)) + ' секунд', font_score, 'green', 500,
                           8)
                write_text('   ВЫ ВЫИГРАЛИ!', font, white, (screen_width // 2) - 200, screen_height // 2)
                win_fx.play()

                time_record_game = all_time[-1] - all_time[0]
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
        if event.type == pygame.QUIT:
            Running = False

    pygame.display.update()

con.commit()
pygame.quit()