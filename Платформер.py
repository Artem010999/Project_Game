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
        write_text('[{8--вышла лютая хpень--8}]', font, (64, 224, 208), 75, 740)
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
        # основные дейctвия
        pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False

    pygame.display.update()

con.commit()
pygame.quit()