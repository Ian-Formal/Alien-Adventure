import pygame as py
from os import listdir
from os.path import join, isfile


class Particles:
    """Stores all particle functions"""
    __slots__ = 'screen', 'images', 'n_particles', 'particles', 'font', 'lim_particles', 'camera_x', 'camera_y'

    def __init__(self, win: py.display, path=''):
        self.screen = win
        self.images = Particle_Img(path).images
        self.n_particles = 0
        self.particles = {}
        self.font = py.font.Font(None, 18)

        self.lim_particles = 0
        self.camera_x = 0
        self.camera_y = 0

    def mainloop(self):
        """Runs all particles"""
        self.delete_particles()
        self.position_particles()
        for particle in self.particles.values():

            if particle['type'] == 'coin':
                self.screen.blit(particle['image'], (particle['draw_x'], particle['draw_y']))

    def paint_particles_after(self):
        """Paints particles after tiles"""
        for particle in self.particles.values():

            if particle['type'] == 'smoke':
                py.draw.circle(self.screen, '#ffffff', (particle['draw_x'], particle['draw_y']), particle['radius'])
            if particle['type'] == 'score':
                self.screen.blit(particle['image'], (particle['draw_x'], particle['draw_y']))

    def position_particles(self):
        """Positions particles onto screen"""
        new_particles = []
        for particle in self.particles.values():

            if particle['type'] == 'smoke':
                particle['radius'] -= 0.1

            elif particle['type'] == 'coin':
                particle['y_vel'] += 1
                if particle['y_vel'] > 8:
                    if particle['show']:
                        new_particles.append({'score': (particle['x'], particle['y'], 100)})
                        particle['show'] = False
                    continue
                particle['y'] += particle['y_vel']

            elif particle['type'] == 'score':
                particle['y_vel'] += 0.1
                if particle['y_vel'] >= 0:
                    particle['show'] = False
                    continue
                particle['y'] += particle['y_vel']
                particle['alpha'] = (1 - (1 / (abs(particle['y_vel']) + 1))) * 255

            particle['draw_x'] = particle['x'] - self.camera_x
            particle['draw_y'] = particle['y'] - self.camera_y
            if 'alpha' in particle:
                particle['image'].set_alpha(particle['alpha'])

        for particle in new_particles:
            key = tuple(particle.keys())[0]
            if key == 'score':
                self.tick_score_at(particle[key][0], particle[key][1], particle[key][2])

    def delete_particles(self):
        """Deletes particles"""
        for i, particle in tuple(self.particles.items()):  # Copying the dictionary to not get an exception

            if particle['type'] == 'smoke':
                if particle['radius'] <= 0:
                    del self.particles[i]
                    self.n_particles -= 1

            elif particle['type'] == 'coin' or particle['type'] == 'score':
                if not particle['show']:
                    del self.particles[i]
                    self.n_particles -= 1

    def tick_smoke_at(self, x, y, size, limit=True):
        radius = size
        if self.lim_particles % 2 == 1 or not limit:
            self.particles[self.n_particles] = {'x': x, 'y': y, 'draw_x': x, 'draw_y': y,
                                                'radius': radius, 'type': 'smoke'}
            self.n_particles += 1
        self.lim_particles += 1

    def tick_coin_at(self, x, y, size):
        self.particles[self.n_particles] = {'x': x, 'y': y, 'draw_x': x, 'draw_y': y, 'y_vel': -8, 'type': 'coin',
                                            'show': True, 'image': py.transform.scale(self.images[1], (size, size))}
        self.n_particles += 1

    def tick_score_at(self, x, y, score):
        self.particles[self.n_particles] = {'x': x, 'y': y, 'draw_x': x, 'draw_y': y, 'y_vel': -4, 'type': 'score',
                                            'show': True, 'image': self.font.render(str(score), True, '#434242'),
                                            'alpha': 255}
        self.n_particles += 1


class Particle_Img:
    """Stores Particle Images"""

    def __init__(self, path):
        """Stores all images into a dictionary"""
        file_path = join(path, 'Particle_Art')
        self.images = {key: load(join(file_path, value)) for key, value in enumerate(sorted(listdir(file_path))) if
                       isfile(join(file_path, value))}


def load(loc):
    """Loads in images from a location"""
    return py.image.load(loc).convert_alpha()


if __name__ == '__main__':
    pass
