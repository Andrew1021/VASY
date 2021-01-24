class LED:
    RED = 0x01
    GREEN_BLUE = 0x02
    RED_GREEN_BLUE_WHITE = 0x03
    BLUE = 0x04
    USER = 0x05

    @staticmethod
    def to_arduino_command(led):
        led_to_char = {
            LED.RED: 'r',
            LED.GREEN_BLUE: 'g',
            LED.RED_GREEN_BLUE_WHITE: 'b',
            LED.BLUE: 'w',
        }

        return led_to_char[led]

    @staticmethod
    def get_char_list(led):
        led_to_char = {
            LED.RED: ['r'],
            LED.GREEN_BLUE: ['g', 'b'],
            LED.RED_GREEN_BLUE_WHITE: ['r', 'g', 'b', 'w'],
            LED.BLUE: ['b'],
            LED.USER: ['u']
        }

        return led_to_char[led]


class LightStates:
    def __init__(self, lights):
        self.light_states = []

        for light in lights:
            self.add_light(light, 0)

    def add_light(self, _light, _value):
        for led in LED.get_char_list(_light):
            self.light_states.append({
                'light': led,
                'value': _value
            })

    def update_light(self, _light, _value):
        for led in LED.get_char_list(_light):
            for light in self.light_states:
                if light['light'] == led:
                    light['value'] = _value
                    break

    def get_light_value(self, _light):
        for led in LED.get_char_list(_light):
            for light in self.light_states:
                if light['light'] == led:
                    return light['value']
