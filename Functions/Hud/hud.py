import pygame as py
from os import listdir
from os.path import join, isfile
from itertools import islice
from math import floor, sin, radians


class Letter:
    """Function for letter placing"""
    __slots__ = 'screen', 'letter_images', 'l_img_sizes', 'letter_height', 'l_img_width', 'l_img_offset_y', 'l_img_dict'

    def __init__(self, win: py.display, all_images):
        self.screen = win
        self.letter_images = dict(islice(all_images.items(), 11))
        self.l_img_sizes = {key: value for key, value in enumerate([w.get_size() for w in self.letter_images.values()])}
        self.letter_height = max([int(i[1]) for i in self.l_img_sizes.values()])
        self.l_img_width = {key: value[0] + 2 for key, value in self.l_img_sizes.items()}
        self.l_img_offset_y = {key: abs(self.letter_height - value[1]) for key, value in self.l_img_sizes.items()}
        self.l_img_dict = {'x': 0, '0': 1, '1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 9, '9': 10}

    def write_numbers(self, txt: str, x, y, size: float):
        """Write the numbers listed at a location"""
        for i in range(0, len(txt)):
            if txt[i] != ' ':
                letter = self.l_img_dict[txt[i]]
                self.screen.blit(py.transform.scale(self.letter_images[letter], (self.l_img_sizes[letter][0] * size,
                                                                                 self.l_img_sizes[letter][1] * size)),
                                 (x, y + self.l_img_offset_y[letter] * size))
                x += self.l_img_width[letter] * size
            else:
                x += 27 * size
        return x

    @staticmethod
    def color_change(frame) -> tuple:
        """Returns the color value from the given frame"""
        if isinstance(frame, str):
            # Preferably get max but any string works, returning the maximum value possible
            return 765,
        frame = round(frame)
        r, g, b = 0, 0, 0
        if 0 <= frame <= 255:
            b = 255 - frame
            r = frame
        elif 255 < frame <= 510:
            r = 255 - (frame - 255)
            g = frame - 255
        elif 510 < frame <= 765:
            g = 255 - (frame - 510)
            b = frame - 510
        else:
            raise KeyError(f'Number {frame} cannot be defined, number must be between 0 and 765')
        return r, g, b


class Planet_Hud(Letter):
    """Functions for displaying planet hud"""
    __slots__ = '__dict__'
    gem_count = 0

    def __init__(self, win: py.display, path, player):
        self.images = get_all_images(join(path, 'HUD'))
        super().__init__(win, self.images)
        self.sc_width, self.sc_height = self.screen.get_size()
        self.level_font = py.font.Font(None, self.sc_width // 26)
        self.menu_font = py.font.Font(None, self.sc_width // 33)
        self.world_font = py.font.Font(None, self.sc_width // 16)

        self.draw_level_pos, self.draw_menu_pos, self.draw_world_pos = [[0, 0] for _ in range(3)]

        self.coins = 0
        self.lives = 3.6
        self.player = player
        self.game_overs = 0
        self.world = None
        self.orig_world = None
        self.level = None
        self.level_progress = None
        self.font_col = '#000000'

    def find_font_color(self):
        """Finds the best contrasting color for the fonts (white or black)"""
        if self.world is None:
            self.font_col = '#000000'
            return None

        if self.world.col[0] == '#':
            color = self.world.col.lstrip('#')
            rgb = list(int(color[i:i + 2], 16) for i in (0, 2, 4))
            combined = sum(rgb) > 383
            if combined:
                self.font_col = '#000000'
            else:
                self.font_col = '#ffffff'

    def tick_level_pos(self, in_or_out):
        """Moves the level hud, in=True, out=False"""
        if in_or_out:
            if self.draw_level_pos[0] < 0:
                self.draw_level_pos[0] += 6
            else:
                self.draw_level_pos[0] = 0
        else:
            font_size = max((self.level_font.size(self.level.name)[0], 58))
            if self.draw_level_pos[0] > (font_size + 3 * 2) * -1:
                self.draw_level_pos[0] -= 6
            else:
                self.draw_level_pos[0] = (font_size + 3 * 2) * -1

    def tick_menu_pos(self, in_or_out):
        """Moves the menu hud, in=True, out=False"""
        if in_or_out:
            if self.draw_menu_pos[0] > 0:
                self.draw_menu_pos[0] -= 3
            else:
                self.draw_menu_pos[0] = 0
        else:
            if self.sc_width - self.sc_width / 6 + self.draw_menu_pos[0] < self.sc_width:
                self.draw_menu_pos[0] += 3

    def tick_world_pos(self, in_or_out):
        """Moves the world hud, in=True, out=False"""
        if in_or_out:
            if self.draw_world_pos[1] > 0:
                self.draw_world_pos[1] -= 2
            else:
                self.draw_world_pos[1] = 0
        else:
            font_size = self.world_font.size(self.world.name)[1]
            if self.draw_world_pos[1] < font_size + 16:
                self.draw_world_pos[1] += 2

    def draw(self):
        """Function for drawing hud images to the screen"""
        self.draw_level_at(self.draw_level_pos[0], self.draw_level_pos[1])
        self.menu_inputs(self.draw_menu_pos[0], self.draw_menu_pos[1])
        self.draw_world(self.draw_world_pos[0], self.draw_world_pos[1])

    def draw_level_at(self, x, y):
        """Draws the level hud to the screen"""
        font_size = (max((self.level_font.size(self.level.name)[0], 58)), self.level_font.size(self.level.name)[1])
        level_surf = py.Surface((font_size[0] + 3 * 2, font_size[1] * 2 + 3 * 3))
        level_surf.fill(self.world.col)
        level_surf.set_alpha(169)
        self.screen.blit(level_surf, (x, y))
        font_height = self.level_font.size(self.level.name)[1]
        font_width = self.level_font.size(self.level.id)[0]
        for text, add_y in ((self.level.name, 3), (self.level.id, font_height + 3 * 2)):
            level_title = self.level_font.render(text, True, self.font_col)
            level_rect = level_title.get_rect(topleft=(3 + x, add_y + y))
            self.screen.blit(level_title, level_rect)
        x = font_width + x + 6
        self.draw_level_info(x, y, font_height, self.level, add_y)

    def show_level(self, x, y, *, level, font, size, add_segs):
        """Shows level info in planet menu"""
        for i, text in enumerate((level.id, level.name)):
            txt = font.render(text, True, '#ffffff')
            rect = txt.get_rect(topleft=(x, y))
            self.screen.blit(txt, rect)
            x += add_segs[i]
        self.draw_level_info(x, y + 3, size + 4, level)

    def draw_level_info(self, x, y, font_height, level, add_y=0):
        for i, state, flag in ((0, 'green', 34), (1, 'red', 35)):
            if state in self.level_progress.level_data[level.id]['state']:
                self.screen.blit(py.transform.scale(self.images[flag], (font_height, font_height)),
                                 (x, add_y + y))
                x += font_height + 2

        y = add_y + y
        prev_idx = 0
        for img_idx in self.level_progress.level_data[level.id]['collected']:
            if not 12 <= img_idx <= 15:
                continue
            if prev_idx == img_idx:
                x += font_height / 3
            elif prev_idx == 0:
                pass
            else:
                x += font_height + 1
            proportion = self.images[img_idx].get_size()
            proportion = proportion[1] / proportion[0]
            self.screen.blit(py.transform.scale(self.images[img_idx], (font_height, font_height * proportion)), (x, y))
            prev_idx = img_idx

    def menu_inputs(self, x, y):
        """Draws menu inputs to the screen"""
        font_size = self.menu_font.size(' Controls ')
        menu_surf = py.Surface((font_size[0] + font_size[1] + 5 * 3, font_size[1] * 2 + 3 * 3))
        menu_surf.fill('#E0e0df')
        menu_surf.set_alpha(130)
        x, y = (self.sc_width - self.sc_width / 6 + x, self.sc_height / 32 + y)
        self.screen.blit(menu_surf, (x, y))
        menu_rect = menu_surf.get_rect(topleft=(x, y))
        add_y = 3
        for key, text in (('0', 'Menu'), ('9', 'Controls')):
            text_surf = self.menu_font.render(key, True, '#000000')
            text_pos = (menu_rect.x + 5 + font_size[1] / 2, menu_rect.y + add_y + font_size[1] / 2)
            text_rect = text_surf.get_rect(center=(text_pos[0], text_pos[1] - 2))
            py.draw.circle(self.screen, '#ffffff', text_pos, font_size[1] / 2, 0)
            self.screen.blit(text_surf, text_rect)

            text_surf = self.menu_font.render(text, True, '#ffffff')
            text_rect = text_surf.get_rect(topleft=(text_pos[0] + font_size[1] / 2 + 3, text_pos[1] - font_size[1] / 2))
            self.screen.blit(text_surf, text_rect)
            add_y += self.menu_font.size(text)[1] + 3

    def draw_world(self, x, y):
        """Draws the world hud to the screen"""
        font_size = self.world_font.size(self.world.name)[1]
        world_surf = py.Surface((self.sc_width, font_size + 16))
        world_surf.fill(self.world.col)
        world_surf.set_alpha(169)
        world_rect = world_surf.get_rect(topleft=(0 + x, self.sc_height - font_size - 16 + y))
        self.screen.blit(world_surf, world_rect)

        world_text = self.world_font.render(self.world.name, True, self.font_col)
        x, y = world_rect.x, world_rect.y + world_rect.height / 2 - world_text.get_size()[1] / 2
        text_rect = world_text.get_rect(topleft=(x + 5, y))
        self.screen.blit(world_text, text_rect)

        x = world_rect.centerx
        self.draw_player_lives(x, y, world_rect.height * 0.6, self.lives)

    def draw_player_lives(self, x, y, img_width, lives):
        """Draws the player lives hud"""
        img_dict = {1: 28, 2: 30, 3: 32}
        self.screen.blit(py.transform.scale(self.images[img_dict[self.player]], (img_width, img_width)), (x, y))
        ix = self.write_numbers(f'x{floor(lives)}', x + img_width - img_width // 12,
                                y + img_width - self.letter_height * (img_width / 76),
                                img_width / (2 * self.letter_height))
        # Hearts
        lives = int(round(10 * (lives - floor(lives))))
        ix += self.sc_width // 66
        for live in range(floor(lives / 2)):
            self.screen.blit(py.transform.scale(self.images[17], (img_width / 2, img_width / 2)),
                             (ix, y + img_width / 2))
            ix += 2 + img_width / 2
        if lives % 2 == 1 and lives > 0:
            self.screen.blit(py.transform.scale(self.images[18], (img_width / 2, img_width / 2)),
                             (ix, y + img_width / 2))

    def draw_gem_count(self, x, y, img_width):
        for img_idx in (12, 13, 14, 15):
            x += img_width / 3
            proportion = self.images[img_idx].get_size()
            proportion = proportion[1] / proportion[0]
            self.screen.blit(py.transform.scale(self.images[img_idx], (img_width, img_width * proportion)), (x, y))
        self.write_numbers(f'x{self.gem_count}', x + img_width - img_width // 12,
                           y + img_width - self.letter_height * (img_width / 76),
                           img_width / (2 * self.letter_height))


class Level_Hud(Letter):
    """Functions for displaying hud in levels"""
    __slots__ = 'images', 'img_sizes', 'sc_width', 'sc_height', 'img_size', 'level_font', 'coin_jump', 'coin_y', \
                'player', 'player_cls', 'coins', 'timer', 'r_timer', 'score', 'score_for_life', 'lives', 'collected', \
                'save_collected', 'temp', 'sc_particle_func'
    orig_score_for_life = [10000, 50000, 100000, 200000, 400000, 800000, 1000000, 2000000, 4000000, 8000000]
    bounce_counter = 0

    def __init__(self, win: py.display, path, main_path, *, player_cls, sc_particle_func):
        """Initializes level hud settings"""
        self.images = get_all_images(join(path, 'HUD'))
        super().__init__(win, self.images)
        self.img_sizes = {key: value for key, value in enumerate([w.get_size() for w in self.images.values()])}
        self.sc_width, self.sc_height = self.screen.get_size()
        self.img_size = self.sc_width // 17
        self.level_font = py.font.Font(join(main_path, 'Font', 'nasalization.ttf'), self.img_size)
        self.coin_jump = 0
        self.coin_y = 0

        self.player = 1
        self.player_cls = player_cls
        self.coins = 0
        self.timer = 300
        self.r_timer = py.time.get_ticks()
        self.score = 0
        self.score_for_life = self.orig_score_for_life.copy()
        self.lives = 3
        self.collected = []
        self.save_collected = []
        self.temp = [0, True, 0]
        self.sc_particle_func = sc_particle_func

    def reset_hud(self):
        """Resets hud settings"""
        self.score, self.timer, self.temp, self.collected = 0, 300, [0, True, 0], list(self.save_collected)
        self.__class__.bounce_counter = 0

    def draw(self):
        """Runs the functions and paints them on the screen"""
        x, y, img_width = self.paint_player()
        space, coin_y = self.paint_coins(x, y, img_width)
        self.show_collected(x, coin_y, img_width, space)
        x = self.display_timer(y, img_width)
        self.display_score(x, y, img_width, space)
        self.run_coin_jump()
        if self.temp[0] > 0:
            self.display_complete()

    def paint_player(self):
        """Paint player hud onto screen"""
        img_dict = {1: 28, 2: 30, 3: 32}
        img_width = self.img_size / 1.2
        x, y = self.sc_width // 26, self.sc_height // 33
        self.screen.blit(py.transform.scale(self.images[img_dict[self.player]], (img_width, img_width)), (x, y))
        ix = self.write_numbers(f'x{self.lives}', x + img_width - img_width // 12,
                                y + img_width - self.letter_height * (img_width / 76),
                                img_width / (2 * self.letter_height))
        # Hearts
        ix += self.sc_width // 66
        for live in range(floor(self.player_cls.lives / 2)):
            self.screen.blit(py.transform.scale(self.images[17], (img_width / 2, img_width / 2)),
                             (ix, y + img_width / 2))
            ix += 2 + img_width / 2
        if self.player_cls.lives % 2 == 1 and self.player_cls.lives > 0:
            self.screen.blit(py.transform.scale(self.images[18], (img_width / 2, img_width / 2)),
                             (ix, y + img_width / 2))
        return x, y, img_width

    def check_player_lives(self):
        """Check if player lives exceeded the 99 limit or 6 hearts limit"""
        if self.lives > 99:
            self.lives = 99
        if self.player_cls.lives > 6 and self.lives >= 99:
            self.player_cls.lives = 6
            return

        if self.player_cls.lives > 6:
            self.lives += 1
            self.player_cls.lives -= 6

    def paint_coins(self, player_x, player_y, player_img_width, from_planet_menu=False):
        """Paint coins hud onto screen"""
        # 100 Coins -> 1 Live
        if self.coins > 100:
            self.lives += 1
            self.check_player_lives()
            self.coins -= 100

        space = self.sc_height // 78
        x, img_width = player_x, player_img_width - 10
        y = player_y if from_planet_menu else player_y + player_img_width + space
        self.screen.blit(py.transform.scale(self.images[11], (img_width, img_width)), (x, y))
        self.write_numbers(f'x{self.coins}', x + img_width - img_width / 30, y + img_width - self.letter_height *
                           (img_width / 46 - self.coin_y), img_width / (1.2 * self.letter_height))
        return space, y

    def show_collected(self, x, y, img_width, space):
        orig_x, y, img_width = x, y + img_width + space, img_width / 2
        if sorted(self.collected) != self.collected:
            self.collected = sorted(self.collected)
        prev_idx = 0

        for img_idx in self.collected:
            if prev_idx == img_idx:
                x += img_width / 3
            elif prev_idx == 0:
                pass
            else:
                x += img_width + space / 2
            if x > self.sc_width / 5.6:
                y += img_width + space
                x = orig_x
            proportion = self.images[img_idx].get_size()
            proportion = proportion[1] / proportion[0]
            self.screen.blit(py.transform.scale(self.images[img_idx], (img_width, img_width * proportion)), (x, y))
            prev_idx = img_idx

    def run_coin_jump(self):
        """Animates the coin counter"""
        if self.coin_jump > 0:
            self.coin_y = round(-0.3 * sin(radians(self.coin_jump)), 4)
            self.coin_jump -= 45
        else:
            self.coin_jump = 0
            self.coin_y = 0

    def animate_coin_jump(self):
        """Makes it easier to read in the future"""
        self.coin_jump = 90

    def display_timer(self, y, img_width):
        """Displays the timer onto the screen"""
        time = str(self.timer).zfill(3)
        x = self.sc_width - self.sc_width // 6
        self.screen.blit(py.transform.scale(self.images[33], (img_width, img_width)), (x, y))
        self.write_numbers(time, x + img_width + img_width / 5, y + img_width - self.letter_height *
                           (img_width / 45), img_width / (1.2 * self.letter_height))
        return x

    def run_timer(self):
        """Ticks the timer"""
        time_passed = floor((py.time.get_ticks() - self.r_timer) / 1000)
        if time_passed >= 1:
            self.timer -= time_passed if time_passed < 2 else 1
            self.r_timer = py.time.get_ticks()
            if self.timer < 0:
                self.timer = 0
                self.player_cls.lives = 0
                self.player_cls.frame = 0

    def display_score(self, x, y, img_width, space):
        """Displays the score onto the screen"""
        if self.score >= self.score_for_life[0]:
            self.lives += 1
            self.check_player_lives()
            del self.score_for_life[0]
        score = str(self.score).zfill(7)
        self.write_numbers(score, x, y + img_width + space, img_width / (1.75 * self.letter_height))

    def update_score(self, *, score=None, pos=None):
        """Updates score based on enemy killing through player jumps"""
        if not pos:
            pos = self.player_cls.x, self.player_cls.y
        if score:
            self.score += score
            self.sc_particle_func(pos[0], pos[1], score)
            return
        if self.__class__.bounce_counter >= 8:
            self.player_cls.lives += 1
            self.check_player_lives()
            self.sc_particle_func(self.player_cls.x, self.player_cls.y, '+1H')
            return

        #                   1, 2, 4 or 8                            How many zeros after
        add_score = 2 ** (self.__class__.bounce_counter % 4) * 10 ** (floor(self.__class__.bounce_counter / 4) + 2)
        self.__class__.bounce_counter = min(self.__class__.bounce_counter + 1, 8)
        self.score += add_score
        self.sc_particle_func(pos[0], pos[1], add_score)

    def display_time_up(self):
        """Displays time's up text"""
        text_surf = self.level_font.render("TIME'S UP...", True, '#ff2020')
        text_rect = text_surf.get_rect(center=(self.sc_width / 2, self.sc_height / 2))
        self.screen.blit(text_surf, text_rect)

    def display_complete(self):
        """Displays level complete"""
        color_switch = 5
        text_surf = self.level_font.render('LEVEL COMPLETE!', True,
                                           (self.color_change((self.temp[0] / 15) * color_switch)))
        size_x, _ = text_surf.get_size()
        x = self.temp[0] if self.temp[0] < (self.sc_width + size_x) / 2 and self.temp[1] \
            else (self.sc_width + size_x) / 2
        text_rect = text_surf.get_rect(center=(x - size_x / 2, self.sc_height / 2))
        self.screen.blit(text_surf, text_rect)
        if (self.temp[0] / 15) * color_switch > self.color_change('')[0] - color_switch:
            self.temp[0] = 1
            self.temp[1] = False
        else:
            self.temp[0] += 15

    def run_down_timer(self):
        """Runs down the timer"""
        if self.temp[0] < 1:
            self.temp[0] = 1
        for _ in range(2):
            if self.timer > 0:
                self.timer -= 1
                self.score += 100
            else:
                if self.temp[2] > 40 * 2:
                    return True
                self.temp[2] += 1
        return False


def get_all_images(path):
    """Gets all the images from the HUD folder"""
    return {key: load(join(path, value)) for key, value in enumerate(
        [f for f in sorted(listdir(path)) if isfile(join(path, f))])}


def load(loc):
    """Loads in images from a location"""
    return py.image.load(loc).convert_alpha()

#
# if __name__ == '__main__':
#     py.init()
#     screen = py.display.set_mode((500, 500))
#     py.display.set_caption("Hud Test")
#     clock = py.time.Clock()
#     l_hud = Level_Hud(screen, '', None)
#
#     run = True
#     j = 0
#     while run:
#         screen.fill((25, 25, 25))
#         l_hud.draw()
#         for event in py.event.get():
#             if event.type == py.QUIT:
#                 run = False
#         py.display.update()
#         clock.tick(60)
#         j += 1
#     py.quit()
