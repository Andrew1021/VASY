import light_link_frame
import struct

PROFILE_ID = 0xC05E


class OnOffCusterClient:
    CLUSTER_ID = 0x0006

    # COMMANDS
    OFF = 0x00
    ON = 0x01
    TOGGLE = 0x02

    @staticmethod
    def off():
        return light_link_frame.pack_command_frame(OnOffCusterClient.OFF)

    @staticmethod
    def on():
        return light_link_frame.pack_command_frame(OnOffCusterClient.ON)

    @staticmethod
    def toggle():
        return light_link_frame.pack_command_frame(OnOffCusterClient.TOGGLE)


class LevelControlClusterClient:
    CLUSTER_ID = 0x0008

    # COMMANDS
    MOVE_TO_LEVEL = 0x00
    MOVE = 0x01
    STEP = 0x02
    STOP = 0x03
    MOVE_TO_LEVEL_WITH_ON_OFF = 0x04
    MOVE_WITH_ON_OFF = 0x05
    STEP_WITH_ON_OFF = 0x06

    # PAYLOAD FIELD VALUES
    UP = 0x00
    DOWN = 0x01

    @staticmethod
    def move_to_level(level, transition_time):
        zcl_payload = struct.pack("BH", level, transition_time)

        return light_link_frame.pack_command_frame(LevelControlClusterClient.MOVE_TO_LEVEL) + zcl_payload

    @staticmethod
    def move(move_mode, rate):
        assert move_mode in (LevelControlClusterClient.UP, LevelControlClusterClient.DOWN)
        zcl_payload = struct.pack("BB", move_mode, rate)

        return light_link_frame.pack_command_frame(LevelControlClusterClient.MOVE) + zcl_payload

    @staticmethod
    def step(step_mode, step_size, transition_time):
        assert step_mode in (LevelControlClusterClient.UP, LevelControlClusterClient.DOWN)
        zcl_payload = struct.pack("BBH", step_mode, step_size, transition_time)

        return light_link_frame.pack_command_frame(LevelControlClusterClient.STEP) + zcl_payload

    @staticmethod
    def stop():
        return light_link_frame.pack_command_frame(LevelControlClusterClient.STOP)

    @staticmethod
    def move_to_level_with_on_off(level, transition_time):
        zcl_payload = struct.pack("BH", level, transition_time)

        return light_link_frame.pack_command_frame(LevelControlClusterClient.MOVE_TO_LEVEL_WITH_ON_OFF) + zcl_payload

    @staticmethod
    def move_with_on_off(move_mode, rate):
        assert move_mode in (LevelControlClusterClient.UP, LevelControlClusterClient.DOWN)
        zcl_payload = struct.pack("BB", move_mode, rate)

        return light_link_frame.pack_command_frame(LevelControlClusterClient.MOVE_WITH_ON_OFF) + zcl_payload

    @staticmethod
    def step_with_on_off(step_mode, step_size, transition_time):
        assert step_mode in (LevelControlClusterClient.UP, LevelControlClusterClient.DOWN)
        zcl_payload = struct.pack("BBH", step_mode, step_size, transition_time)

        return light_link_frame.pack_command_frame(LevelControlClusterClient.STEP_WITH_ON_OFF) + zcl_payload
