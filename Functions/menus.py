import pygame as py
from os import listdir
from os.path import join, isfile


class Menus:
    """Class containing menus and loading screens"""
    playing_translate = {'EARTH': 'The Official Edition', 'The Official Edition': 'EARTH'}
    __slots__ = 'screen', 'sc_width', 'sc_height', 'level', 'planet', 'run', 'on_title', 'clicked', 'temp', 'frame', \
                'title_frame', 'thread', 'title_font', 'font', 'title_img', 'path', 'playing', 'editor', 'input', \
                'text', 'cur_planet', 'y_scroll', 'left_right_pressed', 'prev_planet', 'secret_code'

    def __init__(self, win: py.display):
        """Just configures the screen"""
        self.screen = win
        self.sc_width, self.sc_height = self.screen.get_size()

        self.level = None
        self.planet = None
        self.run = False
        self.on_title = 'title'
        self.clicked = False
        self.temp = True
        self.frame = 0
        self.title_frame = 0
        self.thread = None
        self.title_font = 'Functions\\Font\\nasalization.ttf'
        self.font = None
        self.title_img = py.image.load('Functions\\title_screen.png').convert_alpha()

        self.path = join('Functions', 'Data', 'Planets')
        databases = listdir(self.path)
        default = 'EARTH;Ian_Au'
        self.playing = default if default in databases else databases[0]
        playing = self.playing.split(';')
        if playing[0] in self.playing_translate:
            self.playing = f'{self.playing_translate[playing[0]]};{playing[1]}'
        self.playing = self.playing.split('.')[0]

        self.editor = False
        self.input = ''
        self.text = None

        # For planet menu
        self.cur_planet = 1
        self.y_scroll = -21
        self.left_right_pressed = 0
        self.prev_planet = None

        self.secret_code = '1578'

    def detect_mouse_press(self, button: int) -> bool:
        """Returns a boolean value of True when a defined button of the mouse is clicked"""
        # Button: 0: Right button, 2: Left button
        if py.mouse.get_pressed()[button]:
            self.clicked = True
        elif self.clicked:
            self.clicked = False
            return True
        return False

    def draw_shaded_background(self, frame: int, alpha):
        """Draws a shaded background onto the screen"""
        surface = py.Surface(self.screen.get_size())
        surface.fill((0, 0, 0))
        surface.set_alpha(frame if frame < alpha else alpha)
        self.screen.blit(surface, (0, 0))

    def draw_popup_menu(self, width: int, height: int, ext_instance: bool, after_func):
        """Draws a popup menu"""
        if not ext_instance:
            self.frame -= 15 if self.frame > 0 else 0
            if self.frame < 1:
                self.run = False
                if after_func is not None:
                    after_func()
        else:
            self.frame += 15 if self.frame < max(width, height) + 15 else 0
        self.frame = self.frame if self.frame > 1 else 1
        self.draw_shaded_background(self.frame, 100)

        border = 8
        w, h = self.frame / max(width, height) * width, self.frame / max(width, height) * height
        box = py.Surface((w if w < width else width, h if h < height else height))
        box.fill((25, 25, 25))
        box.set_alpha(180)
        box_rect = box.get_rect(center=(self.sc_width / 2, self.sc_height / 2))
        self.screen.blit(box, box_rect)
        border = py.Rect((box_rect.x - border, box_rect.y - border),
                         (box_rect.width + border * 2, box_rect.height + border * 2))
        py.draw.rect(self.screen, (5, 5, 5), border, round((border.width - box_rect.width) / 2), border_radius=4)
        return box_rect, self.frame >= max(width, height)

    def toggle_editor(self, events):
        """Can toggle editor on and off based on a secret code"""
        if events.type == py.KEYDOWN:
            if events.key == py.K_BACKSPACE:
                self.input = self.input[:-1]
            else:
                self.input += events.unicode
        if events.type == py.MOUSEBUTTONDOWN:
            self.text = None

        if self.on_title == 'title new' or self.text is not None:
            return None
        # Return None looks more readable and cleaner than nested if statements
        if not (self.input in self.secret_code and self.input):
            self.input = ''
            return None
        if self.input[0] != self.secret_code[0]:
            self.input = ''
            return None
        if self.input == self.secret_code:
            self.input = ''
            self.editor = not self.editor

    def title_screen(self):
        """Displays title screen and files tab"""
        self.screen.blit(py.transform.scale(self.title_img, (self.sc_width, self.sc_height)), (0, 0))
        self.title_frame += 2
        font = py.font.Font(self.title_font, round(self.sc_height / 8))
        add_y = 0
        playing = self.playing.split(';')
        for i, row in enumerate(('ALIEN', 'ADVENTURE',
                                 f"{'Editing' if self.editor else 'Playing'}: {playing[0].replace('_', ' ')}")):
            if i == 2:
                font = py.font.Font(self.title_font, round(self.sc_height / 12))
            text = font.render(row, True, self.color_change(self.title_frame % self.color_change('')[0]))
            text.set_alpha(self.title_frame // 2 if self.title_frame // 2 < 255 else 255)
            text_rect = text.get_rect(topleft=(self.sc_width / 13, self.sc_height / 5 + add_y))
            self.screen.blit(text, text_rect)
            add_y += text_rect.height + 4

        if not (self.title_frame > 520 and self.on_title == 'title'):
            return None

        x, y = self.sc_width / 7, self.sc_height / 3 * 2
        font = py.font.Font(self.font, round(self.sc_height / 10))
        mouse_pos = py.mouse.get_pos()
        pressed = self.detect_mouse_press(0)
        buttons = ['Import...', 'Edit' if self.editor else 'Play!', 'Story']
        if self.editor:
            buttons.append('New Planet')
        for idx, button in enumerate(buttons):
            text = font.render(button, True, '#000000')
            size = (self.title_frame - 520) * 0.01
            if size > 1:
                size = 1
            rect = py.Rect((x - size * 50, y), ((text.get_size()[0] + 16 * 2) * size, 30 * 2 * size))
            if rect.collidepoint(mouse_pos) and size >= 1:
                col = '#Cacac9'
                if pressed:
                    if idx == 1:
                        self.on_title = 'load_t'
                        if playing[0] in self.playing_translate:
                            self.playing = f'{self.playing_translate[playing[0]]};{playing[1]}'
                    elif idx == 0:
                        self.on_title = 'title import'
                    elif idx == 2:
                        self.on_title = 'title story'
                    elif idx == 3:
                        self.on_title = 'title new'
            else:
                col = '#E0e0df'
            py.draw.rect(self.screen, col, rect, border_radius=80)
            if size >= 1:
                text_rect = text.get_rect(center=(rect.centerx, rect.centery))
                self.screen.blit(text, text_rect)
            x += text.get_width() + 50

    def show_story(self):
        """Shows the story menu"""

        def after_func():
            self.on_title = 'title'

        box_rect, draw_txt = self.draw_popup_menu(360, 450, self.temp, after_func)
        if draw_txt:
            mouse_pos = py.mouse.get_pos()
            pressed = self.detect_mouse_press(0)
            font = py.font.Font(self.font, box_rect.width // 10)
            ext_txt = font.render('X', True, '#ffffff')
            ext = py.Rect((box_rect.x + box_rect.width - ext_txt.get_size()[0] - 6, box_rect.y + 3),
                          (ext_txt.get_size()[0] + 2, ext_txt.get_size()[0] + 2))
            if ext.collidepoint(mouse_pos):
                col = '#7c7c7c'
                if pressed:
                    self.temp = False
            else:
                col = '#969696'
            py.draw.rect(self.screen, col, ext, border_radius=80)
            txt_rect = ext_txt.get_rect(center=(ext.centerx, ext.centery))
            self.screen.blit(ext_txt, txt_rect)

            title = font.render('From Biege (Translated):', True, '#ffffff')
            self.screen.blit(title, (box_rect.x + 2, box_rect.y + 2))

            STORY = ('To all citizens, we have established that our planet no',
                     'longer satisfies our needs for survival. Our current',
                     'astronauts are on a mission to find a new planet for us',
                     'to stay. The rough journey they might face is unknown',
                     'and dangerous. But with the love of everyone else they',
                     'thrive, and hopefully coming back with good news.',
                     ' ',
                     'To astronauts, we hope you the best to find a place for',
                     'us to stay. We will understand if you cannot find our',
                     'ideal home. But we all wish you good luck as you\'re',
                     'our final hope! We\'re happy with any habitable planets',
                     ' ',
                     'Best wishes from Biege (United Nations President)',
                     ' ',
                     'To other lifeforms, if you have any discoveries about a',
                     'habitable planet, please let them know by guiding them',
                     'or creating them specifically for their stay.')
            font = py.font.Font(self.font, box_rect.width // 18)
            for idx, txt in enumerate(STORY):
                txt = font.render(txt, True, '#ffffff')
                rect = txt.get_rect(topleft=(box_rect.x + 2, box_rect.y + box_rect.width // 8 + 4 + idx *
                                             (box_rect.width // 18 + 2)))
                self.screen.blit(txt, rect)

    def draw_import_menu(self):
        """Draws the import menu"""

        def after_func():
            self.on_title = 'title'

        box_rect, draw_txt = self.draw_popup_menu(300, 400, self.temp, after_func)
        if draw_txt:
            mouse_pos = py.mouse.get_pos()
            pressed = self.detect_mouse_press(0)
            font = py.font.Font(self.font, box_rect.width // 10)
            title = font.render('Select a Planet:', True, '#ffffff')
            title_rect = title.get_rect(topleft=(box_rect.x + 2, box_rect.y + 2))
            self.screen.blit(title, title_rect)

            ext_txt = font.render('X', True, '#ffffff')
            ext = py.Rect((box_rect.x + box_rect.width - ext_txt.get_size()[0] - 6, box_rect.y + 3),
                          (ext_txt.get_size()[0] + 2, ext_txt.get_size()[0] + 2))
            buttons = [(ext, ext_txt, '')]
            i = 0
            sep = 3
            for planets in listdir(self.path):
                if not isfile(join(self.path, planets)) or i > 7:
                    continue
                planet = planets.split('.')
                if planet[1] != 'db':
                    continue
                the_planet = planet[0].split(';')
                r_planet = the_planet[0]
                if the_planet[0] in self.playing_translate:
                    planet = f'{self.playing_translate[the_planet[0]]};{the_planet[1]}'
                else:
                    planet = planet[0]
                bt_text = font.render(r_planet.replace('_', ' '), True,
                                      '#ffffff' if planet != self.playing else '#d8d8d8')
                initial = title_rect.y + title_rect.height + sep * 2
                bt_rect = py.Rect((box_rect.x + 2, initial + i * (box_rect.width // 10 + sep * 2 + 4)),
                                  (box_rect.width - 4, box_rect.width // 10 + 4))
                buttons.append((bt_rect, bt_text, planet if planet != self.playing else None))
                i += 1
            if len(buttons) < 5:
                for idx, text in enumerate(('Want More Planets?', 'Drag yours/your friends\'', 'creations into the',
                                            'Functions/Data/Planets folder!')):
                    text = font.render(text, True, '#ffffff')
                    text_rect = text.get_rect(topleft=(box_rect.x + 4, box_rect.centery + idx *
                                                       (box_rect.width // 10 + 2)))
                    self.screen.blit(text, text_rect)
            for button, txt, typ in buttons:
                col = '#cbcbcb'
                if typ is None:
                    pass
                elif button.collidepoint(mouse_pos):
                    col = '#7c7c7c'
                    if pressed:
                        self.temp = False
                        if typ:
                            self.playing = typ
                else:
                    col = '#969696'
                py.draw.rect(self.screen, col, button, border_radius=80)
                txt_rect = txt.get_rect(center=(button.centerx, button.centery))
                self.screen.blit(txt, txt_rect)

    def new_planet_menu(self):
        """Displaying new planet menu"""

        def after_func():
            self.on_title = 'title'

        box_rect, draw_txt = self.draw_popup_menu(520, 350, self.temp, after_func)
        if draw_txt:
            mouse_pos = py.mouse.get_pos()
            pressed = self.detect_mouse_press(0)
            font = py.font.Font(self.font, box_rect.width // 10)
            ext_txt = font.render('X', True, '#ffffff')
            ext = py.Rect((box_rect.x + box_rect.width - ext_txt.get_size()[0] - 6, box_rect.y + 3),
                          (ext_txt.get_size()[0] + 2, ext_txt.get_size()[0] + 2))
            if ext.collidepoint(mouse_pos):
                col = '#7c7c7c'
                if pressed:
                    self.temp = False
                    self.text = None
            else:
                col = '#969696'
            py.draw.rect(self.screen, col, ext, border_radius=80)
            txt_rect = ext_txt.get_rect(center=(ext.centerx, ext.centery))
            self.screen.blit(ext_txt, txt_rect)

            title = font.render('Create New Planet:', True, '#ffffff')
            self.screen.blit(title, (box_rect.x + 2, box_rect.y + 2))

            small_font = py.font.Font(self.font, box_rect.width // 16)
            y = box_rect.y + title.get_height() + 15

            playing = self.playing.replace('_', ' ').split(';')
            if playing[0] in self.playing_translate and playing[0] not in \
                    set([k for i, k in enumerate(self.playing_translate.keys()) if i % 2 == 0]):
                playing[0] = self.playing_translate[playing[0]]

            for idx, label, entry in ((0, 'Planet Name:', playing[0]), (1, 'Planet Designer:', playing[1])):
                text = font.render(label, True, '#ffffff')
                txt_rect = text.get_rect(topleft=(box_rect.x + 4, y))
                self.screen.blit(text, txt_rect)

                y += txt_rect.height + 3
                entry_rect = py.Rect((box_rect.x + 10, y), (box_rect.width - box_rect.x - 20, font.get_height() + 4))
                if entry_rect.collidepoint(mouse_pos) and self.text != label:
                    col = '#757575'
                    if pressed:
                        self.text = label
                        self.input = entry
                elif self.text == label:
                    col = '#a3a3a3'
                    if 0 < len(self.input) < 23:
                        playing[idx] = self.input
                        entry = playing[idx]
                else:
                    col = '#474747'
                py.draw.rect(self.screen, col, entry_rect)
                text = small_font.render(entry, True, '#ffffff')
                txt_rect = text.get_rect(topleft=(entry_rect.x + 2, entry_rect.y + 2))
                self.screen.blit(text, txt_rect)
                y += entry_rect.height + 15
            if playing != self.playing.split(';'):
                self.playing = f"{playing[0].replace(' ', '_')};{playing[1].replace(' ', '_')}"

    def draw_menu_with_words(self, words):
        """A function that is shared between player select and save files"""
        rect = py.Rect((0, 0), (self.sc_width, self.sc_height / 6))
        py.draw.rect(self.screen, '#72725a', rect)
        py.draw.rect(self.screen, '#72725a', rect, 3)
        font = py.font.Font(self.title_font, round(self.sc_height / 9))
        text = font.render(words, True, '#ffffff')
        rect = text.get_rect(topleft=(5, 3))
        self.screen.blit(text, rect)

    def player_select(self):
        """Displays player selection menu"""
        self.screen.fill('#707070')
        # Menu
        self.draw_menu_with_words('Select a Player:')

        mouse_pos = py.mouse.get_pos()
        pressed = self.detect_mouse_press(0)
        player_images = self.planet.all_player_pics
        length = len(player_images)
        bd = 3  # Border
        for i in range(0, length):
            rect = py.Rect((self.sc_width / length * i + bd, self.sc_height / 6 + bd),
                           (self.sc_width / length - bd * 2, self.sc_height - self.sc_height / 6 - bd * 2))
            if rect.collidepoint(mouse_pos):
                col = '#ccbca2'
                if pressed:
                    self.clicked = i + 1
                    self.on_title = 'load_p' if not self.editor else 'load_ps'
            else:
                col = '#ffebcb'
            py.draw.rect(self.screen, col, rect, border_radius=8)
            surf = player_images[i + 1][0]
            rect = surf.get_rect(center=(rect.centerx, rect.centery))
            self.screen.blit(surf, rect)

    def save_files(self):
        """Displays save files menu"""
        self.screen.fill('#606060')
        # Menu
        self.draw_menu_with_words('Choose a Save File:')

        height = (self.sc_height - self.sc_height / 6) / 3
        add_y = self.sc_height / 6
        # File Buttons
        mouse_pos = py.mouse.get_pos() if self.on_title == 'saves' else (0, 0)
        pressed = self.detect_mouse_press(0) if self.on_title == 'saves' else False
        for i in range(1, 4):
            rect = py.Rect((self.sc_width / 10, add_y + height / 8), (4 * (self.sc_width / 6), 6 * (height / 8)))
            if (self.planet.save_file[i]['planet'] != self.playing.replace('_', ' ')) != \
                    (not self.planet.save_file[i]['planet']):  # This is a xor gate
                col = '#9c9c8c'
            elif rect.collidepoint(mouse_pos):
                col = '#5b5b48'
                if pressed:
                    self.clicked = i
                    self.on_title = 'load_s'
            else:
                col = '#72725a'
            py.draw.rect(self.screen, col, rect, border_radius=5)
            self.draw_save_files(i, rect, (mouse_pos, pressed))
            add_y += height

    def draw_save_files(self, save_file: int, rect: py.Rect, mouse_details: tuple):
        """Draws the save files to show on screen"""
        save = self.planet.save_file[save_file]
        x = rect.x + 2
        font = py.font.Font(self.title_font, round(rect.height / 2 - 2 * 2))
        if save['planet']:
            for text in (save['planet'].split(';')[0], save['spawn']):
                text = font.render(text, True, '#ffffff')
                txt_rect = text.get_rect(topleft=(x, rect.y + 2))
                self.screen.blit(text, txt_rect)
                x += max((txt_rect.width + 6, rect.width // 2))
            self.planet.hud.draw_player_lives(rect.x + 2, rect.y + rect.height / 2 + 2,
                                              round(rect.height / 2 - 2 * 2), float(save['lives']))
            del_rect = py.Rect((rect.x + rect.width + 10, rect.y), (rect.height, rect.height))
            text = font.render('X', True, '#ffffff')
            txt_rect = text.get_rect(center=(del_rect.centerx, del_rect.centery))
            if del_rect.collidepoint(mouse_details[0]):
                col = '#5b5b48'
                if mouse_details[1]:
                    self.on_title = f'saves delete {save_file}'
            else:
                col = '#72725a'
            py.draw.rect(self.screen, col, del_rect)
            self.screen.blit(text, txt_rect)
        else:
            text = font.render('NEW!', True, '#ffffff')
            txt_rect = text.get_rect(center=(rect.centerx, rect.centery))
            self.screen.blit(text, txt_rect)

    def delete_confirmation_save(self, save_file: int):
        """Shows the message for a save file deletion"""

        def after_func():
            self.on_title = 'saves'

        box_rect, draw_txt = self.draw_popup_menu(500, 260, self.temp, after_func)

        if draw_txt:
            font = py.font.Font(self.font, box_rect.width // 10)
            mouse = py.mouse.get_pos()
            pressed = self.detect_mouse_press(0)
            for idx, text in enumerate(('Are you sure you want to', 'delete this save file?',
                                        'Note: This file\'s progress will be gone forever!')):
                if idx == 2:
                    font = py.font.Font(self.font, box_rect.width // 16)
                text = font.render(text, True, '#ffffff')
                text_rect = text.get_rect(topleft=(box_rect.x + 3, box_rect.y + idx * (box_rect.width // 8) + 2))
                self.screen.blit(text, text_rect)
            for idx, text, col, click_col in ((0, 'Yes', '#fe8888', '#cb6d6d'), (1, 'No', '#8de34d', '#71b63e')):
                rect = py.Rect((box_rect.x + 2 + idx * box_rect.width / 2, box_rect.bottom - box_rect.width / 6 + 4),
                               (box_rect.width / 2 - 4, box_rect.width / 6 - 4))
                if rect.collidepoint(mouse):
                    if pressed:
                        if text == 'Yes':
                            self.planet.temp_progress.reset_save_file(save_file)
                            self.planet.update_save_files()
                        self.temp = False
                    py.draw.rect(self.screen, click_col, rect, border_radius=80)
                else:
                    py.draw.rect(self.screen, col, rect, border_radius=80)
                word = py.font.Font(self.font, box_rect.width // 8)
                word = word.render(text, True, '#ffffff')
                word_rect = word.get_rect(center=(rect.centerx, rect.centery))
                self.screen.blit(word, word_rect)

    def black_loading_screen(self, progress=None):
        """Displays black loading screen"""
        self.run = True
        if progress is None:
            progress, limit = False, 600
        else:
            limit = 385
        if not progress and self.frame >= limit:
            self.temp = False
            self.title_frame = 0

        if not self.temp:
            if self.frame > 300:
                self.frame = 300
            self.frame -= 10 if self.frame > 0 else 0
            if self.frame < 1:
                self.run = False
        else:
            self.frame += 15
        self.draw_shaded_background(self.frame, 255)
        if self.frame >= limit:
            # Display Loading
            dots = round(self.frame * 0.005) % 5
            radius = self.sc_height // 30
            for x in range(0, max(0, dots - 1)):
                py.draw.circle(self.screen, '#ffffff', (x * radius * 2.4 + self.sc_width // 20,
                                                        self.sc_height - self.sc_height // 18), radius, 0)

    def credits(self):
        """Shows the credits"""
        if not self.temp:
            self.frame = 0
            self.title_frame = 1
            self.temp = True
        else:
            self.frame += 15
        self.draw_shaded_background(self.frame, 255)
        playing = self.playing.split(';')
        CREDITS = (
            'ALIEN ADVENTURE PLAYING:',
            playing[0],

            {'Level Design: ': (playing[1].replace('_', ' '),)},

            {'Planet Design: ': (playing[1].replace('_', ' '),)},

            {'Code Design: ': ('Ian Au',)},

            {'Art Design: ': ('Kenny',
                              'Craftpix.net')},

            {'Music/SFX: ': ('Ian Au',)},

            {'Inspiration: ': ('Newer Super Mario Bros. Wii',
                               'Newer Team')},

            {'Code Assist: ': ('Dr. David. Hemer',
                               'Griffpatch')},

            {'Play Testing: ': ('Ian Au',
                                'Dr. David. Hemer',
                                'Paul Peilschmidt',
                                'Madden Ackland')},

            {'Special Thanks: ': ('Jay Park',
                                  'Quan Hoang',
                                  'Minh Nguyen',
                                  'Lukaz Solding',
                                  'Fares Aly',
                                  'Madden Ackland')},

            'And YOU For Playing!'
        )

        if self.frame >= 255:
            y = (self.frame - 255) / -15 / 2 + self.sc_height - 3
            title_font = py.font.Font(self.title_font, round(self.sc_height / 12))
            font = py.font.Font(self.font, round(self.sc_height / 13))
            i = 0
            for title in CREDITS:
                if isinstance(title, dict):
                    text = title_font.render(tuple(title.keys())[0], True, '#ffffff')
                    rect = text.get_rect(topleft=(self.sc_width / 2 - text.get_size()[0] - 4, y))
                    self.screen.blit(text, rect)
                    y += font.get_height() / 2
                    for person in tuple(title.values())[0]:
                        text = font.render(person, True, '#ffffff')
                        rect = text.get_rect(topleft=(self.sc_width / 2 + 4, y + 3))
                        self.screen.blit(text, rect)
                        y += text.get_size()[1] + 10
                else:
                    if i > 5:
                        y += 150
                    text = title_font.render(title, True, '#ffffff')
                    rect = text.get_rect(topleft=((self.sc_width - text.get_size()[0]) / 2, y))
                    self.screen.blit(text, rect)
                    y += text.get_size()[1]
                    if y < -25 and i > 5:
                        for text, y_value in (('Want to create your own? Type:', -title_font.get_height() - 7),
                                              (self.secret_code, 0),
                                              ('On the title screen', title_font.get_height() + 7)):
                            if y_value != 0:
                                font_used = title_font
                            else:
                                font_used = font
                            text = font_used.render(text, True, '#ffffff')
                            rect = text.get_rect(center=(self.sc_width / 2, self.sc_height / 2 + y_value))
                            self.screen.blit(text, rect)
                        if y < -200:
                            self.frame = 254
                            self.temp = False
                i += 1
                if i < 2:
                    y += 25
                else:
                    y += 70

    def level_loading_screen(self, progress):
        """Displays level loading screen"""
        if not progress and self.frame >= self.sc_width + 465:
            self.temp = False
        if not self.temp:
            self.frame -= 15 if self.frame > 0 else 0
            if self.frame < 1:
                self.run = False
        else:
            self.frame += 15 if self.frame < self.sc_width + 480 else 0
        py.draw.rect(self.screen, self.planet.hud.world.col, py.Rect(
            (self.sc_width - self.frame if self.frame <= self.sc_width else 0, 0), (self.screen.get_size())))
        # Showing Planet {}
        if self.frame > self.sc_width / 2:
            text = py.font.Font(self.font, round(self.sc_height / 6))
            text = text.render(f'Region {self.planet.hud.level.id}', True, self.planet.hud.font_col)
            x = self.sc_width * 1.5 - self.frame
            size = text.get_size()
            rect = text.get_rect(
                topleft=(x if x > (self.sc_width - size[0]) / 2 else (self.sc_width - size[0]) / 2,
                         self.sc_height / 2 - size[1]))
            self.screen.blit(text, rect)
        # Showing level name
        if self.frame > self.sc_width / 2 + 237:
            text = py.font.Font(self.font, round(self.sc_height / 12))
            text = text.render(self.planet.hud.level.name, True, self.planet.hud.font_col)
            x = self.sc_width * 1.5 - self.frame + 237
            size = text.get_size()
            rect = text.get_rect(
                topleft=(x if x > (self.sc_width - size[0]) / 2 else (self.sc_width - size[0]) / 2,
                         self.sc_height / 2 + size[1]))
            self.screen.blit(text, rect)

    def game_over_screen(self):
        """Game over screen from losing all lives in a level"""
        self.run = True
        if self.frame > 10000:
            if self.temp:
                self.planet.hud.lives = 5.6
                self.planet.hud.game_overs += 1
                self.frame = 300
            self.temp = False
        if not self.temp:
            self.frame -= 15
            if self.frame < 1:
                self.run = False
        else:
            self.frame += 15
        self.draw_shaded_background(self.frame, 255)

        if self.frame > 255:
            text = py.font.Font(self.title_font, round(self.sc_height / 6))
            y = self.frame / 15 - 255 if self.temp else self.sc_height - (self.frame / 15 - 255)
            temp_dict = {True: 1, False: -1}
            if (y - (self.sc_height - text.get_height()) / 2) * temp_dict[self.temp] > 0:
                y = (self.sc_height - text.get_height()) / 2
            text = text.render("GAME OVER!", True, '#D10303')
            rect = text.get_rect(topleft=(self.sc_width / 8, y))
            self.screen.blit(text, rect)

    def completed_level_loading_screen(self, s, hs):
        """Loading Screen for completing a level"""
        if self.frame >= self.sc_width + 1800:
            self.temp = False
        if not self.temp:
            self.frame -= 15 if self.frame > 0 else 0
            if self.frame < 1:
                self.run = False
                self.title_frame = 0
        else:
            self.frame += 15 if self.frame < self.sc_width + 1815 else 0
        py.draw.rect(self.screen, self.planet.hud.world.col, py.Rect(
            (self.sc_width - self.frame if self.frame <= self.sc_width else 0, 0), (self.screen.get_size())))
        # Displaying score
        if self.frame > self.sc_width / 2:
            text = py.font.Font(self.font, round(self.sc_height / 12))
            text = text.render(f'Score: {s}', True, self.planet.hud.world.col)
            x = self.sc_width * 1.5 - self.frame
            size = text.get_size()
            rect = text.get_rect(
                topleft=(x if x > (self.sc_width - size[0]) / 2 else (self.sc_width - size[0]) / 2,
                         self.sc_height / 2))
            bg_rect = py.Rect((rect.x, rect.y), (rect.width, rect.height))
            bg_rect.width += 50
            bg_rect.x -= 50 / 2
            bg_rect.height += 20
            bg_rect.y -= 20 / 2
            py.draw.rect(self.screen, self.planet.hud.font_col, bg_rect, border_radius=80)
            self.screen.blit(text, rect)
        delay = 200
        if self.frame > self.sc_width + delay and hs > 0:  # Displaying High-score
            if s > hs and (self.frame > self.sc_width + delay + 420 or not self.temp):
                word = s
            else:
                word = hs
            text = py.font.Font(self.font, round(self.sc_height / 20))
            text = text.render(f'HighScore: {word}', True, self.planet.hud.font_col)
            size = text.get_size()[0]
            rect = text.get_rect(topleft=((self.sc_width - size) / 2, self.sc_height / 2 + 40))
            text.set_alpha(min(255, (self.frame - self.sc_width + 100) / 4))
            self.screen.blit(text, rect)
        if self.frame > self.sc_width + delay + 350 and s > hs > 0:
            text = py.font.Font(self.font, round(self.sc_height / 18))
            text = text.render("New HighScore!", True, '#ffcd1c')
            size = text.get_size()[0]
            rect = text.get_rect(topleft=((self.sc_width - size) / 2, self.sc_height / 2 - 50))
            bg_rect = py.Rect((rect.x, rect.y), (rect.width, rect.height))
            bg_rect.width += 50
            bg_rect.x -= 50 / 2
            bg_rect.height += 20
            bg_rect.y -= 20 / 2
            py.draw.rect(self.screen, '#000000', bg_rect, border_radius=80)
            self.screen.blit(text, rect)

    def level_pause(self):
        """Level pause menu"""
        box_rect, draw_text = self.draw_popup_menu(300, 150, isinstance(self.temp, bool), None)

        if draw_text:
            text = py.font.Font(self.font, round(box_rect.width / 8))
            text = text.render(f'{self.planet.hud.level.id}: {self.planet.hud.level.name}', True, '#ffffff')
            self.screen.blit(text, (box_rect.x + 2, box_rect.y + 2))

            y = box_rect.y + box_rect.width / 6
            mouse, pressed = py.mouse.get_pos(), py.mouse.get_pressed()[0]
            for text, col, click_col in (('Continue', '#39c3fc', '#15a3d3'), ('Exit', '#Fa8787', '#Ff6262')):
                rect = py.Rect((box_rect.x + 2, y + 2), (box_rect.width - 4, box_rect.width / 6 - 4))
                if rect.collidepoint(mouse):
                    if pressed:
                        if text == 'Continue':
                            self.temp = 'run'
                        else:
                            self.temp = 'exit'
                    py.draw.rect(self.screen, click_col, rect, border_radius=80)
                else:
                    py.draw.rect(self.screen, col, rect, border_radius=80)
                word = py.font.Font(self.font, round(box_rect.width / 8))
                word = word.render(text, True, '#ffffff')
                word_rect = word.get_rect(center=(rect.centerx, rect.centery))
                self.screen.blit(word, word_rect)
                y += box_rect.width / 6

    def planet_menu(self):
        """Planet pause menu"""
        box_rect, draw_text = self.draw_popup_menu(350, 400, isinstance(self.temp, bool), None)

        if draw_text:
            mouse_pos = py.mouse.get_pos()
            pressed = self.detect_mouse_press(0)
            keys = py.key.get_pressed()

            font = py.font.Font(self.font, box_rect.width // 10)
            title = font.render('Planet Menu', True, '#ffffff')
            title_rect = title.get_rect(topleft=(box_rect.x + 2, box_rect.y + 2))
            self.screen.blit(title, title_rect)
            ext_txt = font.render('X', True, '#ffffff')
            ext = py.Rect((box_rect.x + box_rect.width - ext_txt.get_size()[0] - 6, box_rect.y + 3),
                          (ext_txt.get_size()[0] + 2, ext_txt.get_size()[0] + 2))
            if ext.collidepoint(mouse_pos):
                col = '#7c7c7c'
                if pressed:
                    self.y_scroll = -21
                    self.temp = 'run'
            else:
                col = '#969696'
            py.draw.rect(self.screen, col, ext, border_radius=80)
            txt_rect = ext_txt.get_rect(center=(ext.centerx, ext.centery))
            self.screen.blit(ext_txt, txt_rect)

            x, y = title_rect.x + 5, title_rect.y + title_rect.height + 6
            self.planet.hud.draw_player_lives(x, y, title_rect.height, self.planet.hud.lives)
            x = box_rect.width / 3 + box_rect.x + 8
            self.level.hud.paint_coins(x, y, title_rect.height * 1.5, True)
            x = box_rect.width / 3 * 2 + box_rect.x
            self.planet.hud.draw_gem_count(x, y, title_rect.height)
            x, y = title_rect.x + 5, title_rect.y + (title_rect.height + 6) * 2 - 3
            txt = font.render(f'Game Overs: {self.planet.hud.game_overs}', True, '#ffffff')
            txt_rect = txt.get_rect(topleft=(x, y))
            self.screen.blit(txt, txt_rect)
            y += title_rect.height + 12

            if self.cur_planet > len(self.planet.editor.worlds):
                self.cur_planet = 1
            elif self.cur_planet < 1:
                self.cur_planet = len(self.planet.editor.worlds)
            cur_world = tuple(self.planet.editor.worlds.values())[self.cur_planet - 1]
            if self.prev_planet:
                while cur_world.name == self.prev_planet[0] and self.prev_planet[1] != 0:
                    self.cur_planet += self.prev_planet[1]
                    if not 1 < self.cur_planet < len(self.planet.editor.worlds):
                        self.cur_planet = 1 if self.cur_planet >= 0 else len(self.planet.editor.worlds)
                        break
                    cur_world = tuple(self.planet.editor.worlds.values())[self.cur_planet - 1]
                self.prev_planet = None
            worlds = [w for w in self.planet.editor.worlds.values() if w.name == cur_world.name]
            all_levels = []
            for world in worlds:
                all_levels += world.get_all_levels_in_world(self.planet.editor)
            all_levels = sorted(all_levels, key=lambda l: l.id)
            if all_levels:
                cur_planet = f'{all_levels[0].id[0]}: {cur_world.name}'
            else:
                cur_planet = cur_world.name

            planet_rect = py.Rect((x - 5, y), (box_rect.width - 2 * 2, title_rect.height))
            py.draw.rect(self.screen, cur_world.col, planet_rect, border_radius=80)
            col = self.contrast_color(cur_world.col)

            for i, txt in enumerate(('<', cur_planet, '>')):
                txt = font.render(txt, True, col)
                if i < 1:
                    txt_rect = txt.get_rect(topleft=(planet_rect.left + 4, planet_rect.top))
                elif 0 < i < 2:
                    txt_rect = txt.get_rect(center=(planet_rect.centerx, planet_rect.centery))
                else:
                    txt_rect = txt.get_rect(topright=(planet_rect.right - 4, planet_rect.top))
                self.screen.blit(txt, txt_rect)

            orig_y = y + txt_rect.height
            y += 10 - self.y_scroll - title_rect.height + 3
            limiter = set()
            for level in all_levels:
                y += title_rect.height + 3
                if y < orig_y + 13:  # Above the scroll limit
                    limiter.add(True)
                    continue
                elif y > box_rect.bottom - title_rect.height - 6:  # Below the scroll limit
                    limiter.add(False)
                    continue
                self.planet.hud.show_level(x, y, level=level, font=font, size=10,
                                           add_segs=[box_rect.width / 8, box_rect.width / 1.6])

            # User inputs
            if keys[py.K_RIGHT] or keys[py.K_d] or keys[py.K_LEFT] or keys[py.K_a]:
                self.left_right_pressed = (keys[py.K_RIGHT] or keys[py.K_d]) - (keys[py.K_LEFT] or keys[py.K_a])
            elif self.left_right_pressed != 0:
                self.cur_planet += self.left_right_pressed
                self.prev_planet = cur_world.name, self.left_right_pressed
                self.left_right_pressed = 0

            y_scroll = 2 * (keys[py.K_DOWN] or keys[py.K_s]) - (keys[py.K_UP] or keys[py.K_w])
            if True not in limiter and y_scroll < 0:
                pass
            elif False not in limiter and y_scroll > 0:
                pass
            else:
                self.y_scroll += y_scroll

            # Top and bottom rectangles
            length = box_rect.width - 2 * 2, 15
            for y in (orig_y, box_rect.bottom - 10):
                rect = py.Rect((x, y), length)
                py.draw.rect(self.screen, '#191919', rect)

    def controls_menu(self):
        """Displays controls menu"""
        box_rect, draw_text = self.draw_popup_menu(350, 400, isinstance(self.temp, bool), None)

        if draw_text:
            mouse_pos = py.mouse.get_pos()
            pressed = self.detect_mouse_press(0)

            font = py.font.Font(self.font, box_rect.width // 10)
            title = font.render('Controls Description', True, '#ffffff')
            title_rect = title.get_rect(topleft=(box_rect.x + 2, box_rect.y + 2))
            self.screen.blit(title, title_rect)
            ext_txt = font.render('X', True, '#ffffff')
            ext = py.Rect((box_rect.x + box_rect.width - ext_txt.get_size()[0] - 6, box_rect.y + 3),
                          (ext_txt.get_size()[0] + 2, ext_txt.get_size()[0] + 2))
            if ext.collidepoint(mouse_pos):
                col = '#7c7c7c'
                if pressed:
                    self.y_scroll = -21
                    self.temp = 'run'
            else:
                col = '#969696'
            py.draw.rect(self.screen, col, ext, border_radius=80)
            txt_rect = ext_txt.get_rect(center=(ext.centerx, ext.centery))
            self.screen.blit(ext_txt, txt_rect)

            CONTROLS = (
                'Planet:',
                {'WASD or Arrows': 'Moving Around'},
                {'SPACE': 'Enter Level'},
                'Levels:',
                {'AD/<- ->': 'Move'},
                {'W or UP Arrow': 'Access Doors or Climb'},
                {'SPACE': 'Jump'},
                {'CTRL/SHIFT/T/G': 'Sprint'},
                {'R/F/B': 'Use Item'},
                {'S or Down Arrow': 'Use Shield'},
                {'0': 'Menu'}
            )
            y = title_rect.y + title_rect.height + 6
            font = py.font.Font(self.font, box_rect.width // 15)
            for txt in CONTROLS:
                if type(txt) is dict:
                    text = font.render(tuple(txt.keys())[0], True, '#ffffff')
                    rect = text.get_rect(topleft=(box_rect.left + 8, y))
                    self.screen.blit(text, rect)
                    text = font.render(tuple(txt.values())[0], True, '#ffffff')
                    rect = text.get_rect(topleft=(box_rect.centerx + 8, y))
                    self.screen.blit(text, rect)
                    y += rect.height + 2
                else:
                    y += 5
                    text = font.render(txt, True, '#ffffff')
                    rect = text.get_rect(center=(box_rect.centerx, y + 2))
                    y += rect.height + 5
                    self.screen.blit(text, rect)

    @staticmethod
    def color_change(frame) -> tuple:
        """Returns the color value from the given frame, copied from hud"""
        if isinstance(frame, str):
            # Preferably get max but any string works, returning the maximum value possible
            return 765,
        frame = round(frame)
        r, g, b = 0, 0, 0
        if 0 <= frame <= 255:
            b = 255 - frame
            r = frame
        elif 255 < frame <= 510:
            r = 255 - (frame - 255)
            g = frame - 255
        elif 510 < frame <= 765:
            g = 255 - (frame - 510)
            b = frame - 510
        else:
            raise KeyError(f'Number {frame} cannot be defined, number must be between 0 and 765')
        return r, g, b

    @staticmethod
    def contrast_color(col) -> str:
        """Contrasts (background) color with white or black"""
        if col[0] == '#':
            color = col.lstrip('#')
            rgb = list(int(color[i:i + 2], 16) for i in (0, 2, 4))
            combined = sum(rgb) > 383
            if combined:
                return '#000000'
            else:
                return '#ffffff'
        else:
            raise ValueError("Color entered must be in hex format")
