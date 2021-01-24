from machine import Pin, PWM


class CarController:
    def __init__(self):
        # Motor A layout
        self.ain1 = Pin("D3", Pin.OUT, value=0)  # AIN1 -> AD3
        self.ain2 = Pin("P2", Pin.OUT, value=0)  # AIN2 -> DIO12
        self.pwma = PWM(Pin(Pin.board.P0, Pin.OUT, value=0))  # PWMA -> PWM0

        # Motor B layout
        self.bin1 = Pin("P9", Pin.OUT, value=0)  # BIN1 -> DIO19
        self.bin2 = Pin("D1", Pin.OUT, value=0)  # BIN2 -> DIO1
        self.pwmb = PWM(Pin(Pin.board.P1, Pin.OUT, value=0))  # PWMB -> PWM1  -  PWM Pin1 muss in XCTU konfiguriert werden!

    def turn(self, is_turning_right, direction_angle):
        if is_turning_right:  # car direction right
            self.bin1.value(1)
            self.bin2.value(0)
            self.pwmb.duty(direction_angle)
        else:  # car direction left
            self.bin1.value(0)
            self.bin2.value(1)
            self.pwmb.duty(direction_angle)

    def accelerate(self, is_forward, speed):
        if is_forward:  # car drive forward
            self.ain1.value(0)
            self.ain2.value(1)
            self.pwma.duty(speed)
        else:  # car drive backward
            self.ain1.value(1)
            self.ain2.value(0)
            self.pwma.duty(speed)

    def brake(self, speed, old_speed):
        print("Brake")
        if speed > 0:  # car brakes at forward drive
            self.ain1.value(1)
            self.ain2.value(0)
            self.pwma.duty(old_speed-speed)
        elif speed < 0:     # car brakes at backward drive
            self.ain1.value(0)
            self.ain2.value(1)
            self.pwma.duty(old_speed+speed)

    def stop(self):
        self.ain1.value(0)
        self.ain2.value(0)
        self.pwma.duty(0)

        self.bin1.value(0)
        self.bin2.value(0)
        self.pwmb.duty(0)
