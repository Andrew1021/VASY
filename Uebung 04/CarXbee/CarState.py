class CarState:
    def __init__(self, enabled, speed, direction_angle, is_direction_forward, is_turning_right):
        self.enabled = enabled
        self.speed = speed
        self.direction_angle = direction_angle
        self.is_direction_forward = is_direction_forward
        self.is_turning_right = is_turning_right
