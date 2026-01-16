from pygame.rect import Rect
from pygame import Surface
import pygame.mouse as mouse
from math import floor
from tkinter.colorchooser import askcolor


class Worlds:
    """Functions for world rectangles in editor"""
    __slots__ = '__dict__'

    def __init__(self, win, top_left, bottom_right, *, color=None, name=None):
        self.initialising = True
        self.screen = win
        self.sc_width, self.sc_height = self.screen.get_size()
        self.left, self.top = top_left
        self.right, self.bottom = bottom_right
        self.camera_x, self.camera_y = 0, 0
        self.rect = Rect((self.left, self.top), (self.right - self.left, self.bottom - self.top))

        self.levels = {}
        self.col = '#ffebcb' if color is None else color
        self.name = 'My World' if name is None else name
        self.open = False
        self.initialising = False

    def in_world(self, x, y) -> bool:
        """Returns a boolean value of true if given position is in the rect"""
        return self.rect.collidepoint(x, y)

    def get_all_levels_in_world(self, editor_cls) -> list:
        def convert_tile_idx_to_coords(tile_idx) -> tuple[int, int]:
            """Converts tile index to coordinates"""
            x = floor((tile_idx - 1) / editor_cls.grid_height)
            y = (tile_idx - 1) % editor_cls.grid_height - 1
            x *= editor_cls.tiles.tile_size
            x += editor_cls.tiles.tile_size / 2
            y = self.sc_height - y * editor_cls.tiles.tile_size - editor_cls.tiles.tile_size * 3 + \
                editor_cls.tiles.tile_size // 2
            return x, y
        all_levels = []
        for level in editor_cls.levels.values():
            coords = convert_tile_idx_to_coords(level.tile_idx)
            if self.in_world(coords[0], coords[1]):
                all_levels.append(level)
        return all_levels

    def editor_loop(self, cam_x, cam_y):
        """Loop while in editor"""
        self.camera_x, self.camera_y = cam_x, cam_y
        self.check_mouse()
        self.draw()

    def draw(self):
        """Draws the rectangle onto screen"""
        if self.sc_width < self.left - self.camera_x or 0 > self.right - self.camera_x:
            return
        if 0 > self.bottom - self.camera_y or self.sc_height < self.top - self.camera_y:
            return

        left_out = not 0 < self.left - self.camera_x < self.sc_width
        right_out = not 0 < self.right - self.camera_x < self.sc_width
        top_out = not 0 < self.top - self.camera_y < self.sc_height
        bottom_out = not 0 < self.bottom - self.camera_y < self.sc_height

        x, width = 0, self.sc_width
        if not left_out and not right_out:
            x, width = self.left - self.camera_x, self.rect.width
        else:
            if not left_out:
                x = self.left - self.camera_x
            if not right_out:
                width = self.right - self.camera_x

        y, height = 0, self.sc_height
        if not top_out and not bottom_out:
            y, height = self.top - self.camera_y, self.rect.height
        else:
            if not top_out:
                y = self.top - self.camera_y
            if not bottom_out:
                height = self.bottom - self.camera_y

        surface = Surface((width, height))
        surface.fill(self.col)
        surface.set_alpha(100)
        self.screen.blit(surface, (x, y))

    def check_mouse(self):
        """Checks mouse position"""
        mouse_pos = list(mouse.get_pos())
        mouse_pos[0] += self.camera_x
        mouse_pos[1] += self.camera_y
        self.open = self.rect.collidepoint(mouse_pos)

    def open_colorchooser(self):
        """Opens the color chooser"""
        color = askcolor(color=self.col, title='Choose a color')
        self.col = color[1] if color[1] is not None else self.col

    def __setattr__(self, key, value):
        """Updates the current rect"""
        self.__dict__[key] = value
        if key in 'left right top bottom' and not self.initialising:
            self.rect = Rect((self.left, self.top), (self.right - self.left, self.bottom - self.top))

    def __repr__(self):
        """Returns a string representation"""
        return f'{self.name}:{self.top}|{self.bottom}|{self.left}|{self.right}|{self.col}'


class Levels:
    """Functions for all levels"""
    __slots__ = 'id', 'name', 'paths', 'secret_paths', 'gray_paths', 'tile_idx', 'idx'

    def __init__(self, name, paths, secret_paths, tile_idx):
        self.id, self.name = name.split(';')
        self.paths = paths
        self.secret_paths = secret_paths
        self.gray_paths = ''
        self.tile_idx = tile_idx
        self.idx = 200

    def init_gray_arrows(self, possible_nodes):
        """Gives the level gray arrows"""
        if len(self.paths) >= 1:
            self.gray_paths = ''.join([i for i in self.paths + self.secret_paths])
            all_dirs = possible_nodes
            for i in self.gray_paths:
                all_dirs = all_dirs.replace(i, '')
            self.gray_paths = all_dirs

    def get_other_arrows(self, possible_nodes):
        """After initializing gray arrows"""
        all_dirs = possible_nodes
        for i in self.gray_paths:
            all_dirs = all_dirs.replace(i, '')
        self.paths = all_dirs

    def change_arrow(self, arrow):
        """Changes the arrow between paths and secret paths"""
        if arrow in self.paths:
            self.paths = self.paths.replace(arrow, '')
            self.secret_paths = self.secret_paths + arrow
        elif arrow in self.secret_paths:
            self.secret_paths = self.secret_paths.replace(arrow, '')
            self.paths = self.paths + arrow

    def get_list(self):
        """Returns a list representation of the class"""
        return [';'.join([self.id, self.name]), self.paths, self.secret_paths]


class Manage_Level:
    """Manages pathfinding level paths"""
    __slots__ = 'editor', 'prev_paths', 'all_prev_paths', 'gray_arrow_dirs', 'gray_arrow', 'grid_height'

    def __init__(self, editor_cls):
        self.editor = editor_cls
        self.prev_paths = set()
        self.all_prev_paths = set()
        self.gray_arrow_dirs = set()
        self.gray_arrow = False
        self.grid_height = 0

    def clear_prev_data(self):
        """Clears previous usage of this class"""
        self.prev_paths = set()
        self.all_prev_paths = set()
        self.gray_arrow_dirs = set()
        self.gray_arrow = False

    def check_tile(self, tile_idx, return_no_matter_what) -> bool:
        """Checks the tile to see if it is a path or not"""
        if tile_idx in self.editor.overlap_grid:
            if return_no_matter_what:
                return hasattr(self.editor.tiles.tile_class.tiles[self.editor.overlap_grid[tile_idx]], 'node')
            else:
                return hasattr(self.editor.tiles.tile_class.tiles[self.editor.overlap_grid[tile_idx]], 'node') and \
                       tile_idx not in self.all_prev_paths
        else:
            return False

    def check_for_node(self, node, tile_idx, return_no_matter_what):
        """Checks for a node, returning a tile index if the node is a path"""
        if node == '<':  # Left
            tile_idx -= self.grid_height
            return tile_idx if self.check_tile(tile_idx, return_no_matter_what) else None
        elif node == '>':  # Right
            tile_idx += self.grid_height
            return tile_idx if self.check_tile(tile_idx, return_no_matter_what) else None
        elif node == '^':
            tile_idx += 1
            return tile_idx if self.check_tile(tile_idx, return_no_matter_what) else None
        elif node == 'v':
            tile_idx -= 1
            return tile_idx if self.check_tile(tile_idx, return_no_matter_what) else None
        else:
            return None

    def pathfind(self):
        """Finds the next paths"""
        counter = 0
        while self.prev_paths:
            copy_prev_paths = set(self.prev_paths)
            for path in copy_prev_paths:
                tile_idx = path
                for node in self.editor.tiles.tile_class.tiles[self.editor.overlap_grid[tile_idx]].node:
                    temp = self.check_for_node(node, tile_idx, False)

                    # If touching a level
                    if temp in self.editor.levels:
                        for nodes in self.editor.levels[temp].paths:
                            if self.check_for_node(nodes, temp, True) in self.all_prev_paths:
                                self.gray_arrow = True
                        for nodes in self.editor.levels[temp].secret_paths:
                            if self.check_for_node(nodes, temp, True) in self.all_prev_paths:
                                self.gray_arrow = True
                        self.all_prev_paths.add(temp)
                        # if tile_idx in self.prev_paths:
                        #     self.prev_paths.remove(tile_idx)

                    # If touching a path
                    elif temp is not None:
                        self.prev_paths.add(temp)
                        self.all_prev_paths.add(temp)
                    # else:
                    #     if tile_idx in self.prev_paths:
                    #         self.prev_paths.remove(tile_idx)
            if counter > 1000:
                break
            counter += 1
            # Deleting previous paths
            for path in copy_prev_paths:
                if path in self.prev_paths:
                    self.prev_paths.remove(path)

    def find_all_paths_from(self, start_tile_idx, direction):
        """Finds next paths to reveal"""
        self.clear_prev_data()
        for pos in direction:
            tile_idx = self.check_for_node(pos, start_tile_idx, False)
            if tile_idx is None:
                continue
            self.prev_paths.add(tile_idx)
            self.all_prev_paths.add(tile_idx)
            self.pathfind()

        return self.all_prev_paths

    def find_gray_arrows(self, level_tile_idx):
        self.clear_prev_data()
        for direction in self.editor.tiles.tile_class.tiles[self.editor.overlap_grid[level_tile_idx]].node:
            tile_idx = self.check_for_node(direction, level_tile_idx, False)
            if tile_idx is None:
                continue
            self.prev_paths.add(tile_idx)
            self.all_prev_paths.add(tile_idx)
            self.pathfind()
            if self.gray_arrow:
                self.gray_arrow_dirs.add(direction)
            self.gray_arrow = False
        if not self.gray_arrow_dirs:
            return ''
        else:
            return self.gray_arrow_dirs
