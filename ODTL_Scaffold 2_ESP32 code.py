# ESP32 MicroPython code for Horror Game
import machine
import time
import random
from machine import Pin, PWM, UART

# Set up UART communication with laptop
uart = UART(2, baudrate=115200)  # UART2 (TX=GPIO17, RX=GPIO16)
uart.init(115200, bits=8, parity=None, stop=1)

# Set up LED for visual effects (jumpscare)
led_pin = Pin(2, Pin.OUT)  # Onboard LED
led = PWM(led_pin)
led.freq(1000)

# Set up a buzzer for audio effects
buzzer_pin = Pin(5, Pin.OUT)  # Change pin as needed
buzzer = PWM(buzzer_pin)
buzzer.freq(440)  # Initial frequency
buzzer.duty(0)    # Start with buzzer off

# Optional: Set up a relay for controlling external devices
# relay_pin = Pin(13, Pin.OUT)  # Change pin as needed

# Set up ambient light sensor if available
try:
    light_sensor = machine.ADC(machine.Pin(36))  # Change pin as needed
    light_sensor.atten(machine.ADC.ATTN_11DB)  # Full range: 3.3V
    has_light_sensor = True
except:
    has_light_sensor = False

def flash_led():
    """Rapidly flash the LED in a pattern"""
    for i in range(10):
        led.duty(1023)  # Full brightness
        time.sleep(0.05)
        led.duty(0)     # Off
        time.sleep(0.05)

def play_tone(freq, duration):
    """Play a tone on the buzzer"""
    buzzer.freq(freq)
    buzzer.duty(512)  # 50% duty cycle
    time.sleep(duration)
    buzzer.duty(0)    # Turn off

def jumpscare_effect():
    """Create a combined jumpscare effect with LED and buzzer"""
    # Start with rapid LED flashing
    for i in range(5):
        led.duty(1023)
        play_tone(random.randint(800, 2000), 0.1)
        led.duty(0)
        time.sleep(0.05)

    # Finish with sustained tone and light
    led.duty(1023)
    play_tone(1500, 1)

    # Turn everything off
    led.duty(0)
    buzzer.duty(0)

def ambient_effects():
    """Create subtle ambient effects to increase tension"""
    if random.random() < 0.3:  # 30% chance of effect
        effect_type = random.randint(1, 3)

        if effect_type == 1:
            # Subtle LED flicker like a faulty light
            for _ in range(random.randint(2, 5)):
                led.duty(random.randint(100, 300))
                time.sleep(random.uniform(0.05, 0.2))
            led.duty(0)

        elif effect_type == 2:
            # Quiet distant sound
            freq = random.randint(100, 400)
            buzzer.freq(freq)
            buzzer.duty(100)  # Very quiet
            time.sleep(0.3)
            buzzer.duty(0)

        elif effect_type == 3:
            # Quick bright flash
            led.duty(1023)
            time.sleep(0.05)
            led.duty(0)

def read_ambient_light():
    """Read ambient light level if sensor available"""
    if has_light_sensor:
        return light_sensor.read()
    return 0

def main():
    print("ESP32 Horror Game Controller Starting...")
    uart.write("ESP32 ready\n")

    # Initial effect to show it's working
    flash_led()

    try:
        while True:
            # Check for commands from the laptop
            if uart.any():
                cmd = uart.readline()
                if cmd:
                    cmd_str = cmd.decode('utf-8').strip()
                    print("Received:", cmd_str)

                    if "JUMPSCARE" in cmd_str:
                        jumpscare_effect()
                    elif "AMBIENT" in cmd_str:
                        ambient_effects()

            # Random ambient effects
            if random.random() < 0.01:  # 1% chance per loop
                ambient_effects()

            # Optional: Read ambient light and report significant changes
            if has_light_sensor and random.random() < 0.05:  # 5% chance of checking
                light = read_ambient_light()
                uart.write(f"LIGHT:{light}\n")

            time.sleep(0.1)  # Small delay to prevent busy-waiting

    except Exception as e:
        print("Error:", e)
        uart.write(f"ERROR:{e}\n")
    finally:
        # Clean up
        led.duty(0)
        buzzer.duty(0)

if __name__ == "__main__":
    main()
    nigga is dying chat help plz nwnvdjd
