import pygame
import os
import sys
from collections import OrderedDict


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    """Функция безопасной загрузки и преобразования изображения. Конвертирует альфа-канал,
    может преобразовать цвет в альфа-канал, растягивает исходняе изображение в 3 раза"""
    fullname = os.path.join('data', 'images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    image_rect = image.get_rect()
    return pygame.transform.scale(image, (image_rect.w * 3, image_rect.h * 3))


def load_font(name, size):
    """Функция безопасной загрузки и создания шрифтов."""
    fullname = os.path.join('data', 'fonts', name)
    try:
        font = pygame.font.Font(fullname, size)
    except pygame.error as message:
        print('Cannot load font:', name)
        raise SystemExit(message)
    return font


def cut_sheet(sheet, columns, rows):
    """Функция, разрезающая переданный surface на заданное количество частей.
    Всегда возвращает  двумерный список surface'ов"""
    frames = []
    width, height = sheet.get_width() // columns, sheet.get_height() // rows
    for row in range(rows):
        frames_line = []
        for col in range(columns):
            frame_location = (width * col, height * row)
            frames_line.append(sheet.subsurface(pygame.Rect(frame_location, (width, height))))
        frames.append(frames_line)
    return frames


class Hud:
    """Heads-Up Display. Хранит счет, всемя в секундах, название мира, количество монет и жизней.
    Занимается подсчетом времени. Передает в main сообщение об окончании времени или жизней.
    Превращается в заставку gameover"""
    pygame.font.init()
    FONT = load_font("SuperMario256.ttf", 40)

    def __init__(self):
        self.info = OrderedDict([("SCORE", 0), ("TIME", 400), ("WORLD", "1-1"), ("COINS", 0),
                                 ("LIVES", 3)])
        self.first_line = [(key, Hud.FONT.render(key, 1, pygame.Color('White'))) for key in
                           self.info.keys()]
        self.first_line_width = sum([item[1].get_width() for item in self.first_line])
        self.h_indent = (WIDTH - self.first_line_width) // (len(self.first_line) + 1)
        self.v_indent = 10  # Отступ от верхней границы и между строками худа
        self.last_frame = FPS - 1  # Номер кадра, на котором произойдет уменьшение времени
        self.cur_frame = 0  # Счетчик кадров
        self.count = False  # Режим перевода оставшегося времени в счет. Используется в конце карты.
        self.game_over = 0  # оставшееся время заставки gameover
        self.load_level_request = False  # Если True, то в main роизойдет загрузка карты
        self.game_over_time = 240  # общее время заставки gameover

    def update(self):
        if self.game_over:  # На последнем кадре game over вызывается загрузка карты
            self.game_over -= 1
            if self.game_over == 1:
                self.load_level_request = True
                self.info['LIVES'] = 3
            elif not self.game_over:
                self.load_level_request = False
        elif self.count:  # Режим перевода оставшегося времени в счет. Используется в конце карты.
            if self.info['TIME']:
                self.info['TIME'] -= 1
                self.info['SCORE'] += 50
                if not self.info['TIME']:
                    self.count = False
        else:
            self.cur_frame = (self.cur_frame + 1) % 60  # Обновление счетчика кадров
            # Подсчет времени худа
            if self.cur_frame == self.last_frame and self.info['TIME']:
                self.info['TIME'] -= 1
                if not self.info['TIME']:
                    self.start_game_over()

    def draw(self, screen):
        """hud создается всегда по центру экрана"""
        if self.game_over:
            self.game_over_draw(screen)
            return
        x = self.h_indent
        for key, key_surf in self.first_line:
            screen.blit(key_surf, (x, self.v_indent))
            val_surf = Hud.FONT.render(str(self.info[key]), 1, pygame.Color('White'))
            screen.blit(val_surf, (x + (key_surf.get_width() - val_surf.get_width()) // 2,
                                   self.v_indent + key_surf.get_height()))
            x += self.h_indent + key_surf.get_width()

    def start_count(self):
        self.count = True

    def add_score(self, score):
        self.info["SCORE"] += int(score)

    def set_score(self, score):
        self.info["SCORE"] = int(score)

    def set_world(self, world):
        self.info["WORLD"] = str(world)

    def add_coins(self, coins):
        self.info["COINS"] += int(coins)

    def set_coins(self, coins):
        self.info["COINS"] = int(coins)

    def add_lives(self, lives):
        self.info["LIVES"] += int(lives)
        if self.info["LIVES"] < 0:
            self.start_game_over()

    def set_lives(self, lives):
        self.info["LIVES"] = int(lives)

    def get_lives(self):
        return self.info["LIVES"]

    def get_time(self):
        return self.info['TIME']

    def set_time(self, time):
        self.info['TIME'] = time

    def reset(self, score=False):
        if score:
            self.info['SCORE'] = 0
            self.info['COINS'] = 0
        self.info['TIME'] = 400

    def game_over_draw(self, screen):
        """Создание и отрисовка заставки game over"""
        screen.fill((0, 0, 0))
        text = Hud.FONT.render('GAME OVER', 1, pygame.Color('White'))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2,
                           HEIGHT // 2 - text.get_height() // 2))

    def get_game_over(self):
        return self.game_over

    def get_load_level_request(self):
        return self.load_level_request

    def start_game_over(self):
        self.game_over = self.game_over_time


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        if obj.rect.right < 0 or obj.rect.y > HEIGHT:
            obj.kill()

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = min(0, -(target.rect.x + target.rect.w // 2 - WIDTH // 2))
        target.rect.x += self.dx
        if target.rect.x <= 0:
            target.rect.x = 0
            target.vx = max(0, target.vx)


pygame.init()
PPM = 48
FPS = 60
SIZE = WIDTH, HEIGHT = 32 * PPM, 15 * PPM
GRAVITY = 1
screen = pygame.display.set_mode(SIZE)
scores = []

camera = Camera()
hud = Hud()

all_sprites = pygame.sprite.Group()
decor_group = pygame.sprite.Group()
players_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
castle_group = pygame.sprite.Group()
items_group = pygame.sprite.Group()
particles_group = pygame.sprite.Group()

# Группы в правильном для отрисовки порядке
groups = [decor_group, items_group, enemies_group, castle_group, tiles_group, players_group,
          particles_group]
