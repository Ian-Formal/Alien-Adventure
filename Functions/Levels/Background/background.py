import pygame as py
from os import listdir
from os.path import join, isfile


class Bg:
    """Functions for one singular background image"""
    __slots__ = 'length', 'height', 'image', 'x', 'y', 'draw_x', 'draw_y'

    def __init__(self, image, sc_height, x):
        """Initializes background settings"""
        # IMPORTANT! Make sure that these backgrounds are 1024x512 sized, or it will look weird
        self.length, self.height = 1024, 512
        self.image = py.transform.scale(image, (self.length, self.height))
        self.x, self.y = x, sc_height - self.image.get_height()
        self.draw_x, self.draw_y = self.x, self.y

    def display(self, win: py.display):
        """Displays the background onto the screen"""
        win.blit(self.image, (self.draw_x, self.draw_y))


class Background:
    """Background main functions"""
    __slots__ = 'screen', 'sc_width', 'sc_height', 'path', 'all_backgrounds', 'backgrounds'

    def __init__(self, win: py.display, path):
        """Initializes background info"""
        self.screen = win
        self.sc_width, self.sc_height = self.screen.get_size()
        self.path = join(path, 'Levels', 'Background', 'bg_art')
        self.all_backgrounds = {key: load(join(self.path, value)) for key, value in
                                enumerate([f for f in sorted(listdir(self.path)) if isfile(join(self.path, f))])}
        self.backgrounds = {}

    def get_all_backgrounds(self, img_size: tuple, start_pos: tuple) -> dict:
        """Collects all backgrounds, returning them"""
        all_backgrounds = {}
        x, y = start_pos
        for background in self.all_backgrounds.keys():
            all_backgrounds[background] = Bg(self.all_backgrounds[background], self.sc_height, 0)
            all_backgrounds[background].x = x + (img_size[0] + 4) * (background % 2 if background != 2 else 0)
            all_backgrounds[background].y = y + (img_size[1] + 4) * (0 if background < 2 else 1)
            all_backgrounds[background].image = py.transform.scale(all_backgrounds[background].image, img_size)
        return all_backgrounds

    def init_background(self, background):
        """Set up the background"""
        self.backgrounds = {}
        if isinstance(background, str) or isinstance(background, tuple):
            self.backgrounds['col'] = background
            return None
        elif background is None:
            self.backgrounds['col'] = '#191919'
            return None

        if background != 0:
            self.backgrounds = {key: Bg(self.all_backgrounds[background], self.sc_height, key * 1024)
                                for key in range(0, 2)}
        else:
            self.backgrounds = {key: Bg(self.all_backgrounds[background], self.sc_height,
                                        (key % 2 if key != 2 else 0) * 1024) for key in range(0, 4)}
            for i in range(2, 4):
                self.backgrounds[i].y = self.sc_height - self.backgrounds[i].image.get_height() * 2
        col_dict = {0: '#869595', 1: '#d0f4f7', 2: '#d0f4f7', 3: '#7ab71e'}
        self.backgrounds['col'] = col_dict[background]

    def draw(self, cam_x, cam_y):
        """Draws the background onto the screen"""
        self.screen.fill(self.backgrounds['col'])
        for background in self.backgrounds.keys():
            if not isinstance(background, int):
                continue
            x = self.backgrounds[background].x - cam_x / 2
            self.backgrounds[background].draw_x = x % (self.backgrounds[background].length * 2) - \
                self.backgrounds[background].length
            if len(self.backgrounds) < 4:
                self.backgrounds[background].draw_y = self.backgrounds[background].y - cam_y / 2
            else:
                y = self.backgrounds[background].y - cam_y / 2
                self.backgrounds[background].draw_y = y % (self.backgrounds[background].height * 2) - \
                    self.backgrounds[background].height
            self.backgrounds[background].display(self.screen)


def load(loc):
    """Loads in images from a location"""
    return py.image.load(loc).convert_alpha()


if __name__ == '__main__':
    pass
