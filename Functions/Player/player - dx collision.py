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
        self.spawn_idx = self.spawn_idx[0] if self.spawn_idx else 3
        self.reset_pos(self.editor.grid_height, self.tile_size)
        self.x += 3
        self.tile_idx = self.spawn_idx
        self.action = 'level'

    def handle_keys(self):
        """Handle user inputs on player"""
        if self.action != 'walk' and self.action != 'n_walk':
            keys = py.key.get_pressed()
            keys_dict = {True: 1, False: 0}
            self.x_vel = keys_dict[keys[py.K_RIGHT]] - keys_dict[keys[py.K_LEFT]]
            if self.x_vel == 0:
                self.y_vel = keys_dict[keys[py.K_DOWN]] - keys_dict[keys[py.K_UP]]
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

    def move(self):
        """Moves the player"""
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

        # Collision
        self.pins = {}
        self.update_pins()
        self.get_tile = get_tile_at_func
        self.make_smoke = smoke_func
        self.rect = self.image[0].get_rect()
        self.mask = py.mask.from_surface(self.image[0])
        self.on_ice = False
        self.collided = False

        # Other
        self.lives = 6
        self.hurt = False
        self.invis = 0
        self.touching = False

    def reset(self, grid_height):
        """Reset player settings"""
        self.reset_pos(grid_height, self.tile_size)
        # Jumping Mechanics
        self.falling = 69  # Nice
        self.jumping = 69
        self.bounce = 0
        self.bump = False

        self.dir = True
        self.hurt = False
        self.invis = 0
        self.touching = False
        self.on_ice = False

    def minus_life(self):
        """Takes away lives from the player"""
        if not self.invis > 0:
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
        self.move_left_right(right - left, keys[py.K_n])
        self.jump(keys_dict[keys[py.K_SPACE]])

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
        self.x_vel += 6 * (right - left)
        self.y_vel += -6 * (up - down)
        self.x_vel *= 0.8
        self.y_vel *= 0.8
        self.x += self.x_vel
        self.y += self.y_vel
        self.draw_x = self.x - self.camera_x
        self.draw_y = self.y - self.camera_y

    def move_left_right(self, key_press: int, running):
        """Control movements for player left and right"""
        top_speed = {True: 7, False: 3}  # Running vs walking
        keys_dict = {1: True, -1: False}
        # Deceleration: 0.1 -> Ice Deceleration, 0.45 -> Normal Deceleration
        deceleration = (0.1 if self.on_ice else 0.45)
        if key_press == 0:
            if self.falling < 2:
                if self.x_vel > deceleration:
                    self.x_vel -= deceleration
                elif self.x_vel < -deceleration:
                    self.x_vel += deceleration
                else:
                    self.x_vel = 0
                    self.frame = 0
        else:
            self.dir = keys_dict[key_press]
            if key_press * self.x_vel < top_speed[running]:  # Max speed
                if key_press * self.x_vel < 0:
                    if self.falling < 2:
                        # Deceleration when turning: 0.3 -> ice deceleration, 0.7 -> normal deceleration
                        self.x_vel += key_press * (0.3 if self.on_ice else 0.7)
                        # Smoke Particle
                        self.make_smoke(self.x + self.width * (0 if self.x_vel > 0 else 1 / 2),
                                        self.y + (-10.9375 + self.height) * self.scale - self.tile_size,
                                        10.9375 * self.scale)
                    else:
                        self.x_vel += key_press * 0.7  # Deceleration when turning in the air
                else:
                    # Acceleration: 0.1 -> ice acceleration, 0.3 -> normal acceleration
                    self.x_vel += key_press * (0.1 if self.on_ice else 0.3)

        # Animations
        temp = abs(self.x_vel) / 19
        if temp < 0.2:
            temp = 0.2
        self.frame += temp

    def jump(self, key_press: int):
        """Handling the jump key"""
        self.y_vel += 0.9  # Acceleration due to gravity: 0.9
        if self.y_vel > 22:  # Max gravitational velocity
            self.y_vel = 22
        if key_press > 0:
            if self.falling < 2 or self.jumping > 0:  # Coyote Jump
                self.jumping += 1
                if self.jumping < 15:  # How long can you hold the jump button for: 15
                    self.y_vel = -9  # Jump Speed: -12
        else:
            self.jumping = 0

    def draw(self):
        """Draws the player onto the screen"""
        # py.draw.rect(self.win, '#000000', self.rect)
        self.image[0].set_alpha(self.alpha)
        self.win.blit(py.transform.scale(self.image[0], (self.scale * 70, self.scale * 100)),
                      (self.draw_x + (self.width - self.image[1][0]) * self.scale,
                       self.draw_y - (self.height - self.image[1][1]) * self.scale - self.tile_size))

    def animate(self):
        """Animations"""
        if self.falling > 1:
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
        if x is None:
            self.x += self.x_vel
        else:
            self.x += x
        y = self.y
        if not self.collided:
            check_x = False
        else:
            check_x = self.check_move_x()
        collided = self.handle_collision_in_dir(0, 1, True)
        if self.y < y - abs(self.x_vel) - 4 or check_x or (collided and self.collided):
            self.y = y
            orig_x_vel = self.x_vel
            if collided and self.collided and not check_x:
                self.x_vel += self.collided.x_vel
            if self.handle_collision_in_dir(self.x_vel, 0):
                self.x_vel = 0
            else:
                self.x_vel = orig_x_vel
            if not (collided and self.collided):
                self.collided = False
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
        self.x += self.collided.x_vel

        check_x = (self.pins['bottom'] > self.collided.y + self.collided.height * 2 and
                   (self.y_vel > 0 or self.jumping <= 1)) or \
                  (self.pins['top'] < self.collided.y + self.collided.height / 2 and (self.y_vel < 0 or
                   self.jumping > 1))

        return check_x

    def check_y(self):
        """Moves variables around when collided with y"""
        if self.y_vel > 0:
            self.falling = 0
        else:
            self.jumping = 69  # Nice
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
        self.collided = False
        self.update_draw_pos()

    def handle_collision_in_dir(self, dx, dy, test_x=False):
        """Handles collision in a direction"""
        self.update_pins()
        top, mid, bottom = self.pins['top'], self.pins['mid'], self.pins['bottom']
        left, right = self.pins['left'], self.pins['right']
        # The order of how the collision is checked in pins is important. If middle pins are not tested first,
        # there is a bug of the player getting stuck in between blocks when jumping
        collided = self.handle_collision_at_point(left, mid, dx, dy) or \
            self.handle_collision_at_point(right, mid, dx, dy) or \
            self.handle_collision_at_point(left, bottom, dx, dy, True) or \
            self.handle_collision_at_point(right, bottom, dx, dy, True) or \
            self.handle_collision_at_point(left, top, dx, dy) or \
            self.handle_collision_at_point(right, top, dx, dy)

        if self.collided and not test_x:
            collided = collided or self.handle_moving_collision(dx, dy)
        return collided

    def handle_moving_collision(self, fix_dx, fix_dy):
        """Handles collisions with movable tiles"""
        dx, dy = 0, 0
        if fix_dy > 0:
            dy = -0.1
        elif fix_dy < 0:
            dy = 0.1
        if fix_dx < 0:
            dx = 0.1
        elif fix_dx > 0:
            dx = -0.1
        looped = 0
        while py.sprite.collide_rect(self, self.collided):
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
            self.y += self.collided.y_vel
        if looped < 2:
            return False
        return True

    def handle_collision_at_point(self, x, y, fix_dx, fix_dy, feet=False):
        """Handles collision at points of the player"""
        mod_x = x % self.tile_size
        mod_y = y % self.tile_size
        tile = self.get_tile(x, y)[1]
        return self.move_outside_collision(mod_x, mod_y, fix_dx, fix_dy, feet, tile)

    def move_outside_collision(self, mod_x, mod_y, fix_dx, fix_dy, feet, tile):
        """Moves the player outside of collision"""
        dx, dy = 0, 0
        if not tile.solid:
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
            if mod_y - fix_dy > 1 or not feet:
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
                if dx * -1 > mod_x + 5 and abs(self.x_vel) > safe_speed:
                    self.x_vel = safe_speed if self.x_vel > 0 else -safe_speed
                return False
            if 0 < dy < mod_y and not feet:
                return False
            if 0 < dx <= mod_x:
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
