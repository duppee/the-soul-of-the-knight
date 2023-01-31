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


def main():
    global screen, ud, scor, Bhp, Hdmg, all_sprites, f, event
    screen = pygame.display.set_mode((500, 500))
    pygame.init()
    doom = pygame.mixer.Sound('res/DOOM1!.wav')
    doom.play()
    udar = pygame.mixer.Sound('res/ud1.wav')
    running = True
    start_ticks = pygame.time.get_ticks()  # подсчет времени
    spawn = 100  # время между спавнами врагов
    stop = 1  # остановка игры (нужен вместе с running)
    d = 0  # задержка удара мечом у героя
    f = 0  # запоминалка направления героя
    h = 0  # счетчик кадров ходьбы героя
    up, left = False, False  # чтобы не лагала анимация
    best_result = SQL()

    # задний фон и сам экран
    BackGround = Background('res/background.jpg', (-15, -15))  # в выводе изображения продолжение
    ogranFON = [55, 60, (408, 411)]

    surf = pygame.Surface((500, 500))
    surf.fill((200, 0, 0))
    surf.set_alpha(0)

    # главный герой
    HgoAnimation = ['res/Hero.png', 'res/HeGO1.png', 'res/HeGO4.png']  # анимация ходьбы
    HgoAnimation2 = ['res/Hero2.png', 'res/HeGO3.png', 'res/HeGO2.png']  # анимация ходьбы с мечом
    size = (112, 100)
    image = pygame.image.load('res/Hero.png')
    image = pygame.transform.scale(image, size)  # размер картинки

    hero = pygame.sprite.Sprite()
    hero.image = image
    hero.rect = hero.image.get_rect()
    hero.rect.top = 100  # стартовая позиция
    hero.rect.left = 100
    speed1 = 7  # скорость героя
    speed2 = 3  # скорость героя с мечом

    # сундук
    image1 = pygame.image.load('res/box.png')
    image1 = pygame.transform.scale(image1, (65, 60))  # размер картинки

    box = pygame.sprite.Sprite()
    box.image = image1
    box.rect = box.image.get_rect()
    box.rect.top = 225  # стартовая позиция
    box.rect.left = 225

    # объединение всех спрайтов, объектов на экране
    all_sprites = pygame.sprite.Group()
    all_sprites.add(box)
    all_sprites.add(hero)
    all_sprites.update()

    # время
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # fastbox сделан из лени для сундука, чтобы легче регулировать его хитбокс
        speed = speed1
        fastbox = box.rect.left + 26, box.rect.top, (box.rect.size[0] - 45, box.rect.size[1] - 80)

        # реализация ходьбы с помощью pygame.locals (и другого)
        # 90% кривоты из-за анимации, не бейте

        if pygame.key.get_pressed()[K_SPACE] and not stop and d <= 0:  # рестарт
            Bhp = Bhp1
            scor = 0
            stop = 1
            main()

        ud = False
        if pygame.key.get_pressed()[K_SPACE] and d <= 0 and stop:
            ud = True
            d = 15
            udar.play()
            image = pygame.image.load('res/Hero2.png')
            image = pygame.transform.scale(image, size)
            hero.image = image
            hero.image = pygame.transform.flip(image, f, False)

        d -= 1
        if d <= 0:  # удар не ждет начала ходьбы для конца анимации
            image = pygame.image.load('res/Hero.png')
            image = pygame.transform.scale(image, size)
            hero.image = image
            hero.image = pygame.transform.flip(image, f, False)

        if (pygame.key.get_pressed()[K_w] or pygame.key.get_pressed()[K_UP]) and not up:
            up = True
            h += 1
            if hero.rect.top > ogranFON[1] and collision(fastbox, (
                    hero.rect.left, hero.rect.top - speed, hero.rect.size)):  # ограничение ходьбы
                if d <= 0:
                    image = pygame.image.load(HgoAnimation[h % len(HgoAnimation)])
                else:
                    speed = speed2
                    image = pygame.image.load(HgoAnimation2[h % len(HgoAnimation2)])
                hero.rect.top -= speed
                image = pygame.transform.scale(image, size)
                hero.image = image
                hero.image = pygame.transform.flip(image, f, False)
        if (pygame.key.get_pressed()[K_s] or pygame.key.get_pressed()[K_DOWN]) and not up:
            h += 1
            if hero.rect.top + hero.rect.size[1] < ogranFON[1] + ogranFON[2][1] and collision(
                    (hero.rect.left, hero.rect.top + speed, hero.rect.size),
                    fastbox):  # ограничение ходьбы
                if d <= 0:
                    image = pygame.image.load(HgoAnimation[h % len(HgoAnimation)])
                else:
                    speed = speed2
                    image = pygame.image.load(HgoAnimation2[h % len(HgoAnimation2)])
                hero.rect.top += speed
                image = pygame.transform.scale(image, size)
                hero.image = image
                hero.image = pygame.transform.flip(image, f, False)
        if (pygame.key.get_pressed()[K_a] or pygame.key.get_pressed()[K_LEFT]) and not left:
            left = True
            h += 1
            if hero.rect.left > ogranFON[0] and collision(
                    (hero.rect.left - speed, hero.rect.top, hero.rect.size),
                    fastbox):  # ограничение ходьбы
                if d <= 0:
                    image = pygame.image.load(HgoAnimation[h % len(HgoAnimation)])
                else:
                    speed = speed2
                    image = pygame.image.load(HgoAnimation2[h % len(HgoAnimation2)])
                hero.rect.left -= speed
                image = pygame.transform.scale(image, size)
                hero.image = image
            hero.image = pygame.transform.flip(image, True, False)
            f = True
        if (pygame.key.get_pressed()[K_d] or pygame.key.get_pressed()[K_RIGHT]) and not left:
            h += 1
            hero.image = pygame.transform.flip(image, False, False)
            if hero.rect.left + hero.rect.size[0] < ogranFON[0] + ogranFON[2][0] and collision(
                    (hero.rect.left + speed, hero.rect.top, hero.rect.size),
                    fastbox):
                if d <= 0:
                    image = pygame.image.load(HgoAnimation[h % len(HgoAnimation)])
                else:
                    speed = speed2
                    image = pygame.image.load(HgoAnimation2[h % len(HgoAnimation2)])
                hero.rect.left += speed
                image = pygame.transform.scale(image, size)
                hero.image = image
            f = False

        up, left = False, False

        # спавн нечести
        spawn -= 1
        if spawn <= 0 and stop:
            delay = 300
            if scor > 500:
                delay = 250
            elif scor > 1000:
                delay = 150
            elif scor > 1500:
                delay = 100
            elif scor > 2000:
                delay = 50
            spawn = random.randint(1, delay)  # время между появлением нечести
            Enemy(ogranFON, hero, box, all_sprites)

        # вывод изображения
        screen.fill((255, 255, 255))
        screen.blit(BackGround.image, BackGround.rect)
        if not stop:
            screen.fill((0, 0, 0))

        color = '#00FF00'
        if scor >= 860:
            color = '#FF0000'
        pygame.draw.rect(screen, color, (10, 15, Bhp // 5, 10), width=0)

        if Bhp <= 0:
            font = pygame.font.Font(None, 150)
            text = font.render(f"YOU DIED", True, '#ff2400')
            screen.blit(text, (0, 60))
            screen.blit(text, (0, 140))
            screen.blit(text, (0, 220))
            screen.blit(text, (0, 300))
            font = pygame.font.Font(None, 50)
            text = font.render(f"press SPACE to restart", True, '#ff2400')
            screen.blit(text, (55, 420))
            for i in all_sprites:
                i.kill()
            if stop:
                d = 60
            doom.stop()
            stop = 0

        # показ хитбоксов
        # pokazHITbox(screen, hero, 1)
        # if f:
        #     l = hero.rect.left + hero.rect.size[0] * 0.2
        # else:
        #     l = hero.rect.left + hero.rect.size[0] * 0.1
        # pokazHITbox(screen, (l, hero.rect.top + 40, (hero.rect.size[0] * 0.5, hero.rect.size[1] - 60)), 0)
        # pokazHITbox(screen, box, 1)
        # pokazHITbox(screen, ogranFON, 0)

        all_sprites.update(event)
        all_sprites.draw(screen)
        all_sprites.update()
        clock.tick(30)

        # подсчет очков
        if best_result < scor:
            best_result = SQL(scor // 100 * 100)
        font = pygame.font.SysFont('Inkulinati 210706 Regular', 30)
        if stop:
            scor = int((pygame.time.get_ticks() - start_ticks) / 100)
        if stop:
            text = font.render(f"Points: {scor // 100 * 100}", True, color)
            screen.blit(text, (120, 10))
        else:
            text = font.render(f"Points: {scor // 100 * 100}", True, '#ff2400')
            screen.blit(text, (110, 20))

        if stop:
            text = font.render(f"Best: {best_result}", True, color)
            screen.blit(text, (250, 10))
        else:
            text = font.render(f"Best: {best_result}", True, '#ff2400')
            screen.blit(text, (260, 20))

        if scor >= 860:  # кровь на весь экран ВУАХАХХА
            surf.set_alpha(100)
        screen.blit(surf, (0, 0))

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    start_game()
