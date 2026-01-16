import pygame as py
from os.path import join
from math import floor, ceil
from tkinter.colorchooser import askcolor

try:
    from .Level_Tiles.tiles import Tiles, Tile
    from .Level_Store.level_store import Level_Store
    from .Background.background import Background
except ImportError:
    from Level_Tiles.tiles import Tiles, Tile
    from Level_Store.level_store import Level_Store
    from Background.background import Background


class Camera_Rect(py.sprite.Sprite):
    """Functions for camera rectangles"""
    all_idx = {0}

    def __init__(self, win, idx, top_left, bottom_right, *, editor_cls, c_type=None):
        super().__init__()
        self.initialising = True
        self.idx = int(idx)
        self.__class__.all_idx.add(self.idx)
        self.editor = editor_cls
        self.screen = win
        self.sc_width, self.sc_height = self.screen.get_size()
        self.left, self.top = top_left
        self.right, self.bottom = bottom_right
        self.camera_x, self.camera_y = 0, 0
        self.rect = py.Rect((self.left, self.top), (self.right - self.left, self.bottom - self.top))

        # Camera types: lock, lock_screen, free, none
        self.c_type = 'none' if c_type is None else c_type
        x_border = self.sc_width / 5 if self.rect.width < self.rect.height else 0
        y_border = self.sc_height / 7 if self.rect.width > self.rect.height else 0
        self.lock = ''
        if x_border != 0:
            self.lock += 'x'
        if y_border != 0:
            self.lock += 'y'
        self.loc_range = py.Rect((0 + x_border, 0 + y_border),
                                 (self.sc_width - x_border * 2, self.sc_height - y_border * 2))
        self.open = False
        self.exit_editor = False
        self.mouse_pos = (0, 0)
        self.rising_editor = True
        self.clicked = False
        self.frame = 0

        self.initialising = False

    def in_range(self, x, y) -> bool:
        """Returns a boolean showing if coordinates given are in the rectangle"""
        return self.rect.collidepoint(x, y)

    def in_loc_range(self, draw_x, draw_y) -> bool:
        """Returns a boolean showing if coordinates on the screen are in lock range"""
        return self.loc_range.collidepoint(draw_x, draw_y)

    def move_camera(self, *, cam_x, cam_y, mov_cam, player_cls):
        """Moves the camera to fit the camera rectangle limitations and rules"""
        self.frame += 0.3
        if self.c_type == 'lock':
            return cam_x, cam_y, True
        elif self.c_type == 'lock_screen':
            return self.rect.centerx - self.sc_width / 2, self.rect.centery - self.sc_height / 2, True
        elif self.c_type == 'free':
            return self.free_camera_rect(cam_x, cam_y, mov_cam, player_cls)
        else:
            cam_x += (player_cls.x - cam_x - self.sc_width // 2.7) / 4
            cam_y += (player_cls.y - cam_y - self.sc_height // 2) / 8
            return cam_x, cam_y, False

    def free_camera_rect(self, cam_x, cam_y, mov_cam, player_cls):
        """How the free camera rectangle moves the camera"""
        if 'x' not in self.lock:
            cam_x += (player_cls.x - cam_x - self.sc_width // 2.7) / max(4, mov_cam[0] - self.frame)
        elif not self.in_loc_range(player_cls.draw_x, player_cls.draw_y):
            if player_cls.draw_x > self.loc_range.right:
                cam_x += (player_cls.draw_x - self.loc_range.right) / 4
            elif player_cls.draw_x < self.loc_range.left:
                cam_x += (player_cls.draw_x - self.loc_range.left) / 4
        if 'y' not in self.lock:
            cam_y += (player_cls.y - cam_y - self.sc_height // 2) / max(8, mov_cam[1] - self.frame)
        elif not self.in_loc_range(player_cls.draw_x, player_cls.draw_y):
            if player_cls.draw_y > self.loc_range.bottom:
                cam_y += (player_cls.draw_y - self.loc_range.bottom) / 4
            elif player_cls.draw_y < self.loc_range.top:
                cam_y += (player_cls.draw_y - self.loc_range.top) / 4

        return cam_x, cam_y, False

    def editor_loop(self, cam_x, cam_y):
        """Editor functions for camera rect"""
        self.camera_x, self.camera_y = cam_x, cam_y
        self.check_mouse()
        self.draw()

    def draw(self):
        """Draws the camera rectangle onto screen"""
        if self.sc_width < self.left - self.camera_x or 0 > self.right - self.camera_x:
            return
        if 0 > self.bottom - self.camera_y or self.sc_height < self.top - self.camera_y:
            return
        if self.c_type == 'lock':
            col = '#fcb67d'
        elif self.c_type == 'lock_screen':
            col = '#fc857d'
        elif self.c_type == 'free':
            col = '#7dfccd'
        else:
            col = '#8c8d8d'

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

        surface = py.Surface((width, height))
        surface.fill(col)
        surface.set_alpha(100)
        self.screen.blit(surface, (x, y))

    def draw_edit_menu(self):
        """Draws the edit menu for camera rectangles"""
        if self.rising_editor:
            self.mouse_pos = py.mouse.get_pos()
            self.rising_editor = False

        keys = py.key.get_pressed()
        if keys[py.K_ESCAPE]:
            self.exit_editor = True
        elif self.exit_editor:
            self.editor.ent_menu = False
            self.exit_editor = False
            self.rising_editor = True

        width, height = self.sc_width / 3.5, self.sc_height / 3.5
        x, y = self.mouse_pos
        x = x if x + width + 5 < self.sc_width else x - width - 5
        y = y if y + height + 3 < self.sc_height else y - height - 3
        y += 2
        menu = (py.Surface((width, height)), (x, y))
        menu[0].fill('#E0e0df')
        menu[0].set_alpha(135)
        self.screen.blit(menu[0], menu[1])

        font = py.font.Font(None, floor(self.sc_height / 15))
        mouse_pos = py.mouse.get_pos()
        pressed = py.mouse.get_pressed()[0]

        for name, txt in (("C Type:", self.c_type.replace('_', ' ')),):
            text = font.render(name, True, '#000000')
            text_rect = text.get_rect(topleft=(x + 2, y))
            self.screen.blit(text, text_rect)
            x_width = 5 + text_rect.width
            box = py.Rect((x + 2 + x_width, y), (self.sc_width / 3.5 - x_width - 4, text_rect.height))
            if box.collidepoint(mouse_pos):
                col = '#Eeeeed'
                if pressed:
                    self.clicked = True
                elif self.clicked:
                    if name == "C Type:":
                        types = ['lock', 'lock_screen', 'free', 'none']
                        self.c_type = types[types.index(self.c_type) + 1 if self.c_type != types[-1] else 0]
                    self.clicked = False
            else:
                col = '#ffffff'

            py.draw.rect(self.screen, col, box)
            text = font.render(txt, True, '#000000')
            text_rect = text.get_rect(topleft=(x + 3 + x_width, y))
            self.screen.blit(text, text_rect)
            y += text_rect.height + 5

        for button in ("Fill current camera", "^ Just Width", "^ Just Height", "Delete"):
            text = font.render(button, True, '#000000')
            box = py.Rect((x + 2, y), (self.sc_width / 3.5 - 4, text.get_height()))
            if box.collidepoint(mouse_pos):
                col = '#Eeeeed'
                if pressed:
                    self.clicked = True
                elif self.clicked:
                    if button == "Fill current camera":
                        self.left = round(self.camera_x)
                        self.top = round(self.camera_y)
                        self.right = round(self.camera_x + self.sc_width)
                        self.bottom = round(self.camera_y + self.sc_height)
                    elif button == "^ Just Width":
                        self.left = round(self.camera_x)
                        self.right = round(self.camera_x + self.sc_width)
                    elif button == "^ Just Height":
                        self.top = round(self.camera_y)
                        self.bottom = round(self.camera_y + self.sc_height)
                    elif button == "Delete":
                        del self.editor.camera[self.idx]
                        self.editor.ent_menu = False
                    self.clicked = False
            else:
                col = '#ffffff'

            py.draw.rect(self.screen, col, box)
            text_rect = text.get_rect(center=(box.centerx, box.centery))
            self.screen.blit(text, text_rect)
            y += box.height + 5

    def check_mouse(self):
        """Checks mouse position"""
        mouse_pos = list(py.mouse.get_pos())
        mouse_pos[0] += self.camera_x
        mouse_pos[1] += self.camera_y
        self.open = self.rect.collidepoint(mouse_pos)

    def __setattr__(self, key, value):
        """Updates the current rect"""
        self.__dict__[key] = value
        if key in 'left right top bottom' and not self.initialising:
            self.rect = py.Rect((self.left, self.top), (self.right - self.left, self.bottom - self.top))

            x_border = self.sc_width / 13 if self.rect.width < self.rect.height else 0
            y_border = self.sc_height / 13 if self.rect.width > self.rect.height else 0
            self.lock = ''
            if x_border != 0:
                self.lock += 'x'
            if y_border != 0:
                self.lock += 'y'
            self.loc_range = py.Rect((0 + x_border, 0 + y_border),
                                     (self.sc_width - x_border * 2, self.sc_height - y_border * 2))

    def __repr__(self):
        """Returns a string representation"""
        return f'{self.idx}:{self.top}|{self.bottom}|{self.left}|{self.right}|{self.c_type}'


class Level:
    """Class containing level details"""
    __slots__ = 'screen', 'sc_width', 'sc_height', 'tile_grid', 'grid_width', 'grid_height', 'tile_index', 'time', \
                'level_number', 'level_store', 'background_cls', 'overlap_grid', 'entity_grid', 'camera', 'background'

    def __init__(self, win: py.display, path):
        self.screen = win
        self.sc_width, self.sc_height = win.get_size()
        self.tile_grid = {}
        self.grid_width = 0
        self.grid_height = 0
        self.tile_index = -1
        self.time = 500
        self.level_number = '1-1'
        self.level_store = Level_Store(path)
        self.background_cls = Background(self.screen, path)
        self.overlap_grid = {}
        self.entity_grid = {}
        self.camera, self.background = {}, {0: False, 1: False, 2: {}}

    def setup_database(self, db):
        self.level_store.setup_database(db)

    def generate_level(self, level, editor_cls, blank=None):
        """Generates the level from number"""
        self.level_number = level
        if blank:
            self.generate_blank_level(blank)
            self.background_cls.init_background(self.background[0])
            return None

        self.grid_width, self.grid_height, self.tile_grid, self.overlap_grid, self.entity_grid, self.time, self.camera,\
            self.background = self.level_store.load_level(self.level_number)

        self.camera = {key: Camera_Rect(self.screen, key, (int(value[2]), int(value[0])),
                                        (int(value[3]), int(value[1])),
                                        editor_cls=editor_cls, c_type=value[4]) for key, value in self.camera.items()}
        if self.grid_width < 1:
            self.generate_blank_level()
        if self.background[0] == "None":
            self.background[0] = (25, 25, 25)
        self.background_cls.init_background(self.background[0])

    """Creating Blank Level"""

    def generate_blank_level(self, grid_dims=None):
        if grid_dims is None:
            grid_dims = (300, 70)
        self.tile_grid = {}
        self.overlap_grid = {}
        self.entity_grid = {}
        self.grid_width = grid_dims[0]
        self.grid_height = grid_dims[1]
        self.tile_index = -1
        self.time = 500
        self.camera, self.background = {}, {0: '#191919', 1: False, 2: {}}
        self.add_wall_column()
        for _ in range(0, self.grid_width - 2):
            self.add_boxed_column()
        self.add_wall_column()

    def add_wall_column(self):
        """Adds wall columns to the edge of the grid (level-border)"""
        for _ in range(0, self.grid_height):
            self.tile_index += 1
            self.tile_grid[self.tile_index] = 28

    def add_boxed_column(self):
        """Adds horizontal borders to the edge of the grid"""
        self.tile_index += 1
        self.tile_grid[self.tile_index] = 28
        for _ in range(0, self.grid_height - 2):
            self.tile_index += 1
            self.tile_grid[self.tile_index] = -1
        self.tile_index += 1
        self.tile_grid[self.tile_index] = 28


class Editor(Level):
    """Level editor functions"""
    __slots__ = 'tiles', 'entity', 'editor', 'editor_exit_func', 'esc_pressed', 'del_pressed', 'tab_pressed', \
                'back_pressed', 'caps_pressed', 'clicked', 'buttons', 'show_menu', 'full_screen_menu', 'door_placing', \
                'ent_menu', 'user_text', 'user_text_length', 'l2', 'rect_pos', 'camera_menu', 'top_menu', 'side_menu', \
                'selected_tile', 'font', 'button_pressed', 'full_menu_font', 'small_menu_font', 'full_menu_bg', \
                'menu_buttons', 'tile_y', 'max_tile_y', 'tile_y_vel', 'chosen_brush', 't1', 't2', 't3', 't4', 't5', \
                't6', 't7', 't8', 't9', 't0','img_dict', 'once_tiles', 'tile_images', 'tile_font', 'editor_permission',\
                'current_text', 'clearing_level', 'n_grid_dims', 'setup_func', 'grid_func', 'player_move'

    def __init__(self, win: py.display, path, *, tiles_cls, editor_exit_func, setup_func, grid_func):
        super().__init__(win, path)
        self.tiles = tiles_cls
        self.entity = None
        self.editor = False
        self.editor_exit_func = editor_exit_func
        # handling button presses
        self.esc_pressed = False
        self.del_pressed = False
        self.tab_pressed = False
        self.back_pressed = False
        self.caps_pressed = False
        self.clicked = False
        self.buttons = {}
        self.show_menu = True
        self.full_screen_menu = False
        self.door_placing = False
        self.ent_menu = False
        self.user_text = ''
        self.user_text_length = 10
        self.current_text = None

        self.l2 = 0
        self.rect_pos = []
        self.camera_menu = False

        # Menu Items
        self.top_menu = (py.Surface((self.sc_width, self.sc_width // 13)), (0, 0))
        self.side_menu = (py.Surface((self.sc_width // 13, self.sc_width)), (0, 0))
        self.selected_tile = py.Rect((0, 0), (self.sc_width, self.sc_width // 13))
        self.font = py.font.Font(None, self.sc_width // 13 - 3)

        self.top_menu[0].fill('#E0e0df')
        self.top_menu[0].set_alpha(135)
        self.side_menu[0].fill('#E0e0df')
        self.side_menu[0].set_alpha(135)

        # Tiles menu
        self.button_pressed = 0
        self.full_menu_font = py.font.Font(None, 30)
        self.small_menu_font = py.font.Font(None, 15)
        self.full_menu_bg = py.Rect((0, 0), (self.sc_width, self.sc_width))
        self.menu_buttons = {}
        self.tile_y = 0
        self.max_tile_y = 0
        self.tile_y_vel = 0

        """Brushes"""
        self.chosen_brush = 28
        self.t1, self.t2, self.t3, self.t4, self.t5, self.t6, self.t7, self.t8, self.t9, self.t0 = \
            [i for i in range(20, 30)]
        self.img_dict = {1: self.t1, 2: self.t2, 3: self.t3, 4: self.t4, 5: self.t5, 6: self.t6, 7: self.t7, 8: self.t8,
                         9: self.t9, 10: self.t0}

        self.once_tiles = {628: True,  # Player default Spawn tile
                           578: True, 581: True, 584: True, 587: True,  # Checkpoints
                           590: True, 591: True, 592: True, 593: True  # Gems
                           }
        self.tile_images = {}
        self.tile_font = py.font.Font(None, floor(self.tiles.tile_size / 2.6))
        self.editor_permission = True

        self.clearing_level = False
        self.n_grid_dims = [self.grid_width, self.grid_height]
        self.setup_func = setup_func
        self.grid_func = grid_func

        self.player_move = True

    def init_once_tiles(self):
        """Initializes once tiles dictionary"""
        self.once_tiles = {key: True for key in self.once_tiles.keys()}
        for tile in self.tile_grid:
            if int(floor(self.tile_grid[tile])) in self.once_tiles:
                self.once_tiles[int(floor(self.tile_grid[tile]))] = tile
        for tile in self.overlap_grid:
            if int(floor(self.overlap_grid[tile])) in self.once_tiles:
                self.once_tiles[int(floor(self.overlap_grid[tile]))] = tile
        for tile in self.entity_grid:
            if int(floor(self.entity_grid[tile])) in self.once_tiles:
                self.once_tiles[int(floor(self.entity_grid[tile]))] = tile

    def refresh(self):
        """Refreshes tile grids"""
        self.generate_level(self.level_number, self)
        self.tiles.grid_list = self.tile_grid
        self.n_grid_dims = [self.grid_width, self.grid_height]
        Tile.hide_hidden = False
        for tile in self.tiles.tiles.values():
            if tile.tile_idx < 0:
                continue
            tile.idx = self.tiles.grid_list[tile.tile_idx]
            tile.update_settings()
        self.tiles.overlap_grid = self.overlap_grid
        for tile in self.tiles.overlap_tiles.values():
            if tile.tile_idx in self.tiles.overlap_grid:
                tile.idx = self.tiles.overlap_grid[tile.tile_idx]
                tile.update_settings()

    def exit_editor(self):
        """Function for exiting the editor"""
        self.clear_overlap_unimportant()
        for key in self.entity.entities.keys():
            if str(self.entity.entities[key]):
                self.background[2][key] = str(self.entity.entities[key])
            elif key in self.background[2]:
                del self.background[2][key]
        self.level_store.save_level(self.level_number, self.grid_width, self.grid_height, self.tile_grid,
                                    self.overlap_grid, self.entity_grid, self.time,
                                    [repr(value) for value in self.camera.values()], self.background)
        Tile.hide_hidden = True
        for tile in [t for t in self.tiles.tiles.values() if str(int(floor(t.idx))) in '16 18 24 26'] + \
                    [t for t in self.tiles.overlap_tiles.values() if str(int(floor(t.idx))) in '16 18 24 26']:
            tile.alpha = 10 if str(int(floor(tile.idx))) in '16 18' else 0
        self.editor_exit_func()

    def editor_mainloop(self):
        """Mainloop for editor"""
        if self.ent_menu:
            self.player_move = False
        elif not self.full_screen_menu:
            self.player_move = True
            if self.editor_permission and not self.door_placing:
                self.handle_main_keys()
            if self.editor:
                if self.camera_menu:
                    self.handle_camera_rect_inputs()
                if not self.door_placing:
                    self.handle_key_presses()
                touching_menu = py.mouse.get_pos()[1] > self.sc_width // 13 and \
                    py.mouse.get_pos()[0] > self.sc_width // 13
                if touching_menu or not self.show_menu:
                    if self.camera_menu:
                        self.draw_camera_menu()
                    else:
                        self.draw_ghost_block()
                        self.handle_paint_mouse()
        else:
            self.player_move = False
            self.handle_full_menu_keys()

        # Paint Mainloop
        if self.editor:
            if self.camera_menu:
                for rec in self.camera.values():
                    rec.editor_loop(self.tiles.camera_x, self.tiles.camera_y)

            if self.show_menu:
                self.handle_layers()
                if self.ent_menu and not self.camera_menu:
                    self.entity.entities[self.ent_menu].draw_edit_menu()
                elif self.ent_menu and self.camera_menu:
                    self.camera[self.ent_menu].draw_edit_menu()
                self.paint_menu()
            elif self.full_screen_menu == 'tiles':
                self.tiles_menu_mainloop()
            elif self.full_screen_menu == 'level':
                self.level_menu_mainloop()
            elif self.full_screen_menu == 'clear':
                self.clear_menu_mainloop()
            else:
                self.handle_layers()

    def handle_main_keys(self):
        """Handle main key inputs"""
        keys = py.key.get_pressed()
        if keys[py.K_ESCAPE]:
            self.esc_pressed = True
        else:
            if self.esc_pressed:
                self.handle_escape()
        if keys[py.K_DELETE]:
            self.del_pressed = True
        elif self.del_pressed:
            self.show_menu = not self.show_menu
            self.del_pressed = False

    def handle_escape(self):
        """Script for exiting out of editor mode"""
        self.editor = not self.editor
        self.tiles.tiles[-1].idx = -1
        self.tiles.tiles[-1].update_settings()
        self.esc_pressed = False
        self.l2 = 0
        self.rect_pos = []
        self.camera_menu = False
        if self.editor:
            self.refresh()
            self.setup_menu()
        else:
            self.exit_editor()

    def handle_full_menu_keys(self):
        """Handles key presses on tile menu"""
        keys = py.key.get_pressed()
        if keys[py.K_ESCAPE]:
            self.esc_pressed = True
        else:
            if self.esc_pressed:
                self.full_screen_menu = False
                self.show_menu = True
                self.esc_pressed = False

    """Menu Inputs"""

    def setup_menu(self):
        """Set up the editor main menu"""
        self.buttons = {}
        border, i = 4, 0
        length = self.sc_width // 13 - border * 2
        self.selected_tile.width = length + border * 2
        self.selected_tile.height = length + border * 2
        for i in range(0, 11):
            self.buttons[i] = {0: py.Rect((i * (self.sc_width // 13) + border, border), (length, length)), 1: '#ffffff'}
            if i > 0:
                self.tile_images[i] = Tile(self.tiles.tile_class, i * (self.sc_width // 13) + border * 2, border * 2,
                                           self.img_dict[i], i)
                self.tile_images[i].scale = (length - border * 2) / 70
            elif i == 0:
                self.tile_images[i] = (self.screen, '#F91717', (self.sc_width // 26, self.sc_width // 26),
                                       length / 2 - border * 2, 0)  # Creates a circle for the play button
        self.buttons[11] = {0: py.Rect(((i + 1) * (self.sc_width // 13) + border * 2, border), (length * 2, length)),
                            1: '#ffffff'}
        for i in range(12, 16):
            self.buttons[i] = {0: py.Rect((border, (i - 11) * (self.sc_width // 13) + border), (length, length)),
                               1: '#ffffff', 2: False}
        self.buttons[16] = {0: py.Rect((border, self.sc_height - border - length), (length, length)),
                            1: '#ffffff', 2: False}

    def paint_menu(self):
        """Paints the editor main menu"""
        selected_tile_color = '#F9eb00'  # Solid yellow/orange
        self.screen.blit(self.top_menu[0], self.top_menu[1])
        self.screen.blit(self.side_menu[0], self.side_menu[1])
        self.img_dict = {1: self.t1, 2: self.t2, 3: self.t3, 4: self.t4, 5: self.t5, 6: self.t6, 7: self.t7,
                         8: self.t8, 9: self.t9, 10: self.t0}

        for button in self.buttons:
            py.draw.rect(self.screen, self.buttons[button][1], self.buttons[button][0])
            if 0 < button < 11:
                self.tile_images[button].idx = self.img_dict[button]

                # Drawing outline on selected brush
                if self.img_dict[button] == self.chosen_brush:
                    self.selected_tile.x = button * (self.sc_width // 13)
                    py.draw.rect(self.screen, selected_tile_color, self.selected_tile)
                    py.draw.rect(self.screen, self.buttons[button][1], self.buttons[button][0])

                # Drawing the tile
                self.tile_images[button].image = \
                    self.tile_images[button].tiles_cls.tile[self.tile_images[button].idx].image
                self.tile_images[button].draw(self.screen)
            elif button == 0:
                py.draw.circle(self.tile_images[button][0], self.tile_images[button][1], self.tile_images[button][2],
                               self.tile_images[button][3], self.tile_images[button][4])
            elif button == 11:
                text_surf = self.font.render(self.level_number, True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                self.screen.blit(text_surf, text_rect)
            elif button == 12:
                text_surf = self.font.render('L2', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                self.screen.blit(text_surf, text_rect)
            elif button == 13:
                text_surf = self.font.render('C', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                py.draw.rect(self.screen, '#c3fc4e', text_rect)
                self.screen.blit(text_surf, text_rect)
            elif button == 14:
                text_surf = self.font.render('->', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                self.screen.blit(text_surf, text_rect)
            elif button == 15:
                text_surf = self.font.render('x+', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                self.screen.blit(text_surf, text_rect)
            elif button == 16:
                text_surf = self.font.render('R', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                py.draw.rect(self.screen, '#fc3636', text_rect)
                self.screen.blit(text_surf, text_rect)
            if not self.door_placing and not self.ent_menu:
                self.check_clicks_on_button(self.buttons[button][0], button)

        if not self.door_placing and not self.ent_menu:
            keys = py.key.get_pressed()
            if keys[py.K_BACKSPACE]:
                self.back_pressed = True
            elif self.back_pressed:
                self.handle_button(11)
                self.back_pressed = False
            if keys[py.K_CAPSLOCK]:
                self.caps_pressed = True
            elif self.caps_pressed:
                self.handle_button(12)
                self.caps_pressed = False

    def check_clicks_on_button(self, button, button_idx):
        """Checks if mouse clicks on the button"""
        mouse_pos = py.mouse.get_pos()
        toggle_button = 12 <= button_idx <= 14
        toggled = False
        if toggle_button:
            toggled = self.buttons[button_idx][2]
        if button.collidepoint(mouse_pos):
            if not (toggle_button and toggled):
                self.buttons[button_idx][1] = '#Eeeeed'
            if py.mouse.get_pressed()[0]:
                self.clicked = True
            elif self.clicked:
                self.clicked = False
                self.handle_button(button_idx)
        else:
            if not toggle_button:
                self.buttons[button_idx][1] = '#ffffff'
            elif not self.buttons[button_idx][2]:
                self.buttons[button_idx][1] = '#ffffff'

    def handle_button(self, button_idx):
        """Handles button click on a certain button"""
        if button_idx == 0:
            self.handle_escape()
        elif 0 < button_idx < 11:
            if button_idx < 10:
                self.button_pressed = button_idx
                self.full_screen_menu = 'tiles'
                self.show_menu = False
                self.tiles_menu_setup()
            self.chosen_brush = self.tile_images[button_idx].idx
        elif button_idx == 11:
            self.full_screen_menu = 'level'
            self.show_menu = False
            self.level_menu_setup()
        elif button_idx == 12:
            self.buttons[12][2] = not self.buttons[12][2]
            for i in (13, 14):
                self.buttons[i][2] = False
            if self.buttons[12][1]:
                self.buttons[12][1] = '#929291'
        elif button_idx == 13:
            self.buttons[13][2] = not self.buttons[13][2]
            self.rect_pos = []
            for i in (12, 14):
                self.buttons[i][2] = False
            if self.buttons[13][1]:
                self.buttons[13][1] = '#929291'
        elif button_idx == 14:
            self.buttons[14][2] = not self.buttons[14][2]
            for i in (12, 13):
                self.buttons[i][2] = False
            if self.buttons[14][1]:
                self.buttons[14][1] = '#929291'
        elif button_idx == 15:
            temp_list = list(self.tile_grid.keys())
            for idx in temp_list[-self.tiles.grid_height:]:
                del self.tile_grid[idx]
            self.tile_index = len(self.tile_grid) - 1
            self.add_boxed_column()
            self.add_wall_column()
            self.grid_width += 1
            self.grid_func()
        elif button_idx == 16:
            self.full_screen_menu = 'clear'
            self.show_menu = False
            self.clear_menu_setup()

        # Toggle Buttons for L2
        self.l2 = 0.5 if self.buttons[12][2] else 0
        # Camera Functions
        self.camera_menu = True if self.buttons[13][2] or self.buttons[14][2] else False

    def draw_camera_menu(self):
        """Drawing camera rectangle menu functions"""
        clicked = py.mouse.get_pressed()[0]
        if clicked:
            self.clicked = True
        elif self.clicked:
            if len(self.rect_pos) < 2:
                x, y = py.mouse.get_pos()
                self.rect_pos.append((x + self.tiles.camera_x, y + self.tiles.camera_y))
            self.clicked = False
        if len(self.rect_pos) == 2:
            pos1 = (round(min([self.rect_pos[0][0], self.rect_pos[1][0]])),
                    round(min([self.rect_pos[0][1], self.rect_pos[1][1]])))
            pos2 = (round(max([self.rect_pos[0][0], self.rect_pos[1][0]])),
                    round(max([self.rect_pos[0][1], self.rect_pos[1][1]])))
            new_idx = len(Camera_Rect.all_idx)
            self.camera[new_idx] = Camera_Rect(self.screen, new_idx, pos1, pos2, editor_cls=self)
            self.rect_pos = []

    def handle_camera_rect_inputs(self):
        """Handles keyboard inputs in camera rectangle menu"""
        if not self.show_menu:
            return None
        keys = py.key.get_pressed()
        if keys[py.K_SPACE]:
            for rec in self.camera.values():
                if rec.open:
                    self.ent_menu = rec.idx

    def tiles_menu_setup(self):
        """Set up tiles menu"""
        self.menu_buttons = {}
        tile_size = self.tiles.tile_class.tile[0].standard_tile_size
        border = 4
        # Sorting out tile dict from categories
        all_tiles = {key: value for key, value in sorted(self.tiles.tile_class.tile.items(),
                                                         key=lambda k: k[1].category)}
        current_category = ''
        add_y = 0
        category_add_y = 2
        i = 0
        y = 0
        for tile in all_tiles:
            if all_tiles[tile].category == 'None' or all_tiles[tile].category == 'N':
                continue
            x = (i % (self.sc_width // tile_size)) * tile_size
            y = tile_size * (i // (self.sc_width // tile_size)) + add_y
            if all_tiles[tile].category != current_category:
                current_category = all_tiles[tile].category
                text_surf = self.full_menu_font.render(current_category, True, (0, 0, 0))
                text_rect = text_surf.get_rect(topleft=(3, y + category_add_y))
                self.menu_buttons[current_category] = (text_rect, text_surf, y + category_add_y)
                add_y = text_rect.y + 30
                category_add_y = 40
                i = 0
                x = (i % (self.sc_width // tile_size)) * tile_size
                y = tile_size * (i // (self.sc_width // tile_size)) + add_y
            self.menu_buttons[tile] = {0: py.Rect((x, y), (tile_size - border, tile_size - border)),
                                       1: Tile(self.tiles.tile_class, x + border * 1.5, y + border * 1.5, tile, tile),
                                       2: '#ffffff', 3: y}
            self.menu_buttons[tile][1].scale = (tile_size - border * 3) / 70
            i += 1
        self.max_tile_y = y + tile_size

    def tiles_menu_mainloop(self):
        """Runs tiles menu"""
        bg_color = '#E0e0df'  # Light gray
        py.draw.rect(self.screen, bg_color, self.full_menu_bg)

        for tile in self.menu_buttons:
            if isinstance(tile, str):
                self.menu_buttons[tile][0].y = self.menu_buttons[tile][2] - self.tile_y
                self.screen.blit(self.menu_buttons[tile][1], self.menu_buttons[tile][0])
            else:
                self.menu_buttons[tile][1].draw_y = self.menu_buttons[tile][1].y - self.tile_y
                self.menu_buttons[tile][0].y = self.menu_buttons[tile][3] - self.tile_y
                py.draw.rect(self.screen, self.menu_buttons[tile][2], self.menu_buttons[tile][0])
                self.menu_buttons[tile][1].draw(self.screen)
                self.handle_tile_buttons(tile)

        keys = py.key.get_pressed()
        move_dict = {False: 0, True: 1}
        up = move_dict[keys[py.K_UP] or keys[py.K_w]]
        down = move_dict[keys[py.K_DOWN] or keys[py.K_s]]
        self.tile_y_vel += (down - up) * 0.1
        if abs(self.tile_y_vel) > 20:
            self.tile_y += self.tile_y_vel * 7
        elif abs(self.tile_y_vel) > 0:
            self.tile_y += self.tile_y_vel * 3
        if down - up == 0:
            if self.tile_y_vel < 3:
                self.tile_y_vel = 0
            self.tile_y_vel *= 0.6

        if self.tile_y < 0:
            self.tile_y = 0
            self.tile_y_vel = 0
        if self.tile_y > self.max_tile_y - self.sc_height:
            self.tile_y = self.max_tile_y - self.sc_height
            self.tile_y_vel = 0

    def handle_tile_buttons(self, button_idx):
        """Handle mouse and tile buttons"""
        mouse_pos = py.mouse.get_pos()
        if self.menu_buttons[button_idx][0].collidepoint(mouse_pos):
            self.menu_buttons[button_idx][2] = '#Eeeeed'
            if py.mouse.get_pressed()[0]:
                self.clicked = True
            elif self.clicked:
                self.clicked = False
                self.img_dict[self.button_pressed] = button_idx
                self.chosen_brush = button_idx
                self.t1, self.t2, self.t3, self.t4, self.t5, self.t6, self.t7, self.t8, self.t9 = \
                    [self.img_dict[t] for t in range(1, 10)]
                self.full_screen_menu = False
                self.show_menu = True
        else:
            self.menu_buttons[button_idx][2] = '#ffffff'

    def handle_key_presses(self):
        """Handles key presses on brushes"""
        keys = py.key.get_pressed()
        brush_combos = {0: (py.K_1, self.t1), 1: (py.K_2, self.t2), 2: (py.K_3, self.t3), 3: (py.K_4, self.t4),
                        4: (py.K_5, self.t5), 5: (py.K_6, self.t6), 6: (py.K_7, self.t7), 7: (py.K_8, self.t8),
                        8: (py.K_9, self.t9), 9: (py.K_0,)}
        for key in brush_combos:
            if keys[brush_combos[key][0]]:
                if key == 9:  # Eye dropper tool
                    x, y = py.mouse.get_pos()
                    self.chosen_brush = self.get_tile_at_pos(x + self.tiles.camera_x,
                                                             y + self.tiles.camera_y + self.tiles.tile_size)
                    if self.chosen_brush[1].tile_idx in self.entity_grid:
                        self.chosen_brush = self.entity_grid[self.chosen_brush[1].tile_idx]
                    else:
                        self.chosen_brush = floor(self.chosen_brush[1].idx)
                    self.t0 = self.chosen_brush
                else:
                    self.chosen_brush = brush_combos[key][1]
                break

    def level_menu_setup(self):
        """Set up level menu"""
        self.menu_buttons = {}
        x, y = self.sc_width / 10, self.sc_height / 10
        orig_x = x
        self.menu_buttons['bg'] = {0: 'Backgrounds', 1: (x, y), 2: '#000000'}
        y += self.full_menu_font.get_height() + 3
        all_backgrounds = self.background_cls.get_all_backgrounds((self.sc_width / 4, self.sc_height / 6), (x, y))
        i = 0
        for i in all_backgrounds:
            rect = all_backgrounds[i].image.get_rect(topleft=(all_backgrounds[i].x - 4, all_backgrounds[i].y - 4))
            rect.width += 8
            rect.height += 8
            self.menu_buttons[i] = {0: rect, 1: all_backgrounds[i].image, 2: '#ffffff', 3: ''}
            y = all_backgrounds[i].y
        y += all_backgrounds[i].image.get_height() + 3
        i += 1
        size = self.full_menu_font.size('Or Select Color Here')
        self.menu_buttons[i] = {0: py.Rect((x, y), (size[0] + 5, size[1] + 5)), 3: '',
                                1: self.full_menu_font.render('Or Select Color Here', True, '#000000'), 2: '#ffffff'}
        y += self.menu_buttons[i][0].height + 4
        self.menu_buttons['credit'] = {0: 'Show credits at the end of this level?', 1: (x, y), 2: '#000000'}
        x += self.full_menu_font.size('Show credits at the end of this level?')[0] + 5
        for name in ('Yes', 'No'):
            on_or_off = {'Yes': self.background[1] is True, 'No': self.background[1] is False}
            i += 1
            self.menu_buttons[i] = {0: py.Rect((x, y), (self.full_menu_font.size(name)[0] + 4,
                                                        self.full_menu_font.get_height() + 4)), 2: '#ffffff',
                                    1: self.full_menu_font.render(name, True, '#000000'), 3: on_or_off[name]}
            x += self.full_menu_font.size(name)[0] + 8
        x = orig_x
        y += self.full_menu_font.size('T')[1] + self.sc_height // 20
        self.menu_buttons['time'] = {0: 'Set time:', 1: (x, y), 2: '#000000'}
        x += self.full_menu_font.size('Set time')[0] + 5
        i += 1
        self.menu_buttons[i] = {0: py.Rect((x, y), (self.full_menu_font.size('8888')[0] + 4,
                                                    self.full_menu_font.get_height() + 4)), 2: '#ffffff',
                                1: self.full_menu_font.render(str(self.time), True, '#000000'), 3: False}

    def level_menu_mainloop(self):
        """Runs level menu"""
        bg_color = '#E0e0df'  # Light gray
        py.draw.rect(self.screen, bg_color, self.full_menu_bg)

        for button in self.menu_buttons:
            if isinstance(button, str):
                text_surf = self.full_menu_font.render(self.menu_buttons[button][0], True, self.menu_buttons[button][2])
                text_rect = text_surf.get_rect(topleft=self.menu_buttons[button][1])
                self.screen.blit(text_surf, text_rect)
            else:
                self.handle_level_menu_buttons(button)
                py.draw.rect(self.screen, self.menu_buttons[button][2], self.menu_buttons[button][0])
                self.screen.blit(self.menu_buttons[button][1],
                                 (self.menu_buttons[button][0].x + 4, self.menu_buttons[button][0].y + 4))

        if self.current_text == 'T':
            if self.user_text.isdigit():
                self.time = int(self.user_text)
                if self.time < 10:
                    self.time *= 10
                    if self.time < 10:
                        self.time = 10
            else:
                self.user_text = self.user_text[:-1]
            self.menu_buttons[7][1] = self.full_menu_font.render(str(self.time), True, '#000000')
        else:
            self.menu_buttons[7][3] = False

    def handle_level_menu_buttons(self, button_idx):
        """Handle mouse and level buttons"""
        change_button = (str(button_idx) in '5 6' and self.menu_buttons[button_idx][3]) or \
                        (self.menu_buttons[7][3] and button_idx == 7)
        if change_button:
            self.menu_buttons[button_idx][2] = '#bebebe'
        mouse_pos = py.mouse.get_pos()
        if self.menu_buttons[button_idx][0].collidepoint(mouse_pos):
            if not change_button:
                self.menu_buttons[button_idx][2] = '#Eeeeed'
            if py.mouse.get_pressed()[0]:
                self.clicked = True
            elif self.clicked:
                self.clicked = False
                self.handle_level_button_clicked(button_idx)
        else:
            if not change_button:
                self.menu_buttons[button_idx][2] = '#ffffff'

    def handle_level_button_clicked(self, button_idx):
        """Handles button clicks on level menu"""
        if 0 <= button_idx <= 4:
            if button_idx < 4:
                self.background[0] = button_idx
            else:
                background = self.background[0] if isinstance(self.background[0], str) else '#191919'
                color = askcolor(color=background, title='Choose a Color')
                self.background[0] = color[1] if color[1] is not None else background
            self.background_cls.init_background(self.background[0])
            self.full_screen_menu = False
            self.show_menu = True
        elif 5 <= button_idx <= 6:
            if self.menu_buttons[button_idx][3]:
                return None
            self.menu_buttons[button_idx][3] = True
            self.background[1] = (button_idx == 5)
            other_button = 6 if button_idx == 5 else 5
            self.menu_buttons[other_button][3] = False
        elif button_idx == 7:
            self.menu_buttons[button_idx][3] = True
            self.user_text = str(self.time)
            self.user_text_length = 4
            self.current_text = 'T'

    def clear_menu_setup(self):
        """Setup the level deleting and setting dimension menu"""
        self.menu_buttons = {}
        x, y = self.sc_width / 10, self.sc_height / 10
        orig_x = x
        self.menu_buttons['clr'] = {0: 'Clear Level Menu', 1: (x, y), 2: '#000000'}
        y += self.full_menu_font.get_height() + 10
        self.menu_buttons['dim'] = {0: 'Dimensions of new level:', 1: (x, y), 2: '#000000'}
        y += self.full_menu_font.get_height() + 5
        i = 0
        for label, text in (('x', self.grid_width), ('y', self.grid_height)):
            x += self.full_menu_font.get_height() + 5
            self.menu_buttons[label] = {0: label + ':', 1: (x, y), 2: '#000000'}
            x += self.full_menu_font.size('O')[0] + 2
            y -= 3
            self.menu_buttons[i] = {0: py.Rect(py.Rect((x, y), (self.full_menu_font.size('8888')[0] + 4,
                                    self.full_menu_font.get_height() + 4))), 2: '#ffffff', 4: '#bebebe', 5: '#ffffff',
                                    1: self.full_menu_font.render(str(self.n_grid_dims[i]), True, '#000000'), 3: False}
            x = orig_x
            y += self.full_menu_font.get_height() + 7
            if label == 'x':
                warning_text = 'This value can increase, but never decrease later. Set this wisely'
            else:
                warning_text = 'This value CANNOT be changed later, set this wisely'
            self.menu_buttons[f'{label}_war'] = {0: warning_text, 1: (x, y), 2: '#Fc1010'}
            y += self.full_menu_font.get_height()
            i += 1

        y = self.sc_height / 2
        self.menu_buttons['del'] = {0: 'Save above changes and reset whole level?', 1: (x, y), 2: '#000000'}
        y += self.full_menu_font.get_height() + 1
        self.menu_buttons['del_war'] = {1: (x, y), 2: '#Fc1010',
                                        0: 'WARNING: '
                                           'Resetting whole level will remove ALL previous changes to this level'}
        y += self.full_menu_font.get_height()
        for text in ('Reset Level', 'Cancel'):
            length = self.full_menu_font.size(text)[0] + 8
            col = '#Fc3636' if text == 'Reset Level' else '#6ffc36'
            d_col = '#Fa0707' if text == 'Reset Level' else '#2afa07'
            self.menu_buttons[i] = {0: py.Rect((x, y), (length, self.full_menu_font.get_height() + 4)), 2: col,
                                    4: d_col, 1: self.full_menu_font.render(text, True, '#000000'), 3: '', 5: col}
            x += length + 10
            i += 1

    def clear_menu_mainloop(self):
        """Draws the clear menu onto screen"""
        bg_color = '#E0e0df'  # Light gray
        py.draw.rect(self.screen, bg_color, self.full_menu_bg)

        for button in self.menu_buttons:
            if isinstance(button, str):
                font = self.small_menu_font if 'war' in button else self.full_menu_font
                text_surf = font.render(self.menu_buttons[button][0], True, self.menu_buttons[button][2])
                text_rect = text_surf.get_rect(topleft=self.menu_buttons[button][1])
                self.screen.blit(text_surf, text_rect)
            else:
                self.handle_clear_menu_buttons(button)
                br = 80 if button > 1 else 2
                py.draw.rect(self.screen, self.menu_buttons[button][5], self.menu_buttons[button][0], border_radius=br)
                self.screen.blit(self.menu_buttons[button][1],
                                 (self.menu_buttons[button][0].x + 4, self.menu_buttons[button][0].y + 4))

        if self.current_text is None:
            self.menu_buttons[0][3] = False
            self.menu_buttons[1][3] = False
            return None

        if not self.user_text.isdigit():
            if 'n_grid' in self.current_text:
                self.user_text = self.user_text[:-1]
            return None

        if self.current_text == 'n_grid_x' or self.current_text == 'n_grid_y':
            i = 0 if self.current_text == 'n_grid_x' else 1
            if i != 0:
                self.menu_buttons[0][3] = False
                if int(self.user_text) < ceil(self.sc_height / self.tiles.tile_size) + 1:
                    self.n_grid_dims[i] = ceil(self.sc_height / self.tiles.tile_size) + 1
            elif i != 1:
                self.menu_buttons[1][3] = False
                if int(self.user_text) < ceil(self.sc_width / self.tiles.tile_size) + 1:
                    self.n_grid_dims[i] = ceil(self.sc_width / self.tiles.tile_size) + 1
        else:
            return None

        min_value = {0: ceil(self.sc_width / self.tiles.tile_size) + 1,
                     1: ceil(self.sc_height / self.tiles.tile_size) + 1}
        self.n_grid_dims[i] = int(self.user_text)
        if self.n_grid_dims[i] < min_value[i]:
            self.n_grid_dims[i] = min_value[i]
        self.menu_buttons[i][1] = self.full_menu_font.render(str(self.n_grid_dims[i]), True, '#000000')

    def handle_clear_menu_buttons(self, button_idx):
        """Handle mouse and clear menu buttons"""
        change_button = button_idx < 2 and self.menu_buttons[button_idx][3]
        if change_button:
            self.menu_buttons[button_idx][5] = self.menu_buttons[button_idx][4]
        mouse_pos = py.mouse.get_pos()
        if self.menu_buttons[button_idx][0].collidepoint(mouse_pos):
            if button_idx < 2:
                self.menu_buttons[button_idx][5] = '#eeeeed'
            elif not change_button:
                self.menu_buttons[button_idx][5] = self.menu_buttons[button_idx][4]
            if py.mouse.get_pressed()[0]:
                self.clicked = True
            elif self.clicked:
                self.clicked = False
                self.handle_clear_button_clicked(button_idx)
        else:
            if not change_button:
                self.menu_buttons[button_idx][5] = self.menu_buttons[button_idx][2]

    def handle_clear_button_clicked(self, button_idx):
        """Handles button clicks on clear menu"""
        if button_idx < 2:
            self.menu_buttons[button_idx][3] = True
            self.user_text = str(self.n_grid_dims[button_idx])
            self.user_text_length = 4
            self.current_text = f"n_grid_{'x' if button_idx == 0 else 'y'}"
        elif button_idx == 2:
            text = self.font.render('Resetting Level...', True, '#000000')
            text_rect = text.get_rect(center=(self.sc_width / 2, self.sc_height / 2))
            self.screen.blit(text, text_rect)
            py.display.update()
            self.setup_func(level=self.level_number, blank=self.n_grid_dims)
            self.full_screen_menu = False
            self.show_menu = True
        elif button_idx == 3:
            self.full_screen_menu = False
            self.show_menu = True

    def handle_layers(self):
        """Handles painting of layers"""
        for tile in self.tiles.tiles.values():
            if tile.layer == 2:
                text_surf = self.tile_font.render('L2', True, (0, 0, 0))
                text_surf.set_alpha(135)
                text_rect = text_surf.get_rect(topleft=(tile.draw_x + 2, tile.draw_y + 2))
                self.screen.blit(text_surf, text_rect)
        for entity in self.entity.entities.values():
            if entity.group != 0:
                text_surf = self.tile_font.render(str(int(entity.group) if float(entity.group).is_integer()
                                                      else entity.group), True, (0, 0, 0))
                text_surf.set_alpha(155)
                text_rect = text_surf.get_rect(topright=(entity.draw_x + entity.width - 2, entity.draw_y + 2))
                self.screen.blit(text_surf, text_rect)

    """Level Interaction"""

    def handle_paint_mouse(self):
        """Handles mouse inputs"""
        mouse_buttons = py.mouse.get_pressed()
        if mouse_buttons[0]:  # If right-clicked on mouse
            x, y = py.mouse.get_pos()
            self.paint_tile_at(x, y, self.chosen_brush)
        elif mouse_buttons[2]:  # If left-clicked on mouse
            x, y = py.mouse.get_pos()
            self.paint_tile_at(x, y, -1)
        keys = py.key.get_pressed()
        if keys[py.K_SPACE] and not self.door_placing and self.show_menu:
            x, y = py.mouse.get_pos()
            x, y = x + self.tiles.camera_x, y + self.tiles.camera_y + self.tiles.tile_size
            tile_grid_x = floor(x / 32)
            tile_grid_y = -1 * floor((y - self.sc_height) / 32)
            tile_index = tile_grid_y + tile_grid_x * self.tiles.grid_height
            if tile_index in self.entity_grid:
                self.ent_menu = tile_index

    def draw_ghost_block(self):
        """Draws the ghost block underneath the mouse cursor, to show what tile is currently painting"""
        x, y = py.mouse.get_pos()
        self.tiles.tiles[-1].x = 32 * floor((x + self.tiles.camera_x) / 32)
        self.tiles.tiles[-1].y = -32 * floor((-1 * y - self.tiles.camera_y + self.tiles.tile_size) / 32)
        self.tiles.tiles[-1].draw_x = self.tiles.tiles[-1].x - self.tiles.camera_x
        self.tiles.tiles[-1].draw_y = self.tiles.tiles[-1].y - self.tiles.camera_y

        self.tiles.tiles[-1].idx = self.chosen_brush
        self.tiles.tiles[-1].update_settings()
        if self.tiles.tiles[-1].alpha != 100:
            self.tiles.tiles[-1].alpha = 100
        self.tiles.tiles[-1].draw(self.screen)

    def paint_tile_at(self, x, y, new_tile_idx=28):
        """Paints a tile onto the level"""
        if 0 < new_tile_idx < 566:
            # Adding l2 functions to blocks and not entities
            new_tile_idx += self.l2
        if new_tile_idx in self.once_tiles:
            # Checking for placing once only tiles/entities
            can_place = isinstance(self.once_tiles[new_tile_idx], bool)
            placing_once_tiles = True
        else:
            # Just any random tile/entity
            can_place = True
            placing_once_tiles = False
        if not can_place:
            return None

        replace_tile = self.get_tile_at_pos(x + self.tiles.camera_x, y + self.tiles.camera_y + self.tiles.tile_size)
        # On the edge of the levels cannot be air blocks
        if replace_tile[1].tile_idx < self.grid_height or \
                replace_tile[1].tile_idx % self.grid_height == self.grid_height - 1 or \
                replace_tile[1].tile_idx >= self.grid_width * self.grid_height - self.grid_height:
            return None

        if placing_once_tiles:
            self.once_tiles[new_tile_idx] = replace_tile[1].tile_idx
        elif replace_tile[1].tile_idx in self.once_tiles.values() and \
                replace_tile[1].idx not in self.once_tiles.keys():
            # Finding the specific key: value, then update once_tiles dictionary as the tile no longer exists
            idx = {key: value for key, value in self.once_tiles.items() if value == replace_tile[1].tile_idx}
            if idx:
                idx = tuple(idx.keys())[0]
                self.once_tiles[idx] = True

        # Checking l2 and l1
        layer = replace_tile[1].layer == 2 or replace_tile[2]

        if new_tile_idx in self.entity.entity_dict:
            # Entities
            if replace_tile[1].tile_idx in self.entity_grid and new_tile_idx < 566:
                return None
            self.entity_grid[replace_tile[1].tile_idx] = new_tile_idx
            self.entity.grid_list[replace_tile[1].tile_idx] = new_tile_idx
            info = '0'
            # If placing a door
            if isinstance(self.entity.entity_dict[new_tile_idx], list):
                if len(self.entity.entity_dict[new_tile_idx]) > 2:
                    if self.door_placing:
                        self.entity.entities[self.door_placing].other_door = replace_tile[1].tile_idx
                        self.entity.entities[self.door_placing].group = self.entity.total_doors + 1
                        info = f'{self.door_placing}-{self.entity.total_doors + 1}'
                        self.background[2][self.door_placing] = str(self.entity.entities[self.door_placing])
                        self.door_placing = False
                    else:
                        self.door_placing = replace_tile[1].tile_idx
                        info = None
            self.entity.add_to_entities(replace_tile[1].tile_idx, new_tile_idx, info)
            self.background[2][replace_tile[1].tile_idx] = info
        elif layer and round(new_tile_idx) == new_tile_idx and self.l2 != 0.5:
            # Layer 2
            if new_tile_idx < 0 and replace_tile[1].tile_idx in self.entity_grid:
                # Deleting in entities
                if isinstance(self.entity.entity_dict[int(self.entity.grid_list[replace_tile[1].tile_idx])], list):
                    if len(self.entity.entity_dict[int(self.entity.grid_list[replace_tile[1].tile_idx])]) > 2:
                        # Deleting in doors
                        del_idx = self.entity.entities[replace_tile[1].tile_idx].other_door
                        if del_idx in self.entity_grid:
                            del self.entity_grid[del_idx], self.entity.grid_list[del_idx], self.background[2][del_idx]
                            self.entity.delete_from_entities(del_idx)
                        else:
                            self.door_placing = False
                del self.entity_grid[replace_tile[1].tile_idx], self.entity.grid_list[replace_tile[1].tile_idx]
                if replace_tile[1].tile_idx in self.background[2]:
                    del self.background[2][replace_tile[1].tile_idx]
                self.entity.delete_from_entities(replace_tile[1].tile_idx)
                if replace_tile[1].tile_idx == self.ent_menu:
                    self.ent_menu = False
            else:

                self.overlap_grid[replace_tile[1].tile_idx] = new_tile_idx
                self.tiles.overlap_grid[replace_tile[1].tile_idx] = new_tile_idx

                self.tiles.overlap_tiles[replace_tile[0]].idx = new_tile_idx
                self.tiles.overlap_tiles[replace_tile[0]].update_settings()
        else:
            # Layer 1
            if new_tile_idx < 0 and replace_tile[1].tile_idx in self.entity_grid:
                # Deleting in entities
                if isinstance(self.entity.entity_dict[int(self.entity.grid_list[replace_tile[1].tile_idx])], list):
                    if len(self.entity.entity_dict[int(self.entity.grid_list[replace_tile[1].tile_idx])]) > 2:
                        # Deleting in doors
                        del_idx = self.entity.entities[replace_tile[1].tile_idx].other_door
                        if del_idx in self.entity_grid:
                            del self.entity_grid[del_idx], self.entity.grid_list[del_idx], self.background[2][del_idx]
                            self.entity.delete_from_entities(del_idx)
                        else:
                            self.door_placing = False
                del self.entity_grid[replace_tile[1].tile_idx], self.entity.grid_list[replace_tile[1].tile_idx]
                if replace_tile[1].tile_idx in self.background[2]:
                    del self.background[2][replace_tile[1].tile_idx]
                self.entity.delete_from_entities(replace_tile[1].tile_idx)
                if replace_tile[1].tile_idx == self.ent_menu:
                    self.ent_menu = False
            elif new_tile_idx < 0 and self.tile_grid[replace_tile[1].tile_idx] == -1:
                self.draw_coordinates_at(replace_tile[1].tile_idx, (x, y))
            else:

                # Updating tile grids
                self.tile_grid[replace_tile[1].tile_idx] = new_tile_idx
                self.tiles.grid_list[replace_tile[1].tile_idx] = new_tile_idx

                # Updating tile properties
                self.tiles.tiles[replace_tile[0]].idx = new_tile_idx
                self.tiles.tiles[replace_tile[0]].update_settings()

    def draw_coordinates_at(self, tile_idx, mouse_pos: tuple):
        """Draws the coordinates on screen according to tile index"""
        border = 2
        x, y = tile_idx // self.grid_height, tile_idx % self.grid_height
        text = self.full_menu_font.render(f"({x}, {y})", True, '#000000')
        if mouse_pos[0] + text.get_width() + border * 2 > self.sc_width:
            rect = text.get_rect(topright=mouse_pos)
        else:
            rect = text.get_rect(topleft=mouse_pos)
        rect.width += border * 2
        rect.height += border * 2
        py.draw.rect(self.screen, '#ffebcb', rect)
        self.screen.blit(text, (rect.x + border, rect.y + border))

    def clear_overlap_unimportant(self):
        del_items = set()
        for tile, tile_idx in self.overlap_grid.items():
            if tile_idx < 0:
                del_items.add(tile)
        for item in del_items:
            del self.overlap_grid[item]

    def get_tile_at_pos(self, x, y):
        """Collect the tile index at a certain position"""
        tile_grid_x = floor(x / 32)
        tile_grid_y = -1 * floor((y - self.sc_height) / 32)  # y level starts at sc_height and decreases
        tile_index = tile_grid_y + tile_grid_x * self.tiles.grid_height

        overlap = True
        tile = {key: value for key, value in self.tiles.overlap_tiles.items() if value.tile_idx == tile_index
                and value.idx != -1}
        if len(tile) < 1:
            overlap = False
            tile = {key: value for key, value in self.tiles.tiles.items() if value.tile_idx == tile_index}

        if len(tile) < 1:
            if y > self.sc_height + 32:
                self.tiles.tiles[-1].tile_idx = -1
                self.tiles.tiles[-1].idx = -1
                self.tiles.tiles[-1].update_settings()
                return -1, self.tiles.tiles[-1], False
            self.tiles.tiles[-1].tile_idx = tile_index
            self.tiles.tiles[-1].idx = self.tiles.grid_list[tile_index]
            self.tiles.tiles[-1].update_settings()
            return -1, self.tiles.tiles[-1], True

        if overlap:
            return tuple(tile.keys())[0], self.tiles.overlap_tiles[tuple(tile.keys())[0]], overlap
        else:
            return tuple(tile.keys())[0], self.tiles.tiles[tuple(tile.keys())[0]], overlap

    def get_animation_frames(self, tile) -> int:
        """Gets the animations frames (for entities)"""
        category = 'None'
        i = 0
        while category == 'None':
            tile += 1
            i += 1
            if tile + 2 > len(self.tiles.tile_class.tile):
                break
            category = self.tiles.tile_class.tile[tile].category
        return i


def setup():
    """Set up the Level"""
    width, height = 480, 320
    win = py.display.set_mode((width, height))
    py.display.set_caption("Generate Level Test")
    level = Level(win, '')

    camera_x = 0
    camera_y = 0
    level.generate_level('1-1', level)
    tile = Tiles(win, camera_x, camera_y, join("Level_Tiles", "Tile_Arts"))

    tile.setup((level.grid_width, level.grid_height), level.tile_grid)
    return win, camera_x, camera_y, tile


def draw_level(tile_cls):
    """Draws the level onto the screen"""
    tile_cls.position_tiles(True)


if __name__ == '__main__':
    py.init()
    screen, CAMERA_X, CAMERA_Y, TILE = setup()
    clock = py.time.Clock()

    j = 0
    run = True
    while run:
        screen.fill((25, 25, 25))
        draw_level(TILE)
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
        if j % 2 < 1:
            CAMERA_X += 10
            CAMERA_Y += -5

        TILE.camera_x = CAMERA_X
        TILE.camera_y = CAMERA_Y
        py.display.update()
        clock.tick(60)
        j += 1
    py.quit()
