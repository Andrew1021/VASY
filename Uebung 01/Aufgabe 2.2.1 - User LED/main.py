import time
import xbee
from machine import Pin

LED_BLINK_STRING = "LED_BLINK="

print("Receiving messages...\n")

dio10 = Pin("P0", Pin.OUT, value=0)

while True:
    msg = xbee.receive()
    if msg:
        print(msg)

        if 'payload' in msg.keys() and msg['payload'].startswith(LED_BLINK_STRING):
            blink_count = msg['payload'][len(LED_BLINK_STRING):]

            if blink_count.isdigit():
                # start blinking
                print("Blinking now %s times!" % blink_count)

                for i in range(int(blink_count)):
                    dio10.value(1)
                    time.sleep(0.5)
                    dio10.value(0)
                    time.sleep(0.5)
            else:
                # passed payload is not a digit
                print("Error: Passed payload '%s' is not a digit." % blink_count)
        print()