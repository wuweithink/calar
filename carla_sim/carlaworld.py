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
from time import time, sleep
import random
import logging

from controldevice import G920ControlDevice


class CarlaWorld(object):
    def __init__(self, host, port):
        self.client = None
        self.world = None
        self.host = host
        self.port = port
        self.map = None
        self.players = None
        self.ego = None

    def _create_carla_client(self):
        try:
            self.client = carla.Client(self.host, self.port)
            self.client.set_timeout(2.0)
            self.world = self.client.get_world()
            self.map = self.world.get_map()
            print('create carla world success!')
        except RuntimeError as ex:
            logging.error(ex)


    def _spawn_actor(self, number_of_vehicles):
        actor_list = []
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor
        spawn_points = self.map.get_spawn_points()
        blueprints = self.world.get_blueprint_library().filter('vehicle.*')
        batch = []
        for n, transform in enumerate(spawn_points):
            if n > number_of_vehicles:
                break
            blueprint = random.choice(blueprints)
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            blueprint.set_attribute('role_name', 'autopilot')
            batch.append(SpawnActor(blueprint, transform).then(SetAutopilot(FutureActor, True)))
        for response in self.client.apply_batch_sync(batch):
            if response.error:
                return
                logging.error(response.error)
            else:
                actor_list.append(response.actor_id)
        self.players = actor_list
        return self.players

    def start_sim(self):
        self._create_carla_client()
        #self._spawn_actor(30)
        #self._add_ego()

    def add_ego(self):
        blueprints = self.world.get_blueprint_library().filter('vehicle.*')
        blueprint = random.choice(blueprints)
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        blueprint.set_attribute('role_name', 'Ego')
        while self.ego is None:
            spawn_points = self.map.get_spawn_points()
            spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            self.ego = self.world.try_spawn_actor(blueprint, spawn_point)
        return self.ego

    def map_action(self):
        #opendrive = self.map.to_opendrive()
        #print(opendrive)
        #print(self.map.name)
        topo = self.map.get_topology()
        print(topo)

    def destroy(self):
        if self.ego is not None:
            self.ego.destroy()
