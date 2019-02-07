import pygame
from Utilities import *
from BaseCharacter import BaseCharacter


class ItemBase(BaseCharacter):
    ITEMS = {name: surf for name, surf in
             zip(['normal', 'underground', 'castle', 'underwater'],
                 cut_sheet(load_image("Items.png"), 19, 4))}

    def __init__(self, x, y):
        super().__init__(x, y, all_sprites, items_group)
        self.vx = 5
        self.uprise = self.rect.y - self.rect.h + self.rect.h // 3
        self.create_sides()

    def move(self):
        if self.uprise is not None and self.rect.y > self.uprise:
            self.rect.y -= 1
            if self.rect.y == self.uprise:
                self.uprise = None
            return True

    def update(self):
        if self.move():
            return
        self.update_coords()
        self.check_player_collisions()

        vx = self.vx
        self.check_tile_collisions()
        if vx != self.vx:
            self.image = pygame.transform.flip(self.image, True, False)

        self.sides_group.draw(screen)


class MushroomSizeUp(ItemBase):
    def __init__(self, x, y, world):
        self.image = ItemBase.ITEMS[world][0]
        super().__init__(x, y)

    def check_player_collisions(self):
        collided = pygame.sprite.spritecollideany(self, players_group)
        if collided:
            collided.set_state('big')
            print('+1000 Score')
            self.kill()

    def create_top_side(self):
        pass

    def update_top_side(self):
        pass


class MushroomLiveUp(ItemBase):
    def __init__(self, x, y, world):
        self.image = ItemBase.ITEMS[world][1]
        super().__init__(x, y)

    def check_player_collisions(self):
        collided = pygame.sprite.spritecollideany(self, players_group)
        if collided:
            print('+1 live')
            self.kill()

    def create_top_side(self):
        pass

    def update_top_side(self):
        pass


class MushroomDeadly(ItemBase):
    def __init__(self, x, y, world):
        self.image = ItemBase.ITEMS[world][2]
        super().__init__(x, y)

    def check_player_collisions(self):
        collided = pygame.sprite.spritecollideany(self, players_group)
        if collided:
            collided.set_state('small')
            collided.died = True
            print('-1 live')
            self.kill()

    def create_top_side(self):
        pass

    def update_top_side(self):
        pass


class FireFlower(ItemBase):
    def __init__(self, x, y, world):
        self.cur_frame = 0
        self.frames = ItemBase.ITEMS[world][3:7]
        self.image = self.frames[self.cur_frame]
        super().__init__(x, y)
        self.vx = 0

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % 60
        self.image = self.frames[self.cur_frame // 5 % 4]
        super().update()

    def check_player_collisions(self):
        collided = pygame.sprite.spritecollideany(self, players_group)
        if collided:
            collided.set_state('fire', 'big')
            self.kill()

    def check_tile_collisions(self):
        self.update_sides()
        colided_tile = pygame.sprite.spritecollideany(self.down_side, tiles_group)
        if colided_tile:
            self.rect.bottom = colided_tile.rect.y
            self.vy = min(0, self.vy)
            self.update_sides()

    def create_sides(self):
        self.sides_group = pygame.sprite.Group()
        self.down_side = pygame.sprite.Sprite(self.sides_group)
        self.update_sides()

        self.down_side.image = pygame.Surface((self.rect.w, 1))
        self.down_side.image.fill((0, 255, 0))

    def update_sides(self):
        self.down_side.rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, 1)


class Star(ItemBase):
    def __init__(self, x, y, world):
        self.cur_frame = 0
        self.frames = ItemBase.ITEMS[world][7:11]
        self.image = self.frames[self.cur_frame]
        super().__init__(x, y)

        self.max_jumps = 8
        self.cur_jump = 0

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % 60
        self.image = self.frames[self.cur_frame // 5 % 4]
        if self.cur_jump < self.max_jumps:
            self.vy = - self.max_v
            self.cur_jump += 1
        super().update()
        if pygame.sprite.spritecollideany(self.down_side, tiles_group):
            self.cur_jump = 0

    def check_player_collisions(self):
        collided = pygame.sprite.spritecollideany(self, players_group)
        if collided:
            print('invincibility')
            self.kill()


class CoinStatic(pygame.sprite.Sprite):
    def __init__(self, x, y, world):
        self.frames = ItemBase.ITEMS[world][11:15]
        self._load_image(x, y)

    def _load_image(self, x, y):
        super().__init__(all_sprites, items_group)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % 60
        self.image = self.frames[self.cur_frame // 5 % 4]
        self.check_player_collisions()

    def check_player_collisions(self):
        collided = pygame.sprite.spritecollideany(self, players_group)
        if collided:
            print('+1 coins')
            print('+200 score')
            self.kill()


class Coin(CoinStatic):
    def __init__(self, x, y, world):
        self.frames = ItemBase.ITEMS[world][15:19]
        self._load_image(x, y)
        self.start_y = self.rect.y - self.rect.h
        self.end_y = self.start_y - self.rect.h * 2

        print('+1 coins')
        print('+200 score')

    def update(self):
        super().update()
        if self.end_y is not None and self.rect.y > self.end_y:
            self.rect.y -= 7
            if self.rect.y <= self.end_y:
                self.end_y = None
        elif self.rect.y < self.start_y:
            self.rect.y += 7
            if self.rect.y >= self.start_y:
                self.kill()

    def check_player_collisions(self):
        pass
