from .enemies import *
from .items import *


class All_Entities:
    """Storing all entities"""
    __slots__ = 'screen', 'sc_width', 'sc_height', 'player', 'editor', 'hud', 'entity_size', 'path', 'camera_x', \
                'camera_y', 'grid_list', 'grid_list_info', 'entities', 'running_entities', 'entity_dict', 'door_state',\
                'total_doors', 'key_cls'

    def __init__(self, win: py.display, player_cls, editor_cls, hud_cls, size, path=''):
        self.screen = win
        self.sc_width, self.sc_height = self.screen.get_size()
        self.player = player_cls
        self.editor = editor_cls
        self.hud = hud_cls
        self.entity_size = size
        self.path = path
        self.camera_x = 0
        self.camera_y = 0

        self.grid_list = {}
        self.grid_list_info = {}
        self.entities = {}
        self.running_entities = {}
        self.entity_dict = {566: Bomb,
                            567: {0: Button}, 569: {0: Button}, 571: {0: Button}, 573: {0: Button},
                            575: {0: Coin}, 576: {0: Coin}, 577: {0: Coin},
                            578: [Checkpoint], 587: [Checkpoint],
                            581: [Goal_Flag], 584: [Goal_Flag],
                            590: {0: Gem}, 591: {0: Gem}, 592: {0: Gem}, 593: {0: Gem},
                            594: [Key], 595: [Key], 596: [Key], 597: [Key],
                            598: {0: Ladder}, 599: {0: Ladder},
                            600: {0: Laser_Switch}, 602: {0: Laser_Switch}, 604: {0: Laser_Switch},
                            606: {0: Laser_Switch},
                            608: {0: Ray_Gun}, 609: {0: Ray_Gun}, 610: {0: Ray_Gun}, 611: {0: Ray_Gun},
                            612: {0: Shield}, 613: {0: Shield}, 614: {0: Shield},
                            615: Spring, 617: Star, 618: Wooden_Switch,
                            621: {0: Sword}, 622: {0: Sword}, 623: {0: Sword},
                            624: Umbrella, 626: {0: Weight}, 627: {0: Weight},
                            629: Barnacle, 633: Bat, 638: Bee,
                            642: {0: Spike}, 643: {0: Spike}, 644: {0: Fish}, 648: {0: Fish}, 652: Fly,
                            656: Frog, 660: Ghost, 664: (Grass_Block,), 668: Ladybug, 672: Mouse, 676: Piranha,
                            680: (Slime_Block,), 683: {0: Slime}, 688: {0: Slime}, 693: {0: Slime},
                            698: Snail, 702: {0: Snake}, 706: {0: Snake_Up}, 710: {0: Snake_Up}, 714: Spider,
                            719: {0: Spike}, 720: {0: Spike}, 721: {0: Spike}, 722: {0: Spike}, 723: {0: Spike},
                            724: {0: Spike}, 725: {0: Spike}, 726: {0: Spike}, 727: {0: Spinner}, 731: {0: Spinner},
                            735: {0: Spike}, 736: {0: Spike}, 737: {0: Snake},
                            163: [Door, [175, 163], ''], 164: [Door, [176, 164], ''], 165: [Door, [177, 165], ''],
                            166: [Door, [178, 166], ''], 171: [Door, [179, 171], ''], 173: [Door, [180, 173], ''],
                            267: [Door, [181, 267], ''], 272: [Laser_Shooter, [182, 272]],
                            274: [Laser_Shooter, [184, 274]], 276: [Laser_Shooter, [186, 276]],
                            278: [Laser_Shooter, [188, 278]], 741: Fireball, 742: [Laser, [191, 742]],
                            745: [Laser, [194, 745]], 748: Ray_Fire, 750: [Laser, [199, 750]], 753: [Laser, [202, 753]]}

        # For doors and groups
        self.door_state = False
        self.total_doors = 0

        # For Keys
        self.key_cls = Key

    def init_entities(self):
        """Initializes all entities"""
        Door.total_doors = 0
        self.entities = {}
        for entity in self.grid_list:
            spawn_entity = self.entity_dict[int(self.grid_list[entity])]
            if entity in self.grid_list_info:
                info = str(self.grid_list_info[entity])
            else:
                info = "0"

            if isinstance(spawn_entity, tuple):  # Moving Tiles
                self.entities[entity] = spawn_entity[0](self.screen, self.path, self.grid_list_info[entity],
                                                        player_cls=self.player, editor_cls=self.editor,
                                                        hud_cls=self.hud, entity_cls=self)
            elif isinstance(spawn_entity, list):
                if len(spawn_entity) > 1:  # Door & Laser
                    entity_type = spawn_entity[1]
                else:  # Checkpoint
                    entity_type = int(self.grid_list[entity])
                info = f"{entity}|{info}"
                self.entities[entity] = spawn_entity[0](entity_type, self.screen, self.path, info,
                                                        player_cls=self.player, editor_cls=self.editor,
                                                        hud_cls=self.hud, entity_cls=self)

            elif isinstance(spawn_entity, dict):
                self.entities[entity] = spawn_entity[0](int(self.grid_list[entity]), self.screen, self.path, info,
                                                        player_cls=self.player, editor_cls=self.editor,
                                                        hud_cls=self.hud, entity_cls=self)
            else:
                self.entities[entity] = spawn_entity(self.screen, self.path, info,
                                                     player_cls=self.player, editor_cls=self.editor,
                                                     hud_cls=self.hud, entity_cls=self)

        # Init Entities
        other_enemies = {}
        for tile_idx, entity in self.entities.items():
            if hasattr(entity, 'enemies') or hasattr(entity, 'switch_groups'):
                other_enemies[tile_idx] = entity
                continue
            entity.init_entity(tile_idx)
        for tile_idx, entity in other_enemies.items():
            entity.init_entity(tile_idx)

        self.total_doors = Door.total_doors
        Gem.collected = 0

    def add_to_entities(self, tile_idx, idx, info=None):
        """Adds an entity to the entities dict"""
        spawn_entity = self.entity_dict[idx]
        if isinstance(spawn_entity, tuple):  # Moving tiles
            info = f"False;False;2;2;10;1.0;{tile_idx}"
            self.entities[tile_idx] = spawn_entity[0](self.screen, self.path, info,
                                                      player_cls=self.player, editor_cls=self.editor, hud_cls=self.hud,
                                                      entity_cls=self)
        elif isinstance(spawn_entity, list):
            if len(spawn_entity) > 2:  # Door
                entity_type = spawn_entity[1]
                info = f"{tile_idx}|{info if info is not None else '0-0'}"
            elif len(spawn_entity) > 1:  # Laser
                entity_type = spawn_entity[1]
                info = f"{tile_idx}|g"
            else:  # Checkpoint
                entity_type = idx
                info = f"{tile_idx}|{info}"
            self.entities[tile_idx] = spawn_entity[0](entity_type, self.screen, self.path, info,
                                                      player_cls=self.player, editor_cls=self.editor,
                                                      hud_cls=self.hud, entity_cls=self)
        elif isinstance(spawn_entity, dict):
            if spawn_entity[0].__name__ == 'Laser_Switch':
                info = "False-0"
            self.entities[tile_idx] = spawn_entity[0](idx, self.screen, self.path, info,
                                                      player_cls=self.player, editor_cls=self.editor, hud_cls=self.hud,
                                                      entity_cls=self)
        else:
            self.entities[tile_idx] = spawn_entity(self.screen, self.path, info,
                                                   player_cls=self.player, editor_cls=self.editor, hud_cls=self.hud,
                                                   entity_cls=self)
        self.entities[tile_idx].init_entity(tile_idx)
        self.total_doors = Door.total_doors

    def delete_from_entities(self, tile_idx):
        """Removes an entity from the entities dict"""
        del self.entities[tile_idx]

    def update_entities(self, update_all=False):
        """Updates all entities camera positions"""
        if update_all:
            entities = self.entities
        else:
            entities = self.running_entities
        for entity in entities:
            self.entities[entity].camera_x = self.camera_x
            self.entities[entity].camera_y = self.camera_y

    def move_entity(self):
        """Entity Mainloop"""
        i = 0
        self.update_running_entities()
        # self.update_entities(True)
        # Initializes Movable Tile touching values
        for groups, value in Movable_Tile.group_touching.items():
            Movable_Tile.group_touching[groups] += 1
        self.player.can_climb = False

        for entity in self.running_entities:
            # Reset global values
            if not self.entities[entity].__class__.__name__ == "Spike":
                self.entities[entity].global_ = False
            self.entities[entity].update_draw_pos()
            self.entities[entity].mainloop()
            i += 1

        # Updates movable tile positions
        for entity in {k: v for k, v in self.entities.items() if
                       hasattr(v, 'update_touch') and floor(v.group) in Movable_Tile.group_touching}:
            if Movable_Tile.group_touching[floor(self.entities[entity].group)] == 0:
                self.entities[entity].update_touch()
            # i += 1

        self.update_entities()
        Barnacle.img_frame += 0.01
        print(i)

    def draw_entity(self):
        """Draws all entities onto screen"""
        self.update_entities(True)
        for entity in self.entities:
            if hasattr(entity, 'collected'):
                continue
            self.entities[entity].update_draw_pos()
            self.entities[entity].draw()

    def draw_items(self):
        """Draws all items"""
        for entity in (k for k, v in self.entities.items() if hasattr(v, 'collected')):
            self.entities[entity].update_draw_pos()
            self.entities[entity].draw()

    # Optimization: Instead of running for all entities, run the ones on screen
    # From min 56 fps -> min 58 fps
    def on_screen(self, ent) -> bool:
        """Determines if the entity shouuld be checked"""
        if ent.global_ or ent.global__:
            return True
        draw_x = ent.x - self.camera_x
        draw_y = ent.y - self.camera_y
        return not (draw_x < -ent.width - ent.tile_size * 6 or \
                    draw_x > self.sc_width + ent.tile_size * 6 or \
                    draw_y > self.sc_height + ent.tile_size * 6 or \
                    draw_y < -ent.height - ent.tile_size * 6)

    def update_running_entities(self):
        self.running_entities = [(key, value) for key, value in self.entities.items() if self.on_screen(value)]
        self.running_entities = sorted(self.running_entities, key=lambda x: self.sort_entities(x[1]))
        self.running_entities = (key for key, value in self.running_entities)

    @staticmethod
    def sort_entities(entity) -> int:
        """Sorts entities based on drawing priority"""
        if hasattr(entity, 'mov_dir'):
            return 0
        if entity.show_last:
            return 9
        return 10

