import pygame as py
from .entity_settings import Entity, Switch, Collidable_Entity, Power_Up
from math import floor, sin, cos, atan, radians, degrees
"""TOTAL OF 19 Items"""


class Bomb(Entity):
    """Functions for item: Bomb"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        """Initializes entity attributes"""
        super().__init__(win, path, 566, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""


class Button(Switch):
    """Functions for item: Button"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.collided_lasers = {}

    def tick(self):
        """What happens when the entity gets on screen"""
        collided = py.sprite.collide_rect(self.player, self)
        for entity in self.entity.entities.values():
            if entity == self:
                continue
            if py.sprite.collide_rect(entity, self):
                collided = True

        for k, laser in dict(self.collided_lasers).items():
            if py.sprite.collide_rect(laser, self) and laser.show:
                collided = True
            else:
                del self.collided_lasers[k]

        if collided:
            if not self.switched:
                self.toggle(True)
        elif self.switched:
            self.toggle(False)

        self.image = self.images[1 if self.switched else 0]


class Coin(Entity):
    """Functions for item: Coin"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.r_width = 33 * self.scale
        self.r_height = 32 * self.scale

    def tick(self):
        """What happens when the entity gets on screen"""
        self.rect = py.Rect(self.draw_x + 22.5 * self.scale, self.draw_y + 24 * self.scale, self.r_width, self.r_height)
        if py.sprite.collide_rect(self.player, self) and self.show:
            self.collect()

    def collect(self):
        """Collects the coin"""
        # Adding coin counters and scores
        coin_add = {9: (3, 200), 10: (1, 100), 11: (5, 500)}
        self.hud.coins += coin_add[self.idx][0]
        self.hud.animate_coin_jump()
        self.hud.score += coin_add[self.idx][1]

        # Clearing the tile
        self.show = False
        self.destroyed = True

    def bounce_on_mystery(self, from_shell=False):
        if not self.destroyed:
            self.collect()

    def update_rectangle_pos(self):
        """Updates rectangle position"""
        self.rect = py.Rect(self.draw_x + 22.5 * self.scale, self.draw_y + 24 * self.scale, self.r_width, self.r_height)


class Checkpoint(Entity):
    """Functions for item: Checkpoint"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        info = info.split('|')
        super().__init__(win, path, entity_type, info[1], player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.tile_idx = int(info[0])
        self.current_checkpoint = False
        self.save = True

    def tick(self):
        """What happens when the entity gets on screen"""
        if py.sprite.collide_rect(self.player, self) and self.player.checkpoint != self.idx:
            self.player.checkpoint = self.idx + self.__class__.tiles_to_entities
            self.player.spawn_idx = self.tile_idx
            self.handle_other_checkpoints()
            self.current_checkpoint = True
            if self.save:
                # See Alien Adventure file why this list is copied
                self.hud.save_collected = list(self.hud.collected)
                Key.save_collected = set(Key.collected_keys)
                self.tiles.saved_destroyed_tiles = set(self.tiles.destroyed_tiles)
                self.save = False

        if self.current_checkpoint:
            self.image = self.images[round(self.frame * 8) % 2]
            self.save = False
        else:
            self.image = self.images[2]
            self.save = True

    def handle_other_checkpoints(self):
        for entity in self.entity.entities:
            idx = self.entity.entities[entity].idx
            if idx == 12 or idx == 21:
                self.entity.entities[entity].current_checkpoint = False

    def more_init(self):
        self.save = True


class Door(Entity):
    """Functions for item: Button"""
    total_doors = 0

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        info = info.split('|')
        self.tile_idx = int(info[0])
        info = info[1].split('-')

        super().__init__(win, path, entity_type, info[1], player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        if self.group > Door.total_doors:
            Door.total_doors = self.group
        self.other_door = int(info[0])
        self.frame_in_door = 0

    def tick(self):
        """What happens when the entity gets on screen"""
        # If player goes in door by pressing up, touching the door and on the ground
        keys = py.key.get_pressed()
        if py.sprite.collide_rect(self.player, self) and self.player.falling <= 1 and (keys[py.K_UP] or keys[py.K_w])\
                and self.frame_in_door < 1 and \
                self.player.pins['bottom'] < self.y + self.height + self.tiles.tile_size * 1.3:
            self.entity.door_state = True
            self.frame_in_door = 1

        if self.frame_in_door > 0:
            self.frame_in_door += 1
        if not self.entity.door_state and self.frame_in_door > 0:
            self.player.spawn_idx = self.other_door
            self.player.reset_pos(self.editor.grid_height, self.player.tile_size)
            self.frame_in_door = 0

    def check_group_change(self, orig_group):
        if self.group < 1:
            self.group = orig_group
            return None
        self.group = float(floor(self.group))
        self.entity.entities[self.other_door].group = self.group

    def __str__(self):
        """Returns the string for storing this entity data"""
        return f'{self.other_door}-{self.group}'


class Goal_Flag(Entity):
    """Functions for item: Goal Flag"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        info = info.split('|')
        super().__init__(win, path, entity_type, info[1], player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.tile_idx = int(info[0])
        self.touched = False
        self.save = True

    def tick(self):
        """What happens when the entity gets on screen"""
        if py.sprite.collide_rect(self.player, self):
            self.touched = True
            self.player.touching = 'green' if self.idx == 15 else 'red'
        if self.touched:
            self.image = self.images[round(self.frame * 8) % 2]
            if self.save:
                self.player.cp_in_level = None
                keys = [v for v in self.hud.collected if not 12 <= v <= 15]
                if self.hud.score < 1000:
                    score = 0  # Challenge: Score of 0 is possible
                elif self.idx == 15:
                    score = 1000
                else:
                    score = 2000
                self.hud.update_score(score=score, pos=(self.x, self.y))
                if keys:
                    self.hud.collected = self.hud.collected[:-1*len(keys)]
                # See Alien Adventure file on why this list is copied
                self.hud.save_collected = list(self.hud.collected)
                self.save = False
        else:
            self.image = self.images[2]

    def more_init(self):
        self.touched = False
        self.save = True


class Gem(Entity):
    """Functions for item: Gem"""
    collected = 0

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.r_width, self.r_height = 32 * self.scale, 32 * self.scale
        self.collect_animation = -1

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.collect_animation < 0:
            self.rect = py.Rect(self.draw_x + 22.5 * self.scale, self.draw_y + 24 * self.scale,
                                self.r_width, self.r_height)
            if py.sprite.collide_rect(self.player, self) and self.show:
                self.collect()
        else:
            self.y -= 2
            self.alpha = max(self.alpha - 7, 0)
            self.collect_animation += 1
            if self.alpha == 0:
                self.alpha = 255
                self.show = False
                self.hud.update_score(score=1000 * 2 ** self.__class__.collected, pos=(self.orig_x, self.orig_y))
                self.destroyed = True

    def collect(self):
        """Collects the coin"""
        if self.collect_animation >= 0:
            return None
        # Adding gem count
        if self.idx - 12 not in self.hud.collected:
            self.hud.collected.append(self.idx - 12)
        self.__class__.collected += 1
        self.collect_animation = 0

    def more_init(self):
        self.collect_animation = -1

    def bounce_on_mystery(self, from_shell=False):
        if not self.destroyed:
            self.collect()

    def init_toggle_editor(self):
        self.__class__.collected = 0


class Key(Entity):
    """Functions for item: Key"""
    save_collected = set()
    collected_keys = set()

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        info = info.split('|')
        super().__init__(win, path, entity_type, info[1], player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.r_width, self.r_height = 32 * self.scale, 32 * self.scale
        self.collect_animation = -1
        self.tile_idx = int(info[0])
        self.collected = False

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.collect_animation < 0:
            self.rect = py.Rect(self.draw_x + 22.5 * self.scale, self.draw_y + 24 * self.scale, self.r_width,
                                self.r_height)
            if py.sprite.collide_rect(self.player, self) and self.show:
                self.collect()
        else:
            self.y -= 3
            self.alpha = max(self.alpha - 15, 0)
            self.collect_animation += 1
            if self.alpha == 0:
                self.alpha = 255
                self.show = False
                self.destroyed = True
                self.collected = True
                self.__class__.collected_keys.add(self.tile_idx)

    def collect(self):
        """Collects the coin"""
        if self.collect_animation >= 0 or self.collected:
            return None
        to_collected = {28: 19, 29: 22, 30: 23, 31: 25}
        self.hud.collected.append(to_collected[self.idx])
        self.hud.collected.append(to_collected[self.idx])
        self.collect_animation = 0

    def more_init(self):
        self.collect_animation = -1
        self.collected = bool(self.tile_idx in self.__class__.save_collected)
        if self.collected:
            self.alpha = 100

    def bounce_on_mystery(self, from_shell=False):
        if not self.destroyed:
            self.collect()


class Ladder(Entity):
    """Functions for item: Ladder"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""
        if py.sprite.collide_rect(self.player, self):
            if self.idx == 33:
                if self.player.pins['mid'] < self.y + self.height:
                    self.player.can_climb = None
                    return None
            if self.x - self.tile_size / 6 < (self.player.pins['left'] + self.player.pins['right']) / 2 < \
                    self.x + self.width + self.tile_size / 6:
                self.player.can_climb = True


class Laser_Switch(Entity):
    """Functions for item: Laser Switch"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        info = info.split('-')
        super().__init__(win, path, entity_type, info[1], player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.default = info[0] == 'True'
        self.l_switched, self.collided_ = False, False
        self.targets = {}

    def tick(self):
        """What happens when the entity gets on screen"""
        collided = py.sprite.collide_rect(self.player, self)
        collided_dirs = []
        if collided:
            collided_dirs.append(self.player.dir)
        for entity in self.entity.entities.values():
            if entity == self:
                continue
            if py.sprite.collide_rect(entity, self):
                collided = True
                collided_dirs.append(not entity.dir)

        if collided and not self.collided_:
            # Direction calculation
            self.collided_ = True
            collided_dir = collided_dirs.count(True) - collided_dirs.count(False)
            if collided_dir == 0:
                self.l_switched = collided_dirs[0]
            elif collided_dir > 0:
                self.l_switched = True
            else:
                self.l_switched = False
            # Toggling
            self.toggle_lasers()
        elif not collided:
            self.collided_ = False

        img_dict = {False: 0, True: 1}
        self.image = self.images[img_dict[self.l_switched]]

    def toggle_lasers(self):
        """Toggles targeted lasers"""
        for entity in self.targets.values():
            entity.switched = self.l_switched
            entity.global__ = True

    def more_init(self):
        self.l_switched = self.default
        self.image = self.images[0 if not self.l_switched else 1]
        col_dict = {34: 'b', 36: 'g', 38: 'r', 40: 'y'}
        self.targets = {k: v for k, v in self.entity.entities.items() if v.__class__.__name__ == 'Laser_Shooter'}
        self.targets = {k: v for k, v in self.targets.items() if v.col == col_dict[self.idx]}
        self.toggle_lasers()

    def draw_edit_menu(self):
        keys = py.key.get_pressed()
        if keys[py.K_ESCAPE]:
            self.exit_editor = True
        elif self.exit_editor:
            self.editor.ent_menu = False
            self.editor.current_text = None
            self.exit_editor = False
            self.rising_editor = True

        if self.rising_editor and self.editor.ent_menu:
            self.editor.user_text = str(int(self.group) if float(self.group).is_integer() else self.group)
            self.editor.user_text_length = 3
            self.editor.current_text = f'{self.__class__.__name__}_group'
            self.rising_editor = False

        width, height = self.sc_width / 5, self.sc_height / 13
        starting_x = self.draw_x + self.width if self.draw_x < self.sc_width - width else self.draw_x - width
        bg = py.Surface((width, height))
        bg.fill('#E0e0df')
        bg.set_alpha(180)
        self.screen.blit(bg, (starting_x, self.draw_y - height))
        contents = {
            'Group': self.group,
            'Default': self.default
        }
        y = self.draw_y - height + 3
        font = py.font.Font(None, floor(self.sc_height / 15))
        mouse_pos = py.mouse.get_pos()
        pressed = py.mouse.get_pressed()[0]

        for component, user_input in contents.items():
            text = font.render(f'{component}:', True, '#000000')
            text_rect = text.get_rect(topleft=(starting_x + 2, y))
            self.screen.blit(text, text_rect)
            x_width = 5 + text_rect.width
            box = py.Rect((starting_x + 2 + x_width, y), (width - x_width - 4, text_rect.height))
            if box.collidepoint(mouse_pos):
                col = '#Eeeeed'
                if pressed:
                    self.clicked = True
                elif self.clicked:
                    if component == 'Default':
                        self.default = not self.default
                    elif component == 'Group':
                        col = '#Afafac'
                        self.editor.user_text = str(int(self.group) if float(self.group).is_integer() else self.group)
                        self.editor.user_text_length = 3
                        self.editor.current_text = f'{self.__class__.__name__}_group'
                    self.clicked = False
            else:
                col = '#ffffff'
            if self.editor.current_text == f'{self.__class__.__name__}_{component.lower()}':
                col = '#Afafac'
                isfloat = self.editor.user_text.replace('.', '', 1).isdigit()
                isdigit = self.editor.user_text.isdigit()
                if not self.editor.user_text:
                    orig_group = self.group
                    self.group = 0.0
                    self.check_group_change(orig_group)
                elif isfloat:
                    orig_group = self.group
                    self.group = float(self.editor.user_text) if not isdigit else int(self.editor.user_text)
                    self.check_group_change(orig_group)
                else:
                    self.editor.user_text = self.editor.user_text[:-1]
            py.draw.rect(self.screen, col, box)
            text = font.render(str(user_input), True, '#000000')
            text_rect = text.get_rect(topleft=(starting_x + 3 + x_width, y))
            self.screen.blit(text, text_rect)
            y += 4 + text_rect.height

    def __str__(self):
        return f"{self.default}-{self.group}"


class Ray_Gun(Power_Up):
    """Functions for item: Ray Gun"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.durability = 3
        self.ray = None

    def tick_collected(self):
        """Ray Gun when used"""
        self.x, self.y = self.player.pins['right'] - 5 if self.player.dir else self.player.pins['left'] - 13, \
            self.player.pins['mid'] - self.height - self.tile_size + 6
        if self.player.climbing:
            self.show = False
            return None
        elif not self.show:
            self.show = True

        if self.durability < 1 and self.ray is None:
            del super().power_ups_collected[0]
            self.show = False
            self.destroyed = True

        x, y = py.mouse.get_pos()
        dir_dict = {True: 1, False: -1}
        self.dir = self.player.dir
        if dir_dict[self.dir] * (x - self.draw_x + self.width) < 0:
            self.rotation = 0
        else:
            self.rotation = degrees(atan(-(y - self.draw_y - self.height / 2)/(x - self.draw_x + self.width)))

        keys = py.key.get_pressed()
        if (keys[py.K_f] or keys[py.K_r] or keys[py.K_b]) and self.ray is None:
            deg = self.rotation, self.dir
            piercing = 3 if self.idx == 43 or self.idx == 45 else 1
            gravity = 0 if self.idx == 42 or self.idx == 43 else 0.9
            self.ray = Ray_Fire(self.screen, self.entity.path, self, deg, piercing, gravity, player_cls=self.player,
                                editor_cls=self.editor, hud_cls=self.hud, entity_cls=self.entity)

            # Initializing ray object
            self.ray.x = self.x + self.width if self.dir else self.x - self.tile_size
            if self.rotation > 0 and self.dir:
                self.ray.y = self.y - self.height * 2
            elif self.rotation > 0:
                self.ray.y = self.y - self.height
            else:
                self.ray.y = self.y
            self.ray.orig_x, self.ray.orig_y = self.ray.x, self.ray.y
            self.ray.enemies = self.enemies
            self.ray.more_init()
            self.durability -= 1
        elif self.ray is not None:
            self.ray.camera_x = self.camera_x
            self.ray.camera_y = self.camera_y
            self.ray.update_draw_pos()
            self.ray.mainloop()

    def more_init(self):
        self.height, self.width = self.orig_height, self.orig_width
        self.collected = False
        self.global__, self.global_ = False, False
        self.enemies = [e for e in self.entity.entities.values() if hasattr(e, 'frame_after_death') or
                        hasattr(e, 'pins')]
        self.durability = 10
        self.rotation = 0

    def draw_other(self):
        if self.ray is not None:
            self.ray.camera_x = self.camera_x
            self.ray.camera_y = self.camera_y
            self.ray.update_draw_pos()
            self.ray.draw()


class Ray_Fire(Collidable_Entity):
    """Functions for Ray Projectiles"""

    def __init__(self, win, path, orig_gun: Ray_Gun, /, deg: tuple, piercing: int, gravity: float, *,
                 player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, [197, 748], 0, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.orig_gun = orig_gun
        self.rotation = deg[0]
        self.dir = deg[1]
        self.piercing = piercing
        self.gravity = gravity
        self.enemies = []
        self.frame_after = 0
        self.speed = 4

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.piercing < 1:
            self.image = self.images[1]
            self.frame_after += 1

            if self.frame_after > 9:
                self.show = False
                self.destroyed = True
                self.orig_gun.ray = None
                del self
            return None
        else:
            self.image = self.images[0]

        diff = 1
        if self.rotation != 0:
            self.x_vel = self.speed / sin(radians(self.rotation)) * (-1 if self.rotation < 0 else 1) * \
                (1 if self.dir else -1)
            if self.x_vel > self.speed:
                diff = self.speed / abs(self.x_vel)
                self.x_vel *= diff
            self.y_vel = -self.speed / cos(radians(self.rotation)) * (-1 if self.rotation < 0 else 1) * \
                (1 if self.dir else -1)
            self.y_vel *= diff
        else:
            self.x_vel = self.speed
            self.y_vel = 0
        # self.y_vel += self.gravity

        for entity in (e for e in self.enemies if e.state >= 0):
            if py.sprite.collide_rect(entity, self):
                entity.dir = not self.dir
                entity.bounce_on_mystery(True)
                self.hud.update_score(score=100, pos=(entity.x, entity.y))
                self.piercing -= 1

        prev_x_vel, prev_y_vel = self.x_vel, self.y_vel
        self.handle_collision()
        if self.x_vel != prev_x_vel or self.y_vel != prev_y_vel:
            self.piercing = 0

    def more_init(self):
        self.alpha = 255
        self.switched = True
        self.mystery = False
        self.state = 0
        self.global_, self.global__ = True, True


class Shield(Power_Up):
    """Functions for item: Shield"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.durability = 3
        self.init_shield = False

    def tick_collected(self):
        """Shield when collected"""
        self.x, self.y = (self.player.pins['right'] + self.player.pins['left']) / 2, \
            self.player.pins['mid'] - self.height - self.tile_size / 2
        if self.player.climbing:
            self.show = False
            return None
        elif not self.show:
            self.show = True

        if not isinstance(self.player.shielding, bool):
            if self.durability != self.player.shielding:
                self.durability = self.player.shielding
        if self.durability < 1:
            del super().power_ups_collected[0]
            self.show = False
            self.destroyed = True

        keys = py.key.get_pressed()
        if keys[py.K_f] or keys[py.K_r] or keys[py.K_b] or keys[py.K_s] or keys[py.K_DOWN]:
            self.x = self.player.pins['right'] if self.player.dir else self.player.x
            self.y = self.player.pins['mid'] - self.height / 3 - self.tile_size
            self.rect.x = self.draw_x + (6 if self.player.dir else -6)
            if self.init_shield:
                self.player.shielding = self.durability
                self.init_shield = False
            self.dir = self.player.dir
            for entity in (v for v in self.enemies if v.dir == self.dir):
                if py.sprite.collide_rect(entity, self):
                    entity.dir = not self.dir
                    entity.x_vel = 1 if self.dir else -1
                    self.player.shielding -= 1
        elif self.player.shielding:
            self.player.shielding = False
            self.init_shield = True

    def more_init(self):
        self.height, self.width = self.orig_height, self.orig_width
        self.collected = False
        self.global__, self.global_ = False, False
        self.enemies = [e for e in self.entity.entities.values() if hasattr(e, 'frame_after_death') or
                        hasattr(e, 'pins')]
        dur_dict = {46: 5, 47: 15, 48: 30}
        self.durability = dur_dict[self.idx]
        self.init_shield = True


class Spring(Entity):
    """Functions for item: Spring"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 615, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.delay = 0

    def tick(self):
        """What happens when the entity gets on screen"""
        if py.sprite.collide_mask(self.player, self):
            if self.player.y_vel > 1 and self.player.falling > 2:
                keys = py.key.get_pressed()
                if keys[py.K_SPACE]:
                    self.player.bounce = 30
                    self.delay = 100
                else:
                    self.player.bounce = 3
                    self.delay = 0
            else:
                self.delay = 0

        if self.delay > 0:
            self.delay -= 1
            self.image = self.images[1]
        else:
            self.image = self.images[0]

    def more_init(self):
        self.delay = 0
        self.image = self.images[0]


class Star(Entity):
    """Functions for item: Star"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 617, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""


class Wooden_Switch(Switch):
    """Functions for item: Wooden Switch"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 618, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.switched = 0
        self.collided_ = False
        self.image = self.images[2]

    def tick(self):
        """What happens when the entity gets on screen"""
        collided = py.sprite.collide_rect(self.player, self)
        collided_dirs = []
        if collided:
            collided_dirs.append(self.player.dir)
        for entity in self.entity.entities.values():
            if entity == self:
                continue
            if py.sprite.collide_rect(entity, self):
                collided = True
                collided_dirs.append(not entity.dir)

        if collided and not self.collided_:
            # Direction calculation
            self.collided_ = True
            collided_dir = collided_dirs.count(True) - collided_dirs.count(False)
            if collided_dir == 0:
                translate = {True: 1, False: -1}
                collided_dir = translate[collided_dirs[0]]
            elif collided_dir > 0:
                collided_dir = 1
            else:
                collided_dir = -1
            # Toggling
            self.toggle(max(min(self.switched + collided_dir, 1), -1))
        elif not collided:
            self.collided_ = False

        self.image = self.images[self.switched + 1]

    def more_init(self):
        self.switched = 0
        self.image = self.images[1]
        self.toggle(self.switched)


class Sword(Power_Up):
    """Functions for item: Sword"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.r_rotation = 0
        self.using_sword = False
        self.r_frame = 0
        self.durability = 3

    def tick_collected(self):
        """Using the sword"""
        self.x, self.y = self.player.pins['right'] - 5 if self.player.dir else self.player.pins['left'] - 17, \
            self.player.pins['mid'] - self.height - self.tile_size + 6
        if self.player.climbing:
            self.show = False
            return None
        elif not self.show:
            self.show = True

        if self.durability < 1:
            del super().power_ups_collected[0]
            self.show = False
            self.destroyed = True

        keys = py.key.get_pressed()
        if keys[py.K_f] or keys[py.K_r] or keys[py.K_b]:
            if not self.using_sword:
                self.r_rotation = 180
            self.using_sword = True
        elif self.using_sword:
            self.using_sword = False

        if self.using_sword or self.r_rotation > 0:
            direction = 1 if self.player.dir else -1
            rotation = sin(radians(self.r_rotation))
            self.rotation = -90 * rotation * direction
            self.x += rotation * self.width / 2 * direction
            self.y += rotation * self.height / 2
            self.r_frame += 1
            self.r_rotation -= 3

            for entity in (e for e in self.enemies if e.state >= 0):
                if py.sprite.collide_rect(entity, self):
                    entity.dir = not self.dir
                    entity.bounce_on_mystery(True)
                    self.hud.update_score(score=100, pos=(self.x, self.y))
                    self.durability -= 1
        elif self.r_frame != 0:
            self.rotation, self.r_rotation, self.r_frame = 0, 0, 0

    def init_tick_collected(self):
        self.height *= 1.3
        self.width *= 1.3

    def more_init(self):
        self.height, self.width = self.orig_height, self.orig_width
        self.collected = False
        self.global__, self.global_ = False, False
        self.enemies = [e for e in self.entity.entities.values() if hasattr(e, 'frame_after_death') or
                        hasattr(e, 'pins')]
        dur_dict = {55: 5, 56: 10, 57: 20}
        self.durability = dur_dict[self.idx]


class Umbrella(Power_Up):
    """Functions for item: Umbrella"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 624, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick_collected(self):
        """What happens when the entity gets on screen"""
        self.x, self.y = self.player.pins['right'] - 5 if self.player.dir else self.player.pins['left'] - 13, \
            self.player.pins['mid'] - self.height - self.tile_size + 6
        if self.player.climbing:
            self.show = False
            return None
        elif not self.show:
            self.show = True

        keys = py.key.get_pressed()
        if (keys[py.K_f] or keys[py.K_r] or keys[py.K_b]) and self.player.falling > 2 and self.player.y_vel > 0:
            self.player.holding_umbrella = True
            self.image = self.images[1]
            self.player.gravity = 0.1
        elif self.image == self.images[1]:
            self.image = self.images[0]
            self.player.gravity = self.player.orig_gravity

    def overriding_power_up(self):
        self.player.gravity = self.player.orig_gravity


class Weight(Collidable_Entity):
    """Functions for item: Weight"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.mov_dir = False
        self.player_collided = False
        self.width, self.height = self.tile_size, self.tile_size
        self.global__, self.global_ = True, True

    def tick(self):
        """What happens when the entity gets on screen"""
        self.rect.width, self.rect.height = self.width, self.height

        if py.sprite.collide_rect(self.player, self):
            self.player.collided.append(self)
            if self.player.check_move_x():
                dir_dict = {True: 1, False: -1}
                self.x_vel += dir_dict[self.player.dir] * 0.5  # Acceleration
            self.player.x -= self.x_vel
            self.player_collided = True
        else:
            self.player_collided = False

        for entity in (e for e in self.entity.entities.values() if hasattr(e, 'collided') and not e == self):
            if py.sprite.collide_rect(entity, self):
                entity.collided.append(self)

        self.y_vel += 1.5
        top_speed = 12.6
        if abs(self.x_vel) > top_speed:
            self.x_vel = -top_speed if self.x_vel < 0 else top_speed
        if not self.player_collided and self.x_vel != 0:
            self.x_vel = 0
        self.handle_collision()
        self.image = self.images[0]

    def more_init(self):
        self.player_collided = False
        self.global__, self.global_ = True, True
        self.show = True
