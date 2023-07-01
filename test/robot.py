import math


class Cobalt:

    def __init__(self):

        # components
        self.left_encoder = None
        self.right_encoder = None

        self.left_motor = None
        self.right_motor = None

        # last encoder value at the beginning is 0
        self.last_left_count = 0
        self.last_right_count = 0

        # robot geometry
        self.wheel_base = 0.04
        self.wheel_radius = 0.025

        # meters per tick
        self.meters_per_tick_left = (2 * math.pi * self.wheel_radius) / self.left_encoder.ticks_per_revolution
        self.meters_per_tick_right = self.meters_per_tick_left

        # pose of the robot
        self.x = 0
        self.y = 0
        self.theta = 0

    def get_pose(self):
        return self.x, self.y, self.theta
    
    def set_pose(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

    def reset_pose(self):
        self.x = 0
        self.y = 0
        self.theta = 0
    
    def update_odometry(self):

        # compute ticks delta from last read
        delta_ticks_left = (self.left_encoder.count - self.last_left_count) * self.left_encoder.direction
        delta_ticks_right = (self.right_encoder.count - self.last_right_count) * self.right_encoder.direction

        # update counters
        self.last_left_count = self.left_encoder.count
        self.last_right_count = self.right_encoder.count

        # compute new pose
        left_distance = self.meters_per_tick_left * delta_ticks_left
        right_distance = self.meters_per_tick_right * delta_ticks_right
        center_distance = (right_distance + left_distance) / 2

        # compute new pose delta
        delta_x = center_distance * math.cos(self.theta)
        delta_y = center_distance * math.sin(self.theta)
        delta_theta = (right_distance - left_distance) / self.wheel_base

        # compute new pose
        self.x += delta_x
        self.y += delta_y
        self.theta += delta_theta

        return self.x, self.y, self.theta
