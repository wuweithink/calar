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
from controldevice import G920ControlDevice



class EgoControl(object):
    def __init__(self, world):
        self._control = carla.VehicleControl()
        self._dev = G920ControlDevice()
        self._autopilot_enabled = False
        self._world = world

    def start_control(self):
        print('start_control')
        self._dev.start()

    def stop_control(self):
        print('stop_control')
        self._dev.join()

    def get_autopilot(self):
        return self._autopilot_enabled

    def set_autopilot(self):
        self._autopilot_enabled = True
        self._world.ego.set_autopilot(self._autopilot_enabled)

    def unset_autopilot(self):
        self._autopilot_enabled = False
        self._world.ego.set_autopilot(self._autopilot_enabled)

    def set_reverse(self):
        self._control.reverse = not self._control.reverse

    def trigger(self):
        if self._autopilot_enabled:
            return
        #print('manual ego control')
        (steer, throttle, brake) = self._dev.get_control_value()
        self._control.throttle = (255 - throttle) / 128
        self._control.brake = (255 - brake) / 128
        self._control.steer = (steer - 32768) / 32768
        """
        print('dev: ', steer, throttle, brake)
        print('throttle: ', self._control.throttle)
        print('brake: ', self._control.brake)
        print('steer: ', self._control.steer)
        print('\n')
        """
        self._world.ego.apply_control(self._control)
