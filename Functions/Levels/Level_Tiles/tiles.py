import pygame as py
from random import randint
from math import floor, sin, radians

try:
    from .Tile_Arts.tile_properties import All_Tiles
except ImportError:
    from Tile_Arts.tile_properties import All_Tiles


class Tile(py.sprite.Sprite):
    """Object Values for each Tile"""
    hide_hidden = True
    __slots__ = 'x', 'y', 'idx', 'draw_x', 'draw_y', 'tiles_cls', 'tile_idx', 'idx', 'collision', 'layer', 'category', \
                'image', 'tile_space', 'tile_placement', 'img_width', 'img_height', 'scale', 'bumped', 'mask', 'rect', \
                'destroyed', 'col_width', 'col_height', 'alpha', 'solid', 'dir', 'flipped_img'

    def __init__(self, tiles_cls, x, y, idx, tile_idx, *, update=False):
        """Initializes Tile Variables"""
        self.x, self.y, self.idx = x, y, float(idx)
        if not update:
            super().__init__()
            self.draw_x, self.draw_y = self.x, self.y
            self.tiles_cls, self.tile_idx = tiles_cls, tile_idx

        idx = int(floor(idx))
        if self.idx == float(idx):
            self.collision = tiles_cls.tile[idx].collision1
            self.layer = 1
        else:
            self.collision = tiles_cls.tile[idx].collision2
            self.layer = 2
        self.category = tiles_cls.tile[idx].category
        self.image = tiles_cls.tile[idx].image
        self.tile_space = tiles_cls.tile[idx].tile_space
        self.tile_placement = tiles_cls.tile[idx].tile_space
        self.img_width, self.img_height = tiles_cls.tile[idx].img_width, tiles_cls.tile[idx].img_height
        self.scale = tiles_cls.tile[idx].standard_tile_size / 70

        self.bumped = None
        self.mask = None
        self.rect = None
        self.destroyed = False
        self.col_width, self.col_height = 0, 0
        self.alpha = 255
        if self.__class__.hide_hidden and str(idx) in '16 18 24 26':
            self.alpha = 10 if str(idx) in '16 18' else 0  # Hidden Blocks
        self.solid = False
        self.dir = True
        if self.image:
            self.flipped_img = py.transform.flip(self.image, True, False).convert_alpha()
        else:
            self.flipped_img = self.image

        self.update_collision()

    def update_collision(self):
        """Updates the collision for a tile"""
        if self.destroyed:
            self.solid = False
            self.alpha = 150
        elif self.idx >= 0:
            if '~' in self.collision:
                self.solid = True
                if '_' in self.collision:
                    self.find_collision()
            elif '#' in self.collision or '/' in self.collision or '\\' in self.collision or '-' in self.collision \
                    or '|' in self.collision:
                self.solid = True
                if '0' in self.collision or '>' in self.collision or '<' in self.collision:
                    self.find_collision()
            elif '<' in self.collision or '>' in self.collision or '_' in self.collision or '=' in self.collision:
                self.solid = True
                self.find_collision()
            else:
                self.solid = False
        else:
            self.solid = False

    def find_collision(self):
        """Finds the block's collision in special occasions"""
        image = py.transform.scale(self.image, (self.scale * self.img_width, self.scale * self.img_height))
        self.rect = image.get_rect(topleft=(self.draw_x, self.draw_y))
        self.mask = py.mask.from_surface(image)
        rect = self.mask.get_bounding_rects()[0]

        self.col_height = -rect.y if '_' in self.collision else rect.height
        self.col_width = -rect.x if '>' in self.collision else rect.width
        if abs(self.col_height) >= 32:
            self.col_height = 0
        if abs(self.col_width) >= 32:
            self.col_width = 0

    def draw(self, win: py.display):
        """Draws Tiles onto Screen"""
        self.tick_bumped()
        if self.idx >= 0:
            image = self.image if self.dir else self.flipped_img
            image = py.transform.scale(image, (self.scale * self.img_width, self.scale * self.img_height))
            image.set_alpha(self.alpha)
            win.blit(image, (self.draw_x, self.draw_y))
            if self.rect is not None:
                self.rect.x, self.rect.y = self.draw_x, self.draw_y

    def tick_bumped(self):
        """Animates bumped tiles"""
        if self.bumped is not None:
            self.bumped -= 30
            self.draw_y += -5 * sin(radians(self.bumped))
            if self.bumped < 0:
                self.bumped = None

    def update_settings(self):
        """Updates settings based on changes"""
        self.__init__(self.tiles_cls, self.x, self.y, self.idx, self.tile_idx, update=True)


class Tiles:
    """Stores tile functions, working with the camera"""
    __slots__ = 'screen', 'sc_width', 'sc_height', 'tile_class', 'tile_size', 'tiles', 'tile_count_x', 'tile_count_y', \
                'animation_count', 'overlap_tiles', 'overlap_grid', 'destroyed_tiles', 'saved_destroyed_tiles', \
                'grid_width', 'grid_height', 'camera_x', 'camera_y', 'tile_index', 'grid_list'

    def __init__(self, win: py.display, camera_x, camera_y, path="Tile_Arts"):
        self.screen = win
        self.sc_width, self.sc_height = win.get_size()

        self.tile_class = All_Tiles(path)
        self.tile_size = self.tile_class.tile[0].standard_tile_size
        self.tiles = {}
        self.tile_count_x = self.sc_width // self.tile_size + 1
        self.tile_count_y = self.sc_height // self.tile_size + 1
        self.animation_count = 0

        self.overlap_tiles = {}
        self.overlap_grid = {}
        self.destroyed_tiles = set()
        self.saved_destroyed_tiles = set()

        self.grid_width = 30
        self.grid_height = 20
        self.camera_x = camera_x
        self.camera_y = camera_y

        self.tile_index = 0
        self.grid_list = {}  # Dictionaries are 6.6 times faster than lists (both containing 100 items): Reference Below
        """Faster Lookups In Python (2021). Available at: 
        https://towardsdatascience.com/faster-lookups-in-python-1d7503e9cd38 (Accessed: 8 December 2022)."""

    def setup(self, grid_size: tuple, setup_dict=None):
        """Sets the tiles onto the screen"""
        self.tiles = {}
        self.overlap_tiles = {}
        self.destroyed_tiles = set(self.saved_destroyed_tiles)
        if setup_dict is None:
            self.grid_list = {key: value for key, value in enumerate(
                [randint(0, 565) for _ in range(0, self.grid_height * self.grid_width)])}
        else:
            self.grid_list = setup_dict
        self.grid_width, self.grid_height = grid_size[0], grid_size[1]

        self.tile_index = 0
        self.tiles[-1] = Tile(self.tile_class, 0, 0, -1, -1)  # Drawer Block / Position Block
        for x in range(0, self.tile_count_x):
            self.tiles[-1].y = self.sc_height - self.tile_size
            for y in range(0, self.tile_count_y):
                self.tiles[self.tile_index] = Tile(self.tile_class, self.tiles[-1].x, self.tiles[-1].y,
                                                   self.grid_list[self.tile_index], self.tile_index)
                if self.tile_index in self.overlap_grid:
                    tile_idx = self.overlap_grid[self.tile_index]
                else:
                    tile_idx = -1
                self.overlap_tiles[self.tile_index] = Tile(self.tile_class, self.tiles[-1].x, self.tiles[-1].y,
                                                           tile_idx, self.tile_index)
                if self.tile_index in self.destroyed_tiles:  # Clearing destroyed tiles
                    self.tiles[self.tile_index].destroyed = True
                    self.tiles[self.tile_index].update_collision()
                    self.overlap_tiles[self.tile_index].destroyed = True
                    self.overlap_tiles[self.tile_index].update_collision()
                self.tiles[-1].y -= self.tile_size
                self.tile_index += 1
            self.tiles[-1].x += self.tile_size
            self.tile_index += self.grid_height - self.tile_count_y

    def position_tiles(self, editor, move_camera=False):
        """Positions the tiles onto the screen (Mainloop for tiles)"""
        self.animation_count += 0.1
        if move_camera:
            self.move_camera()
        for i in self.tiles:
            if i < 0:  # Drawer Blocks / Editor Blocks causes issues
                continue

            self.check_off_screen(i)
            self.tiles[i].draw_x = self.tiles[i].x - self.camera_x
            if self.tiles[i].bumped is None:
                self.tiles[i].draw_y = self.tiles[i].y - self.camera_y
            tile_idx = self.tiles[i].idx

            if tile_idx == 628 and not editor:
                continue
            # Animating tiles
            if tile_idx == 488 or tile_idx == 489:
                self.tiles[i].idx = round(self.animation_count * 2) % 2 + 488
                self.tiles[i].update_settings()
            elif '~' in self.tiles[i].collision:
                self.tiles[i].dir = bool(round(self.animation_count * 0.8) % 2)

            self.tiles[i].draw(self.screen)
        for i in self.overlap_tiles:
            if i < 0:  # Drawer Blocks / Editor Blocks causes issues
                continue

            self.check_off_screen_overlaps(i)
            self.overlap_tiles[i].draw_x = self.overlap_tiles[i].x - self.camera_x
            if self.overlap_tiles[i].bumped is None:
                self.overlap_tiles[i].draw_y = self.overlap_tiles[i].y - self.camera_y
            tile_idx = self.overlap_tiles[i].idx

            if tile_idx == 628 and not editor:
                continue
            # Animating tiles
            if tile_idx == 488 or tile_idx == 489:
                self.overlap_tiles[i].idx = round(self.animation_count * 2) % 2 + 488
                self.overlap_tiles[i].update_settings()
            elif '~' in self.overlap_tiles[i].collision:
                self.overlap_tiles[i].dir = bool(round(self.animation_count * 0.8) % 2)

            self.overlap_tiles[i].draw(self.screen)

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

    def loop_tile_x(self, tile, tile_skip):
        """Makes it possible to scroll in the x-axis"""
        self.tiles[tile].tile_idx += tile_skip * self.grid_height
        self.tiles[tile].idx = self.grid_list[self.tiles[tile].tile_idx]
        self.tiles[tile].x += tile_skip * self.tile_size
        self.tiles[tile].update_settings()
        self.check_destroyed(tile)

    def loop_tile_y(self, tile, tile_skip):
        """Makes it possible to scroll in the y-axis"""
        self.tiles[tile].tile_idx += -tile_skip
        self.tiles[tile].idx = self.grid_list[self.tiles[tile].tile_idx]
        self.tiles[tile].y += tile_skip * self.tile_size
        self.tiles[tile].update_settings()
        self.check_destroyed(tile)

    def loop_tile_x_overlap(self, tile, tile_skip):
        """Makes it possible to scroll in the x-axis"""
        self.overlap_tiles[tile].tile_idx += tile_skip * self.grid_height
        if self.overlap_tiles[tile].tile_idx in self.overlap_grid:
            self.overlap_tiles[tile].idx = self.overlap_grid[self.overlap_tiles[tile].tile_idx]
        else:
            self.overlap_tiles[tile].idx = -1
        self.overlap_tiles[tile].x += tile_skip * self.tile_size
        self.overlap_tiles[tile].update_settings()
        self.check_destroyed_overlap(tile)

    def loop_tile_y_overlap(self, tile, tile_skip):
        """Makes it possible to scroll in the y-axis"""
        self.overlap_tiles[tile].tile_idx += -tile_skip
        if self.overlap_tiles[tile].tile_idx in self.overlap_grid:
            self.overlap_tiles[tile].idx = self.overlap_grid[self.overlap_tiles[tile].tile_idx]
        else:
            self.overlap_tiles[tile].idx = -1
        self.overlap_tiles[tile].y += tile_skip * self.tile_size
        self.overlap_tiles[tile].update_settings()
        self.check_destroyed_overlap(tile)

    def check_destroyed(self, tile):
        """Checks if the tile is destroyed or not"""
        if self.tiles[tile].tile_idx in self.destroyed_tiles:
            self.tiles[tile].destroyed = True
            self.tiles[tile].update_collision()

    def check_destroyed_overlap(self, tile):
        """Checks if the tile is destroyed or not"""
        if self.overlap_tiles[tile].tile_idx in self.destroyed_tiles:
            self.overlap_tiles[tile].destroyed = True
            self.overlap_tiles[tile].update_collision()

    def move_camera(self):
        """Set camera borders"""
        if self.camera_x < 0:
            self.camera_x = 0
        if self.camera_y > 0:
            self.camera_y = 0
        if self.camera_x > self.tile_size * self.grid_width - self.sc_width:
            self.camera_x = self.tile_size * self.grid_width - self.sc_width
        if self.camera_y < -self.tile_size * self.grid_height + self.sc_height:
            self.camera_y = -self.tile_size * self.grid_height + self.sc_height


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
        TILES.position_tiles(True)

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
