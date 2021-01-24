from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice, XBee64BitAddress
from digi.xbee.exception import XBeeException
import pygame

from CarState import CarState
from FramePacker import FramePacker

MAX_DUTY = 1023

MAX_SPEED = 200
MAX_DIRECTION_ANGLE = 600
SPEED_STEP = 20


def send_frame(_car_state):
    # print(_car_state.__dict__)
    # print("Speed", _car_state.speed)

    try:
        device.send_data_async(car_xbee, FramePacker.pack(_car_state))
    except XBeeException as exception:
        print(exception.__str__())


device = ZigBeeDevice("/dev/ttyUSB0", 9600)
device.open()
car_xbee = RemoteZigBeeDevice(device, XBee64BitAddress.from_hex_string("0013A200418730B3"))

pygame.init()
pygame.display.set_caption('Drive the XbeeCar')
pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
time_elapsed_since_last_action = 0


car_state = CarState(False, 0, 0, True, True)
print("Car is disabled - Start by pressing Space!")

while True:
    dt = clock.tick()

    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        break

    if pygame.key.get_pressed()[pygame.K_w] == 1:
        car_state.is_direction_forward = True
        car_state.speed = min(car_state.speed + SPEED_STEP, MAX_SPEED)

    if pygame.key.get_pressed()[pygame.K_s] == 1:
        car_state.is_direction_forward = False
        car_state.speed = min(car_state.speed + SPEED_STEP, MAX_SPEED)

    if pygame.key.get_pressed()[pygame.K_a] == 1:
        car_state.is_turning_right = False
        car_state.direction_angle = MAX_DIRECTION_ANGLE

    if pygame.key.get_pressed()[pygame.K_d] == 1:
        car_state.is_turning_right = True
        car_state.direction_angle = MAX_DIRECTION_ANGLE

    if event.type == pygame.KEYUP:
        if event.key in (pygame.K_d, pygame.K_a):
            car_state.direction_angle = 0

        if event.key in (pygame.K_w, pygame.K_s):
            car_state.speed = 0

        if event.key is pygame.K_SPACE:
            car_state.enabled = not car_state.enabled
            if car_state.enabled:
                print("Car is now enabled")
            else:
                print("Car is now disabled")

        if event.key is pygame.K_ESCAPE:
            car_state = CarState(False, 0, 0, True, True)
            send_frame(car_state)
            break

        send_frame(car_state)

    if sum(pygame.key.get_pressed()) == 0:
        car_state.speed = 0
        car_state.direction_angle = 0

    time_elapsed_since_last_action += dt
    if time_elapsed_since_last_action > 100:
        time_elapsed_since_last_action = 0
        send_frame(car_state)

pygame.quit()
device.close()
