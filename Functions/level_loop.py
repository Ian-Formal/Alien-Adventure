import pygame as py
from os.path import join

try:
    from .Levels.level_editor import Level, Editor, Tiles
    from .Player.player import L_Player
    from .Hud.hud import Level_Hud
    from .Particles.particles import Particles
    from .Levels.Entities.entities import All_Entities
except ImportError:
    from Levels.level_editor import Level, Editor, Tiles
    from Player.player import L_Player
    from Hud.hud import Level_Hud
    from Particles.particles import Particles
    from Levels.Entities.entities import All_Entities


class Player_Interact:
    """Functions for player interaction with level elements"""
    __slots__ = 'win', 'path', 'camera_x', 'camera_y', 'sc_width', 'sc_height', 'tiles', 'editor', 'particles', \
                'player', 'hud', 'entity', 'state'

    def __init__(self, win, path):
        """Initializes player movement scripts and objects"""
        self.win = win
        self.path = path
        self.camera_x, self.camera_y = 0, 0
        self.sc_width, self.sc_height = self.win.get_size()

        self.tiles = Tiles(win=self.win, camera_x=0, camera_y=0, path=join(path, "Levels", "Level_Tiles",
                                                                           "Tile_Arts"))
        self.editor = Editor(win=self.win, path=path, tiles_cls=self.tiles, editor_exit_func=self.exit_editor,
                             setup_func=self.setup_level, grid_func=self.update_grid)
        self.particles = Particles(win=self.win, path=join(path, "Particles"))
        self.player = L_Player(win=self.win, camera_x=self.camera_x, camera_y=self.camera_y, player_number=1,
                               get_tile_at_func=self.editor.get_tile_at_pos, smoke_func=self.particles.tick_smoke_at,
                               path=join(path, "Player"))
        self.hud = Level_Hud(win=self.win, path=join(path, "Hud"), main_path=path, player_cls=self.player,
                             sc_particle_func=self.particles.tick_score_at)
        self.entity = All_Entities(win=self.win, player_cls=self.player, editor_cls=self.editor, hud_cls=self.hud,
                                   size=self.tiles.tile_size, path=join(path, "Levels", "Entities"))
        self.editor.entity = self.entity

        # Main Mainloop Interaction
        self.state = 'run'

    """Spawn"""
    def setup_level(self):
        pass

    def update_grid(self):
        pass

    def player_mainloop(self):
        """Mainloop functions for player interaction and movement"""
        if self.editor.editor:
            if self.editor.player_move:
                self.player.edit_move()
        elif self.player.lives > 0:
            self.player.bump = False
            if str(self.player.touching) not in 'green red':
                self.player.normal_move()
            else:
                self.player.set_idle()
            if not self.editor.editor and self.player.lives > 0:
                self.player.handle_collision()
                if self.player.falling < 1:
                    self.hud.__class__.bounce_counter = 0
            self.check_around_player()
            self.player.animate()
            self.player.invis_frame()
        else:
            self.player.frame += 1
            if 12 > self.player.frame > 10:
                self.player.y_vel = -17
            elif self.player.frame > 11:
                if not self.player.draw_y > self.sc_height + self.player.height * self.player.scale:
                    self.player.y_vel += 1
                    self.player.y += self.player.y_vel
                elif self.editor.editor_permission:
                    self.player.lives = 6
                    self.editor.handle_escape()
                else:
                    self.state = 'exit'
            self.player.update_draw_pos()
            self.player.draw()

    def move_player_after_entity(self):
        """Moves the player after entities are set"""
        if self.player.bounce > 0:
            self.player.bounce -= 1
            self.player.y_vel = -13
            self.player.falling, self.player.jumping = 2, 1
        self.player.draw()

    def check_around_player(self):
        """Checks around the player"""
        if self.player.y > self.sc_height:
            self.player.lives = 0
            self.player.frame = 0
        self.change_tile(self.editor.get_tile_at_pos(self.player.pins['right'], self.player.pins['top'] - 6), 'top')
        self.change_tile(self.editor.get_tile_at_pos(self.player.pins['left'], self.player.pins['top'] - 6), 'top')
        self.change_tile(self.editor.get_tile_at_pos(self.player.pins['right'] + 5, self.player.pins['mid'] - 20),
                         'mid')
        self.change_tile(self.editor.get_tile_at_pos(self.player.pins['left'] - 5, self.player.pins['mid'] - 20), 'mid')
        self.change_tile(self.editor.get_tile_at_pos(self.player.pins['right'] + 5, self.player.pins['mid'] + 3), 'mid')
        self.change_tile(self.editor.get_tile_at_pos(self.player.pins['left'] - 5, self.player.pins['mid'] + 3), 'mid')
        self.change_tile(self.editor.get_tile_at_pos(self.player.pins['right'], self.player.pins['bottom']), 'bottom')
        self.change_tile(self.editor.get_tile_at_pos(self.player.pins['left'], self.player.pins['bottom']), 'bottom')

    def change_tile(self, tile, check_pos):
        """Changes the tile based on player position"""
        # The Mystery Block
        mystery_block = True if str(int(tile[1].idx)) in '15 17 23 24 25 26' else False
        if mystery_block and self.player.bump and check_pos == 'top':
            self.tick_mystery_block(tile)

        key_block = 286 <= tile[1].idx <= 289
        if key_block:
            self.tick_key_block(tile)

    def tick_mystery_block(self, tile):
        """Ticks the mystery block when player hits it"""
        if tile[2]:
            bumped_tile = self.tiles.overlap_tiles[tile[0]]
            self.tiles.overlap_grid[tile[1].tile_idx] = 19
        else:
            bumped_tile = self.tiles.tiles[tile[0]]
            self.tiles.grid_list[tile[1].tile_idx] = 19
        bumped_tile.idx = 19
        bumped_tile.update_settings()
        bumped_tile.bumped = 180
        if bumped_tile.tile_idx in self.entity.entities:
            self.entity.entities[bumped_tile.tile_idx].spawn_on_mystery()
        else:
            self.particles.tick_coin_at(bumped_tile.x, bumped_tile.y - self.tiles.tile_size,
                                        self.tiles.tile_size)
            self.hud.coins += 1
            self.hud.animate_coin_jump()
            self.hud.score += 100

        # Check above for bouncing entity
        for idx, entity in self.entity.entities.items():
            check_x = bumped_tile.x < entity.x < bumped_tile.x + self.tiles.tile_size or \
                      bumped_tile.x < entity.x + entity.width < bumped_tile.x + self.tiles.tile_size
            if bumped_tile.y - self.tiles.tile_size / 2 < entity.y + entity.height < bumped_tile.y + 1 \
                    and check_x:
                if hasattr(self.entity.entities[idx], 'pins'):  # Checking if bounce on mystery exists
                    self.entity.entities[idx].bounce_on_mystery()

    def tick_key_block(self, tile):
        to_collect = {286: 19, 287: 22, 288: 23, 289: 25}
        if to_collect[tile[1].idx] not in self.hud.collected:
            return None
        if tile[1].tile_idx in self.tiles.destroyed_tiles:
            return None
        self.tiles.destroyed_tiles.add(tile[1].tile_idx)
        if tile[2]:
            self.tiles.overlap_tiles[tile[0]].destroyed = True
            self.tiles.overlap_tiles[tile[0]].update_collision()
        else:
            self.tiles.tiles[tile[0]].destroyed = True
            self.tiles.tiles[tile[0]].update_collision()
        self.hud.collected.remove(to_collect[tile[1].idx])

    def exit_editor(self):
        pass


class Level_Loop(Player_Interact):
    """Class for running a level"""
    __slots__ = 'in_cam_rect', 'clock', 'fps', 'level', 'current_level'

    def __init__(self, win: py.display, tick: py.time, path):
        """Define variables and objects used"""
        super().__init__(win, path)
        self.in_cam_rect = False
        self.clock, self.fps = tick, 60
        self.level = Level(win=self.win, path=self.path)
        self.current_level = '1-1'

    def mainloop(self, *, draw=True):
        """Mainloop of Levels"""
        self.editor.background_cls.draw(self.camera_x, self.camera_y)
        self.player_mainloop()
        if self.player.lives > 0 and str(self.player.touching) not in 'green red':
            self.entity.move_entity()
            self.move_player_after_entity()
            self.move_camera()
            if not self.editor.editor_permission:
                self.hud.run_timer()
        elif str(self.player.touching) in 'green red':
            completed = self.hud.run_down_timer()
            if completed:
                if self.editor.editor_permission:
                    self.player.touching = False
                    self.editor.handle_escape()
                else:
                    self.state = self.player.touching
        elif self.hud.timer <= 0:
            self.hud.display_time_up()

        # Drawing Sprites
        self.paint_mainloop(from_mainloop=True, draw=draw)
        if not self.editor.editor:
            keys = py.key.get_pressed()
            if keys[py.K_0]:
                self.state = 'pause'

        # Updating Window
        if __name__ == '__main__':
            py.display.update()
            self.clock.tick(self.fps)

    def paint_mainloop(self, *, from_mainloop=False, draw=True):
        """Level paint mainloop"""
        if not from_mainloop:
            self.editor.background_cls.draw(self.camera_x, self.camera_y)
        self.particles.mainloop()
        self.tiles.position_tiles(self.editor.editor)
        self.particles.paint_particles_after()
        self.entity.draw_entity()
        if self.editor.editor:
            self.entity.draw_items()
        self.editor.editor_mainloop()

        if not self.editor.full_screen_menu:
            self.player.draw()
            if not self.editor.editor:
                self.entity.draw_items()
        if not self.editor.editor:
            self.hud.draw()
        elif self.editor.editor_permission and self.hud.score != 0:
            self.hud.reset_hud()
            self.hud.coins = 0

        if not draw:
            self.win.fill((0, 0, 0))
            py.display.update()

        if self.entity.door_state:
            self.state = 'door_a'

        if __name__ == '__main__':
            global door_frame
            door_frame = 0 if self.state == 'run' else door_frame
            if 'door' in self.state:
                door_frame += 15
                if door_frame > 600:
                    self.state = 'door_b'
                    self.entity.door_state = False
                    if door_frame < 631:
                        self.adjust_camera()
                if door_frame > 755:
                    self.state = 'run'
                    door_frame = 0

    def init_database(self, world_name):
        """Initializes database"""
        self.level.setup_database(world_name)
        self.level.level_store.setup_levels()
        self.editor.level_store = self.level.level_store

    def set_player_spawn(self):
        """Sets the player's spawn point in the beginning"""
        if self.player.cp_in_level is None or self.player.cp_in_level != self.current_level:
            self.player.cp_in_level = self.current_level
            self.player.checkpoint = 628
            self.hud.save_collected = [v for v in self.hud.save_collected if 12 <= v <= 15]
            self.hud.score_for_life = self.hud.orig_score_for_life.copy()
            self.entity.key_cls.save_collected, self.entity.key_cls.collected_keys = set(), set()
            self.tiles.destroyed_tiles, self.tiles.saved_destroyed_tiles = set(), set()
        self.player.spawn_idx = self.editor.once_tiles[self.player.checkpoint]
        if isinstance(self.player.spawn_idx, bool):
            self.player.spawn_idx = 0

    def setup_level(self, *, level=None, blank=None):
        """Handles setting up level"""
        if level is not None:
            self.current_level = level
        self.level.generate_level(self.current_level, self.editor, blank)
        self.editor.level_number = self.level.level_number

        self.editor.grid_width, self.editor.grid_height, self.editor.tile_grid, self.editor.overlap_grid, \
            self.editor.entity_grid, self.editor.time, self.editor.camera, self.editor.background, \
            self.editor.background_cls = \
            self.level.grid_width, self.level.grid_height, self.level.tile_grid, self.level.overlap_grid, \
            self.level.entity_grid, self.level.time, self.level.camera, self.level.background, self.level.background_cls

        self.tiles.overlap_grid = self.level.overlap_grid
        self.entity.grid_list, self.entity.grid_list_info = self.level.entity_grid, self.level.background[2]
        self.editor.init_once_tiles()
        self.tiles.camera_x = 0
        self.tiles.camera_y = 0
        self.tiles.setup((self.level.grid_width, self.level.grid_height), self.level.tile_grid)
        self.hud.player = self.player.player
        self.set_player_spawn()
        self.hud.reset_hud()
        self.player.reset(self.tiles.grid_height)
        if self.player.lives < 1:
            self.player.lives = 6
            self.hud.lives -= 1
        self.entity.init_entities()
        self.adjust_camera()
        # Do a mainloop once to clear any movements
        self.mainloop(draw=False)
        self.hud.timer = self.editor.time

    def update_grid(self):
        """Updates the level grid from level grid changes"""
        self.level.grid_width, self.level.grid_height, self.level.tile_grid = \
            self.editor.grid_width, self.editor.grid_height, self.editor.tile_grid
        self.tiles.camera_x = 0
        self.tiles.camera_y = 0
        self.tiles.setup((self.level.grid_width, self.level.grid_height), self.level.tile_grid)
        self.mainloop(draw=False)

    def exit_editor(self):
        """Functions for exiting the level editor"""
        for entity in self.entity.entities:
            self.entity.entities[entity].respawn()
            self.entity.entities[entity].ready_spawn = True
        self.level.time, self.hud.timer = self.editor.time, self.editor.time
        self.player.lives = 6

    def adjust_camera(self):
        """Adjusts the camera positions when initializing or teleporting"""
        # Adjust the camera positions to the player immediately
        self.camera_x = self.player.x - self.sc_width // 2.7
        self.camera_y = self.player.y - self.sc_height // 2
        self.move_camera()

    def move_camera(self):
        """Makes the camera follow the player"""
        # Position player near the middle of the screen
        in_cam_rect = [rec for rec in self.editor.camera.values() if rec.in_range(self.player.x, self.player.y) or
                       rec.in_range(self.player.x + self.player.width, self.player.y + self.player.width)]
        if in_cam_rect and not self.editor.editor:
            self.in_cam_rect = [40, 40]
            in_cam_rect = sorted(in_cam_rect, key=lambda x: x.idx, reverse=False)
            self.camera_x, self.camera_y, self.player.camera_loc = in_cam_rect[0].move_camera(
                cam_x=self.camera_x, cam_y=self.camera_y, mov_cam=self.in_cam_rect, player_cls=self.player)
        else:
            if self.player.camera_loc:
                self.player.camera_loc = False
            if self.in_cam_rect:
                mov_x, mov_y = self.in_cam_rect
                self.in_cam_rect = [max(4, mov_x - 0.3), max(8, mov_y - 0.3)]
                if abs(self.camera_x - self.player.x) < 20 and abs(self.camera_y - self.player.y) < 20:
                    self.in_cam_rect = False
            else:
                mov_x, mov_y = 4, 8

            self.camera_x += (self.player.x - self.camera_x - self.sc_width // 2.7) / mov_x
            self.camera_y += (self.player.y - self.camera_y - self.sc_height // 2) / mov_y  # Smoother Camera movement
        if self.editor.editor:
            self.limit_camera(self.tiles.tile_size - 32 / 2, 0, self.tiles.sc_width + 32 / 2,
                              self.tiles.sc_height + 32 / 2)
        else:
            self.limit_camera(self.tiles.tile_size, 0, self.tiles.sc_width + self.tiles.tile_size,
                              self.tiles.sc_height + self.tiles.tile_size)
        self.camera_x = round(self.camera_x)
        self.camera_y = round(self.camera_y)
        self.player.camera_x, self.player.camera_y = self.camera_x, self.camera_y
        self.tiles.camera_x, self.tiles.camera_y = self.camera_x, self.camera_y
        self.entity.camera_x, self.entity.camera_y = self.camera_x, self.camera_y
        self.particles.camera_x, self.particles.camera_y = self.camera_x, self.camera_y

    def limit_camera(self, min_x, min_y, max_x, max_y):
        """Limits the camera movement"""
        if self.camera_x < min_x:
            self.camera_x = min_x
        if self.camera_y > min_y:
            self.camera_y = min_y
        if self.camera_x > self.tiles.tile_size * self.tiles.grid_width - max_x:
            self.camera_x = self.tiles.tile_size * self.tiles.grid_width - max_x
        if self.camera_y < -self.tiles.tile_size * self.tiles.grid_height + max_y:
            self.camera_y = -self.tiles.tile_size * self.tiles.grid_height + max_y

    def update_user_text(self, events):
        """Updates the editor user text"""
        if events.type == py.KEYDOWN and self.editor.editor:
            if events.key == py.K_BACKSPACE:
                self.editor.user_text = self.editor.user_text[:-1]
            elif len(self.editor.user_text) < self.editor.user_text_length:
                self.editor.user_text += events.unicode
        if events.type == py.MOUSEBUTTONDOWN:
            self.editor.current_text = None


if __name__ == '__main__':
    py.init()
    width, height = 768, 480
    screen = py.display.set_mode((width, height))
    py.display.set_caption("Level Test")
    clock = py.time.Clock()
    level_loop = Level_Loop(screen, clock, '')
    level_loop.init_database('EARTH;Ian Au')
    level_loop.setup_level()
    run = True
    fps = 0
    prev_fps = 80
    door_frame = 0
    while run:
        level_loop.mainloop()
        fps = level_loop.clock.get_fps()
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
            level_loop.update_user_text(event)
        if fps < prev_fps and fps != 0:
            prev_fps = fps
    print(prev_fps)
    py.quit()
    level_loop.level.level_store.close()
