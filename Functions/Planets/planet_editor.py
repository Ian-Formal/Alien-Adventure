import pygame as py
from math import floor, ceil

try:
    from .Tiles.tiles import Tiles, Tile
    from .Planet_Store.planet_store import Planet_Store
    from .Paths.pathfinder import Worlds, Levels, Manage_Level
    from .Paths.player_progress import Player_Progress
except ImportError:
    from Tiles.tiles import Tiles, Tile
    from Planet_Store.planet_store import Planet_Store
    from Paths.pathfinder import Worlds, Levels, Manage_Level
    from Paths.player_progress import Player_Progress


class Planet:
    """Generating the planet"""
    __slots__ = 'screen', 'path', 'sc_width', 'sc_height', 'tile_grid', 'overlap_grid', 'levels', 'worlds', \
                'grid_width', 'grid_height', 'tile_idx', 'planet_name', 'planet_store'

    def __init__(self, win: py.display, path):
        """Planet functions"""
        self.screen = win
        self.path = path
        self.sc_width, self.sc_height = self.screen.get_size()
        self.tile_grid = {}
        self.overlap_grid = {}
        self.levels = {}
        self.worlds = {}
        self.grid_width = 0
        self.grid_height = 0
        self.tile_idx = 0
        self.planet_name = ''

        self.planet_store = Planet_Store(self.path)

    def setup_database(self, db):
        self.planet_store.setup_database(db)

    def get_planet(self, blank):
        """Gets planet code"""
        self.planet_name, self.grid_width, self.grid_height, self.tile_grid, self.overlap_grid, self.levels, \
            self.worlds = self.planet_store.load_planet()
        if not self.tile_grid or blank:
            self.generate_blank_planet(blank)
            return None
        self.levels = {int(key): Levels(value[0], value[1], value[2], int(key)) for key, value in self.levels.items()}
        self.worlds = {key: Worlds(self.screen, (int(value[3]), int(value[1])), (int(value[4]), int(value[2])),
                                   name=value[0], color=value[5]) for key, value in self.worlds.items()}

        # Copied from tile properties
        node_dict = {90: '<>^v', 91: '^>', 92: '<^', 100: 'v>', 101: '<>', 102: '<v>', 103: '<^>', 104: '^>v',
                     112: '^v', 113: '<^v', 114: '<>', 115: '.', 116: '<v', 124: '<>', 125: '^v', 126: '.', 127: '.',
                     128: '^v', 129: '^v', 130: '^v', 131: '^v', 137: '<>', 138: '^v', 139: '<>', 140: '<>', 141: '<>',
                     142: '<>', 195: '.'}

        for idx, levels in self.levels.items():
            levels.init_gray_arrows(node_dict[self.overlap_grid[idx]])

    def generate_blank_planet(self, grid_dims=None):
        """Generates a blank planet"""
        if grid_dims is None:
            grid_dims = (800, 800)
        self.planet_name = 'My World'
        self.tile_grid = {}
        self.overlap_grid = {}
        self.levels = {}
        self.worlds = {}
        self.grid_width = grid_dims[0]
        self.grid_height = grid_dims[1]
        for i in range(0, self.grid_width * self.grid_height):
            self.tile_grid[i] = 0


class Editor(Planet):
    """Planet Editor"""
    __slots__ = 'tiles', 'save_file', 'editor', 'del_pressed', 'esc_pressed', 'caps_pressed', 'clicked', 'show_menu', \
                'full_screen_menu', 'rect_menu', 'current_level', 'current_text', 'in_level', 'buttons', \
                'level_buttons', 'top_menu', 'side_menu', 'level_menu', 'selected_tile', 'font', 'user_text', \
                'user_text_length', 'rect_pos', 'button_pressed', 'full_menu_font', 'small_menu_font', 'full_menu_bg', \
                'menu_buttons', 'tile_y', 'max_tile_y', 'tile_y_vel', 'chosen_brush', 't1', 't2', 't3', 't4', 't5', \
                't6', 't7', 't8', 't9', 't0', 'img_dict', 'tile_images', 'tile_font', 'pathfind', 'progress', \
                'n_grid_dims', 'setup_func', 'grid_func'

    def __init__(self, win: py.display, path, *, tiles_cls, setup_func, grid_func):
        super().__init__(win, path)
        self.tiles = tiles_cls
        self.save_file = None
        self.editor = False
        self.del_pressed = False
        self.esc_pressed = False
        self.caps_pressed = False
        self.clicked = False
        self.show_menu = True
        self.full_screen_menu = False
        self.rect_menu = False
        self.current_level = None
        self.current_text = None
        self.in_level = False

        # Menu Items
        self.buttons = {}
        self.level_buttons = {}
        self.top_menu = (py.Surface((self.sc_width, self.sc_width // 13)), (0, 0))
        self.side_menu = (py.Surface((self.sc_width // 13, self.sc_width)), (0, 0))
        self.level_menu = (py.Surface((self.sc_width, self.sc_width // 13)), (0, self.sc_height - self.sc_width // 13))
        self.selected_tile = py.Rect((0, 0), (self.sc_width, self.sc_width // 13))
        self.font = py.font.Font(None, self.sc_width // 13 - 3)
        self.user_text = ''
        self.user_text_length = 10
        self.rect_pos = []

        self.top_menu[0].fill('#E0e0df')
        self.top_menu[0].set_alpha(135)
        self.side_menu[0].fill('#E0e0df')
        self.side_menu[0].set_alpha(135)
        self.level_menu[0].fill('#E0e0df')
        self.level_menu[0].set_alpha(135)

        # Tiles menu
        self.button_pressed = 0
        self.full_menu_font = py.font.Font(None, 30)
        self.small_menu_font = py.font.Font(None, 15)
        self.full_menu_bg = py.Rect((0, 0), (self.sc_width, self.sc_width))
        self.menu_buttons = {}
        self.tile_y = 0
        self.max_tile_y = 0
        self.tile_y_vel = 0

        # Brushes
        self.chosen_brush = 28
        self.t1, self.t2, self.t3, self.t4, self.t5, self.t6, self.t7, self.t8, self.t9, self.t0 = \
            [i for i in range(20, 30)]
        self.img_dict = {1: self.t1, 2: self.t2, 3: self.t3, 4: self.t4, 5: self.t5, 6: self.t6, 7: self.t7, 8: self.t8,
                         9: self.t9, 10: self.t0}
        self.tile_images = {}
        self.tile_font = py.font.Font(None, self.tiles.tile_size // 2)

        self.pathfind = Manage_Level(self)
        self.progress = None
        self.n_grid_dims = [self.grid_width, self.grid_height]
        self.setup_func = setup_func
        self.grid_func = grid_func

    def setup_pathfinding(self):
        """Setup pathfinding grid_height"""
        self.pathfind.grid_height = self.grid_height
        self.progress = Player_Progress(self.save_file, self.path, self)
        if not self.editor:
            for idx, level in self.levels.items():
                if idx in self.progress.paths:
                    level.idx = 196
                if self.progress.level_data[level.id]['state'] != '':
                    level.idx = 197

    def editor_mainloop(self):
        """Mainloop for editor"""
        if not self.full_screen_menu:
            self.handle_main_keys()
            if self.editor:
                if not self.rect_menu:
                    self.handle_key_presses()
                else:
                    self.handle_rect_inputs()
                if self.level_buttons:
                    touching_menu = self.sc_width // 13 < py.mouse.get_pos()[1] < self.sc_height - \
                                    self.sc_width // 13 and py.mouse.get_pos()[0] > self.sc_width // 13
                else:
                    touching_menu = self.sc_width // 13 < py.mouse.get_pos()[1] and \
                                    py.mouse.get_pos()[0] > self.sc_width // 13
                if self.rect_menu:
                    if touching_menu:
                        self.draw_rect_menu()
                elif touching_menu or not self.show_menu:
                    self.draw_ghost_block()
                    self.handle_inputs()
        else:
            self.handle_tile_menu_keys()

        # Paint Mainloop
        if self.editor:
            if self.show_menu:
                if self.rect_menu:
                    for world in self.worlds.values():
                        world.editor_loop(self.tiles.camera_x, self.tiles.camera_y)
                self.paint_menu()
                if self.level_buttons:
                    self.level_menu_mainloop()
            elif self.full_screen_menu == 'tiles':
                self.tiles_menu_mainloop()
            elif self.full_screen_menu == 'clear':
                self.clear_menu_mainloop()

    def handle_main_keys(self):
        keys = py.key.get_pressed()
        if keys[py.K_DELETE]:
            self.del_pressed = True
        elif self.del_pressed:
            self.show_menu = not self.show_menu
            self.del_pressed = False

    def handle_tile_menu_keys(self):
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
        """Set up the menu"""
        self.n_grid_dims = [self.grid_width, self.grid_height]
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
        for i in range(11, 14):
            self.buttons[i] = {0: py.Rect((border, (i - 10) * (self.sc_width // 13) + border), (length, length)),
                               1: '#ffffff', 2: False}

    def paint_menu(self):
        """Paints the menu"""
        selected_tile_color = '#F9eb00'  # Solid yellow/orange
        # self.handle_layers()
        self.draw_arrows()
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
                    self.tile_images[button].tiles_cls.tiles[self.tile_images[button].idx].image
                self.tile_images[button].draw(self.screen)
            elif button == 0:
                text_surf = self.font.render('<-', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                self.screen.blit(text_surf, text_rect)
            elif button == 11:
                text_surf = self.font.render('Wr', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                self.screen.blit(text_surf, text_rect)
            elif button == 12:
                text_surf = self.font.render('x+', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                self.screen.blit(text_surf, text_rect)
            elif button == 13:
                text_surf = self.font.render('R', True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.buttons[button][0].center)
                py.draw.rect(self.screen, '#fc3636', text_rect)
                self.screen.blit(text_surf, text_rect)
            self.check_clicks_on_button(self.buttons[button][0], button)

        keys = py.key.get_pressed()
        if keys[py.K_CAPSLOCK]:
            self.caps_pressed = True
        elif self.caps_pressed:
            self.handle_button(11)
            self.caps_pressed = False

    def check_clicks_on_button(self, button, button_idx):
        """Checks if mouse clicks on the button"""
        mouse_pos = py.mouse.get_pos()
        if button.collidepoint(mouse_pos):
            if button_idx != 11 or not self.buttons[11][2]:
                self.buttons[button_idx][1] = '#Eeeeed'
            if py.mouse.get_pressed()[0]:
                self.clicked = True
            elif self.clicked:
                self.clicked = False
                self.handle_button(button_idx)
        else:
            if button_idx != 11:
                self.buttons[button_idx][1] = '#ffffff'
            elif not self.buttons[button_idx][2]:
                self.buttons[button_idx][1] = '#ffffff'

    def handle_button(self, button_idx):
        """Handles button click on a certain button"""
        if button_idx == 0:
            self.planet_store.save_planet(self.planet_store.planet_name, self.grid_width, self.grid_height,
                                          self.tile_grid, self.overlap_grid,
                                          {key: value.get_list() for key, value in self.levels.items()},
                                          [repr(value) for value in self.worlds.values()])
        elif 0 < button_idx < 11:
            if button_idx < 10:
                self.button_pressed = button_idx
                self.full_screen_menu = 'tiles'
                self.show_menu = False
                self.tiles_menu_setup()
            self.chosen_brush = self.tile_images[button_idx].idx
        elif button_idx == 11:
            self.buttons[11][2] = not self.buttons[11][2]
            self.rect_pos = []
            self.level_buttons = {}
            if self.buttons[11][2]:
                self.rect_menu = True
                self.buttons[11][1] = '#929291'
            else:
                self.rect_menu = False
        elif button_idx == 12:
            for idx in range(len(self.tile_grid), len(self.tile_grid) + self.grid_height):
                self.tile_grid[idx] = 0
            self.grid_width += 1
            self.grid_func()
        elif button_idx == 13:
            self.full_screen_menu = 'clear'
            self.show_menu = False
            self.clear_menu_setup()

    def draw_rect_menu(self):
        """Drawing world rectangle menu functions"""
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
            world = Worlds(self.screen, pos1, pos2)
            i = 0
            while self.worlds:
                if i > 0:
                    world.name = world.name[:-1]
                i += 1
                world.name = world.name + str(i)
                if world.name not in self.worlds:
                    break
            self.worlds[world] = world
            self.rect_pos = []

    def tiles_menu_setup(self):
        """Set up tiles menu"""
        self.menu_buttons = {}
        tile_size = self.tiles.tile_class.tiles[0].tile_size
        border = 4
        # Sorting out tile dict from categories
        all_tiles = {key: value for key, value in sorted(self.tiles.tile_class.tiles.items(),
                                                         key=lambda k: k[1].category)}
        current_category = ''
        add_y = 0
        category_add_y = 2
        i = 0
        y = 0
        for tile in all_tiles:
            if all_tiles[tile].category == 'Fog' or all_tiles[tile].category == 'Shadows':
                continue
            x = (i % 12) * tile_size
            y = tile_size * (i // 12) + add_y
            if all_tiles[tile].category != current_category:
                current_category = all_tiles[tile].category
                text_surf = self.full_menu_font.render(current_category, True, (0, 0, 0))
                text_rect = text_surf.get_rect(topleft=(3, y + category_add_y))
                self.menu_buttons[current_category] = (text_rect, text_surf, y + category_add_y)
                add_y = text_rect.y + 30
                category_add_y = 40
                i = 0
                x = (i % 12) * tile_size
                y = tile_size * (i // 12) + add_y
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
                self.menu_buttons[tile][1].draw(self.screen, True)
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
        """Handles key presses"""
        keys = py.key.get_pressed()
        brush_combos = {0: (py.K_1, self.t1), 1: (py.K_2, self.t2), 2: (py.K_3, self.t3), 3: (py.K_4, self.t4),
                        4: (py.K_5, self.t5), 5: (py.K_6, self.t6), 6: (py.K_7, self.t7), 7: (py.K_8, self.t8),
                        8: (py.K_9, self.t9), 9: (py.K_0,)}
        for key in brush_combos:
            if keys[brush_combos[key][0]]:
                if key == 9:  # Eye dropper tool
                    x, y = py.mouse.get_pos()
                    self.chosen_brush = self.get_tile_at_pos(x + self.tiles.camera_x,
                                                             y + self.tiles.camera_y + self.tiles.tile_size)[1].idx
                    self.t0 = self.chosen_brush
                else:
                    self.chosen_brush = brush_combos[key][1]
                break

    def clear_menu_setup(self):
        """Setup the level deleting and setting dimension menu"""
        self.menu_buttons = {}
        x, y = self.sc_width / 10, self.sc_height / 10
        orig_x = x
        self.menu_buttons['clr'] = {0: 'Clear Planet Menu (Does not clear level data)', 1: (x, y), 2: '#000000'}
        y += self.full_menu_font.get_height() + 10
        self.menu_buttons['dim'] = {0: 'Dimensions of the new planet:', 1: (x, y), 2: '#000000'}
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
        self.menu_buttons['del'] = {0: 'Save above changes and reset whole planet?', 1: (x, y), 2: '#000000'}
        y += self.full_menu_font.get_height() + 1
        self.menu_buttons['del_war'] = {1: (x, y), 2: '#Fc1010',
                                        0: 'WARNING: '
                                           'Resetting whole level will remove ALL previous changes to this level'}
        y += self.full_menu_font.get_height()
        for text in ('Reset Planet', 'Cancel'):
            length = self.full_menu_font.size(text)[0] + 8
            col = '#Fc3636' if text == 'Reset Planet' else '#6ffc36'
            d_col = '#Fa0707' if text == 'Reset Planet' else '#2afa07'
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
            text = self.font.render('Resetting Planet...', True, '#000000')
            text_rect = text.get_rect(center=(self.sc_width / 2, self.sc_height / 2))
            self.screen.blit(text, text_rect)
            py.display.update()
            self.setup_func(self.save_file, blank=self.n_grid_dims)
            self.full_screen_menu = False
            self.show_menu = True
        elif button_idx == 3:
            self.full_screen_menu = False
            self.show_menu = True

    def handle_layers(self):
        """Handles painting of layers"""
        for tile in self.tiles.tiles:
            tile = self.tiles.tiles[tile]
            if tile.layer == 2:
                text_surf = self.tile_font.render('L2', True, (0, 0, 0))
                text_surf.set_alpha(135)
                text_rect = text_surf.get_rect(topleft=(tile.draw_x + 2, tile.draw_y + 2))
                self.screen.blit(text_surf, text_rect)

    def show_level_menu(self, level):
        """Shows the level menu for a given level"""
        self.level_buttons = {}
        border, i = 4, 0
        length = self.sc_width // 13 - border * 2
        x = i * (self.sc_width // 13) + border
        l_ = self.sc_width / 2.63
        for add_length, text in ((l_ / 16, 'Edit'), (l_ / 21, level.id), (l_ / 1.12, level.name), (0, '^'), (0, 'v'),
                                 (0, '<'), (0, '>'), (0, 'x')):
            text_surf = self.font.render(text, True, (0, 0, 0))
            self.level_buttons[i] = {0: py.Rect((x, self.sc_height - border - length),
                                                (length + add_length, length)), 1: text_surf, 2: '#ffffff', 3: False}
            x += length + add_length + border * 2
            i += 1
        self.current_level = level

    def show_world_menu(self, world):
        """Shows the world menu for a world rectangle"""
        self.level_buttons = {}
        border, i = 4, 0
        length = self.sc_width // 13 - border * 2
        x = i * (self.sc_width // 13) + border
        l_ = self.sc_width / 2.63
        for add_length, text, idx in ((l_ / 2.3, world.col, 1), (l_ / 1.12, world.name, 2), (l_ / 2.3, 'Delete', 0),
                                      (0, 'x', 7)):
            text_surf = self.font.render(text, True, (0, 0, 0))
            self.level_buttons[idx] = {0: py.Rect((x, self.sc_height - border - length),
                                                  (length + add_length, length)), 1: text_surf, 2: '#ffffff', 3: False}
            x += length + add_length + border * 2
            i += 1
        self.current_level = world

    def level_menu_mainloop(self):
        """SHows level menu"""
        self.screen.blit(self.level_menu[0], self.level_menu[1])

        for button in self.level_buttons:
            if button not in self.level_buttons:
                continue
            py.draw.rect(self.screen, self.level_buttons[button][2], self.level_buttons[button][0])
            if button == 1:
                if self.rect_menu:
                    text_surf = self.font.render(self.current_level.col, True, (0, 0, 0), self.current_level.col)
                else:
                    text_surf = self.font.render(self.current_level.id, True, (0, 0, 0))
            elif button == 2:
                text_surf = self.font.render(self.current_level.name, True, (0, 0, 0))
            else:
                text_surf = self.level_buttons[button][1]
            text_rect = text_surf.get_rect(center=self.level_buttons[button][0].center)
            self.screen.blit(text_surf, text_rect)
            self.handle_clicks_on_button(self.level_buttons[button][0], button)

        if self.current_text == 'id':
            self.current_level.id = self.user_text
        elif self.current_text == 'name':
            self.current_level.name = self.user_text
        elif self.level_buttons:
            self.level_buttons[1][3] = False
            self.level_buttons[2][3] = False

    def handle_clicks_on_button(self, button, button_idx):
        """Checks if mouse clicks on the button, for level menu buttons"""
        mouse_pos = py.mouse.get_pos()
        if button.collidepoint(mouse_pos):
            if not self.level_buttons[button_idx][3]:
                self.level_buttons[button_idx][2] = '#Eeeeed'
            if py.mouse.get_pressed()[0]:
                self.clicked = True
            elif self.clicked:
                self.clicked = False
                self.level_buttons[button_idx][3] = not self.level_buttons[button_idx][3]
                self.handle_level_button(button_idx)
        elif not self.level_buttons[button_idx][3]:
            self.level_buttons[button_idx][2] = '#ffffff'

    def handle_level_button(self, button_idx):
        if button_idx == 0:
            self.level_buttons[button_idx][3] = False
            if self.rect_menu:
                del self.worlds[self.current_level.name]
                self.level_buttons = {}
            else:
                self.in_level = self.current_level.tile_idx
        elif button_idx == 1:
            self.level_buttons[button_idx][2] = '#Afafac'
            if self.rect_menu:
                self.current_level.open_colorchooser()
            else:
                self.user_text = self.current_level.id
                self.user_text_length = 4
                self.current_text = 'id'
        elif button_idx == 2:
            self.level_buttons[button_idx][2] = '#Afafac'
            self.user_text = self.current_level.name
            self.user_text_length = 15
            self.current_text = 'name'
        elif button_idx == 7:
            self.level_buttons = {}
        else:
            self.level_buttons[button_idx][3] = False
            button_dict = {3: '^', 4: 'v', 5: '<', 6: '>'}
            self.current_level.change_arrow(button_dict[button_idx])

    """Planet Interaction"""

    def handle_rect_inputs(self):
        """Handles keyboard inputs in rect menu"""
        keys = py.key.get_pressed()
        if keys[py.K_SPACE]:
            for world in self.worlds.values():
                if world.open:
                    self.show_world_menu(world)

    def handle_inputs(self):
        """Handles mouse and keyboard inputs"""
        mouse_buttons = py.mouse.get_pressed()
        keys = py.key.get_pressed()
        if mouse_buttons[0]:  # If right-clicked on mouse
            x, y = py.mouse.get_pos()
            self.paint_tile_at(x, y, self.chosen_brush)
        elif mouse_buttons[2]:  # If left-clicked on mouse
            x, y = py.mouse.get_pos()
            if not self.get_tile_at_pos(
                    x + self.tiles.camera_x, y + self.tiles.camera_y + self.tiles.tile_size)[1].tile_idx in self.levels:
                self.paint_tile_at(x, y, -1)
            else:
                self.clicked = True
        elif self.clicked:
            self.clicked = False
            x, y = py.mouse.get_pos()
            self.paint_tile_at(x, y, -1)
        if keys[py.K_SPACE]:
            x, y = py.mouse.get_pos()
            replace_tile = self.get_tile_at_pos(x + self.tiles.camera_x, y + self.tiles.camera_y + self.tiles.tile_size)
            if replace_tile[1].tile_idx in self.levels:
                self.show_level_menu(self.levels[replace_tile[1].tile_idx])

    def draw_ghost_block(self):
        """Draws the ghost block underneath the mouse cursor, to show what tile is currently painting"""
        x, y = py.mouse.get_pos()
        self.tiles.tiles[-1].x = 32 * floor((x + self.tiles.camera_x) / 32)
        self.tiles.tiles[-1].y = -32 * floor((-1 * y - self.tiles.camera_y + self.tiles.tile_size) / 32)
        self.tiles.tiles[-1].draw_x = self.tiles.tiles[-1].x - self.tiles.camera_x
        self.tiles.tiles[-1].draw_y = self.tiles.tiles[-1].y - self.tiles.camera_y

        self.tiles.tiles[-1].idx = self.chosen_brush
        self.tiles.tiles[-1].alpha = 100

        if self.chosen_brush >= 0:  # No Air Please
            self.tiles.tiles[-1].draw(self.screen)

    def paint_tile_at(self, x, y, new_tile_idx=0):
        replace_tile = self.get_tile_at_pos(x + self.tiles.camera_x, y + self.tiles.camera_y + self.tiles.tile_size)
        new_tile = self.tiles.tiles[-1]
        self.tiles.tiles[-1].idx = new_tile_idx
        if new_tile_idx == -1:
            if replace_tile[1].tile_idx in self.levels:
                del self.levels[replace_tile[1].tile_idx]
                del self.tiles.level_grid[replace_tile[1].tile_idx]
                self.tiles.level_tiles[replace_tile[0]].idx = -1
            elif replace_tile[1].tile_idx in self.overlap_grid:
                del self.overlap_grid[replace_tile[1].tile_idx]
                self.tiles.overlap_tiles[replace_tile[0]].idx = -1
            else:
                self.draw_coordinates_at(replace_tile[1].tile_idx, (x, y))
        elif new_tile.layer > 4:
            if hasattr(replace_tile[1], 'node'):
                self.levels[replace_tile[1].tile_idx] = Levels(';', '', '', replace_tile[1].tile_idx)
                self.levels[replace_tile[1].tile_idx].gray_paths = \
                    self.pathfind.find_gray_arrows(replace_tile[1].tile_idx)
                self.levels[replace_tile[1].tile_idx].get_other_arrows(self.tiles.overlap_tiles[replace_tile[0]].node)
                self.tiles.level_grid[replace_tile[1].tile_idx] = self.levels[replace_tile[1].tile_idx].idx

                self.tiles.level_tiles[replace_tile[0]].idx = self.levels[replace_tile[1].tile_idx].idx
        elif new_tile.layer > 1:
            self.overlap_grid[replace_tile[1].tile_idx] = new_tile_idx
            self.tiles.overlap_grid[replace_tile[1].tile_idx] = new_tile_idx

            self.tiles.overlap_tiles[replace_tile[0]].idx = new_tile_idx
        else:
            # Updating tile grids
            self.tile_grid[replace_tile[1].tile_idx] = new_tile_idx
            self.tiles.grid_list[replace_tile[1].tile_idx] = new_tile_idx

            # Updating tile properties
            self.tiles.tiles[replace_tile[0]].idx = new_tile_idx

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

    def draw_arrows(self):
        """Draws arrows to levels"""
        for level in self.levels:
            levels = tuple(key for key, idx in self.tiles.level_tiles.items() if idx.tile_idx == level)
            if levels:
                levels = levels[0]
                tile = self.tiles.level_tiles[levels]
                for color, arrows in (('green', self.levels[level].paths), ('red', self.levels[level].secret_paths),
                                      ('gray', self.levels[level].gray_paths)):
                    for arrow in arrows:
                        if arrow == '^':
                            py.draw.polygon(self.screen, color, (
                                (tile.draw_x + tile.width / 2 - 4, tile.draw_y - 5),
                                (tile.draw_x + tile.width / 2, tile.draw_y - 9),
                                (tile.draw_x + tile.width / 2 + 4, tile.draw_y - 5)))
                        elif arrow == 'v':
                            py.draw.polygon(self.screen, color, (
                                (tile.draw_x + tile.width / 2 - 4, tile.draw_y + tile.height + 5),
                                (tile.draw_x + tile.width / 2, tile.draw_y + tile.height + 9),
                                (tile.draw_x + tile.width / 2 + 4, tile.draw_y + tile.height + 5)))
                        elif arrow == '<':
                            py.draw.polygon(self.screen, color, (
                                (tile.draw_x - 5, tile.draw_y + tile.height / 2 - 4),
                                (tile.draw_x - 9, tile.draw_y + tile.height / 2),
                                (tile.draw_x - 5, tile.draw_y + tile.height / 2 + 4)))
                        elif arrow == '>':
                            py.draw.polygon(self.screen, color, (
                                (tile.draw_x + tile.width + 5, tile.draw_y + tile.height / 2 - 4),
                                (tile.draw_x + tile.width + 9, tile.draw_y + tile.height / 2),
                                (tile.draw_x + tile.width + 5, tile.draw_y + tile.height / 2 + 4)))

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
                return -1, self.tiles.tiles[-1], False
            if self.overlap_grid[tile_index] != -1:
                self.tiles.tiles[-1].tile_idx = tile_index
                self.tiles.tiles[-1].idx = self.tiles.overlap_grid[tile_index]
                return -1, self.tiles.tiles[-1], False
            self.tiles.tiles[-1].tile_idx = tile_index
            self.tiles.tiles[-1].idx = self.tiles.grid_list[tile_index]
            return -1, self.tiles.tiles[-1], False
        if overlap:
            return tuple(tile.keys())[0], self.tiles.overlap_tiles[tuple(tile.keys())[0]], overlap
        else:
            return tuple(tile.keys())[0], self.tiles.tiles[tuple(tile.keys())[0]], overlap


if __name__ == '__main__':
    pass
