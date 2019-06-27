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
import pygame

PIXELS_PER_METER = 12

class MapInfo(object):
    def __init__(self, carla_world, carla_map):
        self.world = carla_world
        self.map = carla_map
        self._pixels_per_meter = PIXELS_PER_METER
        self.scale = 1.0
        self.precision = 0.05
        waypoints = carla_map.generate_waypoints(2)
        #for w in waypoints:
        #    print(w.transform.location)
        margin = 50
        max_x = max(waypoints, key = lambda x: x.transform.location.x).transform.location.x + margin
        max_y = max(waypoints, key = lambda x: x.transform.location.y).transform.location.y + margin
        min_x = min(waypoints, key = lambda x: x.transform.location.x).transform.location.x - margin
        min_y = min(waypoints, key = lambda x: x.transform.location.y).transform.location.y - margin
        #print("max x: ", max_x)
        #print("max y: ", max_y)
        #print("min x: ", min_x)
        #print("min y: ", min_y)
        self.width = max(max_x - min_x, max_y - min_y)
        #print("width: ", self.width)
        self._world_offset = (min_x, min_y)
        #print("world offset", self._world_offset)

        width_in_pixels = (1 << 14) - 1

        # Adapt Pixels per meter to make world fit in surface
        surface_pixel_per_meter = int(width_in_pixels / self.width)
        if surface_pixel_per_meter > PIXELS_PER_METER:
            surface_pixel_per_meter = PIXELS_PER_METER

        self._pixels_per_meter = surface_pixel_per_meter
        width_in_pixels = int(self._pixels_per_meter * self.width)
        #print('width in pixels', width_in_pixels)
        self.big_map_surface = pygame.Surface((width_in_pixels, width_in_pixels)).convert()
        self.surface = self.big_map_surface
        #self.draw_waypoints()
        self.draw_topology()



    def draw_map(self):
        return


    def draw_waypoints(self):
        self.big_map_surface.fill(pygame.Color(0, 0, 0))
        waypoints = self.map.generate_waypoints(2.0)
        waypoints = [self.world_to_pixel(x.transform.location) for x in waypoints]
        for w in waypoints:
            #print('waypoint:', w)
            pygame.draw.circle(self.big_map_surface, pygame.Color(255, 0, 0), w, 3, 1)
        pygame.image.save(self.big_map_surface, "map_draw_waypoints.png")


    def draw_lane(self, surface, lane, color):
        for side in lane:
            lane_left_side = [self.lateral_shift(w.transform, -w.lane_width * 0.5) for w in side]
            lane_right_side = [self.lateral_shift(w.transform, w.lane_width * 0.5) for w in side]
            polygon = lane_left_side + [x for x in reversed(lane_right_side)]
            polygon = [self.world_to_pixel(x) for x in polygon]
            if len(polygon) > 2:
                pygame.draw.polygon(surface, color, polygon, 5)
                pygame.draw.polygon(surface, color, polygon)

    def draw_topology(self):
        print('draw topology')
        self.big_map_surface.fill(pygame.Color(85, 87, 83))
        carla_topology = self.map.get_topology()
        #index=0
        topology = [x[0] for x in carla_topology]
        topology = sorted(topology, key = lambda w: w.transform.location.z)
        set_waypoints = []
        for waypoint in topology:
            waypoints = [waypoint]
            next = waypoint.next(self.precision)
            if len(next) > 0:
                next = next[0]
                while waypoint.road_id == next.road_id:
                    waypoints.append(next)
                    next = next.next(self.precision)
                    if len(next) > 0:
                        next = next[0]
                    else:
                        break

            #draw road
            road_left_side = [self.lateral_shift(w.transform, -w.lane_width * 0.5) for w in waypoints]
            road_right_side = [self.lateral_shift(w.transform, w.lane_width * 0.5) for w in waypoints]
            polygon = road_left_side + [x for x in reversed(road_right_side)]
            polygon = [self.world_to_pixel(x) for x in polygon]
            if len(polygon) > 2:
                pygame.draw.polygon(self.big_map_surface, pygame.Color(46, 72, 54), polygon, 5)
                pygame.draw.polygon(self.big_map_surface, pygame.Color(46, 72, 54), polygon)

            set_waypoints.append(waypoints)
            print('finished getting set_waypoints')
            PARKING_COLOR = pygame.Color(66, 62, 64)
            SHOULDER_COLOR = pygame.Color(46, 52, 54)
            SIDEWALK_COLOR = pygame.Color(136, 138, 133)
            shoulder = [[], []]
            parking = [[], []]
            sidewalk = [[], []]

            for w in waypoints:
                l = w.get_left_lane()
                while l and l.lane_type != carla.LaneType.Driving:
                    if l.lane_type == carla.LaneType.Shoulder:
                        shoulder[0].append(l)
                    if l.lane_type == carla.LaneType.Parking:
                        parking[0].append(l)
                    if l.lane_type == carla.LaneType.Sidewalk:
                        sidewalk[0].append(l)
                    l = l.get_left_lane()
                print('finished left lane')

                r = w.get_right_lane()
                while r and r.lane_type != carla.LaneType.Driving:
                    if r.lane_type == carla.LaneType.Shoulder:
                        shoulder[1].append(r)
                    if r.lane_type == carla.LaneType.Parking:
                        parking[1].append(r)
                    if r.lane_type == carla.LaneType.Sidewalk:
                        sidewalk[1].append(r)
                    r = r.get_right_lane()
                print('finished right lane')

            self.draw_lane(self.big_map_surface, shoulder, SHOULDER_COLOR)
            self.draw_lane(self.big_map_surface, parking, PARKING_COLOR)
            self.draw_lane(self.big_map_surface, sidewalk, SIDEWALK_COLOR)
        pygame.image.save(self.big_map_surface, "map_draw_topology.png")
        print('finished drawing topology')


    def render(self, display):
        if self.surface is not None:
            #self.surface.fill(pygame.Color(211, 0, 0))
            #self.surface = pygame.transform.smoothscale(self.big_map_surface, (400, 400))
            #display.blit(self.surface, (800, 500))
            self.surface = pygame.transform.smoothscale(self.big_map_surface, (960, 960))
            display.blit(self.surface, (1280, 0))


    def lateral_shift(self, transform, shift):
        transform.rotation.yaw += 90
        return transform.location + shift * transform.get_forward_vector()


    def world_to_pixel(self, location, offset=(0, 0)):
        x = self.scale * self._pixels_per_meter * (location.x - self._world_offset[0])
        y = self.scale * self._pixels_per_meter * (location.y - self._world_offset[1])
        return [int(x - offset[0]), int(y - offset[1])]


    def world_to_pixel_width(self, width):
        return int(self.scale * self._pixels_per_meter * width)


    def scale_map(self, scale):
        if scale != self.scale:
            self.scale = scale
            width = int(self.big_map_surface.get_width() * self.scale)
            self.surface = pygame.transform.smoothscale(self.big_map_surface, (width, width))
