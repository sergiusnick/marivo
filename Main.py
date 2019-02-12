import pygame
from Utilities import *
import Map

time = pygame.time.Clock()
cur_frame = 0

while True:
    Map.player.process_events(pygame.event.get())
    screen.fill((92, 148, 252))

    camera.update(Map.player)
    for sprite in all_sprites:
        camera.apply(sprite)

    players_group.update()
    all_sprites.update()
    hud.update()

    decor_group.draw(screen)
    items_group.draw(screen)
    enemies_group.draw(screen)
    castle_group.draw(screen)
    tiles_group.draw(screen)
    players_group.draw(screen)
    particles_group.draw(screen)
    hud.draw(screen)

    pygame.display.flip()
    time.tick(FPS)
