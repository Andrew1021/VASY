import struct
from CarState import CarState


class FramePacker:
    @staticmethod
    def pack(car_state):
        return struct.pack("bhhbb", car_state.enabled, car_state.speed, car_state.direction_angle,
                           car_state.is_direction_forward, car_state.is_turning_right)

    @staticmethod
    def unpack(frame):
        enabled, speed, direction_angle, is_direction_forward, is_turning_right = struct.unpack("bhhbb", frame)

        enabled = enabled == 1
        is_direction_forward = is_direction_forward == 1
        is_turning_right = is_turning_right == 1

        return CarState(enabled, speed, direction_angle, is_direction_forward, is_turning_right)
