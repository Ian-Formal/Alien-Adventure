import pygame as py
from os import listdir
from os.path import isfile, join
try:
    from . import tile_settings as ts
except ImportError:
    import tile_settings as ts

"""This file sorts out all tile costumes, collisions and properties"""


class Tile_Index_Properties:
    """Class for tile properties (read-only)"""
    __slots__ = 'standard_tile_size', 'scale', 'image', 'blank', 'index', 'collision1', 'collision2', 'category', \
                'img_width', 'img_height', 'tile_space'

    def __init__(self, image, index: int):
        self.standard_tile_size = 32
        self.scale = self.standard_tile_size/70  # Testing Only

        standard_img_width, standard_img_height = 70, 70
        if image:
            self.image = image
            self.blank = False
        else:
            self.image = None
            self.blank = True
        self.index = index

        data = ts.tile_settings[self.index]
        self.collision1 = data[0]
        if data[1][:1].isupper():
            self.collision2 = self.collision1
            self.category = data[1]
        else:
            self.collision2 = data[1]
            self.category = data[2]
        if len(data) > 3:
            self.img_width, self.img_height = data[2][0], data[2][1]
            self.tile_space = (data[3][0], data[3][1])
        else:
            self.img_width, self.img_height = standard_img_width, standard_img_height
            self.tile_space = (1, 1)

    def display(self, win: py.display, x: int, y: int):
        """Displays the tile on screen, this function will not be used"""
        if not self.blank:
            win.blit(py.transform.scale(self.image, (self.scale * self.img_width, self.scale * self.img_height)),
                     (x, y))


class All_Tiles:
    """Class storing all tile values, loading all tile data"""
    __slots__ = 'images', 'tile', 'img_count', 'path'

    def __init__(self, path):
        """All tiles data"""
        self.images = []
        self.tile = {}
        self.img_count = 0
        for file in ("Tile_Arts", "Interactive", "Entities", "Particles"):
            self.path = join(path, file)
            self.images = [f for f in sorted(listdir(self.path)) if isfile(join(self.path, f))]
            self.gather_images()

        ## Special Air Block ##
        self.tile[-1] = Tile_Index_Properties(False, -1)

    def gather_images(self):
        """Gathers images from a path"""
        for image in self.images:
            image = load(join(self.path, image))
            self.tile[self.img_count] = Tile_Index_Properties(image, self.img_count)
            self.img_count += 1


def load(loc):
    """Loads in images from a location"""
    return py.image.load(loc).convert_alpha()


if __name__ == '__main__':
    py.init()
    screen = py.display.set_mode((500, 500))
    py.display.set_caption("Tile Placing Test")
    clock = py.time.Clock()
    tile = All_Tiles('')
    run = True
    while run:
        screen.fill((25, 25, 25))
        tile.tile[256].display(screen, 100, 100)
        tile.tile[253].display(screen, 100, 132)
        tile.tile[254].display(screen, 132, 132)
        tile.tile[255].display(screen, 164, 132)

        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
        py.display.update()
        clock.tick(60)
