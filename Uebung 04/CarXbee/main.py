import xbee

from CarState import CarState
from CarController import CarController
from FramePacker import FramePacker

car_controller = CarController()
old_car_state = CarState(False, 0, 0, True, True)

while True:
    frame = xbee.receive()

    if frame:
        car_state = FramePacker.unpack(frame['payload'])
        print(car_state.__dict__)

        if car_state.enabled:
            car_controller.accelerate(car_state.is_direction_forward, car_state.speed)
            car_controller.turn(car_state.is_turning_right, car_state.direction_angle)
        else:
            car_state = CarState(False, 0, 0, True, True)
            car_controller.stop()
