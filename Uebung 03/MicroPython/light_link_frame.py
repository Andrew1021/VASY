import struct


def pack_command_frame(command_id, frame_control=0, transaction_sequence_number=0, manufacturer_code=0):
    return struct.pack("BHBB", frame_control, manufacturer_code, transaction_sequence_number, command_id)


def unpack_command_frame(frame):
    command_frame = frame[:6]

    frame_control, manufacturer_code, transaction_sequence_number, command_id = struct.unpack("BHBB", command_frame)

    return frame_control, manufacturer_code, transaction_sequence_number, command_id
