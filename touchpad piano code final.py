from machine import Pin, PWM, TouchPad
import time

# Define buzzer pin
buzzer = PWM(Pin(26))

# Define touch sensor pins (ensure these are valid touch-capable pins)
touch_sensors = {
    "C4": TouchPad(Pin(4)),   # GPIO4
    "D4": TouchPad(Pin(32)),  # GPIO32
    "E4": TouchPad(Pin(33)),  # GPIO33
    "F4": TouchPad(Pin(27)),  # GPIO27
    "G4": TouchPad(Pin(14)),  # GPIO14
    "A4": TouchPad(Pin(12)),  # GPIO12
    "B4": TouchPad(Pin(13)),  # GPIO13
    "C5": TouchPad(Pin(15))   # GPIO15
}

# Frequency map for notes
notes = {
    "C4": 261,  # Frequency for C4
    "D4": 294,  # Frequency for D4
    "E4": 329,  # Frequency for E4
    "F4": 349,  # Frequency for F4
    "G4": 392,  # Frequency for G4
    "A4": 440,  # Frequency for A4
    "B4": 494,  # Frequency for B4
    "C5": 523   # Frequency for C5
}

# Threshold value for touch sensors
threshold = 150

# Function to play a note
def play_note(note):
    if note in notes:
        buzzer.freq(notes[note])  # Set the frequency for the note
        buzzer.duty(256)          # Set duty cycle (25%)
        time.sleep(0.2)           # Play the note for 0.5 seconds
        buzzer.duty(0)            # Stop the buzzer
    else:
        print(f"Note {note} not found!")

# Main loop
last_note = None
try:
    print("Starting Touch-Controlled Piano...")
    while True:
        for note, touch in touch_sensors.items():
            try:
                touch_value = touch.read()  # Read the touch sensor value
                print(f"Touch Value for {note}: {touch_value}")  # Debugging output
                if touch_value < threshold and last_note != note:
                    print(f"Playing {note}")
                    play_note(note)
                    last_note = note
                    time.sleep(0.1)  # Short delay to debounce
                elif touch_value >= threshold and last_note == note:
                    last_note = None  # Reset when touch is released
            except Exception as e:
                print(f"Error with touch sensor for {note}: {e}")
except KeyboardInterrupt:
    print("Stopping...")
    buzzer.deinit()
# Write your code here :-)
