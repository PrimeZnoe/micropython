import time
from machine import Pin

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        # Trigger- und Echo-Pins einrichten
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        
    def measure_distance(self):
        # Trigger-Puls senden
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()

        # Echo-Zeit messen
        while self.echo.value() == 0:
            signal_off = time.ticks_us()
        while self.echo.value() == 1:
            signal_on = time.ticks_us()

        # Zeitdifferenz und Entfernung berechnen
        time_passed = time.ticks_diff(signal_on, signal_off)
        distance_cm = (time_passed * 0.0343) / 2

        return distance_cm

# Beispiel für die Nutzung:
# Sensor erstellen und Pins anpassen
sensor = UltrasonicSensor(trig_pin=16, echo_pin=17)

while True:
    dist = sensor.measure_distance()
    print("Entfernung: {:.2f} cm".format(dist))
    time.sleep(1)
