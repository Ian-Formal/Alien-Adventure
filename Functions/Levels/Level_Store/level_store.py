from os.path import join
import sqlite3


class Database:
    """Level Database Functions"""
    __slots__ = 'path', 'con', 'cur'

    def __init__(self, path):
        """Connect to Database"""
        self.path = path
        self.con, self.cur = None, None

    def setup_database(self, db):
        """Setups Database"""
        db = db.split(' ')
        db = '_'.join(db)
        self.con = sqlite3.connect(join(self.path, 'Data', 'Planets', f'{db}.db'))
        self.cur = self.con.cursor()

        # Level Table
        try:
            self.cur.execute("CREATE TABLE levels (level_id TEXT, level TEXT, overlaps TEXT, entities TEXT, "
                             "time INTEGER, camera TEXT, background TEXT)")
        except sqlite3.OperationalError:
            pass
        else:
            self.add_level('', '', '', '', 500, '', '')

    def add_level(self, level_id, level_code, overlaps, entity_code, time: int, camera, background):
        """Adds new level to the database"""
        self.cur.execute("INSERT INTO levels VALUES (:level_id, :level_code, :lap, :entity, :time, :camera, :bg)",
                         {'level_id': level_id, 'level_code': level_code, 'lap': overlaps, 'entity': entity_code,
                          'time': time, 'camera': camera, 'bg': background})
        self.con.commit()

    def get_all_levels(self):
        """Returns all level codes"""
        self.cur.execute("SELECT *, oid FROM levels")
        return self.cur.fetchall()

    def delete_all(self):
        """Deletes all from levels"""
        self.cur.execute("DELETE from levels")
        self.con.commit()


class Level_Store(Database):
    """Class for sorting levels and database reading"""
    __slots__ = 'encoded', 'letter', 'read_idx', 'value', 'levels', 'a_to_z', 'z_to_a'

    def __init__(self, path):
        super().__init__(path)
        self.encoded = ''
        self.letter = ''
        self.read_idx = 0
        self.value = ''
        self.levels = None

        self.a_to_z = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i', 10: 'j', 11: 'k',
                       12: 'l', 13: 'm', 14: 'n', 15: 'o', 16: 'p', 17: 'q', 18: 'r', 19: 's', 20: 't', 21: 'u',
                       22: 'v', 23: 'w', 24: 'x', 25: 'y', 26: 'z'}
        self.z_to_a = {key: value for value, key in self.a_to_z.items()}

    def setup_levels(self):
        self.levels = {key: {'level': level, 'overlaps': lap, 'entities': ent, 'time': int(t), 'camera': c, 'bg': bg}
                       for key, level, lap, ent, t, c, bg, _ in self.get_all_levels()}

    def write_value_with_delimiter(self, value, delimiter: str):
        """writes the value with the delimiter into the str list"""
        self.encoded = ''.join([self.encoded, str(value), delimiter])

    def read_letter(self):
        """Gives the letter from the read_idx"""
        self.letter = self.encoded[self.read_idx]
        self.read_idx += 1

    def read_value(self):
        """Translates the value from levels dict"""
        self.value = ''
        self.read_letter()
        while True:
            try:
                if self.letter != '.':
                    self.letter = int(self.letter)
            except ValueError:
                break
            else:
                self.value = ''.join([self.value, str(self.letter)])
                self.read_letter()

    def save_level(self, level_name, level_width, level_height, level_tile_grid, overlaps, entity_grid, time, boxes,
                   background):
        """Saves the level given to the Database"""
        if level_name not in self.levels:
            self.levels[level_name] = {'level': '', 'overlaps': '', 'entities': '', 'time': '', 'camera': '', 'bg': ''}
        self.encoded = ''
        self.write_value_with_delimiter(1, '_')
        self.write_value_with_delimiter(level_width, '_')
        self.write_value_with_delimiter(level_height, '_')
        tile_idx = 0
        tile = level_tile_grid[tile_idx]
        length = 0
        for x in range(level_width):
            for y in range(level_height):
                if tile == level_tile_grid[tile_idx] and length < 26:
                    length += 1
                else:
                    if tile == -1:
                        tile = ''
                    self.write_value_with_delimiter(tile, self.a_to_z[length])
                    tile = level_tile_grid[tile_idx]
                    length = 1
                tile_idx += 1
        self.write_value_with_delimiter(tile, self.a_to_z[length])
        self.levels[level_name]['level'] = self.encoded

        overlap_tiles = ''
        for o_idx, o_tile_idx in overlaps.items():
            overlap_tiles = ','.join([overlap_tiles, ':'.join([str(o_idx), str(o_tile_idx)])])
        self.levels[level_name]['overlaps'] = overlap_tiles

        entities = ''
        for e_idx, e_tile_idx in entity_grid.items():
            entities = ','.join([entities, ':'.join([str(e_idx), str(e_tile_idx)])])
        self.levels[level_name]['entities'] = entities

        self.levels[level_name]['time'] = time

        camera = ','.join([data for data in boxes])
        self.levels[level_name]['camera'] = camera

        backgrounds = '|'.join([str(item) for item in (background[0], background[1])]) + '|'
        for key, value in background[2].items():
            backgrounds += ':'.join([str(key), str(value)]) + ','
        self.levels[level_name]['bg'] = backgrounds

        self.delete_all()
        for level in self.levels:
            self.add_level(level, self.levels[level]['level'], self.levels[level]['overlaps'],
                           self.levels[level]['entities'], self.levels[level]['time'], self.levels[level]['camera'],
                           self.levels[level]['bg'])

    def load_level(self, level: str):
        if level not in self.levels:
            return 0, 0, {}, {}, {}, 500, {}, {0: False, 1: False}
        self.encoded = self.levels[level]['level']
        self.read_idx = 0
        self.read_value()
        grid_width = 0
        grid_height = 0
        tile_grid = {}
        if self.value == '1':
            self.read_value()
            grid_width = int(self.value)
            self.read_value()
            grid_height = int(self.value)
            for tile in range(grid_width * grid_height):
                tile_grid[tile] = -2
            tile_idx = 0
            while self.read_idx < len(self.encoded):
                self.read_value()
                if self.value == '':
                    self.value = -1
                for _ in range(self.z_to_a[self.letter]):
                    tile_grid[tile_idx] = float(self.value)
                    tile_idx += 1
        overlaps = {int(o_idx): float(o_tile_idx) for o_idx, o_tile_idx in
                    [o_tile.split(':') for o_tile in self.levels[level]['overlaps'].split(',') if o_tile != '']}
        entities = {int(e_idx): float(e_tile_idx) for e_idx, e_tile_idx in
                    [e_tile.split(':') for e_tile in self.levels[level]['entities'].split(',') if e_tile != '']}

        camera = {}
        for data in self.levels[level]['camera'].split(','):
            if not data:
                continue
            data = data.split(':')
            camera[data[0]] = data[1].split('|')

        bg = self.levels[level]['bg'].split('|')
        if bg[0]:
            if bg[0].isdigit():
                background = int(bg[0])
            else:
                background = bg[0]
        else:
            background = None
        try:
            show_credits = bg[1] == 'True'
        except IndexError:
            show_credits = False

        all_entity_info = {}
        # In the database: tile_idx:info,839:6374,
        # Following comments track what the code is doing to this string
        try:
            # ["tile_idx:info", "839:6374"]
            entity_info = bg[2].split(',')
        except IndexError:
            pass
        else:
            # Looping through these values one by one
            for entity in entity_info:
                # ["tile_idx", "info"], ...
                entity = entity.split(':')
                if len(entity) < 2:
                    continue
                # {tile_idx: info, ...}
                all_entity_info[int(entity[0])] = entity[1]

        return grid_width, grid_height, tile_grid, overlaps, entities, self.levels[level]['time'], camera, \
            {0: background, 1: show_credits, 2: all_entity_info}

    def close(self):
        """Closes Database and save changes"""
        self.delete_all()
        for level in self.levels:
            self.add_level(level, self.levels[level]['level'], self.levels[level]['overlaps'],
                           self.levels[level]['entities'], self.levels[level]['time'], self.levels[level]['camera'],
                           self.levels[level]['bg'])
        self.con.close()
