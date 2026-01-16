import pygame as py
from random import randint

try:
    from .Tile_Art.tile_properties import Tile_Properties, Tile_Img
except ImportError:
    from Tile_Art.tile_properties import Tile_Properties, Tile_Img
"""NOTE: This is a copy of Level_Tiles\\tiles.py but edited to suit the planet loop"""


class Tile:
    """Tile Properties"""

    def __init__(self, tiles_cls, x, y, idx, tile_idx, update=False):
        if not update:
            self.initialize = True
            super().__init__()
            # Changeable attributes
            self.x, self.y, self.idx, self.alpha = x, y, idx, 255
            self.draw_x, self.draw_y = self.x, self.y
            self.tiles_cls, self.tile_idx = tiles_cls, tile_idx
            self.shade_tile = False

        # All read-only attributes
        tile = self.tiles_cls.tiles[self.idx]
        self.image = tile.image
        self.category = tile.category
        self.width = tile.width
        self.height = tile.height
        self.layer = tile.layer
        if hasattr(tile, 'node'):
            self.node = tile.node
        elif update and hasattr(self, 'node'):
            del self.node
        if hasattr(tile, 'shadow'):
            self.shadow = tile.shadow
            self.shadow_offset = tile.shadow_offset
        elif update and hasattr(self, 'shadow'):
            del self.shadow, self.shadow_offset
        if not update:
            self.initialize = False

    def draw(self, win: py.display, size=False):
        """Draws the tile onto screen"""
        if self.image is not None:
            if size:
                self.width, self.height = 25, 25
            if not hasattr(self, 'node') and not self.shade_tile:
                self.alpha = 255
            self.image.set_alpha(self.alpha)
            win.blit(py.transform.scale(self.image, (self.width, self.height)), (self.draw_x, self.draw_y))

    def draw_shadow(self, win: py.display):
        """Draws the shadow of the object"""
        if hasattr(self, 'shadow'):
            win.blit(py.transform.scale(self.shadow.image, (self.shadow.width, self.shadow.height)),
                     (self.draw_x + self.shadow_offset[0], self.draw_y + self.shadow_offset[1]))

    def __setattr__(self, key, value):
        """Sets changeable values and updates settings"""
        # Reason why this function isn't in levels because this is slower, updating every time a value has changed
        # Nice thing about this is that you don't have to write update_settings() everytime you change something,
        # Note: refer to Tiles in Levels folder
        self.__dict__[key] = value
        # Updates the settings, if statement to avoid loops
        if key == 'idx' and not self.initialize:
            self.__init__(self.tiles_cls, self.x, self.y, self.idx, self.tile_idx, True)


class Tiles:
    """Stores tile functions, working with the camera"""
    __slots__ = 'screen', 'sc_width', 'sc_height', 'tile_class', 'tile_size', 'tiles', 'tile_count_x', 'tile_count_y',\
                'overlap_tiles', 'overlap_grid', 'level_tiles', 'level_grid', 'grid_width', 'grid_height', 'camera_x', \
                'camera_y', 'tile_index', 'grid_list', 'animation', 'tiles_animated'

    def __init__(self, win: py.display, camera_x, camera_y, path="Tile_Art"):
        self.screen = win
        self.sc_width, self.sc_height = win.get_size()

        self.tile_class = Tile_Img(path)
        self.tile_size = self.tile_class.tiles[0].tile_size
        self.tiles = {}
        self.tile_count_x = self.sc_width // self.tile_size + 1
        self.tile_count_y = self.sc_height // self.tile_size + 1

        self.overlap_tiles = {}
        self.overlap_grid = {}
        self.level_tiles = {}
        self.level_grid = {}

        self.grid_width = 30
        self.grid_height = 20
        self.camera_x = camera_x
        self.camera_y = camera_y

        self.tile_index = 0
        self.grid_list = {}

        self.animation = False
        self.tiles_animated = 0

    def setup(self, grid_size: tuple, setup_dict=None):
        """Sets the tiles onto the screen"""
        self.tiles = {}
        self.overlap_tiles = {}
        if setup_dict is None:
            self.grid_list = {key: value for key, value in enumerate(
                [randint(0, 200) for _ in range(0, self.grid_height * self.grid_width)])}
        else:
            self.grid_list = setup_dict
        self.grid_width, self.grid_height = grid_size[0], grid_size[1]
        self.tiles, self.overlap_tiles, self.level_tiles = {}, {}, {}

        self.tile_index = 0
        self.tiles[-1] = Tile(self.tile_class, 0, 0, 0, -1)
        self.tiles[-1].shade_tile = True
        for x in range(0, self.tile_count_x):
            self.tiles[-1].y = self.sc_height - self.tile_size
            for y in range(0, self.tile_count_y):
                self.tiles[self.tile_index] = Tile(self.tile_class, self.tiles[-1].x, self.tiles[-1].y,
                                                   self.grid_list[self.tile_index], self.tile_index)
                self.overlap_tiles[self.tile_index] = Tile(self.tile_class, self.tiles[-1].x, self.tiles[-1].y,
                                                           -1, self.tile_index)
                if self.tile_index in self.overlap_grid:
                    self.overlap_tiles[self.tile_index].idx = self.overlap_grid[self.tile_index]

                self.level_tiles[self.tile_index] = Tile(self.tile_class, self.tiles[-1].x, self.tiles[-1].y,
                                                         -1, self.tile_index)
                if self.tile_index in self.level_grid:
                    self.level_tiles[self.tile_index].idx = self.level_grid[self.tile_index]

                self.tiles[-1].y -= self.tile_size
                self.tile_index += 1
            self.tiles[-1].x += self.tile_size
            self.tile_index += self.grid_height - self.tile_count_y

    def position_tiles(self, path_dict=None):
        """Positions the tiles onto the screen (Mainloop for tiles)"""
        if self.tiles_animated != 0:
            self.tiles_animated = 0
        if path_dict is None:
            path_dict = []
        for i in self.tiles:
            if i < 0:  # Drawer Blocks / Editor Blocks causes issues
                continue

            self.check_off_screen(i)
            self.tiles[i].draw_x = self.tiles[i].x - self.camera_x
            self.tiles[i].draw_y = self.tiles[i].y - self.camera_y

            self.tiles[i].draw(self.screen)
        # Paint shadows before objects
        for i in self.overlap_tiles:
            if i < 0:  # Drawer Blocks / Editor Blocks causes issues
                continue

            self.check_off_screen_overlaps(i)
            self.overlap_tiles[i].draw_x = self.tiles[i].x - self.camera_x
            self.overlap_tiles[i].draw_y = self.tiles[i].y - self.camera_y

            if self.overlap_tiles[i].layer < 3:
                if self.overlap_tiles[i].tile_idx in path_dict:
                    if path_dict[self.overlap_tiles[i].tile_idx] == 1:
                        self.animation = True
                        if self.overlap_tiles[i].alpha < 255:
                            self.overlap_tiles[i].alpha += 2
                            self.tiles_animated += 1
                        elif self.tiles_animated < 1:
                            self.animation = False
                    else:
                        self.overlap_tiles[i].alpha = 255

                elif hasattr(self.overlap_tiles[i], 'node') and isinstance(path_dict, dict):
                    self.overlap_tiles[i].alpha = 0
            else:
                self.overlap_tiles[i].draw_shadow(self.screen)
            self.overlap_tiles[i].draw(self.screen)

        for i in self.level_tiles:
            if i < 0:  # Drawer Blocks / Editor Blocks causes issues
                continue

            self.check_off_screen_levels(i)
            self.level_tiles[i].draw_x = self.level_tiles[i].x - self.camera_x
            self.level_tiles[i].draw_y = self.level_tiles[i].y - self.camera_y

            self.level_tiles[i].draw(self.screen)

    def check_off_screen(self, tile):
        """checks if tile is off_screen"""
        i = tile
        if self.tiles[i].x - self.camera_x < -self.tile_size:
            self.loop_tile_x(i, self.tile_count_x)
        elif self.tiles[i].x - self.camera_x > self.sc_width:
            self.loop_tile_x(i, -self.tile_count_x)

        if self.tiles[i].y - self.camera_y > self.sc_height:
            self.loop_tile_y(i, -self.tile_count_y)
        elif self.tiles[i].y - self.camera_y < -self.tile_size:
            self.loop_tile_y(i, self.tile_count_y)

    def check_off_screen_overlaps(self, tile):
        """checks if tile is off_screen"""
        i = tile
        if self.overlap_tiles[i].x - self.camera_x < -self.tile_size:
            self.loop_tile_x_overlap(i, self.tile_count_x)
        elif self.overlap_tiles[i].x - self.camera_x > self.sc_width:
            self.loop_tile_x_overlap(i, -self.tile_count_x)

        if self.overlap_tiles[i].y - self.camera_y > self.sc_height:
            self.loop_tile_y_overlap(i, -self.tile_count_y)
        elif self.overlap_tiles[i].y - self.camera_y < -self.tile_size:
            self.loop_tile_y_overlap(i, self.tile_count_y)

    def check_off_screen_levels(self, tile):
        """checks if tile is off_screen"""
        i = tile
        if self.level_tiles[i].x - self.camera_x < -self.tile_size:
            self.loop_tile_x_level(i, self.tile_count_x)
        elif self.level_tiles[i].x - self.camera_x > self.sc_width:
            self.loop_tile_x_level(i, -self.tile_count_x)

        if self.level_tiles[i].y - self.camera_y > self.sc_height:
            self.loop_tile_y_level(i, -self.tile_count_y)
        elif self.level_tiles[i].y - self.camera_y < -self.tile_size:
            self.loop_tile_y_level(i, self.tile_count_y)

    def loop_tile_x(self, tile, tile_skip):
        """Makes it possible to scroll in the x-axis"""
        self.tiles[tile].tile_idx += tile_skip * self.grid_height
        if self.tiles[tile].tile_idx in self.grid_list:
            self.tiles[tile].idx = self.grid_list[self.tiles[tile].tile_idx]
        else:
            self.tiles[tile].idx = 0
        self.tiles[tile].x += tile_skip * self.tile_size

    def loop_tile_y(self, tile, tile_skip):
        """Makes it possible to scroll in the y-axis"""
        self.tiles[tile].tile_idx += -tile_skip
        if self.tiles[tile].tile_idx in self.grid_list:
            self.tiles[tile].idx = self.grid_list[self.tiles[tile].tile_idx]
        else:
            self.tiles[tile].idx = 0
        self.tiles[tile].y += tile_skip * self.tile_size

    def loop_tile_x_overlap(self, tile, tile_skip):
        """Makes it possible to scroll in the x-axis"""
        self.overlap_tiles[tile].tile_idx += tile_skip * self.grid_height
        if self.overlap_tiles[tile].tile_idx in self.overlap_grid:
            self.overlap_tiles[tile].idx = self.overlap_grid[self.overlap_tiles[tile].tile_idx]
        else:
            self.overlap_tiles[tile].idx = -1
        self.overlap_tiles[tile].x += tile_skip * self.tile_size

    def loop_tile_y_overlap(self, tile, tile_skip):
        """Makes it possible to scroll in the y-axis"""
        self.overlap_tiles[tile].tile_idx += -tile_skip
        if self.overlap_tiles[tile].tile_idx in self.overlap_grid:
            self.overlap_tiles[tile].idx = self.overlap_grid[self.overlap_tiles[tile].tile_idx]
        else:
            self.overlap_tiles[tile].idx = -1
        self.overlap_tiles[tile].y += tile_skip * self.tile_size

    def loop_tile_x_level(self, tile, tile_skip):
        """Makes it possible to scroll in the x-axis"""
        self.level_tiles[tile].tile_idx += tile_skip * self.grid_height
        if self.level_tiles[tile].tile_idx in self.level_grid:
            self.level_tiles[tile].idx = self.level_grid[self.level_tiles[tile].tile_idx]
        else:
            self.level_tiles[tile].idx = -1
        self.level_tiles[tile].x += tile_skip * self.tile_size

    def loop_tile_y_level(self, tile, tile_skip):
        """Makes it possible to scroll in the y-axis"""
        self.level_tiles[tile].tile_idx += -tile_skip
        if self.level_tiles[tile].tile_idx in self.level_grid:
            self.level_tiles[tile].idx = self.level_grid[self.level_tiles[tile].tile_idx]
        else:
            self.level_tiles[tile].idx = -1
        self.level_tiles[tile].y += tile_skip * self.tile_size


if __name__ == '__main__':
    py.init()
    WIDTH, HEIGHT = 480, 320
    screen = py.display.set_mode((WIDTH, HEIGHT))
    py.display.set_caption("Tiles Test")
    clock = py.time.Clock()

    CAMERA_X = 90
    CAMERA_Y = 0
    g_height = 20
    g_width = 30
    TILES = Tiles(screen, CAMERA_X, CAMERA_Y)

    run = True
    j = 0
    while run:
        screen.fill((25, 25, 25))
        if j < 1:
            TILES.setup((g_width, g_height))
        TILES.position_tiles()

        for event in py.event.get():
            if event.type == py.QUIT:
                run = False

        if j % 2 == 0:
            CAMERA_X += -5
            CAMERA_Y += 5
            pass

        TILES.camera_x = CAMERA_X
        TILES.camera_y = CAMERA_Y
        py.display.update()
        clock.tick(60)
        j += 1
    py.quit()
