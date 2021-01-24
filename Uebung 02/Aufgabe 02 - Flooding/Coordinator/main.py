import xbee
import time
import struct


def pack_frame(type_field, source_addr, destination_addr, payload, _id=None):
    if _id is None:
        _id = abs(hash(str(source_addr) + str(destination_addr))) % (10 ** 4)

    networking_header = struct.pack('bhhh', type_field, source_addr, destination_addr, _id)

    return networking_header + payload.encode()


def unpack_frame(_frame):
    type_field, source_addr, destination_addr, _id = struct.unpack('bhhh', _frame[:8])

    return {
        "type_field": type_field,
        "source_addr": source_addr,
        "destination_addr": destination_addr,
        "id": _id,
        "payload": _frame[8:].decode()
    }


def coordinator(dest, message):
    TIMEOUT = 5000
    start_time = 0

    while True:
        time_delta = time.ticks_diff(time.ticks_ms(), start_time)

        if time_delta >= TIMEOUT:
            start_time = time.ticks_ms()
            print("Sending payload: '" + message + "'")

            xbee.transmit(xbee.ADDR_BROADCAST,
                          pack_frame(type_field=False, source_addr=xbee.atcmd("MY"),
                                     destination_addr=dest, payload=message))

        frame = xbee.receive()
        if frame:
            frame = frame['payload']
            unpacked_frame = unpack_frame(frame)

            if unpacked_frame['type_field']:
                print("received ACK:", unpacked_frame)


def endpoint():
    STORAGE = []
    TIMEOUT = 60000
    start_time = time.ticks_ms()

    while True:
        frame = xbee.receive()

        if frame:
            frame = frame['payload']
            unpacked_frame = unpack_frame(frame)
            hashed_frame = hash(frame)

            if unpacked_frame['type_field']:
                # ACK-Frame
                xbee.transmit(xbee.ADDR_BROADCAST, frame)
            else:
                # Flood-Frame
                if unpacked_frame['destination_addr'] == xbee.atcmd("MY"):
                    # Frame arrived at destination-node
                    message_back = unpacked_frame["payload"] + " - [Arrived at EndDevice " + str(xbee.atcmd("MY")) + "]"

                    xbee.transmit(xbee.ADDR_BROADCAST,
                                  pack_frame(True, unpacked_frame["source_addr"], unpacked_frame['destination_addr'],
                                             message_back, unpacked_frame['id']))
                else:
                    # Frame arrived at neighbor-node

                    if hashed_frame not in STORAGE:
                        STORAGE.append(hashed_frame)

                        message_hop = unpacked_frame["payload"] + " - [Hopped on EndDevice " + str(xbee.atcmd("MY")) + "]"

                        xbee.transmit(xbee.ADDR_BROADCAST,
                                      pack_frame(unpacked_frame["type_field"], unpacked_frame["source_addr"],
                                                 unpacked_frame['destination_addr'], message_hop, unpacked_frame['id']))
                    else:
                        # frame already in storage
                        print("Frame already in storage!")

        time_delta = time.ticks_diff(time.ticks_ms(), start_time)

        if time_delta >= TIMEOUT:
            start_time = time.ticks_ms()
            STORAGE.clear()


print()
if xbee.atcmd("MY") == 0:
    print("I'm Coordinator")
    print("----------------------------\n")
    coordinator(1, "Hello")
else:
    print("I'm EndDevice", xbee.atcmd("MY"))
    print("----------------------------\n")
    endpoint()
