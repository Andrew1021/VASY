import time

from digi.xbee.devices import XBeeDevice
from digi.xbee.io import IOLine, IOMode, IOValue

LED_BLINK_STRING = "LED_BLINK="

coordinator = XBeeDevice("/dev/ttyUSB2", 9600)
coordinator.open()

# led = IOLine.DIO4_AD4
#
# coordinator.set_io_configuration(led, IOMode.DIGITAL_IN)
# coordinator.set_io_configuration(led, IOMode.DIGITAL_OUT_LOW)

while True:
    response = coordinator.read_data()

    if response:
        msg = response.data.decode()

        if msg.startswith(LED_BLINK_STRING):
            blink_count = msg[len(LED_BLINK_STRING):]

            if blink_count.isdigit():
                # start blinking
                print("Blinking now %s times!" % blink_count)

                for i in range(int(blink_count)):
                    # coordinator.set_dio_value(led, IOValue.LOW)
                    coordinator.set_parameter('D4', bytearray([4]))
                    time.sleep(0.5)
                    # coordinator.set_dio_value(led, IOValue.HIGH)
                    coordinator.set_parameter('D4', bytearray([5]))
                    time.sleep(0.5)
            else:
                # passed payload is not a digit
                print("Error: Passed payload '%s' is not a digit." % blink_count)
        print()
