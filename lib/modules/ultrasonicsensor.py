import time
from machine import Pin

class DistanceSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trigger.low()

    def get_distance(self):
        self.trigger.low()
        time.sleep_us(2)
        self.trigger.high()
        time.sleep_us(10)
        self.trigger.low()

        pulse_start = 0
        pulse_end = 0
        while self.echo.value() == 0:
            pulse_start = time.ticks_us()
        while self.echo.value() == 1:
            pulse_end = time.ticks_us()

        duration = time.ticks_diff(pulse_end, pulse_start)
        distance = (duration * 0.0343) / 2

        return distance

    def safe_measurement(self):
        try:
            distance = self.get_distance()
            if 0 < distance < 400:
                return distance
            else:
                return -1
        except Exception as e:
            return -1