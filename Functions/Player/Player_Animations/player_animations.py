import pygame as py
from os.path import join

try:
    from .player_image_settings import player_image as ps
except ImportError:
    from player_image_settings import player_image as ps

"""This file sorts out player sprite-sheets"""


def load(loc):
    """Loads in images from a location"""
    return py.image.load(loc).convert_alpha()


def flip(image):
    """Flips the image horizontally"""
    return py.transform.flip(image, True, False).convert_alpha()


class Pics_Player:
    """Loads in player pictures ready for animation"""

    def __init__(self, path, player):
        """Loads in the pictures of the specified player"""
        self.player = ''.join(['p', str(player)])
        self.path = join(path, self.player)
        self.img_size = ps[player]

        self.climb, self.duck, self.front, self.hurt, self.jump, self.stand, self.swim, self.walk = \
            2, 1, 1, 1, 1, 1, 2, 2

        """Loading in Sprite Sheets"""
        self.right_dict = {'climb': (((load(f'{self.path}\{self.player}_climb1.png'), self.img_size[0]),
                                      (load(f'{self.path}\{self.player}_climb2.png'), self.img_size[1])), self.climb),
                           'duck': ([(load(f'{self.path}\{self.player}_duck.png'), self.img_size[2])], self.duck),
                           'front': ([(load(f'{self.path}\{self.player}_front.png'), self.img_size[3])], self.front),
                           'hurt': ([(load(f'{self.path}\{self.player}_hurt.png'), self.img_size[4])], self.hurt),
                           'jump': ([(load(f'{self.path}\{self.player}_jump.png'), self.img_size[5])], self.jump),
                           'stand': ([(load(f'{self.path}\{self.player}_stand.png'), self.img_size[6])], self.stand),
                           'swim': (((load(f'{self.path}\{self.player}_swim1.png'), self.img_size[7]),
                                     (load(f'{self.path}\{self.player}_swim2.png'), self.img_size[8])), self.swim),
                           'walk': (((load(f'{self.path}\{self.player}_walk1.png'), self.img_size[9]),
                                     (load(f'{self.path}\{self.player}_walk2.png'), self.img_size[10])), self.walk)}
        self.left_dict = {'climb': (((flip(load(f'{self.path}\{self.player}_climb1.png')), self.img_size[0]),
                                     (flip(load(f'{self.path}\{self.player}_climb2.png')), self.img_size[1])),
                                    self.climb),
                          'duck': ([(flip(load(f'{self.path}\{self.player}_duck.png')), self.img_size[2])], self.duck),
                          'front': ([(flip(load(f'{self.path}\{self.player}_front.png')), self.img_size[3])],
                                    self.front),
                          'hurt': ([(flip(load(f'{self.path}\{self.player}_hurt.png')), self.img_size[4])], self.hurt),
                          'jump': ([(flip(load(f'{self.path}\{self.player}_jump.png')), self.img_size[5])], self.jump),
                          'stand': ([(flip(load(f'{self.path}\{self.player}_stand.png')), self.img_size[6])],
                                    self.stand),
                          'swim': (((flip(load(f'{self.path}\{self.player}_swim1.png')), self.img_size[7]),
                                    (flip(load(f'{self.path}\{self.player}_swim2.png')), self.img_size[8])), self.swim),
                          'walk': (((flip(load(f'{self.path}\{self.player}_walk1.png')), self.img_size[9]),
                                    (flip(load(f'{self.path}\{self.player}_walk2.png')), self.img_size[10])),
                                   self.walk)}

    @classmethod
    def get_all_images(cls, path):
        """Collects all player images in the standing position"""
        all_pics = {}
        for i in range(1, 4):
            all_pics[i] = cls(path, i).frame('stand', 0, False)
        return all_pics

    def frame(self, category, costume: int, facing_right=True):
        """Returns the image frame requested"""
        if facing_right:
            sheet = self.right_dict[category]
        else:
            sheet = self.left_dict[category]

        if sheet[1] <= costume:
            raise ValueError(f"Animation has {sheet[1] - 1} pictures, tried to get {costume}")

        return sheet[0][costume]

    def display(self, win: py.display, action: str, frame: int, x: int, y: int, facing_right=True):
        """Displays frame on screen"""
        image = self.frame(action, frame, facing_right)
        win.blit(image[0], (x + (70 - image[1][0]), y + (100 - image[1][1])))


if __name__ == '__main__':
    """Testing player animation getting"""
    py.init()
    screen = py.display.set_mode((500, 500))
    py.display.set_caption("Player Animations Test")
    clock = py.time.Clock()
    player_pics = Pics_Player('', 1)

    j = 0
    run = True
    while run:
        screen.fill((25, 25, 25))

        player_pics.display(screen, 'climb', j // 8 % player_pics.climb, 10, 10, True)

        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
        j += 1
        py.display.update()
        clock.tick(60)
        # print(clock.get_fps())
