#!/usr/bin/env python3


"""G920 device control interface"""
import evdev
from evdev import ecodes
import os
import sys
from threading import Thread, Event


class G920ControlDevice(Thread):
    def __init__(self):
        super().__init__()
        self._device = self._get_g920_device()
        self._stop_event = Event()
        self._steer = 0.0
        self._throttle = 255.0
        self._brake = 255.0

    @staticmethod
    def _get_g920_device():
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name.find("G920") != -1:
                print(device)
                return device

    def run(self):
        #device = self._get_g920_device()
        for event in self._device.read_loop():
            #print('dev event', event)
            if event.type == 3:
                if event.code == 0:
                    self._steer = event.value
                if event.code == 1:
                    self._throttle = event.value
                if event.code == 2:
                    self._brake = event.value
            if event.type == 1:
                if event.code == 298:
                    print('quit thread')
                    return

    def get_control_value(self):
        return (self._steer, self._throttle, self._brake)

#This code is only for test!
"""
def main():
    dev_thread = G920ControlDevice()
    dev_thread.start()
    dev_thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone')
"""
