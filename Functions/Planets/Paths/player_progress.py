from os.path import join
import sqlite3


class Database:
    """Planet Database Functions"""
    __slots__ = 'path', 'con', 'cur', 'save_file'

    def __init__(self, save_file, path):
        """Connect to Database"""
        self.path = path
        self.con = sqlite3.connect(join(path, 'Data', 'Save_Files.db'))
        self.cur = self.con.cursor()
        self.save_file = save_file

        # Save Files
        for i in range(0, 4):
            try:
                self.cur.execute(f"CREATE TABLE Save{i} (level TEXT, state TEXT, collected TEXT, high_score INTEGER)")
            except sqlite3.OperationalError:
                if i == 0:
                    self.delete_all(i)
                    self.init_save_file(i)
            else:
                self.init_save_file(i)

    def init_save_file(self, save_file):
        """initializes current save file"""
        # First row is Coins, Lives, Items, Total_Gems_Collected
        self.insert_to_save('0', '3.6', '', '0', save_file)
        # Second row is player position, game_over_count, planet name, None
        self.insert_to_save('1-1', '0', '', '', save_file)

    def insert_to_save(self, level, state, collected, high_score, save_file=None):
        """Adds level data to current save file"""
        if save_file is None:
            save_file = self.save_file
        self.cur.execute(f"INSERT INTO Save{save_file} VALUES (:level, :state, :collected, :high_score)",
                         {'level': level, 'state': state, 'collected': collected, 'high_score': high_score})
        self.con.commit()

    def get_data_in_save(self):
        """Returns save file data"""
        self.cur.execute(f"SELECT *, oid FROM Save{self.save_file}")
        return self.cur.fetchall()

    def delete_all(self, save_file=None):
        """Deletes all from current save file"""
        if save_file is None:
            save_file = self.save_file
        self.cur.execute(f"DELETE from Save{save_file}")
        self.con.commit()

    def reset_save_file(self, save_file):
        """Resets save file specified"""
        orig_save_file = self.save_file
        self.save_file = save_file
        self.delete_all()
        self.init_save_file(self.save_file)
        self.save_file = orig_save_file


class Player_Progress(Database):
    """Class for handling player progress"""
    __slots__ = 'hud_data', 'level_data', 'paths', 'editor'

    def __init__(self, save_file: int, path, editor_cls):
        super().__init__(save_file, path)

        data = self.get_data_in_save()
        self.hud_data = {'coins': data[0][0], 'lives': data[0][1], 'items': data[0][2], 'gem_count': int(data[0][3]),
                         'spawn': data[1][0], 'game_over': int(data[1][1]), 'planet': data[1][2]}
        del data[:2]  # How to delete the first two items of the list

        self.level_data = {level: {'state': s, 'collected': [int(v) for v in (c.split(',') if c else [])],
                                   'high_score': int(h)} for level, s, c, h, _ in data}

        self.paths = {}
        self.editor = editor_cls

        self.init_level_data()
        self.init_paths()

    @classmethod
    def get_all_save_data(cls, path, editor_cls) -> dict:
        """Collects all save data information (only hud data)"""
        saves = {}
        for i in range(0, 4):
            saves[i] = cls(i, path, editor_cls).hud_data
        return saves

    def save_hud_data(self, coins, lives, items, gem_count, spawn, game_overs):
        """Saves hud data to hud_data dict"""
        for key, value in (('coins', coins), ('lives', lives), ('items', items), ('gem_count', gem_count),
                           ('spawn', spawn), ('game_over', game_overs)):
            self.hud_data[key] = value

    def init_level_data(self):
        """Initializes level data to check for any missed levels"""
        for level in dict(self.level_data):
            levels = {key: value for key, value in self.editor.levels.items() if level == value.id}
            if not levels:
                del self.level_data[level]
        for level in self.editor.levels.values():
            if level.id not in self.level_data:
                self.level_data[level.id] = {'state': '', 'collected': [], 'high_score': 0}

    """Path functions"""

    def init_paths(self):
        """Initializes paths dictionary: shows paths or not"""
        for level_id, level in self.level_data.items():
            if 'green' in level['state']:
                tile_idx = tuple({key: value for key, value in self.editor.levels.items()
                                  if value.id == level_id}.keys())[0]
                all_paths = self.editor.pathfind.find_all_paths_from(tile_idx, self.editor.levels[tile_idx].paths)
                for path in all_paths:
                    self.paths[path] = 255
            if 'red' in level['state']:
                tile_idx = tuple({key: value for key, value in self.editor.levels.items()
                                  if value.id == level_id}.keys())[0]
                all_paths = self.editor.pathfind.find_all_paths_from(tile_idx,
                                                                     self.editor.levels[tile_idx].secret_paths)
                for path in all_paths:
                    self.paths[path] = 255

    def unlock_path(self, level, green_or_red):
        """Unlocks the next path, Green=True, Red=False"""
        if green_or_red and 'green' not in self.level_data[level]['state']:
            self.level_data[level]['state'] += 'green'
            tile_idx = tuple({key: value for key, value in self.editor.levels.items()
                              if value.id == level}.keys())[0]
            all_paths = self.editor.pathfind.find_all_paths_from(tile_idx, self.editor.levels[tile_idx].paths)
            for path in all_paths:
                self.paths[path] = 1
        elif not green_or_red and 'red' not in self.level_data[level]['state']:
            self.level_data[level]['state'] += 'red'
            tile_idx = tuple({key: value for key, value in self.editor.levels.items()
                              if value.id == level}.keys())[0]
            all_paths = self.editor.pathfind.find_all_paths_from(tile_idx, self.editor.levels[tile_idx].secret_paths)
            for path in all_paths:
                self.paths[path] = 1

    def close(self):
        self.delete_all()
        if self.save_file == 0:
            self.con.close()
            return None

        self.insert_to_save(self.hud_data['coins'], self.hud_data['lives'], self.hud_data['items'],
                            self.hud_data['gem_count'])
        self.insert_to_save(self.hud_data['spawn'], self.hud_data['game_over'], self.hud_data['planet'], '')
        for row in self.level_data:
            self.insert_to_save(row, self.level_data[row]['state'],
                                ','.join([str(v) for v in self.level_data[row]['collected'] if 12 <= v <= 15]),
                                self.level_data[row]['high_score'])
        self.con.close()
