from os.path import join
import sqlite3


class Database:
    """Planet Database Functions"""
    __slots__ = 'path', 'con', 'cur'

    def __init__(self, path):
        """Connect to Database"""
        self.path = path
        self.con, self.cur = None, None

    def setup_database(self, db):
        """Setups database"""
        db = db.split(' ')
        db = '_'.join(db)
        self.con = sqlite3.connect(join(self.path, 'Data', 'Planets', f'{db}.db'))
        self.cur = self.con.cursor()

        # Planet Table
        try:
            self.cur.execute("CREATE TABLE planet (name TEXT, grid TEXT, overlaps TEXT, levels TEXT, worlds TEXT)")
        except sqlite3.OperationalError:
            pass
        else:
            self.add_planet('My World', '', '', '', '')

    def add_planet(self, name, grid, overlaps, levels, worlds):
        """Adds new level to the database"""
        self.cur.execute("INSERT INTO planet VALUES (:name, :grid, :overlap, :levels, :worlds)",
                         {'name': name, 'grid': grid, 'overlap': overlaps, 'levels': levels, 'worlds': worlds})
        self.con.commit()

    def get_planet(self):
        """Returns planet code"""
        self.cur.execute("SELECT *, oid FROM planet")
        return self.cur.fetchall()

    def delete_all(self):
        """Deletes all from planet"""
        self.cur.execute("DELETE from planet")
        self.con.commit()


class Planet_Store(Database):
    """Class for sorting levels and database reading"""
    __slots__ = 'encoded', 'letter', 'read_idx', 'value', 'planet', 'planet_name', 'a_to_z', 'z_to_a'

    def __init__(self, path):
        super().__init__(path)
        self.encoded = ''
        self.letter = ''
        self.read_idx = 0
        self.value = ''
        self.planet = None
        self.planet_name = None

        self.a_to_z = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i', 10: 'j', 11: 'k',
                       12: 'l', 13: 'm', 14: 'n', 15: 'o', 16: 'p', 17: 'q', 18: 'r', 19: 's', 20: 't', 21: 'u',
                       22: 'v', 23: 'w', 24: 'x', 25: 'y', 26: 'z'}
        self.z_to_a = {key: value for value, key in self.a_to_z.items()}

    def setup_planet(self):
        self.planet = {name: {'grid': grid, 'overlap': overlap, 'level': level, 'world': world}
                       for name, grid, overlap, level, world, _ in self.get_planet()}
        self.planet_name = tuple(self.planet.keys())[0]

    def write_value_with_delimiter(self, value, delimiter: str):
        """writes the value with the delimiter into the str list"""
        self.encoded = ''.join([self.encoded, str(value), delimiter])

    def read_letter(self):
        """Gives the letter from the read_idx"""
        if len(self.encoded) < 1:
            self.letter = ''
        else:
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
                self.value = ''.join([self.value, str(self.letter)])
                self.read_letter()
            except ValueError:
                break

    def save_planet(self, planet_name, grid_width, grid_height, grid, overlaps, level, world):
        """Saves the level given to the Database"""
        self.encoded = ''
        self.write_value_with_delimiter(1, '_')
        self.write_value_with_delimiter(grid_width, '_')
        self.write_value_with_delimiter(grid_height, '_')
        tile_idx = 0
        tile = grid[tile_idx]
        length = 0
        for x in range(grid_width):
            for y in range(grid_height):
                if tile == grid[tile_idx] and length < 26:
                    length += 1
                else:
                    self.write_value_with_delimiter(tile, self.a_to_z[length])
                    tile = grid[tile_idx]
                    length = 1
                tile_idx += 1
        self.write_value_with_delimiter(tile, self.a_to_z[length])
        self.planet[planet_name]['grid'] = self.encoded

        overlap_tiles = ''
        for o_idx, o_tile_idx in overlaps.items():
            overlap_tiles = ','.join([overlap_tiles, ':'.join([str(o_idx), str(o_tile_idx)])])
        self.planet[planet_name]['overlap'] = overlap_tiles

        levels = ''
        for tile_idx, level_data in level.items():
            levels = ','.join([levels, ':'.join([str(tile_idx), '|'.join(level_data)])])
        self.planet[planet_name]['level'] = levels

        worlds = ','.join([world_data for world_data in world])
        self.planet[planet_name]['world'] = worlds
        self.planet_name = planet_name

        self.delete_all()
        self.add_planet(self.planet_name, self.planet[self.planet_name]['grid'],
                        self.planet[self.planet_name]['overlap'],
                        self.planet[self.planet_name]['level'], self.planet[self.planet_name]['world'])

    def load_planet(self):
        self.encoded = self.planet[self.planet_name]['grid']
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
                    [o_tile.split(':') for o_tile in self.planet[self.planet_name]['overlap'].split(',')
                     if o_tile != '']}
        levels = {}
        for level in self.planet[self.planet_name]['level'].split(','):
            tile_idx = level.split(':')
            if len(tile_idx) < 2:
                continue
            levels[tile_idx[0]] = tile_idx[1].split('|')

        worlds = {}
        i = 0
        for world in self.planet[self.planet_name]['world'].split(','):
            world_name = world.split(':')
            if len(world_name) < 2:
                continue
            world_name = [world_name[0]] + world_name[1].split('|')
            worlds[i] = world_name
            i += 1
        return self.planet_name, grid_width, grid_height, tile_grid, overlaps, levels, worlds

    def close(self):
        """Closes Database and save changes"""
        self.delete_all()
        self.add_planet(self.planet_name, self.planet[self.planet_name]['grid'],
                        self.planet[self.planet_name]['overlap'],
                        self.planet[self.planet_name]['level'], self.planet[self.planet_name]['world'])
        self.con.close()
