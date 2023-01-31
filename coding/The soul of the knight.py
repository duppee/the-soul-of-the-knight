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


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def SQL(new=0):
    con = sqlite3.connect('res/POINTS.sqlite')
    cursor = con.cursor()
    res = cursor.execute('''SELECT points FROM scor''').fetchall()
    if new > int(res[0][0]):
        cursor.execute(f'''UPDATE scor SET points = {new}''').fetchall()
    con.commit()
    con.close()
    return int(res[0][0])


def pokazHITbox(screen, hero, f):  # показывает хитбокс спрайта (годно, но временно)
    if f:
        pygame.draw.rect(screen, '#000000',
                         (hero.rect.left, hero.rect.top, 10, 10), width=0)  # черный
        pygame.draw.rect(screen, '#0000FF',
                         (hero.rect.left + hero.rect.size[0], hero.rect.top, 10, 10), width=0)  # синий
        pygame.draw.rect(screen, '#00FF00',
                         (hero.rect.left, hero.rect.top + hero.rect.size[1], 10, 10), width=0)  # зеленый
        pygame.draw.rect(screen, '#FF0000',
                         (hero.rect.left + hero.rect.size[0], hero.rect.top + hero.rect.size[1], 10, 10),
                         width=0)
    else:
        x, y = hero[0:2]
        a, b = hero[2]
        pygame.draw.rect(screen, '#000000',
                         (x, y, 10, 10), width=0)  # черный
        pygame.draw.rect(screen, '#0000FF',
                         (x + a, y, 10, 10), width=0)  # синий
        pygame.draw.rect(screen, '#00FF00',
                         (x, y + b, 10, 10), width=0)  # зеленый
        pygame.draw.rect(screen, '#FF0000',
                         (x + a, y + b, 10, 10),
                         width=0)


def collision(w1, w2):
    x1, y1 = w1[0:2]
    x2, y2 = w2[0:2]
    a1, b1 = w1[2]
    a2, b2 = w2[2]
    one = [(x1, y1), (x1 + a1, y1), (x1, y1 + b1), (x1 + a1, y1 + b1)]
    two = [(x2, y2), (x2 + a2, y2), (x2, y2 + b2), (x2 + a2, y2 + b2)]
    if (one[0][1] < two[3][1] and one[0][1] < two[3][1]) and (one[1][0] > two[0][0] and one[0][0] < two[1][0]) and \
            one[3][1] > two[0][1]:
        return False
    return True


def load_image(name, colorkey=None):
    fullname = os.path.join('', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    try:
        image = pygame.image.load(fullname)
    except pygame.error as Message:
        print(Message)
        raise SystemExit(Message)
    if colorkey is not None:
        image = image.convert()
    if colorkey == -1:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Enemy(pygame.sprite.Sprite):
    def __init__(self, ogranFON, hero, box, *group):
        super().__init__(*group)
        pygame.init()
        self.stan = 0  # иначе моментально сжирают сундук
        self.box = box
        self.hero = hero

        self.udar = pygame.mixer.Sound('res/ud2.wav')
        self.udar1 = pygame.mixer.Sound('res/box.wav')

        # все виды врагов (4 штуки) у всех все различается
        self.enemy1 = load_image("res/E-easy1.png")
        self.enemy2 = load_image("res/E-easy2.png")
        self.image = self.enemy1
        self.enemyGO = ['res/E-easyGO1.png', 'res/E-easyGO2.png', 'res/E-easyGO3.png']
        self.h = 0
        self.hp = 20
        self.dmg = 20
        self.speed = 1
        self.size = (100, 100)
        self.image = pygame.transform.scale(self.image, self.size)
        self.fastbox = box.rect.left + 26, box.rect.top, (box.rect.size[0] - 45, box.rect.size[1] - 80)
        self.fastbox1 = box.rect.left + 76, box.rect.top - 100, (box.rect.size[0] - 160, 1)
        if scor >= 300 and random.randint(1, 3) == 1:
            self.enemy1 = load_image("res/E-normal.png")
            self.enemy2 = load_image("res/E-normal2.png")
            self.image = self.enemy1
            self.enemyGO = ['res/E-normalGO1.png', 'res/E-normalGO3.png', 'res/E-normalGO2.png']
            self.hp = 30
            self.dmg = 50
            self.speed = 2
            self.size = (200, 150)
            self.image = pygame.transform.scale(self.image, self.size)
            self.fastbox = box.rect.left + 76, box.rect.top, (box.rect.size[0] - 160, box.rect.size[1] - 60)
        if scor >= 900 and random.randint(1, 3) == 1:
            self.enemy1 = load_image("res/E-hard1.png")
            self.enemy2 = load_image("res/E-hard2.png")
            self.image = self.enemy1
            self.enemyGO = ['res/E-hardGO1.png', 'res/E-hardGO2.png', 'res/E-hardGO3.png']
            self.hp = 10
            self.dmg = 100
            self.speed = 4
            self.size = (130, 100)
            self.image = pygame.transform.scale(self.image, self.size)
            self.fastbox = box.rect.left + 26, box.rect.top, (box.rect.size[0] - 45, box.rect.size[1] - 80)
        if scor >= 1500 and random.randint(1, 6) == 1:
            self.enemy1 = load_image("res/E-impossible1.png")
            self.enemy2 = load_image("res/E-impossible3.png")
            self.image = self.enemy1
            self.enemyGO = ['res/E-impossibleGO1.png', 'res/E-impossibleGO2.png', 'res/E-impossibleGO3.png']
            self.hp = 50
            self.dmg = 120
            self.speed = 1
            self.size = (200, 150)
            self.image = pygame.transform.scale(self.image, self.size)
            self.fastbox = box.rect.left + 76, box.rect.top, (box.rect.size[0] - 140, box.rect.size[1] - 80)
        self.rect = self.image.get_rect()

        storona = random.randrange(1, 5)
        if storona == 1:
            self.rect.x = random.randrange(ogranFON[0], ogranFON[0] + ogranFON[2][0])  # > -
            self.rect.y = ogranFON[1] - 100
        if storona == 2:
            self.rect.x = random.randrange(ogranFON[0], ogranFON[0] + ogranFON[2][0])  # > _
            self.rect.y = ogranFON[1] + ogranFON[2][1] + 25
        if storona == 3:
            self.rect.x = ogranFON[0] - 100  # >|
            self.rect.y = random.randrange(ogranFON[1], ogranFON[1] + ogranFON[2][1])
        if storona == 4:
            self.rect.x = ogranFON[0] + ogranFON[2][0] + 25  # >  |
            self.rect.y = random.randrange(ogranFON[1], ogranFON[1] + ogranFON[2][1])

        x = (self.box.rect.x + self.box.rect.size[0] * 0.5)
        x2 = (self.rect.x + self.rect.size[0] * 0.5)

        if x < x2:
            self.image = pygame.transform.flip(self.image, True, False)
            self.f = True
        else:
            self.image = pygame.transform.flip(self.image, False, False)
            self.f = False

    def update(self, *args):
        global ud, Bhp, f
        if f:
            self.l = self.hero.rect.left + self.hero.rect.size[0] * 0.2
        else:
            self.l = self.hero.rect.left + self.hero.rect.size[0] * 0.1
        if ud and not \
                collision(
                    (self.l, self.hero.rect.top + 40, (self.hero.rect.size[0] * 0.5, self.hero.rect.size[1] - 60)),
                    (self.rect.left, self.rect.top, self.rect.size)):
            ud = False
            self.hp -= Hdmg
            self.udar.play()
        if self.hp <= 0:
            self.kill()
        s = 1

        self.x = (self.box.rect.x + self.box.rect.size[0] * 0.5)
        self.y = (self.box.rect.y + self.box.rect.size[1] * 0.3)
        self.x2 = (self.rect.x + self.rect.size[0] * 0.5)
        self.y2 = (self.rect.y + self.rect.size[1] * 0.5)

        if self.x2 < self.x and collision(self.fastbox, (self.rect.left, self.rect.top, self.rect.size)):
            self.rect.x += self.speed
            s = 0
        elif self.x2 > self.x and collision((self.rect.left, self.rect.top, self.rect.size), self.fastbox):
            self.rect.x -= self.speed
            s = 0
        if self.size[1] <= 100:
            a = self.fastbox
        else:
            a = self.fastbox1
        if self.y2 < self.y and collision((self.rect.left, self.rect.top, self.rect.size), self.fastbox):
            self.rect.y += self.speed
            s = 0
        elif self.y2 > self.y and collision((self.rect.left, self.rect.top, self.rect.size), a):
            self.rect.y -= self.speed
            s = 0
        self.stan -= 1
        if not s:
            self.h += 1
            self.image = load_image(self.enemyGO[self.h % len(self.enemyGO)])
            self.image = pygame.transform.scale(self.image, self.size)
            self.image = pygame.transform.flip(self.image, self.f, False)
        if s and self.stan < 80:
            self.image = self.enemy1
            self.image = pygame.transform.scale(self.image, self.size)
            self.image = pygame.transform.flip(self.image, self.f, False)
        if s and self.stan <= 0:
            self.image = self.enemy2
            self.image = pygame.transform.scale(self.image, self.size)
            self.image = pygame.transform.flip(self.image, self.f, False)
            Bhp -= self.dmg
            self.udar1.play()
            self.stan = 100


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
                stop = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                stop = False
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
        font = pygame.font.Font(None, 30)
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
    try:
        start_game()
    except:
        pass
