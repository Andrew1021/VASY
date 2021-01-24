try:
    from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice, XBee64BitAddress
    from digi.xbee.io import IOLine, IOMode, IOValue
    import threading

    IO_LINE = IOLine.DIO4_AD4
    IS_MICROPYTHON = False
except ImportError:
    from machine import I2C, Pin
    import xbee

    IO_LINE = None
    IS_MICROPYTHON = True

import light_link
from light_link import OnOffCusterClient, LevelControlClusterClient
import light_link_frame
from xbee_devices import XBEE_PC, XBEE_ARDUINO, XBEE_OTHER
from led import LED, LightStates
import time
import struct


class Transmitter:
    @staticmethod
    def transmit(destination, aps_header, destination_endpoint, cluster):
        if IS_MICROPYTHON:
            xbee.transmit(destination, aps_header,
                          source_ep=0x01, dest_ep=destination_endpoint,
                          cluster=cluster, profile=light_link.PROFILE_ID)
        else:
            device.send_expl_data(remote_xbee_device=destination, data=aps_header,
                                  src_endpoint=0x01, dest_endpoint=destination_endpoint,
                                  cluster_id=cluster, profile_id=light_link.PROFILE_ID)


class ServerCluster:
    @staticmethod
    def set_light(_led, value, time_transition):
        if _led == LED.USER:
            usrLed = Pin("D4", Pin.OUT, value=value)
            light_states.update_light(_led, value)
        else:
            try:
                bytes_to_send = bytearray(LED.to_arduino_command(_led)) + bytearray([value]) + \
                                bytearray(time_transition.to_bytes(2, 'big')) + \
                                bytearray([light_states.get_light_value(_led)])

                print(bytearray(time_transition.to_bytes(2, 'big')),
                      bytearray([light_states.get_light_value(_led)]))

                ack = i2c.writeto(8, bytes_to_send)
                light_states.update_light(_led, value)
            except:
                print("Error while writing to I2C.")

    @staticmethod
    def set_light_on(_led):
        if _led == LED.USER:
            _value = 1
        else:
            _value = 255

        ServerCluster.set_light(_led, _value, 0)

    @staticmethod
    def set_light_off(_led):
        ServerCluster.set_light(_led, 0, 0)

    @staticmethod
    def toggle_light(_led, current_light_value):
        if current_light_value == 0:
            ServerCluster.set_light_on(_led)
        else:
            ServerCluster.set_light_off(_led)


if IS_MICROPYTHON:
    node_id = xbee.atcmd('NI')
else:
    node_id = XBEE_PC.node_id

print(node_id)


if node_id == XBEE_PC.node_id:
    def xbee_pc_user_button_callback():
        while True:
            if device.get_dio_value(IO_LINE) == IOValue.LOW:
                print("User Button pressed")
                aps_header = OnOffCusterClient.toggle()
                Transmitter.transmit(xbee_arduino, aps_header, LED.BLUE, OnOffCusterClient.CLUSTER_ID)
                time.sleep(1)

    def console_get_dim_value():
        while True:
            dim_input = input("$ Dim value? (0-255) ")

            if dim_input.isnumeric() and int(dim_input) in range(0, 255+1):
                transition_input = input("$ Transition time? ") #  (0-65535)

                if transition_input.isnumeric() and int(transition_input) in range(0, 65535+1):
                    return int(dim_input), int(transition_input)
                print("> Invalid Transition time value. Try again.")
            else:
                print("> Invalid dim value. Try again.")

    device = ZigBeeDevice("/dev/ttyUSB0", 9600)
    device.open()
    device.set_io_configuration(IO_LINE, IOMode.DIGITAL_IN)

    xbee_other = RemoteZigBeeDevice(device, XBee64BitAddress.from_hex_string(XBEE_OTHER.addr_64str))
    xbee_arduino = RemoteZigBeeDevice(device, XBee64BitAddress.from_hex_string(XBEE_ARDUINO.addr_64str))

    threading.Thread(target=xbee_pc_user_button_callback).start()

    while True:
        dim_value, time_transition_value, led_id = None, None, None
        controller_input = input("$ Which Controller? (1-3) ")

        if controller_input == "1":
            dim_value, time_transition_value = console_get_dim_value()
            led_id = LED.RED
        elif controller_input == "2":
            dim_value, time_transition_value = console_get_dim_value()
            led_id = LED.GREEN_BLUE
        elif controller_input == "3":
            dim_value, time_transition_value = console_get_dim_value()
            led_id = LED.RED_GREEN_BLUE_WHITE
        elif controller_input == "q":
            print("Quitting")
            break

        if led_id:
            aps_header = LevelControlClusterClient.move_to_level(dim_value, time_transition_value)
            Transmitter.transmit(xbee_arduino, aps_header, led_id, LevelControlClusterClient.CLUSTER_ID)

    device.close()
if node_id == XBEE_ARDUINO.node_id:
    light_states = LightStates([
        LED.RED_GREEN_BLUE_WHITE,
        LED.USER
    ])

    print("Init I2C")
    i2c = I2C(1)
    print(i2c.scan())

    print("Start receiving")
    while True:
        received_msg = xbee.receive()
        if received_msg:
            _, _, _, command_id = light_link_frame.unpack_command_frame(received_msg['payload'])
            led = received_msg['dest_ep']
            print("Received command about LED", LED.to_arduino_command(led))

            if received_msg['cluster'] == OnOffCusterClient.CLUSTER_ID:
                if command_id == OnOffCusterClient.ON:
                    ServerCluster.set_light_on(led)
                elif command_id == OnOffCusterClient.OFF:
                    ServerCluster.set_light_off(led)
                elif command_id == OnOffCusterClient.TOGGLE:
                    ServerCluster.toggle_light(led, light_states.get_light_value(led))
                else:
                    print("Unknown ON/OFF command:", command_id)
            elif received_msg['cluster'] == LevelControlClusterClient.CLUSTER_ID:
                if command_id == LevelControlClusterClient.MOVE_TO_LEVEL:
                    level, transition_time = struct.unpack("BH", received_msg['payload'][-4:])

                    ServerCluster.set_light(led, level, transition_time)
                else:
                    print("Unknown LevelControl command:", command_id)
            else:
                print("Unknown Cluster ID:", received_msg['cluster'])

            print(light_states.light_states)
if node_id == XBEE_OTHER.node_id:
    light_states = LightStates(['u'])
    user_button = Pin("D4", Pin.IN, Pin.PULL_UP)

    while True:
        if user_button.value() == 0:
            print("User Button pressed")

            aps_header = OnOffCusterClient.toggle()
            Transmitter.transmit(XBEE_ARDUINO.addr_64bit, aps_header, LED.RED_GREEN_BLUE_WHITE,
                                 OnOffCusterClient.CLUSTER_ID)
            time.sleep(1)
