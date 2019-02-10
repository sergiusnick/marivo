import pygame
from Utilities import *
from BaseCharacter import BaseCharacter
from PointsUp import PointsUp


class Koopa(BaseCharacter):
    IMAGES = {name: surf for name, surf in
              zip(['normal', 'underground', 'castle', 'underwater'],
                  cut_sheet(load_image("Koopa.png"), 6, 4))}
    L_KOOPA = {key: (images[:2] + [img.convert_alpha() for img in images[4:6]]) for key, images in
               IMAGES.items()}
    R_KOOPA = {key: [pygame.transform.flip(frame, True, False) for frame in images]
               for key, images in L_KOOPA.items()}

    def __init__(self, x, y, world):
        self.smert = 0
        self.REVIVAL_TIME = 60 * 6
        self.SMERT_TIME = 60 * 8
        self.cur_frame = 0

        self.load_frames()
        self.image = self.frames[self.cur_frame]
        super().__init__(x, y, all_sprites, enemies_group)
        self.vx = -2

    def load_frames(self):
        self.l_frames = Koopa.L_KOOPA[world]
        self.r_frames = Koopa.R_KOOPA[world]
        self.frames = self.l_frames

    def load_image(self, index):
        topleft = self.rect.topleft
        self.image = self.frames[index]
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.update_sides()

    def update(self):
        self.update_coords()
        self.check_tile_collisions()
        self.frames = self.l_frames if self.vx < 0 else self.r_frames
        self.check_enemies_collisions()
        self.sides_group.draw(screen)

        if self.smert:
            if not self.vx:
                self.smert += 1
                if self.smert == self.REVIVAL_TIME:
                    self.image = self.frames[3]
                elif self.smert == self.SMERT_TIME:
                    self.load_image(self.cur_frame // 15 % 2)
                    self.smert = 0
                    self.vx = -2
        else:
            self.cur_frame = (self.cur_frame + 1) % 60
            self.image = self.frames[self.cur_frame // 15 % 2]

    def die(self, rate):
        if not self.smert:
            self.load_image(2)
            self.smert = 1
            self.vx = 0
        else:
            if not self.vx:
                self.vx = 15
            else:
                PointsUp(*self.rect.topleft, 400 * rate)
                hud.add_score(400 * rate)
                self.kill()

    def check_enemies_collisions(self):
        if self.smert and self.vx:
            [enemy.die(4) if enemy is not self else None for enemy in
             pygame.sprite.spritecollide(self, enemies_group, False)]
        else:
            super().check_enemies_collisions()


class JumpingKoopa(Koopa):
    L_FLYING_KOOPA = {key: images[2:6] for key, images in Koopa.IMAGES.items()}
    R_FLYING_KOOPA = {key: [pygame.transform.flip(frame, True, False) for frame in images]
                      for key, images in L_FLYING_KOOPA.items()}

    def __init__(self, x, y, world):
        self.world = world
        super().__init__(x, y, world)
        self.cur_jump = 0
        self.max_jumps = 25

        self.gravity = 0.7
        self.max_vy = 5

    def load_frames(self):
        self.l_frames = JumpingKoopa.L_FLYING_KOOPA[world]
        self.r_frames = JumpingKoopa.R_FLYING_KOOPA[world]
        self.frames = self.l_frames

    def update(self):
        super().update()
        if pygame.sprite.spritecollideany(self.down_side, tiles_group):
            self.cur_jump = 0
        if self.cur_jump < self.max_jumps:
            self.cur_jump += 1
            self.vy = -self.max_vy

    def die(self, rate):
        Koopa(self.rect.x, self.rect.y, self.world).die(rate)
        self.kill()