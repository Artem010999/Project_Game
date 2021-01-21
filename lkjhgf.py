import pygame

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption('Попытка игры')

Right_walk = [pygame.image.load('player.png')]  # список спрайтов при движении вправо
Left_walk = [pygame.image.load('player.png')]  # список спрайтов при движении влево
Background = pygame.image.load('dungeon.png')  # фон
Standing = [pygame.image.load('player.png')]  # персонаж стоит
clock = pygame.time.Clock()


class Player(object):
    def __init__(self, x_pos, y_pos, height, width):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.height = height
        self.width = width
        self.shift = 10  # само движение
        self.can_jump = False
        self.count_of_jump = 10
        self.Left_shift = False
        self.Right_shift = False
        self.Count_of_movements = 0

    def animation(self, screen):
        if self.Count_of_movements + 1 >= 27:
            self.Count_of_movements = 0
        if self.Left_shift:  # персонаж двигается влево -> меняются спрайты
            screen.blit(Left_walk[self.Count_of_movements // 3], (self.x_pos, self.y_pos))
            self.Count_of_movements += 1
        elif self.Right_shift:  # персонаж двигается вправо -> меняются спрайты
            screen.blit(Right_walk[self.Count_of_movements // 3], (self.x_pos, self.y_pos))
            self.Count_of_movements += 1
        else:  # персонаж не двигается ни вправо, ни влево
            screen.blit(Standing[self.Count_of_movements // 3], (self.x_pos, self.y_pos))


def new_window():  # движение и анимация персонажа99
    screen.blit(Background, (0, 0))
    main_player.animation(screen)
    pygame.display.update()


main_player = Player(50, 460, 40, 40)
Running = True
while Running:
    clock.tick(27)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and main_player.x_pos >= main_player.shift:
        main_player.x_pos -= main_player.shift
        main_player.Left_walk = True
        main_player.Right_walk = False
    elif keys[pygame.K_RIGHT] and main_player.x_pos <= (500 - main_player.width - main_player.shift):
        main_player.x_pos += main_player.shift
        main_player.Left_walk = False
        main_player.Right_walk = True
    else:
        main_player.Right_walk = False
        main_player.Left_walk = False
        main_player.Count_of_movements = 0

    if keys[pygame.K_ESCAPE]:  # Выход из игры
        Running = False

    if keys[pygame.K_LALT]:  # Сворачивание окна
        pygame.display.iconify()
        
    if not main_player.can_jump:
        if keys[pygame.K_SPACE]:
            main_player.can_jump = True
            main_player.Left_walk = False
            main_player.Right_walk = False
            main_player.Count_of_movements = 0
    else:
        if main_player.count_of_jump >= -10:
            ground = 1
            if main_player.count_of_jump < 0:
                ground = -1
            main_player.y_pos -= ((main_player.count_of_jump ** 2) / 2) * ground
            main_player.count_of_jump -= 1
        else:
            main_player.can_jump = False
            main_player.count_of_jump = 10
    new_window()

pygame.quit()
