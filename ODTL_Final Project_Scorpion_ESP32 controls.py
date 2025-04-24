import machine
import time
import math

class Servo:
    def __init__(self,pin_id,min_us=544.0,max_us=2400.0,min_deg=0.0,max_deg=180.0,freq=50):
        self.pwm = machine.PWM(machine.Pin(pin_id))
        self.pwm.freq(freq)
        self.current_us = 0.0
        self._slope = (min_us-max_us)/(math.radians(min_deg)-math.radians(max_deg))
        self._offset = min_us

    def write(self,deg):
        self.write_rad(math.radians(deg))

    def read(self):
        return math.degrees(self.read_rad())

    def write_rad(self,rad):
        self.write_us(rad*self._slope+self._offset)

    def read_rad(self):
        return (self.current_us-self._offset)/self._slope

    def write_us(self,us):
        self.current_us=us
        self.pwm.duty_ns(int(self.current_us*1000.0))

    def read_us(self):
        return self.current_us

    def off(self):
        self.pwm.duty_ns(0)


class SRControl:
    def __init__(self, data_pin, clock_pin, latch_pin, oe_pin, num_chips=1):
        """
        Initialize the 74HC595 shift register class.

        Args:
            data_pin (int): GPIO pin connected to the Data Input (DS) pin.
            clock_pin (int): GPIO pin connected to the Clock (SHCP) pin.
            latch_pin (int): GPIO pin connected to the Latch (STCP) pin.
            oe_pin (int): GPIO pin connected to the Output Enable pin.
            num_chips (int): Number of daisy-chained 74HC595 chips.
        """
        self.data = machine.Pin(data_pin, machine.Pin.OUT)
        self.clock = machine.Pin(clock_pin, machine.Pin.OUT)
        self.latch = machine.Pin(latch_pin, machine.Pin.OUT)
        self.oepin = machine.Pin(oe_pin, machine.Pin.OUT)

        # Initialize pins to low state
        self.data.value(0)
        self.clock.value(0)
        self.latch.value(0)
        self.oepin.value(1)

        self.num_chips = num_chips
        self.state = [0x00] * num_chips  # Current state of all shift registers

    def _pulse(self, pin):
        """Generate a pulse on the specified pin."""
        pin.value(1)
        time.sleep_ms(1)
        pin.value(0)
        time.sleep_ms(1)  # Small delay for stability

    def _shift_out(self):
        """
        Shift out the states of all daisy-chained 74HC595 chips.
        """
        for byte in reversed(self.state):
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                self.data.value(bit)
                self._pulse(self.clock)

    def update(self):
        """
        Latch and update the outputs of the shift register.
        """
        print(self.state)
        self.oepin.value(1)  # Disable output while updating
        self._shift_out()
        self._pulse(self.latch)  # Latch the data
        self.oepin.value(0)  # Enable output

    def set_relays(self, chip_index, low_nibble, duration=None):
        """
        Update the relays connected to a specific chip's low nibble.

        Args:
            chip_index (int): The index of the chip to update (0-based).
            low_nibble (int): The lower 4 bits (0-15) controlling relays.
                Bits 0 and 1 will turn on together and are mutually exclusive to bits 2 and 3.
            duration (int, optional): Time in seconds to keep the relays on. If None, relays remain on indefinitely.
        """
        if chip_index < 0 or chip_index >= self.num_chips:
            raise ValueError("Invalid chip index.")

        if low_nibble & 0b0011 and low_nibble & 0b1100:
            raise ValueError("Bits 0 and 1 cannot be active simultaneously with bits 2 and 3.")

        # Ensure only the lower nibble is considered
        low_nibble &= 0x0F

        # Update the state for the specified chip
        self.state[chip_index] = (self.state[chip_index] & 0xF0) | low_nibble

        self.update()

        if duration:
            time.sleep(duration)
            self.hold(chip_index)  # Turn off all relays for the specified chip after the duration

    def inflate(self, chip_index):
        """
        Activate relays 0 and 1 on the specified chip to turn on inflation for 15 seconds.
        """
        self.set_relays(chip_index, 0b0011)

    def deflate(self, chip_index):
        """
        Activate relays 2 and 3 on the specified chip to turn on deflation for 15 seconds.
        """
        self.set_relays(chip_index, 0b1100)

    def hold(self, chip_index=None):
        """
        Turn off all relays for a specific chip or all chips.

        Args:
            chip_index (int, optional): The index of the chip to hold. If None, all chips are held.
        """
        if chip_index is None:
            self.state = [0x00] * self.num_chips
        else:
            if chip_index < 0 or chip_index >= self.num_chips:
                raise ValueError("Invalid chip index.")
            self.state[chip_index] = 0x00
        self.update()

import network
import socket
from machine import Pin
import neopixel as np

# Set up LED on GPIO2 (built-in LED on most ESP32 boards)
led = Pin(2, Pin.OUT)
led.off()

# Create an access point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32AP', password='123')  # At least 8 characters

# Wait for AP to be active
while not ap.active():
    time.sleep(0.1)

ip = ap.ifconfig()[0]
print('Access Point active')
print('IP address:', ip)

# Set up web server
addr = socket.getaddrinfo(ip, 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Web server started on http://{}:80'.format(ip))

# Main loop
src = SRControl(25, 33, 32, 23)
servo = Servo(pin_id=12)
np_pin = 13
num_leds = 9
neo = np.NeoPixel(Pin(np_pin), num_leds)
while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        # Extract command from the request
        response = 'Unknown command'
        if 'GET /control?command=LIGHT_ON' in request:
            src.inflate(0)
            for i in range(num_leds):
                neo[i] = (255, 0, 0)
                neo.write()
                time.sleep_ms(10)
            response = 'Scorpion arm engaged'
            print(response)
        elif 'GET /control?command=LIGHT_OFF' in request:
            src.deflate(0)
            for i in range (num_leds):
                neo[i] = (0, 255, 0)
                neo.write()
                time.sleep_ms(10)
            response = 'Scorpion arm disengaged'
            print(response)
        elif 'GET /control?command=LIGHT_HOLD' in request:
            src.hold(0)
            for i in range(num_leds):
                neo[i] = (255, 92, 0)
                neo.write()
                time.sleep_ms(10)
            response = 'Holding'
            print(response)
        elif 'GET /control?command=MOVE_LEFT' in request:
            servo.write(180)
            for i in range(num_leds):
                neo[i] = (255, 0, 200)
                neo.write()
                time.sleep_ms(10)
            response = 'Moved left'
            print(response)
        elif 'GET /control?command=MOVE_RIGHT' in request:
            servo.write(0)
            for i in range(num_leds):
                neo[i] = (255, 0, 200)
                neo.write()
                time.sleep_ms(10)
            response = 'Moved right'
            print (response)
        elif 'GET /control?command=MOVE_MID' in request:
            servo.write(90)
            response = 'Moved to the middle'
            print(response)

        # Send HTTP response
        cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n')
        cl.send(response)
        cl.close()

    except Exception as e:
        print('Error:', e)
        try:
            cl.close()
        except:
            pass
