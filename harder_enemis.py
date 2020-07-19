import math
import random
from time import perf_counter

import pygame as pg

import template_level as tl

harder_enemy_pics = {'base': pg.image.load(f'{tl.PIC_PATH}ufo.png'),
                     'lasers': pg.image.load(f'{tl.PIC_PATH}ufo.png'),
                     'invisible': pg.image.load(f'{tl.PIC_PATH}transparent.png'),
                     'fireballs': pg.image.load(f'{tl.PIC_PATH}ufo.png')
                     }

harder_enemy_group = pg.sprite.Group()


class HarderEnemy(pg.sprite.Sprite):
    def __init__(self, descent, hp, enemyX_change, enemyY_change, powerup, timer, enemy_group, laser_arr, fireball_arr,
                 time_in_state=0.1):
        # Power up can be lasers, base, or invisible
        self.descent = descent
        self.hp = hp
        self.enemyX_change = enemyX_change
        self.enemyY_change = enemyY_change
        self.powerup = powerup
        self.timer = timer
        self.states = ['base'] + [powerup]
        self.time = perf_counter() % self.timer
        self.frame = 0
        self.state = self.states[self.frame]
        self.time_in_state = time_in_state
        self.rect = harder_enemy_pics[self.state].get_rect()
        self.y = random.randrange(tl.spawn_min, tl.spawn_max)
        self.ammo = 1
        if not tl.possible_x:
            possible_x = list(range(64, 801, 65))[:-1]
            tl.spawn_min -= tl.wave_distance
            tl.spawn_max -= tl.wave_distance
            self.y = random.randrange(tl.spawn_min, tl.spawn_max)
        self.x = random.choice(tl.possible_x)
        self.enemy_group = enemy_group
        self.laser_arr = laser_arr
        self.fireball_arr = fireball_arr
        pg.sprite.Sprite.__init__(self, enemy_group)

    def draw(self, screen):
        screen.blit(harder_enemy_pics[self.state], (self.x, self.y))

    def update(self):
        self.time = perf_counter() % self.timer
        if self.time <= self.time_in_state:
            self.frame = 1
            if self.state == 'lasers' and self.ammo:
                laser = tl.Laser(self.x + 32, self.y + 64, self.laser_arr)
                self.laser_arr.append(laser)
                self.ammo = 0
            elif self.ammo and self.state == 'fireballs':
                [tl.Fireball(self.x, self.y, angle, self.fireball_arr) for angle in range(90, 271, 30)]
                self.ammo = 0
        else:
            self.ammo = 1
            self.frame = 0
        self.state = self.states[self.frame]
        self.rect = harder_enemy_pics[self.state].get_rect()
        self.x, self.y, self.enemyX_change = self.descent(self.x, self.y, self.enemyX_change, self.enemyY_change)


def Harderlevel(enemy_speedX, enemy_speedY, num_transparents, num_fireballs, num_lasers, enemy_hp, hero_hp,
                laser_cooldowns, rockets_in=True, rocket_cooldown=10, limeted_lasers=False, lasers_p_enemy=9,
                fireballs_in=True,
                fire_ball_cooldowns=[0.5, 3], fireball_p_enemy=0.25, boosters=False, ammo_boost=7, hero_boost=300,
                speed_mul=1.5):
    # create screen
    screen = pg.display.set_mode((800, 700))
    # pg.mixer.music.play(-1)
    # Global variables
    base = 1
    rocketCooldown = -rocket_cooldown
    rocket_fired_tm = 0
    lazerCooldown = -laser_cooldowns[0]
    laser_fired_tm = 0
    fireball_fired_tm = 0
    fireballCooldown = -fire_ball_cooldowns[0]
    running = True
    weapons = ['lazer', 'rocket', 'fireball']
    weapon = weapons[0]
    enemies = []
    time_to_cross = round(0.0026 * len(enemies) ** 2 + 0.0475 * len(enemies) + 2.94, 1)
    lag_multiplier = time_to_cross / 4.05
    booster_speed_multiplier = 1
    hero_dead = False
    if limeted_lasers:
        laser_ammo = lasers_p_enemy * len(enemies)
    else:
        laser_ammo = 1
    fire_ball_ammo = fireball_p_enemy * len(enemies)

    # Lazer stuff
    lasers_fired, lasers_fired_bad = [], []
    rockets_fired = []
    weapons_n_aliens = pg.sprite.Group()
    enemies = pg.sprite.Group()
    # Possible enemy spawning position
    # Single group hero
    hero_group = pg.sprite.GroupSingle()
    # Booster group
    if boosters:
        booster_group = pg.sprite.Group()
    # Explosion group
    exploded = pg.sprite.Group()
    # Fireball Groups
    good_fireballs = pg.sprite.Group()
    bad_fireballs = pg.sprite.Group()

    # Create 5 enemies
    [HarderEnemy(random.choice([tl.y_descent, tl.v_descent, tl.random_descent]), enemy_hp, enemy_speedX, enemy_speedY,
                 'lasers', laser_cooldowns[1], enemies, lasers_fired_bad, bad_fireballs) for _ in range(num_lasers)]
    [HarderEnemy(random.choice([tl.y_descent, tl.v_descent, tl.random_descent]), enemy_hp, enemy_speedX, enemy_speedY,
                 'invisible', 5, enemies, lasers_fired_bad, bad_fireballs, 4) for _ in range(num_transparents)]
    [HarderEnemy(random.choice([tl.y_descent, tl.v_descent, tl.random_descent]), enemy_hp, enemy_speedX, enemy_speedY,
                 'fireballs', fire_ball_cooldowns[1], enemies, lasers_fired_bad, bad_fireballs) for _ in
     range(num_fireballs)]

    ourHero = tl.Hero(370, 480, hero_hp, hero_group)

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
        screen.blit(tl.background, (0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
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
            a = tl.Laser(ourHero.x + 27, ourHero.y, lasers_fired)
            a.launch_lazer()
            laser_fired_tm = perf_counter()
            lazerCooldown = laser_cooldowns[0]
            if limeted_lasers:
                laser_ammo -= 1
            # bulletSound = tl.mixer.Sound(f'{tl.SOUND_PATH}laser.wav')
            # bulletSound.play()
        elif keys[pg.K_SPACE] and perf_counter() - rocket_fired_tm > rocketCooldown and weapon == 'rocket':
            distances = [tl.distance(i.x, i.y, ourHero.x, ourHero.y) for i in enemies]
            if distances:
                c = sorted(distances.copy())[0]
            target = [i for i in weapons_n_aliens if type(i) == HarderEnemy][distances.index(c)]
            b = tl.Rocket(ourHero.x + 27, ourHero.y + 35, rockets_fired, screen)
            b.launch_rocket()
            rocket_fired_tm = perf_counter()
            rocketCooldown = rocket_cooldown
        elif keys[
            pg.K_SPACE] and perf_counter() - fireball_fired_tm > fireballCooldown and weapon == 'fireball' and fire_ball_ammo > 0:
            [tl.Fireball(ourHero.x, ourHero.y, ang, good_fireballs) for ang in range(0, 91, 30)]
            [tl.Fireball(ourHero.x, ourHero.y, ang, good_fireballs) for ang in range(270, 360, 30)]
            fireball_fired_tm = perf_counter()
            fireballCooldown = fire_ball_cooldowns[0]
            fire_ball_ammo -= 1

        if fireballs_in:
            [i.update(2) for i in good_fireballs]
            [good_fireballs.remove(i) for i in good_fireballs if i.y < 30 or i.x < 0 or i.x > 800]
            [i.draw(screen) for i in good_fireballs]

        [i.update(2) for i in bad_fireballs]
        [bad_fireballs.remove(i) for i in bad_fireballs if i.y > 480 or i.x < 0 or i.x > 800]
        [i.draw(screen) for i in bad_fireballs]

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
        [i.update_lazer(-2) for i in lasers_fired_bad]
        [lasers_fired.remove(i) for i in lasers_fired if i.y < 30]
        [lasers_fired_bad.remove(i) for i in lasers_fired_bad if i.y > 480]
        [i.draw_lazer(screen) for i in lasers_fired + lasers_fired_bad]

        [hero.draw(screen) for hero in hero_group]

        # Enemy checking / Drawing loop
        for enemy in enemies:
            enemy.draw(screen)
            enemy.update()
            center_x = enemy.rect.center[0] + enemy.x
            center_y = enemy.rect.center[1] + enemy.y
            radius = tl.distance(center_x, center_y, enemy.x, enemy.y)
            new_enemies = enemies.copy()
            new_enemies.remove(enemy)
            for ufo in new_enemies:
                if tl.distance(center_x, center_y, ufo.rect.center[0] + ufo.x, enemy.rect.center[1] + ufo.y) < radius:
                    enemy.enemyX_change *= -1
                    ufo.enemyX_change *= -1
            for l in lasers_fired + rockets_fired + list(good_fireballs):
                if tl.distance(center_x, center_y, l.x, l.y) < radius:
                    if type(l) == tl.Laser:
                        lasers_fired.remove(l)
                        enemy.hp -= 100
                    elif type(l) == tl.Fireball:
                        good_fireballs.remove(l)
                        enemy.hp -= 50
                    elif type(l) == tl.Fireball:
                        rockets_fired.remove(l)
                        enemy.hp -= 400
                    weapons_n_aliens.remove(l)
                    tl.Explosion(25, center_x, center_y, exploded, screen)
            if enemy.hp <= 0 or enemy.y >= 491:
                enemies.remove(enemy)
                weapons_n_aliens.remove(enemy)
                tl.Explosion(100, center_x, center_y, exploded, screen)
                if boosters:
                    tl.Booster(center_x, center_y, booster_group)
            if enemy.y >= 490:
                base -= 1
                base = abs(base)
            if tl.distance(center_x, center_y, ourHero.rect.center[0], ourHero.rect.center[1]) < radius:
                tl.Explosion(50, ourHero.x, ourHero.y, exploded, screen)
                enemies.remove(enemy)
                weapons_n_aliens.remove(enemy)
                ourHero.hp -= 500
        # Booster is_hit loop
        if boosters:
            for booster in booster_group:
                if tl.distance(booster.x, booster.y, ourHero.x, ourHero.y) < 32 * 1.42:
                    booster_group.remove(booster)
                    effect = booster.apply_boost(ammo_boost, speed_mul)
                    laser_ammo += effect[0]
                    fire_ball_ammo += effect[1]
                    ourHero.hp += effect[2]
                    base += effect[3]
                    if effect[4]:
                        booster_speed_multiplier *= effect[4]

        if ourHero.hp <= 0 and not hero_dead:
            tl.Explosion(100, ourHero.rect.center[0] + ourHero.x, ourHero.rect.center[1] + ourHero.y, exploded, screen)
            hero_group.remove(ourHero)
            hero_dead = True
        # Checking if the enemy is hitting the player
        for laser in lasers_fired_bad:
            if laser.rect.colliderect(ourHero.rect):
                lasers_fired_bad.remove(laser)
                tl.Explosion(35, ourHero.x, ourHero.y, exploded, screen)
                ourHero.hp -= 150

        for fireball in bad_fireballs:
            if fireball.rect.colliderect(ourHero.rect):
                bad_fireballs.remove(fireball)
                tl.Explosion(35, ourHero.x, ourHero.y, exploded, screen)
                ourHero.hp -= 100

        for explosion in exploded:
            explosion.draw()
            explosion.next_frame()

        # Global variables that need to be changed every frame
        time_to_cross = round(0.0026 * len(enemies) ** 2 + 0.0475 * len(enemies) + 2.94, 1)
        lag_multiplier = time_to_cross / 4.05

        # Text
        enemies_rem = f'{len(enemies)} enemies remaining'
        try:
            enemy_hp = f'{tl.reduce(lambda x, y: x + y, [i.hp for i in enemies])} hp point to shoot'
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
            fireball_ammo_text = f'Fireball ammo: {math.ceil(fire_ball_ammo)}'
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


# enemy_speedX, enemy_speedY, num_transparents, num_fireballs, num_lasers, enemy_hp, hero_hp,
#                laser_cooldowns, rockets_in=True, rocket_cooldown=10, limeted_lasers=False, lasers_p_enemy=9, fireballs_in=True,
#                fire_ball_cooldown=0.5, fireball_p_enemy=0.25, boosters=False, ammo_boost=7, hero_boost=300, speed_mul=1.5

Harderlevel(0.9, 0.07, 0, 3, 0, 100, 560, [0.5, 3])
