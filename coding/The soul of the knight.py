import os
import sys
import random
import sqlite3

from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from pygame.locals import *  # для адекватного перемещения гг

# глобальные переменные:
global scor, Hdmg, Bhp, ud, f
scor = 0
Hdmg = 10
Bhp = 500
Bhp1 = Bhp
ud = False

def start_game():
    global screen
    pygame.init()
    d = -100
    screen = pygame.display.set_mode((500, 500))
    pygame.mixer.music.load('res/start3.wav')
    alien3 = pygame.mixer.Sound('res/alien3.wav')
    clock = pygame.time.Clock()
    BackGround = Background('res/home_screen.png', (0, 0))
    screen.blit(BackGround.image, BackGround.rect)
    surf = pygame.Surface((500, 500))
    alien3.play()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and d < 0:
                alien3.stop()
                pygame.mixer.music.play()
                d = 108
        clock.tick(20)
        d -= 1
        if d == 0:
            main()
        if d >= -50:
            screen.blit(surf, (0, 0))
        pygame.display.flip()


if __name__ == '__main__':
    start_game()
