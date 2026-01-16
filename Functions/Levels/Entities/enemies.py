import pygame.sprite
from math import floor, sin, degrees, sqrt
from random import randint

from .entity_settings import Entity, Collidable_Entity, Movable_Tile

"""TOTAL OF 22 ENEMIES"""


class Barnacle(Entity):
    """Barnacle enemy functions (Mario Fans: This is a muncher)"""
    # NOTE: Only the player gets affected by barnacles, entities don't
    img_frame = 0

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 629, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.width, self.height = self.tile_size, self.tile_size

    def tick(self):
        """Ticks the enemy when it is alive"""
        self.rect.width, self.rect.height = self.width, self.height
        self.image = self.images[0 if round(self.__class__.img_frame * 6) % 2 < 0.5 else 1]

        if pygame.sprite.collide_rect(self.player, self):
            self.player.collided.append(self)
            if False:  # If the player has a star? Killing barnacle script
                pass
            else:
                self.player.minus_life()

    def more_init(self):
        self.__class__.img_frame = 0


class Bat(Entity):
    """Bat enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 633, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.fall_frame = -1
        self.frame_after_death = 0
        self.fly_x, self.fly_y = 0, 0

        self.initializing = True
        self.define_as_enemy()

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.y_vel += 0.4
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[4][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[4]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
            self.y += self.y_vel
        elif not self.destroyed:
            if self.fall_frame >= 0:
                self.tick_alive()
            else:
                self.detect_player()

            if pygame.sprite.collide_mask(self.player, self):
                if self.player.y_vel > 1 and self.player.falling > 2:
                    self.frame_after_death = 1
                    self.player.bounce = 4
                    self.hud.update_score()
                else:
                    self.player.minus_life()

    def detect_player(self):
        """Detects if the player is nearby"""
        detect_radius = self.tile_size * 3
        if self.x - detect_radius - self.player.width <= self.player.x <= self.x + self.width + detect_radius and \
                self.y < self.player.y < self.y + 3 * 50:
            self.fall_frame = 0

    def tick_alive(self):
        """Ticks the enemy when it is alive"""
        fall_frame = 50
        if self.fall_frame < 1:
            self.fly_x = self.x
        if self.fall_frame < fall_frame:
            self.y += 3
            self.x = self.fly_x + 3 * sin(self.frame * 79)
        elif self.fall_frame < fall_frame + 1:
            self.fly_y = self.y
        else:
            self.image = self.images[0]

        if self.image == self.images[3]:
            self.fall_frame += 1
        else:
            self.tick_fly()

    def tick_fly(self):
        """Lets the bat fly"""
        self.image = self.images[0 if round(self.frame * 24) % 2 < 1 else 2]
        dir_dict = {True: -1, False: 1}
        self.x += dir_dict[self.dir] * randint(1, 3)
        self.y = self.fly_y - self.fly_path(self.x)

    def fly_path(self, x):
        """The function for the bat's fly path"""
        x = self.fly_x - x
        # Adding a bit of variation, make it look more natural
        add_y = 5 * sin(self.frame * 28)
        # The fly path follows the quadratic function y=(1/1064)x**2
        return (1 / 1064) * x ** 2 + add_y

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False
        self.image = self.images[3]
        self.fall_frame = -1
        self.frame_after_death = 0
        self.fly_x, self.fly_y = 0, 0
        if self.initializing:
            self.orig_y -= self.tile_size / 4.3  # Line up bat against the top block
            self.initializing = False

    def init_toggle_editor(self):
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale


class Bee(Entity):
    """Bee enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 638, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.frame_after_death = 0
        self.fly_x, self.fly_y = 0, 0
        self.define_as_enemy()

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.y_vel += 0.4
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[3][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[3]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
            self.y += self.y_vel
        elif not self.destroyed:
            self.tick_alive()
            if pygame.sprite.collide_mask(self.player, self):
                if self.player.y_vel > 1 and self.player.falling > 2:
                    self.frame_after_death = 1
                    self.player.bounce = 5
                    self.hud.update_score()
                else:
                    self.player.minus_life()

    def tick_alive(self):
        """Ticks the bee when it is alive"""
        self.image = self.images[0 if round(self.frame * 27) % 2 < 1 else 2]
        self.y = self.fly_y + 6 * sin(self.frame * 24)
        self.x = self.fly_x + self.fly_path()

    def fly_path(self):
        """The fly path for bees"""
        # Using sine waves, the horizontal position will be shifting back and forth
        return_value = self.tile_size * 4 * sin(self.frame * 3)
        # Returning direction based on sine wave's slope at given point self.frame * 3
        self.dir = True if 90 < degrees(self.frame * 3) % 360 < 270 else False
        return return_value

    def more_init(self):
        """Initializes after tick"""
        self.dir = True
        self.fly_x, self.fly_y = self.x, self.y
        self.frame_after_death = 0

    def init_toggle_editor(self):
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale


class Spike(Entity):
    """Spike enemy functions"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.global_, self.global__ = True, True

    def tick(self):
        """What happens when the entity gets on screen"""
        if pygame.sprite.collide_mask(self.player, self):
            self.player.minus_life()
        self.manage_global_entities()

    def manage_global_entities(self):
        """Gives the spike the function of being a global ground"""
        # Spikes are global grounds, meaning entities on spikes will never de-spawn
        for entity in self.entity.entities.values():
            if entity == self:
                continue
            if pygame.sprite.collide_rect(entity, self):
                entity.global_ = True
            above = entity.rect.copy()
            above.y += self.tile_size
            if self.rect.colliderect(above):
                entity.global_ = True


class Fireball(Entity):
    """Functions for Fireball"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, [190, 741], info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""


class Fish(Entity):
    """Fish enemy functions"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""
        pass

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False


class Fly(Entity):
    """Fly enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 652, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.frame_after_death = 0
        self.fly_x, self.fly_y = 0, 0
        self.define_as_enemy()

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.y_vel += 0.4
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[3][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[3]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
            self.y += self.y_vel
        elif not self.destroyed:
            self.tick_alive()
            if pygame.sprite.collide_mask(self.player, self):
                if self.player.y_vel > 1 and self.player.falling > 2:
                    self.frame_after_death = 1
                    self.player.bounce = 5
                    self.hud.update_score()
                else:
                    self.player.minus_life()

    def tick_alive(self):
        """Ticks the bee when it is alive"""
        self.image = self.images[0 if round(self.frame * 15) % 2 < 1 else 2]
        self.y = self.fly_y + self.fly_path()
        self.x = self.fly_x + 3 * sin(self.frame * 24)

    def fly_path(self):
        """The fly path for bees"""
        # Using sine waves, the vertical position will be shifting back and forth
        return_value = self.tile_size * 4 * sin(self.frame * 3)
        return return_value

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False
        self.fly_x, self.fly_y = self.x, self.y
        self.frame_after_death = 0

    def init_toggle_editor(self):
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale


class Frog(Collidable_Entity):
    """Frog enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 656, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.frame_after_death = 0
        self.delaying = False
        self.hit_img, self.ded_img = self.images[2], self.images[1]

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[2][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[2]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
        elif not self.destroyed:
            self.tick_alive()

    def tick_alive(self):
        """What happens when the entity gets on screen"""
        self.y_vel += 1.3
        if self.y_vel > 24:
            self.y_vel = 24

        self.handle_collision()
        if self.falling == 0 and not self.delaying:
            self.jumping = -1 * randint(30, 60)
            self.delaying = True
        if self.falling < 2 or self.jumping > 0:
            self.jumping += 1
            if 0 <= self.jumping < 9:
                self.y_vel = -10
                if 1 < self.jumping < 4:
                    self.delaying = False

        if self.falling > 1:
            dir_dict = {True: -1, False: 1}
            self.x_vel = 3 * dir_dict[self.dir]
        else:
            self.x_vel = 0

        self.image = self.images[0 if self.falling < 1 else 3]

        if pygame.sprite.collide_mask(self.player, self):
            if self.player.y_vel > 1 and self.player.falling > 2:
                self.frame_after_death = 1
                self.player.bounce = 5
                self.hud.update_score()
            else:
                self.player.minus_life()

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False
        self.frame_after_death = 0
        self.delaying = False

    def init_toggle_editor(self):
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale


class Ghost(Entity):
    """Ghost enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 660, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.frame_after_death = 0

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.y_vel += 0.4
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[2][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[2]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
            self.y += self.y_vel
        elif not self.destroyed:
            self.tick_alive()
            if pygame.sprite.collide_mask(self.player, self):
                if False:
                    self.frame_after_death = 1
                else:
                    self.player.minus_life()

    def tick_alive(self):
        """Ticks the ghost when it is alive"""
        if self.dir == self.player.dir:
            # Stopping the ghost when the player is looking at it
            if self.player.dir is True and self.player.x < self.x:
                self.image = self.images[3]
                return None
            elif self.player.dir is False and self.player.x > self.x:
                self.image = self.images[3]
                return None
            else:
                self.image = self.images[0]
        else:
            self.image = self.images[0]

        speed = 1.3
        add_x, add_y = self.player.x - self.x, self.player.y - self.y
        hyp = sqrt(add_x ** 2 + add_y ** 2)  # Pythagoras
        times_ratio = speed / hyp

        self.dir = True if add_x < 0 else False

        self.x += add_x * times_ratio
        self.y += add_y * times_ratio + 0.5 * sin(self.frame * 4)

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False
        self.frame_after_death = 0

    def init_toggle_editor(self):
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale


class Grass_Block(Movable_Tile):
    """Grass Block enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 664, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        # Entity info: player_touch_activate: bool; continuous_warp: bool; moves_after: int_state(1, 2, 3);
        # (speed, delay, group, path)

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.touched:
            self.image = self.images[0]
            self.move()
        else:
            self.image = self.images[1]
            self.check_collisions()

    def check_finished(self):
        """Checks the continuous warp"""
        if self.reached_end:
            if self.fin and not self.at_start:
                self.x = self.orig_x
                self.y = self.orig_y
                self.update_draw_pos()
                self.init_tick()
                return None
            self.reached_end = False
        return None


class Ladybug(Entity):
    """Ladybug enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 668, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.frame_after_death = 0
        self.define_as_enemy()

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.y_vel += 0.4
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[2][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[2]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
            self.y += self.y_vel
        elif not self.destroyed:
            self.tick_alive()

    def tick_alive(self):
        """Ticks the ladybug when it is alive"""
        self.image = self.images[3 if round(self.frame * 24) % 2 < 1 else 1]
        if pygame.sprite.collide_mask(self.player, self):
            if self.player.y_vel > 1 and self.player.falling > 2:
                self.frame_after_death = 1
                self.player.bounce = 5
                self.hud.update_score()
            else:
                self.player.minus_life()

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False
        self.frame_after_death = 0

    def init_toggle_editor(self):
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale


class Laser_Shooter(Entity):
    """Laser Shooter functions"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, 0, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        info = info.split('|')
        self.width, self.height = self.tile_size, self.tile_size
        self.tile_idx = int(info[0])
        self.init = True

        dir_dict = {182: 'v', 184: '<', 186: '>', 188: '^'}
        self.shoot_dir = dir_dict[self.idx]
        self.lasers = {}
        self.col = info[1]

    def run_tick(self):
        """Both tick and off tick will run this script"""
        self.rect.width, self.rect.height = self.width, self.height

        if pygame.sprite.collide_rect(self.player, self):
            self.player.collided.append(self)

        for entity in (v for v in self.entity.entities.values() if not v == self and hasattr(v, 'collided')):
            if pygame.sprite.collide_rect(entity, self):
                entity.collided.append(self)

        for laser in self.lasers.values():
            laser.camera_x = self.camera_x
            laser.camera_y = self.camera_y
            laser.update_draw_pos()
            laser.run()

    def off_tick(self):
        self.run_tick()
        self.image = self.images[0]

        if self.init:
            for laser in self.lasers.values():
                laser.show = False
            self.init = False

    def tick(self):
        self.run_tick()
        self.image = self.images[1]

        if not self.init:
            for laser in self.lasers.values():
                laser.show = True
            self.init = True

    def more_init(self):
        self.init = not self.switched
        entity_type = {'b': 742, 'g': 745, 'r': 750, 'y': 753}
        entity_type = self.entity.entity_dict[entity_type[self.col]][1]
        self.lasers = {k: Laser(tile_idx, self, entity_type, self.entity.screen, self.entity.path,
                                player_cls=self.player, editor_cls=self.editor, hud_cls=self.hud,
                                entity_cls=self.entity) for k, tile_idx in enumerate(self.next_tile_idx())}
        for laser in self.lasers.values():
            laser.init_entity(laser.tile_idx)

    def next_tile_idx(self):
        """Generator for new tile idx until hitting a wall"""
        def get_solid(tile_index) -> bool:
            """"Gets the collision from a tile index"""
            if tile_index in self.tiles.overlap_grid:
                grid_list = self.tiles.overlap_grid
            else:
                grid_list = self.tiles.grid_list
            self.tiles.tiles[-1].idx = grid_list[tile_index]
            self.tiles.tiles[-1].update_settings()
            if self.shoot_dir == '^' and self.tiles.tiles[-1].collision == '-':
                return False
            return self.tiles.tiles[-1].solid
        tile_idx = self.tile_idx
        if self.shoot_dir == '^':
            adder = 1
        elif self.shoot_dir == 'v':
            adder = -1
        elif self.shoot_dir == '>':
            adder = self.tiles.grid_height
        else:
            adder = -self.tiles.grid_height
        while not get_solid(tile_idx):
            tile_idx += adder
            yield tile_idx

    def draw_edit_menu(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.exit_editor = True
        elif self.exit_editor:
            self.editor.ent_menu = False
            self.editor.current_text = None
            self.exit_editor = False
            self.rising_editor = True

        width, height = self.sc_width / 5, self.sc_height / 13
        starting_x = self.draw_x + self.width if self.draw_x < self.sc_width - width else self.draw_x - width
        bg = pygame.Surface((width, height))
        bg.fill('#E0e0df')
        bg.set_alpha(180)
        self.screen.blit(bg, (starting_x, self.draw_y - height))
        y = self.draw_y - height + 3
        font = pygame.font.Font(None, floor(self.sc_height / 15))
        mouse_pos = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        text = font.render('Colour:', True, '#000000')
        text_rect = text.get_rect(topleft=(starting_x + 2, y))
        self.screen.blit(text, text_rect)
        x_width = 5 + text_rect.width
        box = pygame.Rect((starting_x + 2 + x_width, y), (width - x_width - 4, text_rect.height))
        if box.collidepoint(mouse_pos):
            col = '#Eeeeed'
            if pressed:
                self.clicked = True
            elif self.clicked:
                col_options = ['b', 'g', 'r', 'y']
                self.col = col_options[col_options.index(self.col) + 1
                                       if self.col != col_options[-1] else 0]
                self.clicked = False
        else:
            col = '#ffffff'
        col_translate = {'b': 'blue', 'g': 'green', 'r': 'red', 'y': 'yellow'}
        pygame.draw.rect(self.screen, col, box)
        text = font.render(col_translate[self.col], True, '#000000')
        text_rect = text.get_rect(topleft=(starting_x + 3 + x_width, y))
        self.screen.blit(text, text_rect)

    def draw_other(self):
        for laser in self.lasers.values():
            laser.camera_x = self.camera_x
            laser.camera_y = self.camera_y
            laser.update_draw_pos()
            laser.draw()

    def __str__(self):
        return self.col


class Laser(Entity):
    """Laser enemy functions"""

    def __init__(self, tile_idx, orig_launcher: Laser_Shooter, /, entity_type, win, path, *,
                 player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, 0, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.tile_idx = tile_idx
        self.orig_launcher = orig_launcher

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.image == self.images[0] and self.orig_launcher.switched and \
                tuple(self.find_my_idx().keys())[0] != tuple(self.orig_launcher.lasers.keys())[-1]:
            self.image = self.images[1 if self.orig_launcher.shoot_dir in '<>' else 2]
            self.x, self.y = self.orig_x, self.orig_y
            for laser in (v for k, v in self.orig_launcher.lasers.items()
                          if k > tuple(self.find_my_idx().keys())[0]):
                laser.show = True
        if not self.show:
            return None
        if pygame.sprite.collide_mask(self.player, self):
            self.player.lives = 0
            self.player.frame = 0
            # self.player.minus_life()

        for _, entity in {key: value for key, value in self.entity.entities.items() if not value == self and
                          self.x - 16 < value.x < self.x + 16 and self.y - 16 < value.y < self.y + 16 and
                          (hasattr(value, 'pins') or hasattr(value, 'frame_after_death') or hasattr(value, 'mov_dir')
                          or value.__class__.__name__ == 'Coin' or value.__class__.__name__ == 'Button')}.items():
            if pygame.sprite.collide_rect(entity, self):
                if hasattr(entity, 'mov_dir'):
                    value = tuple(self.find_my_idx().keys())[0]
                    for laser in (v for k, v in self.orig_launcher.lasers.items() if k > value):
                        laser.show = False
                    self.more_init()
                elif entity.__class__.__name__ == 'Button':
                    value_dict = self.find_my_idx()
                    entity.collided_lasers[tuple(value_dict.keys())[0]] = self
                else:
                    # entity.state = -1  # For instant kill
                    entity.dir = not entity.dir
                    entity.bounce_on_mystery(True)

    def more_init(self):
        value_dict = self.find_my_idx()
        if tuple(value_dict.keys())[0] == tuple(self.orig_launcher.lasers.keys())[-1]:
            self.image = self.images[0]
        elif not self.orig_launcher.lasers[tuple(value_dict.keys())[0] + 1].show:
            self.image = self.images[0]
        else:
            self.image = self.images[1 if self.orig_launcher.shoot_dir in '<>' else 2]

        if self.image == self.images[0]:
            if self.orig_launcher.shoot_dir in '<>':
                self.x -= self.tile_size / 2 * (-1 if self.orig_launcher.shoot_dir == '<' else 1)
            else:
                self.y -= self.tile_size / 2 * (-1 if self.orig_launcher.shoot_dir == '^' else 1)

    def find_my_idx(self) -> dict:
        """Finds the laser's index in the orig launcher's dictionary"""
        return {key: value for key, value in self.orig_launcher.lasers.items() if not value != self}


class Mouse(Collidable_Entity):
    """Mouse enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 672, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.frame_after_death = 0
        self.hit_img, self.ded_img = self.images[2], self.images[1]

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[2][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[2]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
        elif not self.destroyed:
            self.tick_alive()

    def tick_alive(self):
        """Ticks the enemy when it is alive"""
        self.y_vel += 1
        dir_dict = {True: -1, False: 1}
        # Speed X
        if self.x_vel * dir_dict[self.dir] < 3.5:
            if self.x_vel * dir_dict[self.dir] < 0:
                self.x_vel += 0.35 * dir_dict[self.dir]  # Turning Deceleration
            else:
                self.x_vel += 0.1 * dir_dict[self.dir]  # Acceleration

        self.handle_collision()
        self.image = self.images[0 if round(self.frame * 4) % 2 < 0.5 else 3]

        # Blind range: 16
        if not self.player.x - 16 < self.x < self.player.x + 16:
            # Adjusting direction
            self.dir = True if self.x > self.player.x else False

        if pygame.sprite.collide_mask(self.player, self):
            if self.player.y_vel > 1 and self.player.falling > 2:
                self.frame_after_death = 1
                self.player.bounce = 5
                self.hud.update_score()
            else:
                self.player.minus_life()

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False
        self.frame_after_death = 0

    def init_toggle_editor(self):
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale


class Piranha(Entity):
    """Piranha enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 676, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.jump_height, self.orig_jump_height = 0, 0
        self.jump_frame = 0
        self.frame_after_death = 0
        self.define_as_enemy()
        self.delay, self.frame_after_delay = 0, 0

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.y_vel += 0.4
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[3][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[3]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
            self.y += self.y_vel
        elif not self.destroyed:
            self.tick_alive()
            if pygame.sprite.collide_mask(self.player, self):
                if self.player.y_vel > 1 and self.player.falling > 2:
                    self.frame_after_death = 1
                    self.player.bounce = 5
                    self.hud.update_score()
                else:
                    self.player.minus_life()

    def tick_alive(self):
        if self.jump_frame < 0:  # Initialize values
            self.set_jump_height()
            self.jump_frame = 0
            self.delay = randint(5, 40) * 0.1
            self.frame_after_delay = 0
        elif self.jump_frame < 1:  # Delay
            self.frame_after_delay += 1 / 60
            if self.frame_after_delay > self.delay:
                self.jump_frame = 1
        if self.jump_frame >= 1:  # Fly fish!
            self.y = self.fly_path()
            self.jump_frame += 4
            if self.y > self.sc_height + self.camera_y - 0.1:
                self.jump_frame = -1
                self.y = self.sc_height + self.camera_y - 0.1

    def fly_path(self) -> int | float:
        """The fly path for piranha enemy"""
        x = self.jump_height + self.jump_frame
        self.image = self.images[2 if x > 0 else 0]
        return (1 / abs(self.jump_height)) * x ** 2 + self.orig_jump_height

    def more_init(self):
        """Initializes after tick"""
        self.dir = True
        self.jump_height, self.orig_jump_height = int(self.y), int(self.y)
        self.frame_after_death = 0
        self.jump_frame = 0
        self.delay, self.frame_after_delay = 0, 0
        if 0 < self.x - self.camera_x < self.sc_width:
            self.set_jump_height()

    def set_jump_height(self):
        """Setting jump height of piranha"""
        self.y = self.sc_height + self.camera_y - 0.1
        self.jump_height = min(self.orig_jump_height - self.y, 0.01)

    def init_toggle_editor(self):
        self.x, self.y = self.orig_x, self.orig_y
        self.jump_frame = 0
        self.delay, self.frame_after_delay = 0, 0
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale

    def despawn(self):
        self.x, self.y = self.orig_x, self.orig_y
        self.jump_frame = 0
        self.delay, self.frame_after_delay = 0, 0


class Slime_Block(Movable_Tile):
    """Slime Block enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 680, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        # Entity info: player_touch_activate: bool; stationary_finish: bool; moves_after: int(1, 2, 3);
        # (speed, delay, group, path)

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.touched:
            self.image = self.images[0]
            self.move()
        else:
            self.image = self.images[1]
            self.check_collisions()

    def check_finished(self):
        """Checks the continuous warp"""
        if self.reached_end:
            if self.fin and not self.at_start:
                return ''
            self.reached_end = False
        return None


class Slime(Collidable_Entity):
    """Slime enemy functions"""

    # Congrats for being the first enemy coded!

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.ded_img, self.hit_img = self.images[1], self.images[2]
        self.frame_after_death = 0

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_after_death >= 1:
            self.frame_after_death += 0.01
            orig_height = self.height
            self.height = self.images[3][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[3]
            if self.frame_after_death > 1.3:
                self.frame_after_death = 0
                self.show = False
                self.destroyed = True
                self.height = self.images[0][0].get_height() * self.scale
                self.image = self.images[0]
        elif not self.destroyed:
            self.tick_alive()

    def tick_alive(self):
        """Ticks the enemy when it is alive"""
        self.y_vel += 1
        if abs(self.x_vel) < 1:
            dir_dict = {True: -1, False: 1}
            self.x_vel += 0.1 * dir_dict[self.dir]

        self.handle_collision()
        self.image = self.images[0 if round(self.frame * 4) % 2 < 0.5 else 4]

        if pygame.sprite.collide_mask(self.player, self):
            if self.player.y_vel > 1 and self.player.falling > 2:
                self.frame_after_death = 1
                self.player.bounce = 5
                self.hud.update_score()
            else:
                self.player.minus_life()

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False
        self.frame_after_death = 0

    def init_toggle_editor(self):
        self.frame_after_death = 0
        self.height = self.images[0][0].get_height() * self.scale


class Snail(Collidable_Entity):
    """Snail enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 698, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)
        self.state = 1  # 0: Shell, 1: Snail
        self.kicked = False
        self.delay = 0
        self.ded_img, self.hit_img = self.images[0], self.images[1]
        self.frame_change = 0

    def tick(self):
        """What happens when the entity gets on screen"""
        if self.frame_change >= 1:
            self.frame_change += 0.01
            orig_height = self.height
            self.height = self.images[1][0].get_height() * self.scale
            self.y = self.y + (orig_height - self.height)
            self.image = self.images[1]
            if self.frame_change > 1.3:
                self.frame_change = 0
                i = 1 if self.state == 0 else 0
                self.state = i
                self.delay = 0
                self.height = self.images[abs(2 * i - 2)][0].get_height() * self.scale
                self.image = self.images[abs(2 * i - 2)]
        elif not self.destroyed:
            if self.state == 1:
                self.tick_snail()
            else:
                self.tick_shell()

    def tick_snail(self):
        """Ticks the snail"""
        self.y_vel += 1
        if abs(self.x_vel) < 0.7:
            dir_dict = {True: -1, False: 1}
            self.x_vel += 0.1 * dir_dict[self.dir]

        self.handle_collision()
        self.image = self.images[0 if round(self.frame * 4) % 2 < 0.5 else 3]

        if pygame.sprite.collide_mask(self.player, self):
            if self.player.y_vel > 1 and self.player.falling > 2:
                self.frame_change = 1
                self.player.bounce = 5
                self.hud.update_score()
            else:
                self.player.minus_life()

    def tick_shell(self):
        """Ticks the shell"""
        self.y_vel += 1.5
        if self.kicked:
            dir_dict = {True: -1, False: 1}
            self.x_vel = dir_dict[self.dir] * 8
        else:
            self.x_vel = 0

        self.handle_collision()
        self.image = self.images[2]

        if pygame.sprite.collide_mask(self.player, self):
            if self.kicked:
                if self.player.y_vel > 1 and self.player.falling > 2:
                    self.kicked = False
                    self.delay = 0
                    self.player.bounce = 5
                    self.hud.update_score()
                else:
                    self.player.minus_life()
            else:
                self.kicked = True
                self.dir = self.x < self.player.x
                if self.player.y_vel > 1 and self.player.falling > 2:
                    self.player.bounce = 5
                    self.hud.update_score()

        if self.kicked:
            # Loops through entities near the shell
            self.global_, self.global__ = True, True
            for _, entity in {key: value for key, value in self.entity.entities.items() if value != self and
                              self.x - 16 < value.x < self.x + 16 and self.y - 16 < value.y < self.y + 16 and
                              (hasattr(value, 'pins') or hasattr(value, 'frame_after_death') or
                               value.__class__.__name__ == 'Coin')}.items():
                if entity.__class__.__name__ == 'Weight':
                    continue
                # Killing entities
                if pygame.sprite.collide_mask(entity, self):
                    entity.dir = not self.dir
                    entity.bounce_on_mystery(True)
                    self.hud.update_score(score=100)
        else:
            if self.global__:
                self.global_, self.global__ = False, False
            self.delay += 1
            base_delay = 240
            if self.delay > base_delay:
                # Flickering animation
                self.dir = not self.dir
                self.alpha = 255 if self.alpha == 136 else 136
            if self.delay > base_delay + 45:
                self.state = 1
                self.dir = True if self.x > self.player.x else False
                self.alpha = 255

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False
        self.frame_change = 0
        self.state = 1
        self.kicked = False
        self.delay = 0

    def init_toggle_editor(self):
        self.frame_change = 0
        self.height = self.images[0][0].get_height() * self.scale


class Snake(Collidable_Entity):
    """Snake enemy functions"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""
        pass

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False


class Snake_Up(Entity):
    """Snake Up (Geyser) enemy functions"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""
        pass

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False


class Spider(Collidable_Entity):
    """Spider enemy functions"""

    def __init__(self, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, 714, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""
        pass

    def more_init(self):
        """Initializes after tick"""
        self.dir = True if self.x > self.player.x else False


class Spinner(Entity):
    """Spinner enemy functions"""

    def __init__(self, entity_type, /, win, path, info, *, player_cls, editor_cls, hud_cls, entity_cls):
        super().__init__(win, path, entity_type, info, player_cls=player_cls, editor_cls=editor_cls, hud_cls=hud_cls,
                         entity_cls=entity_cls)

    def tick(self):
        """What happens when the entity gets on screen"""
        self.image = self.images[0 if round(self.frame * 3) % 2 < 0.5 else 3]
        if pygame.sprite.collide_mask(self.player, self):
            self.player.minus_life()
