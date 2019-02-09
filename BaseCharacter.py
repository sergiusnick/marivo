import pygame
from Utilities import *
import Map
from PointsUp import PointsUp


class BaseCharacter(pygame.sprite.Sprite):
    ENEMIES = {name: surf for name, surf in
               zip(['normal', 'underground', 'castle', 'underwater'],
                   cut_sheet(load_image("Goomba.png"), 3, 4))}

    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.max_v = 10
        self.vy = 0
        self.create_sides()

    def update_coords(self):
        self.vy += GRAVITY
        self.vy = max(min(self.vy, self.max_v), -self.max_v)
        self.rect = self.rect.move(self.vx, self.vy)

    def check_tile_collisions(self):
        self.check_any_collisions(tiles_group)

    def check_enemies_collisions(self):
        self.check_any_collisions(enemies_group)

    def check_any_collisions(self, group):
        self.update_sides()
        colided_tile = pygame.sprite.spritecollideany(self.left_side, group)
        if colided_tile:
            self.rect.x = colided_tile.rect.right
            self.vx = -self.vx
            self.update_sides()

        colided_tile = pygame.sprite.spritecollideany(self.right_side, group)
        if colided_tile:
            self.rect.right = colided_tile.rect.x
            self.vx = -self.vx
            self.update_sides()

        colided_tile = pygame.sprite.spritecollideany(self.down_side, group)
        if colided_tile:
            self.rect.bottom = colided_tile.rect.y
            self.vy = min(0, self.vy)
            self.update_sides()

    def create_top_side(self):
        # Наследники класса, которым не нужна верхняя коллизия, дожны заменить этот метод на pass
        self.top_side = pygame.sprite.Sprite(self.sides_group)
        self.top_side.image = pygame.Surface((self.rect.w, 1))
        self.top_side.image.fill((0, 255, 0))

    def update_top_side(self):
        # Наследники класса, которым не нужна верхняя коллизия, дожны заменить этот метод на pass
        self.top_side.rect = pygame.Rect(self.rect.x, self.rect.y - 1,
                                         self.rect.w, 1)

    def create_sides(self):
        self.sides_group = pygame.sprite.Group()

        self.create_top_side()
        self.down_side = pygame.sprite.Sprite(self.sides_group)
        self.left_side = pygame.sprite.Sprite(self.sides_group)
        self.right_side = pygame.sprite.Sprite(self.sides_group)
        self.update_sides()

        self.down_side.image = pygame.Surface((self.rect.w, 1))
        self.down_side.image.fill((0, 255, 0))
        self.left_side.image = pygame.Surface((1, self.rect.h - self.max_v * 2))
        self.left_side.image.fill((0, 255, 0))
        self.right_side.image = pygame.Surface((1, self.rect.h - self.max_v * 2))
        self.right_side.image.fill((0, 255, 0))

    def update_sides(self):
        self.update_top_side()
        self.down_side.rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, 1)
        self.left_side.rect = pygame.Rect(self.rect.x - 1, self.rect.y + self.max_v, 1,
                                          self.rect.h - self.max_v * 2)
        self.right_side.rect = pygame.Rect(self.rect.right, self.rect.y + self.max_v, 1,
                                           self.rect.h - self.max_v * 2)

    def show_points(self, collided, points):
        Map.scores.append(PointsUp(collided.rect.left, collided.rect.top, points, Map.scores))
