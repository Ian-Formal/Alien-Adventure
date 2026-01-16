import pygame as py
from os.path import join
from math import floor

try:
    from .Player_Animations.player_animations import Pics_Player
except ImportError:
    from Player_Animations.player_animations import Pics_Player


class Player(py.sprite.Sprite):
    """Player basic functions"""

    def __init__(self, win: py.display, camera_x, camera_y, player_number, path=''):
        super().__init__()
        self.win = win
        self.sc_width, self.sc_height = self.win.get_size()
        self.camera_x, self.camera_y = camera_x, camera_y

        # Animations
        self.images, self.image = None, None
        self.path = join(path, "Player_Animations")
        self.player = player_number
        self.dir = True
        self.frame = 0
        self.alpha = 255

        # Spawn position and positions
        self.spawn_idx = 0
        self.x = 48
        self.y = self.sc_height - 128
        self.draw_x = self.x
        self.draw_y = self.y
        self.x_vel = 0
        self.y_vel = 0

    def reset_pos(self, grid_height, tile_size):
        """Resets player position"""
        # Player Position
        if self.spawn_idx > 0:
            self.x = floor((self.spawn_idx - 1) / grid_height)
            self.y = (self.spawn_idx - 1) % grid_height - 1
        else:
            self.x = 3
            self.y = 3
        self.x *= tile_size
        self.y = self.sc_height - self.y * tile_size - 100 + tile_size // 2  # Player height = 100
        self.draw_x = self.x
        self.draw_y = self.y
        self.x_vel = 0
        self.y_vel = 0

    def update_images(self):
        """Updates player images"""
        self.images = Pics_Player(self.path, self.player)
        self.image = self.images.frame('stand', 0)

    def __setattr__(self, key, value):
        """Sets the values and updates the images"""
        self.__dict__[key] = value
        if key == 'player':
            self.update_images()


class P_Player(Player):
    """Player functions in planet map"""

    def __init__(self, win: py.display, camera_x, camera_y, player_number, editor_cls, path=''):
        super().__init__(win, camera_x, camera_y, player_number, path)
        self.editor = editor_cls
        self.action = 'stand'
        self.level = ''
        self.tile_size = self.editor.tiles.tile_size

        self.scale = self.editor.tiles.tile_size / 90
        self.width = 70 * self.scale
        self.height = 100 * self.scale

        self.speed = 3
        self.frame = 0
        self.prev_x = 0
        self.tile_idx = 0

    def find_spawn_idx(self, player_level_spawn):
        """Finding the spawn index of the player"""
        self.spawn_idx = [key for key, value in self.editor.levels.items() if value.id == player_level_spawn]
        self.spawn_idx = self.spawn_idx[0] if self.spawn_idx else tuple(self.editor.levels.keys())[0]
        self.reset_pos(self.editor.grid_height, self.tile_size)
        self.x += 3
        self.tile_idx = self.spawn_idx
        self.action = 'level'

    def handle_keys(self):
        """Handle user inputs on player"""
        if self.action != 'walk' and self.action != 'n_walk':
            keys = py.key.get_pressed()
            keys_dict = {True: 1, False: 0}
            right = keys_dict[keys[py.K_RIGHT] or keys[py.K_d]]
            left = keys_dict[keys[py.K_LEFT] or keys[py.K_a]]
            up = keys_dict[keys[py.K_UP] or keys[py.K_w]]
            down = keys_dict[keys[py.K_DOWN] or keys[py.K_s]]
            self.x_vel = right - left
            if self.x_vel == 0:
                self.y_vel = down - up
            if self.x_vel != 0 or self.y_vel != 0:
                self.action = 'n_walk'
                self.prev_x = self.x_vel

    def move_to_next_path(self):
        """Moves the player to the next node"""
        x, y = self.x + self.width / 2, self.y + self.height
        tile = self.editor.get_tile_at_pos(x, y)[1]
        node = tile.node
        x_mid = self.tile_size / 2 - 2 < x % self.tile_size < self.tile_size / 2 + 2
        y_mid = self.tile_size / 2 - 2 < y % self.tile_size < self.tile_size / 2 + 2
        touching_level = x_mid and y_mid and tile.tile_idx in self.editor.levels
        if len(node) > 2 or touching_level:
            if x_mid and y_mid and self.action == 'walk':
                self.x_vel, self.y_vel = 0, 0
                self.action = 'stand' if not touching_level else 'level'
                self.tile_idx = tile.tile_idx
            if self.action == 'n_walk':
                if '<' not in node and self.x_vel < 0:
                    self.action = 'stand' if not touching_level else 'level'
                    self.x_vel = 0
                if self.editor.get_tile_at_pos(x - self.tile_size, y)[1].tile_idx not in self.editor.progress.paths \
                        and self.x_vel < 0:
                    self.action = 'stand' if not touching_level else 'level'
                    self.x_vel = 0

                if '>' not in node and self.x_vel > 0:
                    self.action = 'stand' if not touching_level else 'level'
                    self.x_vel = 0
                if self.editor.get_tile_at_pos(x + self.tile_size, y)[1].tile_idx not in self.editor.progress.paths \
                        and self.x_vel > 0:
                    self.action = 'stand' if not touching_level else 'level'
                    self.x_vel = 0

                if '^' not in node and self.y_vel < 0:
                    self.action = 'stand' if not touching_level else 'level'
                    self.y_vel = 0
                if self.editor.get_tile_at_pos(x, y - self.tile_size)[1].tile_idx not in self.editor.progress.paths \
                        and self.y_vel < 0:
                    self.action = 'stand' if not touching_level else 'level'
                    self.y_vel = 0

                if 'v' not in node and self.y_vel > 0:
                    self.action = 'stand' if not touching_level else 'level'
                    self.y_vel = 0
                if self.editor.get_tile_at_pos(x, y + self.tile_size)[1].tile_idx not in self.editor.progress.paths \
                        and self.y_vel > 0:
                    self.action = 'stand' if not touching_level else 'level'
                    self.y_vel = 0
        elif len(node) == 2:
            if self.y_vel != 0 or self.x_vel != 0:
                self.action = 'walk'
            if '<' in node and '>' in node:
                self.y_vel = 0
            elif '^' in node and 'v' in node:
                self.x_vel = 0
            elif self.x_vel != 0:
                if ('>' in node and self.x_vel < 0) or ('<' in node and self.x_vel > 0):
                    if x_mid:
                        self.x_vel = 0
                        self.y_vel = -1 if '^' in node else 1
            else:
                if ('^' in node and self.y_vel > 0) or ('v' in node and self.y_vel < 0):
                    if y_mid:
                        self.y_vel = 0
                        self.x_vel = -1 if '<' in node else 1
                        self.prev_x = self.x_vel

    def move(self, controlling=True):
        """Moves the player"""
        if controlling:
            self.handle_keys()
        self.move_to_next_path()

    def animate(self):
        """Animates the player"""
        if 'walk' in self.action:
            self.image = self.images.frame('walk', floor(self.frame * self.speed) % self.images.walk, self.prev_x > 0)
        else:
            self.image = self.images.frame('stand', 0, self.prev_x > 0)

    def draw(self):
        """Draws the player onto the screen"""
        self.frame += 0.1
        self.animate()
        self.x += self.x_vel * self.speed
        self.y += self.y_vel * self.speed
        self.draw_x = self.x - self.camera_x
        self.draw_y = self.y - self.camera_y - self.tile_size * 0.8
        self.win.blit(py.transform.scale(self.image[0], (self.width, self.height)), (self.draw_x, self.draw_y))


class L_Player(Player):
    """Player functions in level"""

    def __init__(self, win: py.display, camera_x, camera_y, player_number, get_tile_at_func, smoke_func, path=""):
        """Initializes player settings"""
        super().__init__(win, camera_x, camera_y, player_number, path)
        # System Settings
        self.tile_size = 32
        self.scale = self.tile_size / 70
        self.width, self.height = 70, 100

        self.checkpoint = 628
        self.cp_in_level = None

        # Jumping Mechanics
        self.falling = 69  # Nice
        self.jumping = 69
        self.bounce = 0
        self.bump = False
        self.carry_p = 0, True, 'x'  # p for momentum

        # Collision
        self.pins = {}
        self.update_pins()
        self.get_tile = get_tile_at_func
        self.make_smoke = smoke_func
        self.rect = self.image[0].get_rect()
        self.mask = py.mask.from_surface(self.image[0])
        self.on_ice = False
        self.collided = []

        # Other
        self.lives = 6
        self.hurt = False
        self.invis = 0
        self.touching = False
        self.shielding = False
        self.orig_gravity = 0.9  # Acceleration due to gravity: 0.9
        self.gravity = self.orig_gravity
        self.camera_loc = ''

        # Climbing
        self.can_climb, self.climbing = False, False

        # Swim
        self.swimming = False
        self.holding_umbrella = False

    def reset(self, grid_height):
        """Reset player settings"""
        self.reset_pos(grid_height, self.tile_size)
        # Jumping Mechanics
        self.falling = 69
        self.jumping = 69
        self.bounce = 0
        self.bump = False
        self.alpha = 255

        self.dir = True
        self.hurt = False
        self.invis = 0
        self.touching = False
        self.on_ice = False
        self.can_climb, self.climbing = False, False
        self.shielding = False
        self.swimming = False
        self.gravity = self.orig_gravity
        self.holding_umbrella = False

    def minus_life(self):
        """Takes away lives from the player"""
        if self.shielding and not self.invis > 0:
            self.shielding -= 1
        if not self.invis > 0 and self.shielding is False:
            self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.frame = 0
        elif self.invis < 1:
            self.hurt = True
            self.invis = 150

    def invis_frame(self):
        """Invisibility frames function"""
        if self.invis > 0:
            self.alpha = 51 * (self.invis % 5 + 1)
            self.invis -= 1
            if self.invis < 100:
                self.hurt = False
        else:
            self.alpha = 255

    def normal_move(self):
        """Moves player according to user inputs - in normal gravity and playing mode"""
        keys = py.key.get_pressed()
        keys_dict = {True: 1, False: 0}
        right = keys_dict[keys[py.K_RIGHT] or keys[py.K_d]]
        left = keys_dict[keys[py.K_LEFT] or keys[py.K_a]]
        if self.swimming:
            self.gravity = 0.1
        elif not self.holding_umbrella:
            self.gravity = self.orig_gravity
        self.move_left_right(right - left, keys[py.K_LSHIFT] or keys[py.K_LCTRL] or keys[py.K_t] or keys[py.K_g])
        self.jump(keys_dict[keys[py.K_SPACE]])
        if self.can_climb or self.can_climb is None:
            up = keys_dict[keys[py.K_UP] or keys[py.K_w]]
            down = keys_dict[keys[py.K_DOWN] or keys[py.K_s]]
            self.climb(up - down)
        elif self.climbing:
            self.climbing = False
        if self.holding_umbrella:
            self.holding_umbrella = False

        if abs(self.y_vel) > self.tile_size - 1:
            self.y_vel = (self.tile_size - 1) * (-1 if self.y_vel < 0 else 1)

    def set_idle(self):
        """Sets the player to the idle position"""
        self.move_left_right(0, False)
        self.jump(0)

    def edit_move(self):
        """Moves player according to user inputs - while editing"""
        keys = py.key.get_pressed()
        keys_dict = {True: 1, False: 0}
        right = keys_dict[keys[py.K_RIGHT] or keys[py.K_d]]
        left = keys_dict[keys[py.K_LEFT] or keys[py.K_a]]
        up = keys_dict[keys[py.K_UP] or keys[py.K_w]]
        down = keys_dict[keys[py.K_DOWN] or keys[py.K_s]]
        if keys[py.K_TAB]:
            # Moving by tile
            self.x -= self.x % self.tile_size
            self.y -= self.y % self.tile_size
            self.x_vel = self.tile_size * (right - left)
            self.y_vel = -self.tile_size * (up - down)
        else:
            self.x_vel += 6 * (right - left)
            self.y_vel += -6 * (up - down)
            self.x_vel *= 0.8
            self.y_vel *= 0.8
        self.x += self.x_vel
        self.y += self.y_vel

        self.draw_x = self.x - self.camera_x
        self.draw_y = self.y - self.camera_y

        # Limit Player Bounds
        if not 0 <= self.draw_x <= self.sc_width - self.width:
            if self.draw_x < 0:
                move_x = self.draw_x
            else:
                move_x = self.draw_x - self.sc_width + self.width
            self.x -= move_x
            self.draw_x -= move_x

        if not 0 <= self.draw_y <= self.sc_height:
            if self.draw_y < 0:
                move_y = self.draw_y
            else:
                move_y = self.draw_y - self.sc_height
            self.y -= move_y
            self.draw_y -= move_y

    def move_left_right(self, key_press: int, running):
        """Control movements for player left and right"""
        if not self.swimming:
            top_speed = {True: 7, False: 3}  # Running vs walking
        else:
            top_speed = {True: 4, False: 2}
        if self.shielding:
            top_speed = {True: 1, False: 1}
        keys_dict = {1: True, -1: False}
        # Deceleration: 0.1 -> Ice Deceleration, 0.45 -> Normal Deceleration and Swimming deceleration
        deceleration = (0.1 if self.on_ice else 0.45)
        if key_press == 0:
            if self.falling < 2:
                if self.climbing:
                    self.x_vel = 0
                elif self.x_vel > deceleration:
                    self.x_vel -= deceleration
                elif self.x_vel < -deceleration:
                    self.x_vel += deceleration
                else:
                    self.x_vel = 0
                    self.frame = 0
        elif not self.climbing:
            self.dir = keys_dict[key_press]
            if key_press * self.x_vel < top_speed[running]:  # Max speed
                if key_press * self.x_vel < 0:
                    if self.falling < 2:
                        if self.swimming:
                            turn_decel = 0.2  # Deceleration when turning in water
                        elif self.on_ice:
                            turn_decel = 0.3  # Deceleration when turning on ice
                        else:
                            turn_decel = 0.7  # Normal deceleration when turning
                        self.x_vel += key_press * turn_decel
                        # Smoke Particle
                        self.make_smoke(self.x + self.width * (0 if self.x_vel > 0 else 1 / 2),
                                        self.y + (-10.9375 + self.height) * self.scale - self.tile_size,
                                        10.9375 * self.scale)
                    else:
                        self.x_vel += key_press * 0.7  # Deceleration when turning in the air
                else:
                    if self.swimming:
                        acceleration = 0.2  # Swimming Acceleration
                    elif self.on_ice:
                        acceleration = 0.1  # Ice Acceleration
                    else:
                        acceleration = 0.3  # Normal Acceleration
                    self.x_vel += key_press * acceleration
        else:
            self.x_vel = key_press * 3  # Horizontal speed when climbing: 3

        # Speed limit
        if abs(self.x_vel) > self.tile_size - 1:
            self.x_vel = (self.tile_size - 1) * (-1 if self.x_vel < 0 else 1)

        # Animations
        if not self.climbing:
            temp = abs(self.x_vel) / 19
            if temp < 0.2:
                temp = 0.2
            self.frame += temp

    def jump(self, key_press: int):
        """Handling the jump key"""
        if self.swimming:
            jump_speed = -3  # Player jump speed
            jump_lim = 4  # How long can you hold the jump button for
            can_jump = True
        else:
            jump_speed = -9  # Player jump speed
            jump_lim = 15  # How long can you hold the jump button for
            can_jump = self.falling < 2

        # Terminal Velocity
        if not self.climbing:
            self.y_vel += self.gravity
        if self.y_vel > round(self.gravity * 24.44444444):  # Max gravitational velocity / Terminal Velocity
            self.y_vel = round(self.gravity * 24.4444444444)

        # Jumping
        if key_press > 0:
            if can_jump or self.jumping > 0:  # Coyote Jump
                self.jumping += 1
                if self.jumping < jump_lim:
                    self.y_vel = jump_speed
                    if self.can_climb:
                        self.can_climb = False
        else:
            self.jumping = 0

    def climb(self, key_press: int):
        if key_press == 1 and not self.climbing:
            self.climbing = True
        if not self.climbing:
            return None
        self.dir = True
        self.falling = 0
        if key_press == 1 and self.can_climb is None:
            self.y_vel = 0
        elif key_press == 0:
            self.y_vel = 0
        else:
            self.y_vel = -key_press * 3  # Vertical speed when climbing: 3
        if self.x_vel == 0 and self.y_vel == 0:
            self.frame = 0

        # Animations
        temp = (abs(self.x_vel) + abs(self.y_vel)) / 5
        if temp < 0.2:
            temp = 0.2
        self.frame += temp

    def draw(self):
        """Draws the player onto the screen"""
        # py.draw.rect(self.win, '#000000', self.rect)
        self.image[0].set_alpha(self.alpha)
        self.win.blit(py.transform.scale(self.image[0], (self.scale * 70, self.scale * 100)),
                      (self.draw_x + (self.width - self.image[1][0]) * self.scale,
                       self.draw_y - (self.height - self.image[1][1]) * self.scale - self.tile_size))

    def animate(self):
        """Animations"""
        if self.climbing:
            self.image = self.images.frame('climb', floor(self.frame) % self.images.climb, True)
        elif self.swimming:
            self.image = self.images.frame('swim', floor(self.frame) % self.images.swim, self.dir)
        elif self.falling > 1:
            self.image = self.images.frame('jump', 0, self.dir)
        elif self.frame > 0.21:
            self.image = self.images.frame('walk', floor(self.frame) % self.images.walk, self.dir)
        elif self.hurt:
            self.image = self.images.frame('hurt', 0, not self.dir)
        else:
            self.image = self.images.frame('stand', 0, self.dir)

        # Updating player-entity collision detections
        self.rect = py.transform.scale(self.image[0], (self.scale * 70, self.scale * 100))\
            .get_rect(topleft=(self.draw_x, self.draw_y - (-20 + self.height) * self.scale))
        self.mask = py.mask.from_surface(py.transform.scale(self.image[0], (self.scale * 70, self.scale * 100)))

    """Handling Collision"""

    def update_draw_pos(self):
        """Updates drawing position"""
        self.draw_x = self.x - self.camera_x
        self.draw_y = self.y - self.camera_y

    def update_pins(self):
        """Update collision pins"""
        self.pins = {'top': self.y, 'bottom': self.y + (-10.9375 + self.height) * self.scale,
                     'mid': (self.y * 2 + (-10.9375 + self.height) * self.scale) / 2,
                     'left': self.x + 13.125 * self.scale, 'right': self.x + (- 6.5625 + self.width) * self.scale,
                     'bottom_': self.y + self.height * self.scale, 'bottom+': self.y + (-21 + self.height) * self.scale}

    def move_x(self, x=None):
        """Moves player along the x-axis"""
        if self.collided:
            if self.collided[0].x_vel != 0:
                self.carry_p = max(self.carry_p[0], abs(self.collided[0].x_vel)), self.collided[0].x_vel < 0, 'x'
            elif self.collided[0].y_vel != 0:
                self.carry_p = max(self.carry_p[0], abs(self.collided[0].y_vel)), self.collided[0].y_vel < 0, 'y'
        elif self.carry_p[0] > 0:
            if self.carry_p[0] <= 0.1:
                pass
            else:
                if self.carry_p[2] == 'x':
                    self.x_vel += (1/(-self.carry_p[0]/3 - 1) + 1) * (self.carry_p[0]) * (-1 if self.carry_p[1] else 1)
                elif self.carry_p[2] == 'y':
                    self.y_vel += (1/(-self.carry_p[0]/3 - 1) + 1) * (self.carry_p[0]) * (-1 if self.carry_p[1] else 1)
            self.carry_p = 0, True, 'x'
        if x is None:
            self.x += self.x_vel
        else:
            self.x += x
        y = self.y
        if not self.collided:
            check_x = False
        else:
            self.collided = sorted(self.collided, key=lambda entity: entity.y)
            check_x = self.check_move_x()
        collided = self.handle_collision_in_dir(0, 1, True)
        if self.y < y - abs(self.x_vel) - 4 or check_x or (collided and self.collided):
            self.y = y
            orig_x_vel = self.x_vel
            if collided and self.collided:
                self.x_vel += self.collided[0].x_vel
            if self.handle_collision_in_dir(self.x_vel, 0):
                self.x_vel = 0
            else:
                self.x_vel = orig_x_vel
            # if not (collided and self.collided):
            #     self.collided = []
        elif self.y < y:
            # walking up a slope
            self.x_vel *= 0.8

    def move_y(self, y=None):
        """Moves player along the y-axis"""
        if y is None:
            self.y += self.y_vel
        else:
            self.y += y
        self.falling += 1
        if self.handle_collision_in_dir(0, self.y_vel):
            self.check_y()

    def check_move_x(self) -> bool:
        """Checks if the player is on the side of a movable tile"""
        if not self.collided:
            return False

        self.x += self.collided[0].x_vel
        if self.carry_p[0] < 0.1:
            pass
        elif self.carry_p[2] == 'x':
            if abs(self.collided[0].x_vel) < self.carry_p[0]:
                self.x_vel += (1/(-self.carry_p[0]/3 - 1) + 1) * (self.carry_p[0]) * (-1 if self.carry_p[1] else 1)
                self.carry_p = 0, True, 'x'
        elif self.carry_p[2] == 'y':
            if abs(self.collided[0].y_vel) < self.carry_p[0]:
                self.y_vel += (1/(-self.carry_p[0]/3 - 1) + 1) * (self.carry_p[0]) * (-1 if self.carry_p[1] else 1)
                self.carry_p = 0, True, 'x'
        if len(self.collided) > 1:
            diff_y = round(self.collided[0].y) == round(self.collided[1].y)
            if diff_y:
                return False

        check_x = (True if self.pins['right'] < self.collided[0].x + self.x_vel + 0.000001 else False) or \
                  (True if self.pins['left'] > self.collided[0].x + self.collided[0].width + self.x_vel - 0.000001
                   else False)
        check_x = check_x and not (self.falling < 2 and self.pins['bottom'] >= self.collided[0].y > self.pins['top'])

        if self.collided[0] == 'Grass_Block':
            if not check_x and not self.pins['bottom'] >= self.collided[0].y > self.pins['top']:
                return True

        # if check_x:
        #     print(self.collided[0].x)
        return check_x

    def check_y(self):
        """Moves variables around when collided with y"""
        if self.y_vel > 0:
            self.falling = 0
        else:
            self.jumping = 69
            self.bump = True
        # Smoke Particles when landing
        if self.y_vel > 20:
            for i in range(0, round(self.width * self.scale), 5):
                self.make_smoke(self.x + i, self.y + (-10.9375 + self.height) * self.scale -
                                self.tile_size, 10.9375 * self.scale, False)
        self.y_vel = 0

    """COLLISION"""
    def handle_collision(self):
        """Handles collisions with tiles"""
        self.move_x()
        self.move_y()
        self.collided = []
        self.update_draw_pos()

    def handle_collision_in_dir(self, dx, dy, test_x=False):
        """Handles collision in a direction"""
        self.swimming = False
        self.update_pins()
        top, mid, bottom = self.pins['top'], self.pins['mid'], self.pins['bottom']
        left, right = self.pins['left'], self.pins['right']
        # The order of how the collision is checked in pins is important. If middle pins are not tested first,
        # there is a bug of the player getting stuck in between blocks when jumping
        # Running this script twice will prevent slope jank when landing on a small corner of the slope
        collided = False
        for _ in range(2):
            collided = collided or self.handle_collision_at_point(left, mid, dx, dy) or \
                self.handle_collision_at_point(right, mid, dx, dy) or \
                self.handle_collision_at_point(left, bottom, dx, dy, True) or \
                self.handle_collision_at_point(right, bottom, dx, dy, True) or \
                self.handle_collision_at_point(left, top, dx, dy) or \
                self.handle_collision_at_point(right, top, dx, dy)
            if not collided:
                break

        if self.collided and not test_x:
            collided = collided or self.handle_moving_collision(dx, dy)
        return collided

    def handle_moving_collision(self, fix_dx, fix_dy):
        """Handles collisions with movable tiles"""
        grass_block = self.collided[0].__class__.__name__ == 'Grass_Block'
        dx, dy = 0, 0
        if fix_dy > 0:
            dy = -0.1
        elif fix_dy < 0 and not grass_block:
            dy = 0.1
        if fix_dx < 0 and not grass_block:
            dx = 0.1
        elif fix_dx > 0 and not grass_block:
            dx = -0.1
        looped = 0
        while py.sprite.collide_rect(self, self.collided[0]):
            self.x += dx
            self.y += dy
            self.update_draw_pos()
            self.rect = py.transform.scale(self.image[0], (self.scale * 70, self.scale * 100)) \
                .get_rect(topleft=(self.draw_x, self.draw_y - (-20 + self.height) * self.scale))
            self.mask = py.mask.from_surface(py.transform.scale(self.image[0], (self.scale * 70, self.scale * 100)))
            if looped > 1000 or (dx == 0 and dy == 0):
                break
            looped += 1
        if looped > 550:
            self.x -= dx * looped
            self.y -= dy * looped
            if not dy * looped > 500:
                self.lives = 1
                self.minus_life()
        if fix_dy > 0:
            self.y = round(self.y)
            self.y += self.collided[0].y_vel + 0.1
        if looped < 2:
            return False
        return True

    def handle_collision_at_point(self, x, y, fix_dx, fix_dy, feet=False):
        """Handles collision at points of the player"""
        if self.collided and feet:
            y -= 2  # Allowing same block level to walk up to the solid block from a moving block
        mod_x = x % self.tile_size
        mod_y = y % self.tile_size
        tile = self.get_tile(x, y)[1]
        return self.move_outside_collision(mod_x, mod_y, fix_dx, fix_dy, feet, tile)

    def move_outside_collision(self, mod_x, mod_y, fix_dx, fix_dy, feet, tile):
        """Moves the player outside of collision"""
        dx, dy = 0, 0
        if not tile.solid:
            return False
        if tile.alpha == 0 and not fix_dy < 0:
            return False
        if tile.category == 'Tundra':
            self.on_ice = True
        elif feet:
            self.on_ice = False
        if (fix_dx < 0 and tile.collision in '/1 \\0') or (fix_dx > 0 and tile.collision in '\\1 /0'):
            pass
        elif '\\' in tile.collision or '/' in tile.collision:
            m = -1 if '/' in tile.collision else 1  # gradient
            c = self.tile_size if '/' in tile.collision else 0  # y-intercept
            offset_y = mod_y - (m * mod_x + c)  # Linear equation
            if tile.layer == 2:
                return False
            if '0' in tile.collision:
                if offset_y >= 0:
                    return False
                elif fix_dy > 0:
                    pass  # It's a solid so go down to the solid block collision scripts
                else:
                    self.y += self.tile_size - offset_y
                    return True
            elif '1' in tile.collision:
                if offset_y <= 0:
                    return False
                elif fix_dy < 0:
                    pass
                else:
                    self.y -= offset_y
                    return True
        if '-' in tile.collision:
            if mod_y - fix_dy > 1 or not feet or self.climbing:
                return False
        if '=' in tile.collision or '_' in tile.collision or '>' in tile.collision or '<' in tile.collision:
            dx, dy = tile.col_width, tile.col_height
            if self.y_vel > 21 and dy * -1 > 20:
                return False
            if dy < 0 and mod_y + 0.000001 < dy * -1:
                if 4 < self.y_vel:
                    self.y_vel = dy * -1 - mod_y - 0.0001
                return False
            if dx < 0 and mod_x + 0.000001 < dx * -1:
                safe_speed = 3
                if dx * -1 > mod_x + 5 and self.x_vel > safe_speed:
                    self.x_vel = safe_speed
                return False
            if 0 < dy < mod_y and not feet:
                return False
            if 0 < dx <= mod_x:
                safe_speed = 3
                if mod_x - 5 < dx and -self.x_vel > safe_speed:
                    self.x_vel = -safe_speed
                return False
        if '~' in tile.collision:
            self.swimming = True
            if 280 <= tile.idx <= 282:
                self.lives = 0
                self.frame = 0
            return False
        # To account for slopes, 0.000001 is added after the mod instead of a higher value
        if fix_dy > 0:
            if not feet:
                fix_dx = self.x_vel
            else:
                self.y -= mod_y + 0.000001 + (dy if dy < 0 else 0)
        elif fix_dy < 0:
            self.y += self.tile_size - (mod_y - (dy if dy > 0 else 0))
        if fix_dx < 0:
            self.x += self.tile_size - (mod_x + (32 - dx if dx > 0 else 0))
        elif fix_dx > 0:
            self.x -= mod_x + 0.000001 + (dx + 1 if dx < 0 else 0)
        return True


if __name__ == '__main__':
    py.init()
    width, height = 380, 400
    screen = py.display.set_mode((width, height))
    py.display.set_caption("Player Test")
    clock = py.time.Clock()
    p1 = L_Player(screen, 0, 0, 1, None, None, '')

    run = True
    while run:
        screen.fill((25, 25, 25))
        p1.edit_move()
        p1.draw()
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
        py.display.update()
        clock.tick(60)
