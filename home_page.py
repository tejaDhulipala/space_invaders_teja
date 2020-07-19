import pygame as pg

from template_level import level

# Initialize pygame
pg.init()
# Pic Path
PIC_PATH = "pics/"
# Home page photo
home_page_img = pg.image.load(f'{PIC_PATH}home_page.png')
# running variable ( says whether game loop is running or not )
running = True
# Screen
screen = pg.display.set_mode((800, 600))
# Button Array
buttons = []
# Guide picture
guide_pic = pg.image.load(f'{PIC_PATH}guide.png')
# Home button_pic
home_button_pic = pg.image.load(f'{PIC_PATH}home_button.png')
# locks
unlocked_lock = pg.image.load(f'{PIC_PATH}unlocked_level.png')
locked_lock = pg.image.load(f'{PIC_PATH}locked_lock.png')
locked_lock = pg.transform.scale(locked_lock, (64, 64))
unlocked_lock = pg.transform.scale(unlocked_lock, (64, 64))
# Levels
levels = [
    [0.9, 0.1, 0, 3, 0, 0, 100, 0, 1, 500, 0.3, level, False],
    [0.9, 0.1, 0, 3, 0, 0, 100, 0, 1, 500, 0.3, level, True]
]


# Button class
class Button:
    def __init__(self, topleft, bottomright, scrolled_over, clicked, image=False, text=False, font=False,
                 fontsize=False, fontcolor=(0, 0, 0)):
        self.topleft = topleft
        self.bottomright = bottomright
        self.scrolled_over = scrolled_over
        self.clicked = clicked
        self.image = image
        self.text = text
        self.font = font
        self.fontsize = fontsize
        self.fontcolor = fontcolor
        buttons.append(self)

    def draw(self):
        if self.image:
            screen.blit(self.image, (self.topleft[0], self.topleft[1]))
        if self.text:
            font = pg.font.Font(self.font, self.fontsize)
            img = font.render(self.text, True, self.fontcolor)
            screen.blit(img, list(map(lambda x: x + 10, self.topleft)))
        else:
            pass

    def Is_over(self, x, y):
        if self.topleft[0] <= x <= self.bottomright[0] and self.topleft[1] <= y <= self.bottomright[1]:
            return True
        return False

    def attempt_click(self, Userx, Usery):
        if self.Is_over(Userx, Usery):
            self.clicked()
            return True
        return False


class level_icon(Button):
    def __init__(self, topleft, bottomright, locked, number):
        self.topleft = topleft
        self.bottomright = bottomright
        self.locked = locked
        self.number = number
        if locked:
            super().__init__(topleft, bottomright, lambda: 0, lambda: 0, locked_lock)
        else:
            attributes = levels[number - 1][:-2]
            print(attributes)
            super().__init__(topleft, bottomright, lambda: 0, lambda: levels[number - 1][-2](*attributes),
                             unlocked_lock, str(number),
                             'freesansbold.ttf', 50)


# Guide button callback
def guide():
    global running
    running_guide = True

    # Home button
    def go_home():
        nonlocal running_guide
        running_guide = False

    home_button = Button((0, 0), (100, 100), lambda: 0, go_home, home_button_pic)
    # Game loop
    while running_guide:
        screen.fill((0, 0, 0))
        for event in pg.event.get():
            # Checking if the user pressed the exit button
            if event.type == pg.QUIT:
                running_guide, running = False, False
            elif event.type == pg.MOUSEBUTTONUP:
                mouse_pos = pg.mouse.get_pos()
                home_button.attempt_click(mouse_pos[0], mouse_pos[1])
        screen.blit(guide_pic, (0, 0))
        for button in buttons:
            button.draw()
        pg.display.update()


def levels_page():
    global running
    running_levels = True

    # Home button
    def go_home():
        nonlocal running_levels
        running_levels = False

    home_button = Button((0, 0), (100, 100), lambda: 0, go_home, home_button_pic)
    for level in levels:
        x = ((levels.index(level) + 1) % 5) * 150
        y = ((levels.index(level) + 1) // 5) * 150
        locked = level[-1]
        level_button = level_icon([x, y], [x + 128, y + 111], locked, levels.index(level) + 1)
    # Game loop
    while running_levels:
        screen.fill((0, 0, 0))
        for event in pg.event.get():
            # Checking if the user pressed the exit button
            if event.type == pg.QUIT:
                running_levels, running = False, False
            elif event.type == pg.MOUSEBUTTONUP:
                mouse_pos = pg.mouse.get_pos()
                home_button.attempt_click(mouse_pos[0], mouse_pos[1])
                for b in buttons:
                    b.attempt_click(mouse_pos[0], mouse_pos[1])
        for button in buttons:
            button.draw()
            if not running_levels and type(button) == level_icon:
                buttons.remove(button)
        pg.display.update()


# Campaign button
campaign_button = Button((287, 301), (500, 350), lambda: 0, levels_page)
# Waves Button
waves_button = Button((291, 381), (485, 428), lambda: 0, lambda: print('Endless, you want?'))
# Guide Button
guide_button = Button((294, 468), (479, 513), lambda: 0, guide)
# Shop Button
shop_button = Button((8, 517), (222, 590), lambda: 0, lambda: print('Come back when you have money'))
# Home Page loop
while running:
    # Putting the background
    screen.fill((0, 0, 0))
    screen.blit(home_page_img, (0, 0))
    # Event loop
    for event in pg.event.get():
        # Checking if the user pressed the exit button
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONUP:
            mouse_pos = pg.mouse.get_pos()
            for button in buttons:
                button.attempt_click(mouse_pos[0], mouse_pos[1])

    for button in buttons:
        button.draw()
    # Updating the screen every iteration of the game loop
    pg.display.update()
