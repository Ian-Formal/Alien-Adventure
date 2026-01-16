from Functions.level_loop import Level_Loop
from Functions.planet_loop import Planet_Loop
from Functions.menus import Menus
from threading import Thread
from math import floor
import pygame as py


class Main:
    """Mainloop functions"""
    # Using slots will save up a lot of memory, depending on the amount of attributes.
    # Slots can be applied to this class because no new attributes will be added
    __slots__ = 'sc_width', 'sc_height', 'screen', 'clock', 'fps', 'run', 'planet', 'level', 'menus', 'initializing', \
                'temp', 'temp2'

    def __init__(self):
        """Mainloop variables"""
        py.init()
        self.sc_width, self.sc_height = 768, 480
        self.screen = py.display.set_mode((self.sc_width, self.sc_height))
        py.display.set_caption("Alien Adventure V1.1 (Copyright 2023, Ian Au)")
        self.clock, self.fps, self.run = py.time.Clock(), 60, True
        self.planet = None
        self.level = None
        self.menus = None
        self.initializing = False
        self.temp = False
        self.temp2 = False

    def setup_level_cls(self):
        """Set up the level class"""
        self.level = Level_Loop(self.screen, self.clock, 'Functions')
        self.level.editor.editor_permission = self.menus.editor
        self.menus.level = self.level
        self.configure_player_number(self.menus.clicked)
        self.initializing = False

    def setup_planet_cls(self):
        """Set up the planet class"""
        self.planet = Planet_Loop(self.screen, self.clock, 'Functions')
        self.planet.editor.editor = self.menus.editor
        self.menus.planet = self.planet
        self.initializing = False

    def configure_player_number(self, number):
        """Sets the player number after the player select menu"""
        self.level.player.player, self.planet.player.player, self.planet.hud.player = number, number, number

    def init_classes(self):
        """Initializes all classes"""
        database = self.planet.save_file[self.menus.clicked]['planet']
        if database:
            self.planet.init_database(database)
            self.level.init_database(database)
            self.planet.setup(self.menus.clicked)
        else:
            database = self.menus.playing.replace('_', ' ')
            self.planet.init_database(database)
            self.level.init_database(database)
            self.planet.setup(self.menus.clicked)
            self.planet.editor.progress.hud_data['planet'] = database
        self.level.hud.lives, self.level.player.lives = floor(self.planet.hud.lives), \
            round((self.planet.hud.lives - floor(self.planet.hud.lives)) * 10)
        self.level.hud.coins = self.planet.hud.coins
        self.level.setup_level(level='####')  # Temporary level
        self.level.state = 'map'
        self.initializing = False

    def black_loading_from(self, func1, func2):
        """Setups black loading screen to load from func1 to func2"""
        self.initializing = True
        self.menus.run = True
        self.menus.temp = True
        while self.menus.run:
            func1() if self.initializing and self.menus.temp else func2()
            self.menus.black_loading_screen(self.initializing)

            self.update_pygame()

    def planet_to_level(self):
        """Loading from planet to level"""
        self.level.hud.lives, self.level.player.lives = floor(self.planet.hud.lives),\
            round((self.planet.hud.lives - floor(self.planet.hud.lives)) * 10)
        self.temp2 = True
        self.level.hud.save_collected = \
            self.planet.editor.progress.level_data[self.planet.hud.level.id]['collected'].copy()
        self.level.setup_level(level=self.planet.hud.level.id)
        self.temp2 = False

    def title_mainloop(self):
        """Mainloop function for title screen"""
        if 'title' in self.menus.on_title:
            self.menus.title_screen()
            if 'import' in self.menus.on_title:
                self.menus.draw_import_menu()
            elif 'story' in self.menus.on_title:
                self.menus.show_story()
            elif 'new' in self.menus.on_title:
                self.menus.new_planet_menu()
            else:
                self.menus.temp = True
        elif self.menus.on_title == 'player':
            self.menus.player_select()
        elif 'saves' in self.menus.on_title:
            self.menus.save_files()
            if 'delete' in self.menus.on_title:
                self.menus.delete_confirmation_save(int(self.menus.on_title.split(' ')[-1]))
            else:
                self.menus.temp = True
        elif self.menus.on_title == 'load_t':
            thread = Thread(target=self.black_loading_from, args=(self.menus.title_screen, self.menus.player_select))
            thread.start()
            self.setup_planet_cls()
            thread.join()
            self.menus.on_title = 'player'
        elif self.menus.on_title == 'load_p':
            thread = Thread(target=self.black_loading_from, args=(self.menus.player_select, self.menus.save_files))
            thread.start()
            self.setup_level_cls()
            thread.join()
            self.menus.on_title, self.menus.clicked = 'saves', False
        elif self.menus.on_title == 'load_s':
            thread = Thread(target=self.black_loading_from, args=(self.menus.save_files, self.planet.mainloop))
            thread.start()
            self.init_classes()
            thread.join()
            self.menus.on_title, self.menus.temp, self.menus.clicked = False, False, False
        elif self.menus.on_title == 'load_ps':
            thread = Thread(target=self.black_loading_from, args=(self.menus.player_select, self.planet.mainloop))
            thread.start()
            self.setup_level_cls()
            self.initializing = True
            self.menus.clicked = 0
            self.init_classes()
            thread.join()
            self.menus.on_title, self.menus.temp, self.menus.clicked = False, False, False

    def mainloop(self):
        """Mainloop for the game"""
        self.menus = Menus(self.screen)
        while self.run:
            self.screen.fill((25, 25, 25))
            if not self.menus.run and self.menus.on_title:
                self.title_mainloop()
            elif not self.menus.on_title:
                self.r_mainloop()

            self.update_pygame()
        self.check_quit_mainloop()

    def r_mainloop(self):
        """Mainloop for planet and level interactions"""
        if self.planet.state in 'run pause_0 pause_9 cutscene':
            if 'pause' in self.planet.state:
                self.planet.mainloop()
                if self.temp:
                    self.menus.run = True
                    self.menus.temp = True
                    self.temp = False
                if self.menus.run:
                    if self.planet.state == 'pause_0':
                        self.menus.planet_menu()
                    elif self.planet.state == 'pause_9':
                        self.menus.controls_menu()
                else:
                    self.planet.state = str(self.menus.temp)
                    self.temp = True
            else:
                self.temp = True
                self.planet.mainloop()
        elif self.level.state in 'run pause door_a door_b':
            if self.level.state == 'pause':
                self.level.paint_mainloop()
                if self.temp:
                    self.menus.run = True
                    self.menus.temp = True
                    self.temp = False
                if self.menus.run:
                    self.menus.level_pause()
                else:
                    self.level.state = str(self.menus.temp)
                    self.temp = True
            elif 'door' in self.level.state:
                self.level.paint_mainloop()
                if self.temp:
                    self.menus.run = True
                    self.menus.temp = True
                    self.temp = False
                    self.level.entity.door_state = True
                if self.level.entity.door_state != self.menus.temp:
                    self.level.entity.door_state = self.menus.temp
                    # Adjusting camera
                    self.level.mainloop()
                    self.level.adjust_camera()
                    self.level.mainloop()
                if self.menus.run:
                    self.menus.black_loading_screen()
                    self.level.state = 'door_a' if self.menus.temp else 'door_b'
                else:
                    self.level.state = 'run'
                    self.temp = True
            else:
                self.level.mainloop()
                self.temp = True
        elif self.planet.state == 'level' and self.level.state == 'map':
            # Loading from planet map to level
            if self.temp:
                self.menus.run = True
                self.menus.temp = True
                Thread(target=self.planet_to_level).start()
                self.temp = False
            elif self.menus.run:
                if self.menus.temp:
                    self.planet.mainloop()
                else:
                    self.level.paint_mainloop()
                self.menus.level_loading_screen(self.temp2)
            else:
                self.level.state = 'run'

        elif self.level.state in 'exit green red' and self.planet.state == 'level':
            # Loading from level to planet map
            if self.temp:
                self.menus.run = True
                self.menus.temp = True
                self.planet.hud.lives = self.level.hud.lives + 0.1 * self.level.player.lives \
                    if self.level.player.lives > 0 else self.level.hud.lives - 0.4
                self.temp = False
            elif self.menus.run:
                if self.menus.temp:
                    self.level.paint_mainloop()
                else:
                    self.planet.mainloop()
                self.planet.hud.tick_level_pos(False)
                self.planet.hud.tick_menu_pos(False)
                self.planet.hud.tick_world_pos(False)
                if self.level.state == 'exit':
                    if self.planet.hud.lives < 0:
                        self.menus.game_over_screen()
                    else:
                        self.menus.black_loading_screen()
                    if not self.temp2:
                        self.update_level_finished(False)
                elif self.level.level.background[1]:
                    if self.menus.title_frame > 0:
                        self.menus.completed_level_loading_screen(
                            self.level.hud.score,
                            self.planet.editor.progress.level_data[self.level.current_level]['high_score'])
                    else:
                        if not self.temp2 and self.menus.frame < 300 and not self.menus.temp:
                            self.update_level_finished()
                        self.menus.credits()
                else:
                    if not self.temp2 and self.menus.frame < 300 and not self.menus.temp:
                        self.update_level_finished()
                    self.menus.completed_level_loading_screen(
                        self.level.hud.score,
                        self.planet.editor.progress.level_data[self.level.current_level]['high_score'])
            else:
                self.planet.return_to_map(self.level.state, self.level.current_level)
                self.level.state = 'map'
                self.temp2 = False

    def update_level_finished(self, record_score=True):
        """Updating planet hud settings when finishing a level"""
        def gem_count(collected):
            """Gives the gem count in a collected list"""
            return len([v for v in collected if 12 <= v <= 15])
        # High score and collected recording
        if record_score:
            self.planet.editor.progress.level_data[self.level.current_level]['high_score'] = \
                max(self.planet.editor.progress.level_data[self.level.current_level]['high_score'],
                    self.level.hud.score)
        self.planet.hud.gem_count += gem_count(self.level.hud.save_collected) - \
            gem_count(self.planet.editor.progress.level_data[self.level.current_level]['collected'])
        self.planet.editor.progress.level_data[self.level.current_level]['collected'] = \
            self.level.hud.save_collected

        # Reset collected key values
        self.level.entity.key_cls.collected_keys = set(self.level.entity.key_cls.save_collected)
        self.temp2 = True

    def check_quit_mainloop(self):
        """Portion of the mainloop for checking if quitting"""
        if not self.run:
            if self.level is not None:
                self.level.level.level_store.close()
            if self.planet is not None:
                self.planet.close(self.level.hud.coins)
            py.quit()

    def update_pygame(self):
        """Pygame basic mainloop functions"""
        for event in py.event.get():
            if event.type == py.QUIT:
                self.run = False
            if 'title' in str(self.menus.on_title):
                self.menus.toggle_editor(event)
            if self.planet is not None:
                self.planet.update_user_text(event)
            if self.level is not None:
                self.level.update_user_text(event)
        py.display.update()
        self.clock.tick(self.fps)


if __name__ == '__main__':
    Main().mainloop()
