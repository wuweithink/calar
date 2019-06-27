#!/usr/bin/env python3

import glob
import os
import sys
try:
    sys.path.append(glob.glob('./carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

try:
    import pygame
    from pygame.locals import K_TAB
    from pygame.locals import K_r
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')
from time import time, sleep
import random
import argparse

from carlaworld import CarlaWorld
from cameramanager import CameraManager
from carlamap import MapInfo
from egocontrol import EgoControl

def exit_game():
    pygame.quit()
    sys.exit()

class ModuleInput(object):
    def __init__(self, ego_ctrl):
        self._ego_control = ego_ctrl
        self.wheel_offset = 0.1
        self.wheel_amount = 0.025

    def tick(self, clock):
        self.parse_input(clock)
        self._ego_control.trigger()

    def _parse_events(self):
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.locals.K_TAB:
                    if self._ego_control is not None:
                        if self._ego_control.get_autopilot():
                            self._ego_control.unset_autopilot()
                            #self._ego_control.start_control()
                        else:
                            self._ego_control.set_autopilot()
                            #self._ego_control.stop_control()
                elif event.key == pygame.locals.K_r:
                    if self._ego_control is not None:
                        self._ego_control.set_reverse()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.wheel_offset += self.wheel_amount
                    if self.wheel_offset >= 1.0:
                        self.wheel_offset = 1.0
                elif event.button == 5:
                    self.wheel_offset -= self.wheel_amount
                    if self.wheel_offset <= 0.1:
                        self.wheel_offset = 0.1

    def parse_input(self, clock):
        self._parse_events()



def game_loop(args):
    pygame.init()
    pygame.font.init()
    carla_world = None
    try:
        display = pygame.display.set_mode((args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        carla_world = CarlaWorld('127.0.0.1', 2000)
        carla_world.start_sim()
        mapinfo = MapInfo(carla_world.world, carla_world.map)
        print('carla simulation start!')
        #return
        actor = carla_world.add_ego()
        control = EgoControl(carla_world)
        minput = ModuleInput(control)
        control.start_control()
        camera = CameraManager(carla_world.ego, args.width - 960, args.height)
        camera.set_sensor(0)
        clock = pygame.time.Clock()
        while True:
            carla_world.world.wait_for_tick()
            #control.trigger()
            minput.tick(clock)
            camera.render(display)
            mapinfo.render(display)
            pygame.display.flip()
    finally:
        carla_world.destroy()
        control.stop_control()
        camera.unset_sensor()
        pygame.quit()


def main():
    argparser = argparse.ArgumentParser(description = 'Carla simulation')
    argparser.add_argument(
        '--width',
        default=2240,
        type=int,
        help='window width(default: 1280)'
        )
    argparser.add_argument(
        '--height',
        default=960,
        type=int,
        help='window height(default: 960)'
        )
    args = argparser.parse_args()

    try:
        game_loop(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':
        main()
