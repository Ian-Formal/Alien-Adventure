import pygame as py
from os.path import join
from math import floor

try:
    from .Planets.planet_editor import Planet, Editor
    from .Planets.Paths.player_progress import Player_Progress
    from .Planets.Tiles.tiles import Tiles
    from .Player.player import P_Player
    from .Hud.hud import Planet_Hud
except ImportError:
    from Planets.planet_editor import Planet, Editor
    from Planets.Paths.player_progress import Player_Progress
    from Planets.Tiles.tiles import Tiles
    from Player.player import P_Player
    from Hud.hud import Planet_Hud


class Planet_Loop:
    """Planet loop functions"""
    __slots__ = 'win', 'camera_x', 'camera_y', 'sc_width', 'sc_height', 'clock', 'fps', 'player_number', 'tiles', \
                'editor', 'hud', 'player', 'all_player_pics', 'temp_progress', 'save_file', 'x_vel', 'y_vel', 'state', \
                'cutscene_length', 'frame'

    def __init__(self, win, tick: py.time, path):
        self.win = win
        self.camera_x, self.camera_y = 0, 0
        self.sc_width, self.sc_height = self.win.get_size()
        self.clock, self.fps = tick, 60
        self.player_number = 1

        self.tiles = Tiles(win=self.win, camera_x=self.camera_x, camera_y=self.camera_y,
                           path=join(path, "Planets", "Tiles", "Tile_Art"))
        self.editor = Editor(win=self.win, path=path, tiles_cls=self.tiles, setup_func=self.setup,
                             grid_func=self.update_grid)
        self.hud = Planet_Hud(win=self.win, path=join(path, "Hud"), player=self.player_number)
        self.player = P_Player(win=self.win, camera_x=0, camera_y=0, player_number=self.player_number,
                               editor_cls=self.editor, path=join(path, "Player"))

        self.all_player_pics = self.player.images.get_all_images(self.player.path)
        self.temp_progress = Player_Progress(1, path, self.editor)
        self.save_file = None
        self.update_save_files()

        """For Editor"""
        self.x_vel = 0
        self.y_vel = 0

        self.state = 'run'
        self.cutscene_length = 0
        self.frame = 0

    def update_save_files(self):
        """Updates save files dictionary"""
        self.save_file = self.temp_progress.get_all_save_data(self.temp_progress.path, self.editor)

    def init_database(self, world_name):
        """Setups Database"""
        self.editor.setup_database(world_name)
        self.editor.planet_store.setup_planet()

    def setup_hud(self):
        """Functions for setting up hud"""
        self.hud.level_progress = self.editor.progress
        self.hud.gem_count = self.editor.progress.hud_data['gem_count']
        if self.editor.worlds:
            self.hud.world = tuple(self.editor.worlds.values())[0]
        else:
            self.hud.world = None
        if self.editor.levels:
            self.hud.level = tuple(self.editor.levels.values())[0]
        else:
            self.hud.level = None
        self.hud.lives = float(self.editor.progress.hud_data['lives'])
        self.hud.game_overs = int(self.editor.progress.hud_data['game_over'])
        self.hud.coins = int(self.editor.progress.hud_data['coins'])
        self.hud.find_font_color()

    def setup(self, save_file, blank=None):
        """Setup planet"""
        self.editor.save_file = save_file
        self.editor.get_planet(blank)
        self.editor.setup_pathfinding()
        self.setup_hud()
        self.tiles.level_grid = {key: value.idx for key, value in self.editor.levels.items()}
        self.tiles.overlap_grid = self.editor.overlap_grid
        self.tiles.grid_list = self.editor.tile_grid
        self.tiles.camera_x, self.tiles.camera_y = 0, 0
        self.tiles.setup((self.editor.grid_width, self.editor.grid_height), self.editor.tile_grid)
        if self.editor.editor:
            self.editor.setup_menu()
        if self.editor.levels:
            self.player.find_spawn_idx(self.editor.progress.hud_data['spawn'])
            self.adjust_camera()
            self.sort_worlds()
        elif not self.editor.editor:
            raise KeyError('No Levels found within level grids (Un-playable world)')

    def adjust_camera(self):
        """Adjusts the camera positions when initializing or teleporting"""
        # Adjust the camera positions to the player immediately
        self.camera_x = self.player.x - self.sc_width // 2.7
        self.camera_y = self.player.y - self.sc_height // 2
        self.move_camera()

    def update_grid(self):
        """Updates the tile grid from changes"""
        self.tiles.camera_x, self.tiles.camera_y = 0, 0
        self.tiles.setup((self.editor.grid_width, self.editor.grid_height), self.editor.tile_grid)
        self.mainloop()

    def return_to_map(self, state, from_level):
        """Runs the animation for showing next path"""
        state_dict = {'exit': 'exit', 'green': True, 'red': False}
        self.player.find_spawn_idx(from_level)
        self.editor.in_level = False
        if self.hud.lives < 0.1:
            self.hud.game_overs += 1
            self.hud.lives = 3.6
        if state_dict[state] != 'exit':
            # Setting the completed level state
            self.editor.levels[self.player.spawn_idx].idx = 197
            self.tiles.level_grid[self.player.spawn_idx] = 197
            level_tiles = [key for key, value in self.tiles.level_tiles.items()
                           if value.tile_idx == self.player.spawn_idx]
            self.tiles.level_tiles[level_tiles[0]].idx = 197

            self.editor.progress.unlock_path(from_level, state_dict[state])
            self.state = 'cutscene'
            self.cutscene_length = 2
        else:
            self.state = 'cutscene'
            self.cutscene_length = 1

    def complete_unlock_path(self):
        """Completes the unlocking path animation by revealing the level"""
        levels_unlock = [key for key in self.editor.levels.keys()
                         if key in self.editor.progress.paths and key != self.player.spawn_idx]
        for level in levels_unlock:
            if self.editor.progress.paths[level] > 100:
                continue
            self.editor.levels[level].idx = 196
            self.tiles.level_grid[level] = 196
            level_tiles = [key for key, value in self.tiles.level_tiles.items()
                           if value.tile_idx == level]
            if level_tiles:
                self.tiles.level_tiles[level_tiles[0]].idx = 196

        self.update_progress_paths()

    def mainloop(self):
        """Mainloop for planet"""
        self.move_mainloop()
        self.r_mainloop()
        if self.state == 'cutscene':
            if self.cutscene_length == 2:
                if not self.tiles.animation:
                    self.complete_unlock_path()
                    self.state = 'run'
                    self.cutscene_length = 0
            elif self.cutscene_length == 1:
                self.frame += 1
                if self.frame > 80:
                    self.frame = 0
                    self.state = 'run'
                    self.cutscene_length = 0

    def move_mainloop(self):
        """Mainloop for movement"""
        if not self.editor.editor:
            self.player.move(self.state == 'run')

    def r_mainloop(self):
        """Mainloop for planet interaction"""
        if __name__ == '__main__':
            self.win.fill((25, 25, 25))
        self.move_camera()
        if self.editor.editor:
            self.tiles.position_tiles()
        else:
            self.tiles.position_tiles(self.editor.progress.paths)
        self.editor.editor_mainloop()
        if not self.editor.editor:
            self.player.draw()
            self.update_hud()
            self.hud.draw()
        elif self.editor.in_level:
            self.hud.level = self.editor.levels[self.editor.in_level]
            worlds = [world for world in self.editor.worlds.values()
                      if world.in_world(floor((self.editor.in_level - 1) / self.editor.grid_height) * 32 + 16,
                                        self.sc_height - ((self.editor.in_level - 1) % self.editor.grid_height - 1)
                                        * 32 + 16)]
            if worlds:
                self.hud.world = worlds[0]
            self.editor.in_level = False
            self.state = 'level'

        if __name__ == '__main__':
            py.display.update()
            self.clock.tick(self.fps)

    def update_hud(self):
        """Updates hud based on cutscenes"""
        keys = py.key.get_pressed()
        if self.state == 'cutscene':
            self.hud.tick_level_pos(False)
            self.hud.tick_menu_pos(False)
            self.hud.tick_world_pos(False)
        else:
            if 'pause' not in self.state:
                if keys[py.K_0]:
                    self.state = 'pause_0'
                if keys[py.K_9]:
                    self.state = 'pause_9'
            if self.player.action != 'level':
                self.hud.tick_level_pos(False)
            else:
                self.hud.level = self.editor.levels[self.player.tile_idx]
                self.hud.tick_level_pos(True)
                if keys[py.K_SPACE] and 'pause' not in self.state:
                    self.state = 'level'
            self.hud.tick_menu_pos(self.player.action != 'walk')
            self.hud.world = [world for world in self.editor.worlds.values()
                              if world.in_world(self.player.x, self.player.y)]
            if self.hud.world:
                self.hud.world = self.hud.world[0]
                self.hud.orig_world = self.hud.world
                self.hud.find_font_color()
                self.hud.tick_world_pos(True)
            else:
                self.hud.world = self.hud.orig_world
                self.hud.tick_world_pos(False)

    def update_user_text(self, events):
        """Updates the editor user text"""
        if events.type == py.KEYDOWN and self.editor.editor:
            if events.key == py.K_BACKSPACE:
                self.editor.user_text = self.editor.user_text[:-1]
            elif len(self.editor.user_text) < self.editor.user_text_length:
                self.editor.user_text += events.unicode
        if events.type == py.MOUSEBUTTONDOWN:
            self.editor.current_text = None

    def update_progress_paths(self):
        """Updates the progress path when returning to the planet map"""
        for path, alpha in self.editor.progress.paths.items():
            if alpha < 255:
                self.editor.progress.paths[path] = 255

    def sort_worlds(self):
        """Sorts the worlds from level order"""
        order = {}
        prev_worlds = set()
        for world in self.editor.worlds.values():
            if world.name in prev_worlds:
                continue
            prev_worlds.add(world.name)
            order[world.name] = sorted(world.get_all_levels_in_world(self.editor), key=lambda l: l.id)[0].id[0]
        #                               Sorting world levels in order                           Gets the world id
        self.editor.worlds = {key: value for key, value in enumerate(sorted(self.editor.worlds.values(),
                                                                            key=lambda x: order[x.name]))}

    def move_camera(self):
        """Moves camera"""
        if not self.editor.editor:
            self.camera_x += round((self.player.x - self.camera_x - self.sc_width // 2.7) / 4)
            self.camera_y += round((self.player.y - self.camera_y - self.sc_height // 2) / 8)
        elif not self.editor.full_screen_menu and not self.editor.level_buttons:
            keys = py.key.get_pressed()
            keys_dict = {True: 1, False: 0}
            right = keys_dict[keys[py.K_RIGHT] or keys[py.K_d]]
            left = keys_dict[keys[py.K_LEFT] or keys[py.K_a]]
            up = keys_dict[keys[py.K_UP] or keys[py.K_w]]
            down = keys_dict[keys[py.K_DOWN] or keys[py.K_s]]
            self.x_vel += 6 * (right - left)
            self.y_vel += -6 * (up - down)
            self.x_vel *= 0.8
            self.y_vel *= 0.8
            self.camera_x += self.x_vel
            self.camera_y += self.y_vel
            self.limit_camera(self.tiles.tile_size - 32 / 2, 0, self.tiles.sc_width + 32 / 2,
                              self.tiles.sc_height + 32 / 2)
        self.tiles.camera_x, self.tiles.camera_y = self.camera_x, self.camera_y
        self.player.camera_x, self.player.camera_y = self.camera_x, self.camera_y

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

    def close(self, coins):
        """Closing and saving changes to Database"""
        self.editor.planet_store.close()
        if self.editor.progress is not None and not self.editor.editor:
            self.editor.progress.hud_data['coins'] = coins
            self.editor.progress.hud_data['lives'] = self.hud.lives
            # self.editor.progress.hud_data['items'] =
            self.editor.progress.hud_data['gem_count'] = self.hud.gem_count
            self.editor.progress.hud_data['spawn'] = self.hud.level.id
            self.editor.progress.hud_data['game_over'] = self.hud.game_overs
        self.editor.progress.close()


if __name__ == '__main__':
    py.init()
    width, height = 768, 480
    screen = py.display.set_mode((width, height))
    py.display.set_caption("Planet Test")
    clock = py.time.Clock()
    planet_loop = Planet_Loop(screen, clock, '')
    planet_loop.init_database('EARTH;Ian Au')
    planet_loop.setup(1)
    run = True
    fps = 0
    prev_fps = 80
    while run:
        fps = planet_loop.clock.get_fps()
        planet_loop.mainloop()
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
            planet_loop.update_user_text(event)
        if fps < prev_fps and fps != 0:
            prev_fps = fps
    print(prev_fps)
    py.quit()
    planet_loop.editor.planet_store.close()
    planet_loop.editor.progress.close()
