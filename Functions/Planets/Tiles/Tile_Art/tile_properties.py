import pygame as py
from os import listdir
from os.path import join, isfile


class Tile_Properties:
    """Class Storing tile properties"""

    def __init__(self, image, idx, category):
        self.tile_size = 32
        if idx == -1:
            self.image = None
            self.height = 0
            self.width = 0
        else:
            self.image = image
            self.height = self.image.get_height() / 32 * self.tile_size
            self.width = self.image.get_width() / 32 * self.tile_size
        self.idx = idx
        self.category = category
        self.layer = 1

        node_dict = {90: '<>^v', 91: '^>', 92: '<^', 100: 'v>', 101: '<>', 102: '<v>', 103: '<^>', 104: '^>v',
                     112: '^v', 113: '<^v', 114: '<>', 115: '.', 116: '<v', 124: '<>', 125: '^v', 126: '.', 127: '.',
                     128: '^v', 129: '^v', 130: '^v', 131: '^v', 136: '<>', 137: '^v', 138: '<>', 139: '<>', 140: '<>',
                     141: '<>', 142: '<>', 195: '.'}
        shadow_dict = {143: 218, 144: 218, 149: 223, 150: 223, 151: 224, 152: 223, 153: 221, 154: 220,
                       165: 239, 166: 239, 167: 239, 168: 240, 169: 239, 170: 230, 171: 224, 175: 222,
                       176: 222, 177: 222, 178: 221, 179: 221, 186: 230, 187: 229, 188: 229, 189: 229,
                       190: 229, 191: 228, 192: 227, 193: 227, 194: 227}
        if self.idx in node_dict:
            self.node = node_dict[self.idx]
            self.layer = 2
        if self.idx in shadow_dict:
            self.shadow = shadow_dict[self.idx]

            # Buildings are slightly different
            if 165 <= self.idx <= 170:
                if self.idx != 170:
                    self.shadow_offset = {0: -self.width * 0.7, 1: None}
                    self.shadow_width = self.width * 1.4
                else:
                    self.shadow_offset = {0: 0, 1: self.height * 0.4}
                    self.shadow_width = self.width
            else:
                self.shadow_offset = {0: -self.width * 0.2, 1: self.height * 0.7}
                self.shadow_width = self.width
        if self.idx == 64 or self.idx == 67 or self.idx == 70 or 93 <= self.idx <= 95 or 105 <= self.idx <= 107 or \
                117 <= self.idx <= 119 or self.idx == 62 or self.idx == 133:
            self.layer = 2
        elif 143 <= self.idx <= 194:
            self.layer = 4
        elif 196 <= self.idx <= 200:
            self.layer = 5
        elif 201 <= self.idx <= 216:
            self.layer = 6
        elif self.idx > 216:
            self.layer = 3
            self.image.set_alpha(185)

    def display(self, win: py.display, x: int, y: int):
        """Displays the tile on screen, this function will not be used"""
        if self.image is not None:
            win.blit(py.transform.scale(self.image, (self.width, self.height)), (x, y))


class Tile_Img:
    """Loads tile images"""

    def __init__(self, path):
        self.images = []
        self.tiles = {}
        self.img_count = 0
        self.category = ''
        for file in ('1_Tiles', join('2_Objects', 'Bushes'), join('2_Objects', 'Crystals'), join('2_Objects', 'Grass'),
                     join('2_Objects', 'Houses'), join('2_Objects', 'Other'), join('2_Objects', 'Rocks'),
                     join('2_Objects', 'Ruins'), join('2_Objects', 'Trees'), '3_UI', '4_Fog', '5_Shadows'):
            self.path = join(path, file)
            self.images = [f for f in sorted(listdir(self.path)) if isfile(join(self.path, f))]
            if file[0] == '2':
                self.category = file.split('\\')[1]
            else:
                self.category = file.split('_')[1]
            self.gather_images()

        """Air block for overlap tiles"""
        self.tiles[-1] = Tile_Properties('', -1, 'Fog')

        # Init Shadows
        for obj in self.tiles:
            if hasattr(self.tiles[obj], 'shadow'):
                self.tiles[self.tiles[obj].shadow].width = self.tiles[obj].shadow_width
                if self.tiles[obj].shadow_offset[1] is None:
                    self.tiles[obj].shadow_offset[1] = self.tiles[obj].height - \
                                                       self.tiles[self.tiles[obj].shadow].height
                self.tiles[obj].shadow = self.tiles[self.tiles[obj].shadow]

    def gather_images(self):
        """Gathers images in a directory"""
        for image in self.images:
            self.tiles[self.img_count] = Tile_Properties(self.load(join(self.path, image)), self.img_count,
                                                         self.category)
            self.img_count += 1

    @staticmethod
    def load(loc):
        """Loads in images from a location"""
        return py.image.load(loc).convert_alpha()


if __name__ == '__main__':
    py.init()
    screen = py.display.set_mode((500, 500))
    py.display.set_caption("Tile Placing Test")
    clock = py.time.Clock()
    tile = Tile_Img('')
    run = True
    while run:
        screen.fill((25, 25, 25))
        tile.tiles[16].display(screen, 100, 100)

        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
        py.display.update()
        clock.tick(60)
