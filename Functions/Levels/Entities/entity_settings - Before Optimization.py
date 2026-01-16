import pygame as py
from os import listdir
from os.path import join, isfile
from math import floor


class Entity(py.sprite.Sprite):
    """Attributes for all entities"""
    __slots__ = 'screen', 'sc_width', 'sc_height', 'player', 'editor', 'tiles', 'entity', 'hud', 'show_last', 'idx', \
                'images', 'image', 'dir', 'show', 'destroyed', 'de_spawn', 'global_', 'global__', 'ready_spawn', \
                'mystery', 'x', 'draw_x', 'x_vel', 'y', 'draw_y', 'y_vel', 'orig_x', 'orig_y', 'camera_x', 'camera_y', \
                'img_height', 'img_width', 'scale', 'height', 'width', 'tile_size', 'frame', 'alpha', 'rect', 'mask', \
                'state', 'hit_img', 'ded_img', 'init_editor'

    def __init__(self, win: py.display, path, entity_type, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__()
        # Basic yet important variables, also including classes
        self.screen = win
        self.sc_width, self.sc_height = self.screen.get_size()
        self.player = player_cls
        self.editor = editor_cls
        self.tiles = editor_cls.tiles
        self.entity = entity_cls
        self.hud = hud_cls

        # Image Configuration
        tiles_to_entities = 566
        self.show_last = False
        if entity_type < 566:
            tiles_to_entities = 0
            self.show_last = True
        self.idx = entity_type - tiles_to_entities
        self.images = {key: Entity_Img(path).image[self.idx + i] for key, i in
                       enumerate(range(self.editor.get_animation_frames(entity_type)))}
        self.image = self.images[0]

        # Misc Variables
        self.dir = True
        self.show = True  # Show or hide, can be manually set
        self.destroyed = False  # Show = False until editor is on
        self.de_spawn = False  # If entity is off-screen
        self.global_ = False  # If entity cannot de-spawn
        self.global__ = False  # Entity is forever cannot de-spawn when set to true
        self.ready_spawn = True  # To Prevent entity from spawning on the screen
        self.mystery = False  # If it is inside a mystery block

        self.x = 0
        self.draw_x = 0
        self.x_vel = 0  # Will not update automatically to x, update it in entities class

        self.y = 0
        self.draw_y = 0
        self.y_vel = 0  # Will not update automatically to y, update it in entities class

        self.orig_x = self.x
        self.orig_y = self.y

        self.camera_x = 0
        self.camera_y = 0
        self.img_height = self.image[0].get_height()
        self.img_width = self.image[0].get_width()
        self.scale = self.player.scale
        self.height = self.img_height * self.scale
        self.width = self.img_width * self.scale
        self.tile_size = self.player.tile_size
        self.frame = 0
        self.alpha = 255

        self.rect = self.image[0].get_rect()
        self.mask = py.mask.from_surface(self.image[0])

        self.state = 0  # -1: Killed, 0: Alive
        self.hit_img = self.images[0]
        self.ded_img = self.images[0]
        self.init_editor = False

    def init_entity(self, tile_idx):
        """Initialises entity scripts"""
        self.x = floor((tile_idx - 1) / self.editor.grid_height) * self.tile_size
        self.y = (tile_idx - 1) % self.editor.grid_height + 2
        self.y = self.sc_height - self.y * self.tile_size - self.height + self.tile_size
        self.orig_x = self.x
        self.orig_y = self.y
        self.alpha = 255
        tile = self.editor.get_tile_at_pos(self.x, self.y + self.tile_size)
        self.mystery = 1 if tile[1].idx == 23 or tile[1].idx == 25 or tile[1].idx == 15 or tile[1].idx == 17 \
            else False
        self.state = 0
        self.more_init()

    def respawn(self):
        """Respawns the entity onto the screen"""
        self.x = self.orig_x
        self.y = self.orig_y
        self.x_vel = 0
        self.y_vel = 0
        self.dir = True
        self.ready_spawn = False
        self.more_init()

    def draw(self):
        """Draws onto screen"""
        if self.editor.editor and hasattr(self, 'mov_dir'):
            self.draw_path()
        if self.show:
            dir_dict = {True: 0, False: 1}
            image = py.transform.scale(self.image[dir_dict[self.dir]], (self.width, self.height))
            if image is not None:
                image.set_alpha(self.alpha)
            self.screen.blit(image, (self.draw_x, self.draw_y))

    def update_draw_pos(self):
        """Updates drawing position"""
        self.draw_x = self.x - self.camera_x
        self.draw_y = self.y - self.camera_y
        self.update_rectangle_pos()

    def mainloop(self):
        """Mainloop for entity"""
        off_screen = self.draw_x < -self.width or \
            self.draw_x > self.sc_width or \
            self.draw_y > self.sc_height or \
            self.draw_y < -self.height
        if not self.editor.editor:
            # If entity is outside
            if self.draw_y > self.sc_height + self.height:
                self.de_spawn = True
            if self.global_ or self.global__:  # Managing global entities and non-global entities
                self.run()
            else:
                self.spawning_scripts(off_screen)

            if self.init_editor:
                self.init_editor = False
        else:
            if not self.init_editor:
                if not isinstance(self.mystery, bool):
                    self.mystery = 1
                if self.editor.editor and self.image is not self.images[0]:
                    self.image = self.images[0]
                self.x = self.orig_x
                self.y = self.orig_y
                self.destroyed = False
                self.frame = 0
                self.init_toggle_editor()
                self.init_editor = True
            self.show = not off_screen

    def spawning_scripts(self, off_screen):
        """Handle spawning of entity"""
        mystery = self.mystery == 0 or isinstance(self.mystery, bool)
        if self.destroyed or not mystery:
            if self.mystery == 1:
                self.show = False
                self.frame = 0
            elif self.mystery == -1:
                self.show = True
                self.update_on_mystery()
        # Spawning in entity
        elif self.frame < 1:
            if self.ready_spawn and not off_screen:
                if isinstance(self.mystery, bool):
                    self.respawn()
                self.ready_spawn = True
                self.init_tick()
                self.de_spawn = False
                self.show = True
                self.frame = 1

            # Makes sure the entity spawns off-screen
            elif off_screen:
                self.ready_spawn = True

        # If entity is in the camera range
        elif not off_screen:
            self.run()

        # If entity is not in camera range
        else:

            # Continues running entity after off-screen for 4 blocks
            if not self.de_spawn:
                self.run()

            # De-spawning the entity
            de_spawn = self.draw_x < -self.width - self.tile_size * 4 or \
                self.draw_x > self.sc_width + self.tile_size * 4 or \
                self.draw_y > self.sc_height + self.tile_size * 4 or \
                self.draw_y < -self.height - self.tile_size * 4
            if de_spawn:
                if isinstance(self.mystery, bool):
                    self.respawn()
                else:
                    self.destroyed = True
                self.show = False
                self.de_spawn = True
                self.frame = 0

    def run(self):
        """Runs the entity"""
        dir_dict = {True: 0, False: 1}
        self.mask = py.mask.from_surface(py.transform.scale(self.image[dir_dict[self.dir]],
                                                            (self.width, self.height)))
        self.rect = py.transform.scale(self.image[0], (self.width, self.height)) \
            .get_rect(topleft=(self.draw_x, self.draw_y))
        self.frame += 0.01
        # If the entity is killed
        if self.state < 0:
            # Image for killing an entity
            if self.frame < 1.1:
                self.image = self.hit_img
            else:
                self.image = self.ded_img

            # After a certain amount of time, kills the entity completely
            if self.frame > 1.15:
                self.show = False
                self.destroyed = True
                self.hud.score += 100

            # Movement Animation
            self.x += self.x_vel
            self.y_vel += 1
            self.y += self.y_vel
        else:
            # It's ALIVE! Tick it
            self.tick()

    def spawn_on_mystery(self):
        """Spawning entity on mystery block"""
        self.mystery = -1
        self.y_vel = -self.tile_size / 4

    def update_on_mystery(self):
        """Updating y pos of spawning entity"""
        self.y_vel += 1
        if self.y_vel > 0:
            self.y_vel = 0
            self.mystery = 0
        self.y += self.y_vel

    """Dummy Functions"""
    def init_tick(self):
        pass

    def tick(self):
        pass

    def more_init(self):
        pass

    def init_toggle_editor(self):
        pass

    def draw_edit_menu(self):
        self.editor.ent_menu = False

    def update_rectangle_pos(self):
        """Updates the rectangle position"""
        self.rect.x, self.rect.y = self.draw_x, self.draw_y

    def define_as_enemy(self):
        """Fixes the adjustments to make enemies bigger"""
        self.img_height = self.image[0].get_height()
        self.img_width = self.image[0].get_width()
        self.scale = 32 / 50
        self.height = self.img_height * self.scale
        self.width = self.img_width * self.scale

    """Bouncing on mystery block"""
    def bounce_on_mystery(self, from_shell=False):
        """Bounces entity upwards when above the mystery block"""
        self.y_vel = -14
        self.x_vel = -1.5 if self.x_vel < 0 else 1.5
        self.state = max(self.state - 1, -1)
        # If shell collides with this entity
        if from_shell:
            self.state = -1
        self.frame = 1


class Movable_Tile(Entity):
    """Functions for a movable entity which has player collision detection"""
    group_touching = {}  # storing integers for each group's touch values
    copied = ''

    def __init__(self, win: py.display, path, entity_type, ent_info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.r_mov_dir = True
        self.mov_dir = True
        self.change_mov_dir = False
        self.prev_x, self.prev_y = 0, 0
        info = ent_info.split(';')
        self.pta, self.fin, self.mov_after, self.speed, self.delay, self.group, self.path = info
        self.pta = bool(self.pta)
        self.fin = bool(self.fin)
        self.mov_after = int(self.mov_after)
        self.speed = int(self.speed)
        self.delay = int(self.delay)
        self.group = float(self.group)

        self.touched = not self.pta
        self.touching = False
        self.reached_end = False
        self.at_start = True
        self.dx, self.dy = 0, 0
        self.frame_on_delay = 0
        self.in_center = None

        self.path_in_idx = self.path.replace('>', ',').replace('<', ',').replace('^', ',').replace('v', ',')
        self.path_in_idx = [int(v) for v in self.path_in_idx.split(',')]
        self.width, self.height = self.tiles.tile_size, self.tiles.tile_size
        self.prev_idx = self.path_in_idx[0]
        self.tile_idx = self.path_in_idx[0]

        if self.group not in self.__class__.group_touching:
            self.__class__.group_touching[floor(self.group)] = 1

        # Editor functions
        self.exit_editor = False
        self.clicked = False
        self.space = False
        self.draw_path_menu = False
        self.e_path = self.path

        self.global__, self.global_ = True, True

    def init_tick(self):
        self.touched = not self.pta
        self.touching = False
        self.reached_end = False
        self.at_start = True
        self.dx, self.dy = 0, 0
        self.frame_on_delay = 0
        self.__class__.group_touching[floor(self.group)] = 1
        self.in_center = None

    def move(self):
        """Moves the block"""
        if self.in_center:
            self.in_center = None
        direction = self.find_dir_to_move()
        direction = direction if self.check_finished() is None else None
        direction = self.check_player_touching(direction)
        translate = {True: 1, False: -1}
        self.x_vel, self.y_vel = 0, 0
        if direction is None:
            self.frame_on_delay += 1
        if direction == '>':
            self.x_vel = 1 * self.speed * translate[self.mov_dir]
        elif direction == '<':
            self.x_vel = -1 * self.speed * translate[self.mov_dir]
        elif direction == '^':
            self.y_vel = -1 * self.speed * translate[self.mov_dir]
        elif direction == 'v':
            self.y_vel = 1 * self.speed * translate[self.mov_dir]
        self.prev_x, self.prev_y = self.x, self.y
        for _ in range(floor(abs(self.x_vel))):
            another_block = self.check_in_center()
            if another_block or self.in_center:
                break
            self.x += 1 if self.x_vel > 0 else -1
        for _ in range(floor(abs(self.y_vel))):
            another_block = self.check_in_center()
            if another_block or self.in_center:
                break
            self.y += 1 if self.y_vel > 0 else -1
        self.check_collisions()

    def check_in_center(self) -> bool:
        """Checks if the block is in the center, returns a boolean value weather it crossed into another block or not"""
        self.update_draw_pos()
        self.tile_idx = self.convert_coords_to_tile_idx((self.draw_x, self.draw_y))
        if self.tile_idx != self.prev_idx and self.tile_idx in self.path_in_idx:
            self.x_vel = self.x - self.prev_x
            self.y_vel = self.y - self.prev_y
            return True
        if round(self.x % self.tile_size) == 0 and round(self.y % self.tile_size) == 0 and \
                self.tile_idx in self.path_in_idx and self.in_center is False:
            self.in_center = True
        return False

    def check_finished(self):
        """Dummy function"""
        pass

    def check_player_touching(self, direction):
        """CHecks if the player is touching the tile and perform actions accordingly"""
        if not self.touched:
            return direction
        if not self.touching:
            if self.mov_after == 1 or (self.mov_after == 3 and self.at_start):
                return None
            self.mov_dir = self.mov_after == 2
            if self.change_mov_dir and not self.at_start and self.mov_after == 3:
                self.prev_idx = 0
                self.change_mov_dir = False
            if not self.r_mov_dir:
                self.mov_dir = not self.mov_dir
        else:
            self.mov_dir = True
            if not self.change_mov_dir and not self.at_start and self.mov_after == 3:
                self.prev_idx = 0
                self.change_mov_dir = True
            if not self.r_mov_dir:
                self.mov_dir = not self.mov_dir
        return direction

    def find_dir_to_move(self):
        """Finds the direction to move into"""
        # self.path = (example) 294>571^584>1092
        # Separating all values into index lists without directions

        # Finding the current pos in tile_idx
        tile_idx = self.convert_coords_to_tile_idx((self.draw_x, self.draw_y))
        self.tile_idx = tile_idx

        # Resetting delay
        if self.tile_idx != self.prev_idx:
            self.frame_on_delay = 0
            self.prev_idx = self.tile_idx
            self.reached_end = False
            self.at_start = False
            if self.tile_idx not in self.path_in_idx:
                self.in_center = False

        # Finding where the tile_idx is in the path allocated to the movable tile
        betweens = []
        for i, idx in enumerate(self.path_in_idx):
            if i == len(self.path_in_idx) - 1:
                continue
            other_idx = self.path_in_idx[i + 1]
            if tile_idx in self.path_in_idx:
                betweens = []
                break
            if idx < tile_idx < other_idx or other_idx < tile_idx < idx:
                betweens.append(idx)

        # Returning the direction
        if len(betweens) > 1:
            return self.bruteforce_direction(self.path_in_idx, betweens, tile_idx)
        elif betweens:
            idx = self.path.find(str(betweens[0]))
            return self.path[idx + len(str(betweens[0]))]
        else:
            idx = self.path.find(str(tile_idx))
            if self.in_center is False:
                if not self.mov_dir:
                    return self.path[idx + len(str(tile_idx))]
                else:
                    return self.path[idx - 1]
            if idx < 0 or self.frame_on_delay < self.delay or len(self.path_in_idx) < 2:
                return None
            # If first item in the path
            elif idx == 0:
                self.r_mov_dir = True
                self.mov_dir = True
                self.reached_end = True
                self.at_start = True
            # If last item in the path
            elif idx == len(self.path) - len(str(tile_idx)):
                self.r_mov_dir = False
                self.mov_dir = False
                self.reached_end = True

            if self.mov_dir:
                return self.path[idx + len(str(tile_idx))]
            else:
                return self.path[idx - 1]

    def bruteforce_direction(self, all_idx_list: list, all_idx: list, tile_idx: int):
        """Bruteforce the path code to identify the direction"""
        for idx in all_idx:
            direction = self.path[self.path.find(str(idx)) + len(str(idx))]
            end = all_idx_list[all_idx_list.index(idx) + 1]
            while idx != end:
                if direction == '>':
                    idx += self.tiles.grid_height
                elif direction == '<':
                    idx -= self.tiles.grid_height
                elif direction == '^':
                    idx += 1
                elif direction == 'v':
                    idx -= 1
                if idx == tile_idx:
                    return direction
        return None

    def check_collisions(self):
        """Makes the tile collidable and solid"""
        # Returns all entities that need to be checked
        def near_me(entity) -> bool:
            """Returns True if near, False if not"""
            if entity is self.player:
                self.rect.y -= 3
                if py.sprite.collide_rect(entity, self):
                    self.rect.y += 3
                    return True
                self.rect.y += 3
                if py.sprite.collide_rect(entity, self):
                    return True
            return py.sprite.collide_rect(entity, self) and hasattr(entity, 'falling')

        all_entities = {key: value for key, value in self.entity.entities.items() if near_me(value)}
        if near_me(self.player):
            all_entities[-1] = self.player
        else:
            if self.__class__.group_touching[floor(self.group)] > 5:
                self.touching = False
        for idx in all_entities.keys():
            if idx < 0:
                self.__class__.group_touching[floor(self.group)] = 0
                self.player.collided = self
            else:
                self.entity.entities[idx].collided = self

    def update_touch(self):
        """When the player touches the movable tile"""
        if self.pta:
            self.touched = True
        self.touching = True

    def draw_path(self):
        """Draws own path in editor"""
        if self.draw_path_menu or len(self.path_in_idx) < 2:
            return
        py.draw.lines(self.screen, '#535353', False,
                      [self.convert_tile_idx_to_coords(point) for point in self.path_in_idx], width=3)

    def draw_edit_menu(self):
        """Draws the edit menu for movable tiles"""
        keys = py.key.get_pressed()
        if keys[py.K_ESCAPE]:
            self.exit_editor = True
        elif self.exit_editor:
            self.editor.ent_menu = False
            self.editor.current_text = None
            self.exit_editor = False
        if keys[py.K_SPACE]:
            self.space = True
        elif self.space:
            self.draw_path_menu = not self.draw_path_menu
            if self.draw_path_menu:
                self.tile_idx = self.convert_coords_to_tile_idx((self.draw_x, self.draw_y))
                self.e_path = f'{self.tile_idx}'
            else:
                e_path = self.e_path.replace('>', ',').replace('<', ',').replace('^', ',').replace('v', ',')
                e_path = [int(v) for v in e_path.split(',')]
                if len(e_path) > 1:
                    self.path = self.e_path
                    self.update_path_in_idx()
            self.space = False
        if keys[py.K_c]:
            self.__class__.copied = str(self)
        elif keys[py.K_v] and self.__class__.copied:
            self.pta, self.fin, self.mov_after, self.speed, self.delay, self.group, self.path = \
                self.__class__.copied.split(';')
            self.pta = bool(self.pta)
            self.fin = bool(self.fin)
            self.mov_after = int(self.mov_after)
            self.speed = int(self.speed)
            self.delay = int(self.delay)
            self.group = float(self.group)
            self.paste_path()
        if self.draw_path_menu:
            self.draw_edit_path()
        else:
            self.draw_settings_menu()

    def paste_path(self):
        """Pasting path so that the path aligns with the tile's indexes"""
        self.tile_idx = self.convert_coords_to_tile_idx((self.draw_x, self.draw_y))
        str_path = self.path
        path = self.path.replace('>', ',').replace('<', ',').replace('^', ',').replace('v', ',')
        path = [int(v) for v in path.split(',')]

        # Finding the difference
        diff = self.tile_idx - path[0]
        for idx, cor_idx in zip(path, list(path)):  # Creating a copy of the path
            idx += diff
            str_path = str_path.replace(str(cor_idx), str(idx))

        self.path = str_path
        self.update_path_in_idx()

    def draw_edit_path(self):
        """Draws the path edit mode in the editor"""
        # Connection between mouse pos and last node
        mouse_idx = self.convert_coords_to_tile_idx(py.mouse.get_pos())
        path_in_idx = self.e_path.replace('>', ',').replace('<', ',').replace('^', ',').replace('v', ',')
        path_in_idx = [int(v) for v in path_in_idx.split(',')]
        last_idx = path_in_idx[-1]

        flip_dir = {'v': '^', '^': 'v', '<': '>', '>': '<'}
        last_dir = flip_dir[self.e_path[-1 * len(str(last_idx)) - 1]] if len(self.e_path) > len(str(last_idx)) else ''
        possible = self.is_possible_idx(last_idx, mouse_idx, last_dir)

        if possible[0]:
            path_in_idx.append(mouse_idx)
        if len(path_in_idx) > 1:
            py.draw.lines(self.screen, '#fc432f', False,
                          [self.convert_tile_idx_to_coords(point) for point in path_in_idx], width=3)

        if py.mouse.get_pressed()[0]:
            self.clicked = True
        elif self.clicked:
            if possible[0]:
                # Don't use += because it is glitchy when working with non-integers
                self.e_path = f'{self.e_path}{possible[1]}{mouse_idx}'
            self.clicked = False

    def is_possible_idx(self, orig_tile_idx: int, new_tile_idx: int, forbid_direction: str) -> tuple:
        """Returns a tuple that states if the new_tile_idx can be placed with respect to the orig_tile_idx in the first
        slot, followed by the direction if possible"""
        # Vertical
        base_y = floor(orig_tile_idx / self.tiles.grid_height) * self.tiles.grid_height + 1
        if base_y <= new_tile_idx <= base_y + self.tiles.grid_height - 1:
            direction = 'v' if new_tile_idx < orig_tile_idx else '^'
            if direction in forbid_direction:
                return False, None
            return True, direction
        # Horizontal
        base_x = abs(orig_tile_idx - new_tile_idx)
        if base_x != 0 and base_x % self.tiles.grid_height == 0:
            direction = '<' if new_tile_idx < orig_tile_idx else '>'
            if direction in forbid_direction:
                return False, None
            return True, direction
        return False, None

    def draw_settings_menu(self):
        """Draws the settings menu onto the screen"""
        width, height = self.sc_width / 6, self.sc_height / 3
        bg = py.Surface((width, height))
        bg.fill('#E0e0df')
        bg.set_alpha(180)
        self.screen.blit(bg, (self.draw_x + self.width, self.draw_y - height))
        contents = {
            'PTA': self.pta,
            'Fin': self.fin,
            'MA': self.mov_after,
            'S': self.speed,
            'D': self.delay,
            'G': self.group
        }
        y = self.draw_y - height + 3
        font = py.font.Font(None, floor(self.sc_height / 15))
        mouse_pos = py.mouse.get_pos()
        pressed = py.mouse.get_pressed()[0]
        for component, user_input in contents.items():
            text = font.render(component + ':', True, '#000000')
            text_rect = text.get_rect(topleft=(self.draw_x + self.width + 2, y))
            self.screen.blit(text, text_rect)
            x_width = 5 + text_rect.width
            box = py.Rect((self.draw_x + self.width + 2 + x_width, y), (width - x_width - 4, text_rect.height))
            if box.collidepoint(mouse_pos):
                col = '#Eeeeed'
                if pressed:
                    self.clicked = True
                elif self.clicked:
                    if component == 'PTA':
                        self.pta = not self.pta
                    elif component == 'Fin':
                        self.fin = not self.fin
                    elif component == 'MA':
                        # Loops around 1, 2 and 3 on click
                        self.mov_after += 1 if self.mov_after < 3 else -2
                    elif component == 'S' or component == 'D':
                        col = '#Afafac'
                        self.editor.user_text = str(self.speed if component == 'S' else self.delay)
                        self.editor.user_text_length = 3
                        self.editor.current_text = f'{self.__class__.__name__}_{component}'
                    elif component == 'G':
                        col = '#Afafac'
                        self.editor.user_text = str(self.group)
                        self.editor.user_text_length = 5
                        self.editor.current_text = f'{self.__class__.__name__}_{component}'
                    self.clicked = False
            else:
                col = '#ffffff'
            if self.editor.current_text == f'{self.__class__.__name__}_{component}':
                col = '#Afafac'
                isfloat = self.editor.user_text.replace('.', '', 1).isdigit()
                isdigit = self.editor.user_text.isdigit()
                if component == 'S' or component == 'D' or component == 'G':
                    if not self.editor.user_text:
                        if component == 'S':
                            self.speed = 0
                        elif component == 'D':
                            self.delay = 0
                        else:
                            self.group = 1
                    elif isfloat:
                        if component == 'S':
                            self.speed = float(self.editor.user_text) if not isdigit else int(self.editor.user_text)
                            if self.speed > 32:
                                self.speed = 32
                        elif component == 'D':
                            self.delay = float(self.editor.user_text) if not isdigit else int(self.editor.user_text)
                        else:
                            self.group = float(self.editor.user_text) if not isdigit else int(self.editor.user_text)
                    else:
                        self.editor.user_text = self.editor.user_text[:-1]
            py.draw.rect(self.screen, col, box)
            text = font.render(str(user_input), True, '#000000')
            text_rect = text.get_rect(topleft=(self.draw_x + self.width + 3 + x_width, y))
            self.screen.blit(text, text_rect)
            y += 4 + text_rect.height

    def update_path_in_idx(self):
        """Updates path in idx when path is changed"""
        self.path_in_idx = self.path.replace('>', ',').replace('<', ',').replace('^', ',').replace('v', ',')
        self.path_in_idx = [int(v) for v in self.path_in_idx.split(',')]

    def convert_tile_idx_to_coords(self, tile_idx) -> tuple[int, int]:
        """Converts tile index to coordinates"""
        x = floor((tile_idx - 1) / self.tiles.grid_height)
        y = (tile_idx - 1) % self.tiles.grid_height - 1
        x *= self.tile_size
        x += self.tile_size / 2
        y = self.sc_height - y * self.tile_size - self.tile_size * 3 + self.tile_size // 2
        x -= self.camera_x
        y -= self.camera_y
        return x, y

    def convert_coords_to_tile_idx(self, coords) -> int:
        x, y = coords
        x += self.camera_x
        y += self.camera_y + self.tile_size
        tile_grid_x = floor(x / 32)
        tile_grid_y = -1 * floor((y - self.sc_height) / 32)
        return tile_grid_y + tile_grid_x * self.tiles.grid_height

    def __str__(self):
        """Returns the string for data storage"""
        return f"{self.pta};{self.fin};{self.mov_after};{self.speed};{self.delay};{self.group};{self.path}"


class Collidable_Entity(Entity):
    """Functions for entities that collide with tiles"""
    __slots__ = 'falling', 'jumping', 'pins', 'collided'

    def __init__(self, win: py.display, path, entity_type, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.falling = 69
        self.jumping = 69
        self.pins = {'top': self.y, 'bottom': self.y - self.height, 'left': self.x, 'right': self.x + self.width}
        self.collided = False
        self.define_as_enemy()

    """Handling Collision"""

    def move_x(self, x=None):
        """Moves entity along the x-axis"""
        if x is None:
            self.x += self.x_vel
        else:
            self.x += x
        y = self.y
        if not self.collided:
            check_x = False
        else:
            check_x = self.check_move_x()
        collided = self.handle_collision_in_dir(0, 1, True)
        if self.y < y - abs(self.x_vel) - 4 or check_x or (collided and self.collided):
            self.y = y
            orig_x_vel = self.x_vel
            if collided and self.collided and not check_x:
                self.x_vel += self.collided.x_vel
            if self.handle_collision_in_dir(self.x_vel, 0):
                self.x_vel = 0
                self.dir = not self.dir
            else:
                self.x_vel = orig_x_vel
            if not (collided and self.collided):
                self.collided = False
        elif self.y < y:
            # walking up a slope
            self.x_vel *= 0.8

    def move_y(self, y=None):
        """Moves entity along the y-axis"""
        if y is None:
            self.y += self.y_vel
        else:
            self.y += y
        self.falling += 1
        if self.handle_collision_in_dir(0, self.y_vel):
            if self.y_vel > 0:
                self.falling = 0
            else:
                self.jumping = 69  # Nice
            self.y_vel = 0

    def check_move_x(self) -> bool:
        """Checks if the entity is on the side of a movable tile"""
        self.x += self.collided.x_vel

        check_x = (self.pins['bottom'] > self.collided.y + self.collided.height * 2 and self.y_vel > 0) or \
                  (self.pins['top'] < self.collided.y + self.collided.height / 2 and self.y_vel < 0 and
                   not self.jumping > 0)

        return check_x

    """COLLISION"""
    def handle_collision(self):
        """Handles collisions with tiles"""
        self.move_x()
        self.move_y()
        self.collided = False
        self.update_draw_pos()

    def update_pins(self):
        self.pins = {'top': self.y, 'bottom': self.y + self.height, 'left': self.x, 'right': self.x + self.width}

    def handle_collision_in_dir(self, dx, dy, test_x=False):
        """Handles collision in a direction"""
        # collided follows: top-left, top-right, bottom-left, bottom-right
        self.update_pins()
        top, bottom = self.pins['top'], self.pins['bottom']
        left, right = self.pins['left'], self.pins['right']
        collided = self.handle_collision_at_point(left, top, dx, dy) or \
            self.handle_collision_at_point(right, top, dx, dy) or \
            self.handle_collision_at_point(left, bottom, dx, dy, True) or \
            self.handle_collision_at_point(right, bottom, dx, dy, True)

        if self.collided and not test_x:
            collided = collided or self.handle_moving_collision(dx, dy)
        return collided

    def handle_moving_collision(self, fix_dx, fix_dy):
        """Handles collisions with movable tiles"""
        dx, dy = 0, 0
        if fix_dy > 0:
            dy = -0.1
        elif fix_dy < 0:
            dy = 0.1
        if fix_dx < 0:
            dx = 0.1
        elif fix_dx > 0:
            dx = -0.1
        looped = 0
        while py.sprite.collide_rect(self, self.collided):
            self.x += dx
            self.y += dy
            self.update_draw_pos()
            self.rect = py.transform.scale(self.image[0], (self.scale * 70, self.scale * 100)) \
                .get_rect(topleft=(self.draw_x, self.draw_y - (-20 + self.height) * self.scale))
            self.mask = py.mask.from_surface(py.transform.scale(self.image[0], (self.scale * 70, self.scale * 100)))
            if looped > 1000 or (dx == 0 and dy == 0):
                break
            looped += 1
        if fix_dy > 0:
            self.y = round(self.y)
            self.y += self.collided.y_vel
        if looped < 2:
            return False
        return True

    def handle_collision_at_point(self, x, y, fix_dx, fix_dy, feet=False):
        """Handles collision at points of the entity"""
        y += self.tile_size - 1
        mod_x = x % self.tile_size
        mod_y = y % self.tile_size
        tile = self.editor.get_tile_at_pos(x, y)[1]
        return self.move_outside_collision(mod_x, mod_y, fix_dx, fix_dy, feet, tile)

    def move_outside_collision(self, mod_x, mod_y, fix_dx, fix_dy, feet, tile):
        """Moves the entity outside of collision"""
        dx, dy = 0, 0
        if not tile.solid:
            return False
        if (fix_dx < 0 and tile.collision in '/1 \\0') or (fix_dx > 0 and tile.collision in '\\1 /0'):
            pass
        elif '\\' in tile.collision or '/' in tile.collision:
            m = -1 if '/' in tile.collision else 1  # gradient
            c = self.tile_size if '/' in tile.collision else 0  # y-intercept
            offset_y = mod_y - (m * mod_x + c)  # Linear equation
            if '0' in tile.collision:
                if offset_y >= 0:
                    return False
                elif fix_dy > 0:
                    pass
                else:
                    self.y += self.tile_size - offset_y
                    return True
            elif '1' in tile.collision:
                if offset_y <= 0:
                    return False
                elif fix_dy < 0:
                    pass
                else:
                    self.y -= offset_y
                    return True
        if '-' in tile.collision:
            if mod_y - fix_dy > 1 or not feet:
                return False
        if '=' in tile.collision or '_' in tile.collision or '>' in tile.collision or '<' in tile.collision:
            dx, dy = tile.col_width, tile.col_height
            if dy < 0 and mod_y + 0.000001 < dy * -1:
                if 4 < self.y_vel:
                    self.y_vel = dy * -1 - mod_y - 0.0001
                return False
            if dx < 0 and mod_x + 0.000001 < dx * -1:
                safe_speed = 4
                if dx * -1 > mod_x + 5 and abs(self.x_vel) > safe_speed:
                    self.x_vel = safe_speed if self.x_vel > 0 else -safe_speed
                return False
            if 0 < dy < mod_y and not fix_dy > 0:
                return False
            if 0 < dx <= mod_x:
                return False
        # To account for slopes, 0.000001 is added after the mod instead of a higher value
        if fix_dy > 0:
            self.y -= mod_y + 0.000001 + (dy if dy < 0 else 0)
        elif fix_dy < 0:
            self.y += self.tile_size - (mod_y - (dy if dy > 0 else 0))
        if fix_dx < 0:
            self.x += self.tile_size - (mod_x + (32 - dx if dx > 0 else 0))
        elif fix_dx > 0:
            self.x -= mod_x + 0.000001 + (dx + 1 if dx < 0 else 0)
        return True


class Entity_Img:
    """Class storing basic entity properties"""

    def __init__(self, path):
        """Stores all images into a dictionary"""
        self.image = {}
        i = 0
        for paths in ["Items", "Entity_Art", "Doors"]:
            file_path = join(path, paths)
            self.images = [f for f in sorted(listdir(file_path)) if isfile(join(file_path, f))]
            for image in self.images:
                self.image[i] = {0: load(join(file_path, image)), 1: flip(load(join(file_path, image)))}
                i += 1


def load(loc):
    """Loads in images from a location"""
    return py.image.load(loc).convert_alpha()


def flip(image):
    """Flips the image horizontally"""
    return py.transform.flip(image, True, False).convert_alpha()


if __name__ == '__main__':
    pass
