import random
from functools import reduce
from math import atan, degrees, cos, sin, radians, ceil
from time import perf_counter

import pygame as pg
from pygame import mixer

# Note that if this wasn't a stem from the home screen you would have to initialize pygame
pg.init()
PIC_PATH = "pics/"
SOUND_PATH = "sound/"


# Global classes and functions and variables
def distance(x1, y1, x2, y2):
    return round(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5, 1)


lazer_pic = pg.image.load(f'{PIC_PATH}lazer2.png')
rocket_pic = pg.image.load(f'{PIC_PATH}rocket.png')
# Background
background = pg.image.load(f'{PIC_PATH}output-onlinejpgtools.jpg')
# Background music
background_music = mixer.music.load(f'{SOUND_PATH}background_music.mp3')
# Title
pg.display.set_caption('Space Invaders')
icon = pg.image.load(f'{PIC_PATH}spaceship.png')
pg.display.set_icon(icon)
# Player
playerImg = pg.image.load(f'{PIC_PATH}space-invaders.png')
# Enemy
enemyImg = pg.image.load(f'{PIC_PATH}ufo.png')
# Explosion
explosion_pic = pg.image.load(f'{PIC_PATH}explosion.png')

# vairiables for Enemy class
spawn_min = -40
spawn_max = 0
wave_distance = 60
# Booster imgs
booster_ammo = pg.image.load(f'{PIC_PATH}ammo_booster_fire.png')
booster_base = pg.image.load(f'{PIC_PATH}ammo_booster_base.png')
booster_hero = pg.image.load(f'{PIC_PATH}hp_boosterpng.png')
booster_damage = pg.image.load(f'{PIC_PATH}damage_booster.png')
booster_and_pic = {'ammo': booster_ammo, 'base': booster_base, 'hero': booster_hero, 'speed': booster_damage}
possible_x = list(range(64, 801, 65))[:-1]
# Fireball img, group
fireball_img = pg.image.load(f'{PIC_PATH}Fireball.png')


# V-descent
def v_descent(x, y, x_change, y_change):
    if x >= 736:
        x_c = -x_change
    elif x <= 10:
        x_c = -x_change
    else:
        x_c = x_change
    return x + x_c, y + y_change, x_c


def y_descent(x, y, x_change, y_change):
    return x, y + y_change * 5, x_change


def random_descent(x, y, x_change, y_change):
    if x >= 736 or random.randint(0, 200) == 17:
        x_c = -x_change
    elif x <= 10 or random.randint(0, 100) == 17:
        x_c = -x_change
    else:
        x_c = x_change
    return x + x_c, y + y_change, x_c


# Fireball Class
class Fireball(pg.sprite.Sprite):
    def __init__(self, x, y, angle, group):
        self.x = x
        self.y = y
        self.rect = fireball_img.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.angle = angle
        self.group = group
        pg.sprite.Sprite.__init__(self, group)

    def draw(self, screen):
        img = pg.transform.rotate(fireball_img, self.angle)
        screen.blit(img, (self.x, self.y))

    def update(self, speed):
        if self.angle > 270:
            x_c = speed * sin(radians(self.angle - 270))
            y_c = -speed * cos(radians(self.angle - 270))
        elif self.angle <= 90:
            x_c = -speed * sin(radians(self.angle))
            y_c = -speed * cos(radians(self.angle))
        elif 90 < self.angle <= 180:
            x_c = -speed * sin(radians(self.angle))
            y_c = speed * cos(radians(self.angle - 90))
        elif 180 < self.angle <= 270:
            x_c = speed * sin(radians(self.angle - 180))
            y_c = -speed * cos(radians(self.angle))
        if self.angle == 180:
            x_c = 0
            y_c = speed
        self.rect = fireball_img.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.x += x_c
        self.y += y_c


# Class Hero
class Hero(pg.sprite.Sprite):
    def __init__(self, x, y, hp, hero_group):
        self.x = x
        self.y = y
        self.hp = hp
        self.rect = playerImg.get_rect()
        self.rect.topleft = (self.x, self.y)
        pg.sprite.Sprite.__init__(self, hero_group)

    def draw(self, screen):
        screen.blit(playerImg, (int(self.x), int(self.y)))

    def move_left(self, lag_multiplier, booster_speed_multiplier, norm_speed=1.3):
        self.x -= norm_speed * lag_multiplier * booster_speed_multiplier
        self.rect = playerImg.get_rect()
        self.rect.topleft = (self.x, self.y)

    def move_right(self, lag_multiplier, booster_speed_multiplier, norm_speed=1.3):
        self.x += norm_speed * lag_multiplier * booster_speed_multiplier
        self.rect = playerImg.get_rect()
        self.rect.topleft = (self.x, self.y)


# class Booster
class Booster(pg.sprite.Sprite):
    def __init__(self, x, y, group):
        self.x = x
        self.y = y
        self.booster = random.choice(['ammo', 'base', 'hero', 'speed'])
        self.image = booster_and_pic[self.booster]
        self.group = group
        pg.sprite.Sprite.__init__(self, group)

    def draw(self, screen):
        screen.blit(self.image, (self.x + 16, self.y + 15))

    def update(self, lag_multiplier):
        # Require a lag multiplier variable
        self.y += 0.5 * lag_multiplier

    def apply_boost(self, ammo_boost, speed_mul):
        # requires var fireballs_in
        if self.booster == 'ammo':
            if fireballs_in:
                ammo_type = random.choice(['lasers', 'fireballs'])
            else:
                ammo_type = 'lasers'
            if ammo_type == 'laser':
                return ammo_boost, 0, 0, 0, 0
            else:
                return 0, ammo_boost, 0, 0, 0
        elif self.booster == 'base':
            return 0, 0, 0, 0.5, 0
        elif self.booster == 'hero':
            return 0, 0, hero_boost, 0, 0
        elif self.booster == 'speed':
            return 0, 0, 0, 0, speed_mul


# explosion class
class Explosion(pg.sprite.Sprite):
    def __init__(self, pic_frame, x, y, group, screen):
        self.pic_frame = pic_frame
        self.x = x
        self.y = y
        self.group = group
        self.screen = screen
        pg.sprite.Sprite.__init__(self, group)

    def draw(self):
        width = round(self.pic_frame)
        height = int(round(self.pic_frame * 107 / 128))
        new_pic = pg.transform.scale(explosion_pic, (width, height))
        self.screen.blit(new_pic, (self.x - width / 2, self.y - height / 2))

    def next_frame(self):
        if self.pic_frame > 1:
            self.pic_frame -= 1
        else:
            self.group.remove(self)


class Rocket(pg.sprite.Sprite):
    def __init__(self, x, y, arr, screen):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.rect = rocket_pic.get_rect()
        self.rect.topleft = [x, y]
        self.angle = 0
        self.arr = arr
        self.screen = screen

    def launch_rocket(self):
        self.arr.append(self)

    def draw_rocket(self, targetX, targetY):
        angle = abs((self.y - targetY) / (self.x - targetX))
        angle = atan(angle)
        angle = degrees(angle)
        if self.x < targetX and self.y > targetY:
            angle += 270
        img = pg.transform.rotate(rocket_pic, abs(angle))
        self.angle = angle
        self.screen.blit(img, (self.x, self.y))

    def update_rocket(self, speed, targetX, targetY):
        if distance(self.x, self.y, targetX, targetY) >= 100:
            x_c = (targetY - self.y) / 20
            y_c = (targetX - self.x) / 20
            self.y += x_c
            self.x += y_c
        else:
            ang = self.angle % 270
            add = self.angle == ang
            x_change = abs(sin(ang) * speed)
            y_change = abs(cos(ang) * speed)
            if not add:
                self.x += x_change
                self.y -= y_change
            else:
                self.x -= x_change
                self.y -= y_change


# Enemy Class
class Enemy(pg.sprite.Sprite):
    def __init__(self, descent, hp, enemyX_change, enemyY_change, group, image=enemyImg):
        global possible_x, spawn_min, spawn_max
        # Descent is a function that takes in an x and y and specifies the next x and y based on x_change and y_change
        # It returns a tuple x, y
        self.y = random.randrange(spawn_min, spawn_max)
        if not possible_x:
            possible_x = list(range(64, 801, 65))[:-1]
            spawn_min -= wave_distance
            spawn_max -= wave_distance
            self.y = random.randrange(spawn_min, spawn_max)
        self.x = random.choice(possible_x)
        possible_x.remove(self.x)
        self.image = image
        self.rect = enemyImg.get_rect()
        self.descent = descent
        self.x_change = enemyX_change + random.randint(0, 3) / 100
        self.y_change = enemyY_change + random.randint(0, 3) / 100
        self.hp = hp
        pg.sprite.Sprite.__init__(self, group)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def update(self):
        self.x, self.y, self.x_change = self.descent(self.x, self.y, self.x_change, self.y_change)


# Laser class
class Laser(pg.sprite.Sprite):
    def __init__(self, x, y, arr):
        self.x = x
        self.y = y
        self.rect = lazer_pic.get_rect()
        self.rect.topleft = [x, y]
        self.image = lazer_pic
        self.arr = arr
        pg.sprite.Sprite.__init__(self)

    def launch_lazer(self):
        self.arr.append(self)

    def draw_lazer(self, screen):
        screen.blit(self.image, (round(self.x), round(self.y)))

    def update_lazer(self, y_change):
        self.y = (self.y - y_change)
        self.rect = lazer_pic.get_rect()
        self.rect.topleft = [self.x, self.y]


def level(enemy_speedX, enemy_speedY, num_verticals, num_vs, num_rands, verticals_hp, vs_hp, rands_hp, base, hero_hp,
          laser_cooldown, rockets_in=True, rocket_cooldown=10, limeted_lasers=False, lasers_p_enemy=9,
          fireballs_in=True,
          fire_ball_cooldown=0.5, fireball_p_enemy=0.25, boosters=False, ammo_boost=7, hero_boost=300, speed_mul=1.5):
    # create screen
    screen = pg.display.set_mode((800, 700))
    mixer.music.play(-1)
    # Global variables
    fireball_group = pg.sprite.Group()
    rocketCooldown = -rocket_cooldown
    rocket_fired_tm = 0
    lazerCooldown = -laser_cooldown
    laser_fired_tm = 0
    fireball_fired_tm = 0
    fireballCooldown = -fire_ball_cooldown
    running = True
    weapons = ['lazer', 'rocket', 'fireball']
    weapon = weapons[0]
    enemies = []
    time_to_cross = round(0.0026 * len(enemies) ** 2 + 0.0475 * len(enemies) + 2.94, 1)
    lag_multiplier = time_to_cross / 4.05
    enemyX_change = enemy_speedX * lag_multiplier
    enemyY_change = enemy_speedY * lag_multiplier
    booster_speed_multiplier = 1
    hero_dead = False
    if limeted_lasers:
        laser_ammo = lasers_p_enemy * len(enemies)
    else:
        laser_ammo = 1
    fire_ball_ammo = fireball_p_enemy * len(enemies)

    # Lazer stuff
    lasers_fired = []
    rockets_fired = []
    weapons_n_aliens = pg.sprite.Group()
    enemies = pg.sprite.Group()
    # Possible enemy spawning position
    # Single group hero
    hero_group = pg.sprite.GroupSingle()
    # Booster group
    if boosters:
        booster_group = pg.sprite.Group()
    # Booster class

    # Explosion group
    exploded = pg.sprite.Group()

    # Create 5 enemies

    [weapons_n_aliens.add(Enemy(v_descent, vs_hp, enemyX_change, enemyY_change, enemies)) for _ in range(num_vs)]
    [weapons_n_aliens.add(Enemy(y_descent, verticals_hp, enemyX_change, enemyY_change, enemies)) for _ in
     range(num_verticals)]
    [weapons_n_aliens.add(Enemy(random_descent, rands_hp, enemyX_change, enemyY_change, enemies)) for _ in
     range(num_rands)]

    ourHero = Hero(370, 480, hero_hp, hero_group)

    font = pg.font.Font('freesansbold.ttf', 20)

    def show_text(x, y, text):
        score = font.render(text, True, (255, 255, 255))
        screen.blit(score, (int(x), int(y)))

    frames = 0
    """
    ****
    Game Loop
    ****
    """
    while running:
        start = perf_counter()
        # background
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit(0)
        keys = pg.key.get_pressed()
        try:
            if (keys[pg.K_LEFT] or keys[pg.K_d]) and ourHero.x > 0:
                [hero.move_left(lag_multiplier, booster_speed_multiplier) for hero in hero_group]
            elif (keys[pg.K_RIGHT] or keys[pg.K_a]) and ourHero.x < 800 - 64:
                [hero.move_right(lag_multiplier, booster_speed_multiplier) for hero in hero_group]
        except NameError:
            pass
        if keys[pg.K_0]:
            weapon = weapons[0]
        elif keys[pg.K_1] and rockets_in:
            weapon = weapons[1]
        elif keys[pg.K_2] and fireballs_in:
            weapon = 'fireball'
        if keys[pg.K_SPACE] and perf_counter() - laser_fired_tm > lazerCooldown and weapon == 'lazer' and laser_ammo:
            a = Laser(ourHero.x + 27, ourHero.y, lasers_fired)
            a.launch_lazer()
            laser_fired_tm = perf_counter()
            lazerCooldown = laser_cooldown
            if limeted_lasers:
                laser_ammo -= 1
            bulletSound = mixer.Sound(f'{SOUND_PATH}laser.wav')
            bulletSound.play()
        elif keys[pg.K_SPACE] and perf_counter() - rocket_fired_tm > rocketCooldown and weapon == 'rocket':
            distances = [distance(i.x, i.y, ourHero.x, ourHero.y) for i in enemies]
            if distances:
                c = sorted(distances.copy())[0]
            target = [i for i in weapons_n_aliens if type(i) == Enemy][distances.index(c)]
            b = Rocket(ourHero.x + 27, ourHero.y + 35, rockets_fired, screen)
            b.launch_rocket()
            rocket_fired_tm = perf_counter()
            rocketCooldown = rocket_cooldown
        elif keys[
            pg.K_SPACE] and perf_counter() - fireball_fired_tm > fireballCooldown and weapon == 'fireball' and fire_ball_ammo > 0:
            [Fireball(ourHero.x, ourHero.y, ang, fireball_group) for ang in range(0, 91, 30)]
            [Fireball(ourHero.x, ourHero.y, ang, fireball_group) for ang in range(270, 360, 30)]
            fireball_fired_tm = perf_counter()
            fireballCooldown = fire_ball_cooldown
            fire_ball_ammo -= 1

        if fireballs_in:
            [i.update(2) for i in fireball_group]
            [i.draw(screen) for i in fireball_group]

        if rockets_in:
            [i.update_rocket(2, target.x, target.y) for i in rockets_fired]
            [rockets_fired.remove(i) for i in rockets_fired if i.y < 30]
            [i.draw_rocket(target.x, target.y) for i in rockets_fired if i.y < 600]
        # booster drawing and updating
        if boosters:
            booster_group.remove(*[booster for booster in booster_group if booster.y >= 450])
            [i.update(lag_multiplier) for i in booster_group]
            [i.draw(screen) for i in booster_group]

        [i.update_lazer(2) for i in lasers_fired]
        [lasers_fired.remove(i) for i in lasers_fired if i.y < 30]
        [i.draw_lazer(screen) for i in lasers_fired]

        [hero.draw(screen) for hero in hero_group]

        # Enemy checking / Drawing loop
        for enemy in enemies:
            enemy.draw(screen)
            enemy.update()
            center_x = enemy.rect.center[0] + enemy.x
            center_y = enemy.rect.center[1] + enemy.y
            radius = distance(center_x, center_y, enemy.x, enemy.y)
            new_enemies = enemies.copy()
            new_enemies.remove(enemy)
            for ufo in new_enemies:
                if distance(center_x, center_y, ufo.rect.center[0] + ufo.x, enemy.rect.center[1] + ufo.y) < radius:
                    enemy.x_change *= -1
                    ufo.x_change *= -1
            for l in lasers_fired + rockets_fired + list(fireball_group):
                if distance(center_x, center_y, l.x, l.y) < radius:
                    if type(l) == Laser:
                        lasers_fired.remove(l)
                        enemy.hp -= 100
                    elif type(l) == Fireball:
                        fireball_group.remove(l)
                        enemy.hp -= 50
                    elif type(l) == Fireball:
                        rockets_fired.remove(l)
                        enemy.hp -= 400
                    weapons_n_aliens.remove(l)
                    Explosion(25, center_x, center_y, exploded, screen)
            if enemy.hp <= 0 or enemy.y >= 491:
                enemies.remove(enemy)
                weapons_n_aliens.remove(enemy)
                Explosion(100, center_x, center_y, exploded, screen)
                if boosters:
                    Booster(center_x, center_y, booster_group)
            if enemy.y >= 490:
                base -= 1
                base = abs(base)
            if distance(center_x, center_y, ourHero.rect.center[0],
                        ourHero.rect.center[1]) < radius:
                Explosion(50, ourHero.x, ourHero.y, exploded, screen)
                enemies.remove(enemy)
                weapons_n_aliens.remove(enemy)
                ourHero.hp -= 500
        # Booster is_hit loop
        if boosters:
            for booster in booster_group:
                if distance(booster.x, booster.y, ourHero.x, ourHero.y) < 32 * 1.42:
                    booster_group.remove(booster)
                    effect = booster.apply_boost(ammo_boost, speed_mul)
                    laser_ammo += effect[0]
                    fire_ball_ammo += effect[1]
                    ourHero.hp += effect[2]
                    base += effect[3]
                    if effect[4]:
                        booster_speed_multiplier *= effect[4]

        if ourHero.hp <= 0 and not hero_dead:
            Explosion(100, ourHero.rect.center[0] + ourHero.x, ourHero.rect.center[1] + ourHero.y, exploded, screen)
            hero_group.remove(ourHero)
            hero_dead = True

        for explosion in exploded:
            explosion.draw()
            explosion.next_frame()

        # Global variables that need to be changed every frame
        time_to_cross = round(0.0026 * len(enemies) ** 2 + 0.0475 * len(enemies) + 2.94, 1)
        lag_multiplier = time_to_cross / 4.05

        # Text
        enemies_rem = f'{len(enemies)} enemies remaining'
        try:
            enemy_hp = f'{reduce(lambda x, y: x + y, [i.hp for i in enemies])} hp point to shoot'
        except TypeError:
            enemy_hp = f'{0} hp point to shoot'
        try:
            hero_hp = f'Hero HP: {ourHero.hp}'
        except NameError:
            hero_hp = f'Hero HP: {0}'
        base_lives = f'Base HP: {base}'
        weapon_text = f'Weapon: {weapon}'
        if limeted_lasers:
            laser_ammo_text = f'Laser Ammo: {laser_ammo}'
            show_text(350, 635, laser_ammo_text)
        if fireballs_in:
            fireball_ammo_text = f'Fireball ammo: {ceil(fire_ball_ammo)}'
            show_text(350, 660, fireball_ammo_text)
        show_text(10, 600, enemies_rem)
        show_text(10, 625, enemy_hp)
        show_text(10, 650, hero_hp)
        show_text(10, 675, base_lives)
        show_text(350, 610, weapon_text)

        try:
            won
        except NameError:
            if base <= 0 or not len(hero_group):
                won = False
                frames2 = frames
            elif len(enemies) <= 0:
                won = True
                frames2 = frames

        if frames == 0:
            laser_ammo = len(enemies) * lasers_p_enemy
            fire_ball_ammo = len(enemies) * fireball_p_enemy
        try:
            if frames - frames2 > 300:
                running = False
        except NameError:
            pass
        frames += 1
        pg.display.update()

    frames2 = 0
    running2 = True
    exit = False
    try:
        won
    except NameError:
        exit = True
    while running2 and not exit:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running2 = False
        if won == True:
            screen.fill((0, 255, 0))
            font = pg.font.Font('freesansbold.ttf', 50)
            you_won = font.render('All Enemies Destroyed', True, (0, 0, 255))
            screen.blit(you_won, (100, 275))
        else:
            screen.fill((255, 0, 0))
            font = pg.font.Font('freesansbold.ttf', 50)
            you_won = font.render('Game Over', True, (255, 255, 255))
            screen.blit(you_won, (300, 275))
        frames2 += 1
        if frames2 == 400:
            running2 = False
        pg.display.update()


# enemy_speedX, enemy_speedY, num_verticals, num_vs, num_rands, verticals_hp, vs_hp, rands_hp, base, hero_hp,
#          laser_cooldown, rockets_in=True, rocket_cooldown=10, limeted_lasers=False, lasers_p_enemy=9, fireballs_in=True,
#          fire_ball_cooldown=0.5, fireball_p_enemy=0.25, boosters=False, ammo_boost=7, hero_boost=300, damage_booster=1.5


if __name__ == '__main__':
    enemy_speedx = 0.9
    enemy_speedy = 0.1
    num_verts = 10
    num_vs = 0
    num_rands = 0
    vert_hp = 100
    vs_hp = 200
    rands_hp = 20
    base = 1
    hero_hp = 500
    laser_cooldown = 0.3
    rockets_in = True
    rocket_cooldown = 5
    limeted_lasers = True
    lasers_p_enemy = 3
    fireballs_in = True
    fire_ball_cooldown = 0.5
    fire_b_enemy = 10
    booster = True
    ammo_boost = 10
    hero_boost = 100
    level(enemy_speedx, enemy_speedy, num_verts, num_vs, num_rands, vert_hp, vs_hp, rands_hp, base, hero_hp,
          laser_cooldown, rockets_in, rocket_cooldown, limeted_lasers, lasers_p_enemy, fireballs_in, fire_ball_cooldown
          , fire_b_enemy, False)
