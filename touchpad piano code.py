from machine import Pin, PWM, TouchPad
import time

# Define buzzer pin
buzzer = PWM(Pin(26))

# Define touch sensor pins
touch_sensors = {
    "C4": TouchPad(Pin(4)),   # GPIO4
    "D4": TouchPad(Pin(2)),   # GPIO2
    "E4": TouchPad(Pin(15)),  # GPIO15
    "F4": TouchPad(Pin(32)),  # GPIO32
    "G4": TouchPad(Pin(33))   # GPIO33
}

# Frequency map for notes
notes = {
    "C4": 261,  # Frequency for C4
    "D4": 294,  # Frequency for D4
    "E4": 329,  # Frequency for E4
    "F4": 349,  # Frequency for F4
    "G4": 392   # Frequency for G4
}

# Threshold value for touch sensors (calibrate as needed)
threshold = 150

# Function to play a note
def play_note(note):
    if note in notes:
        buzzer.freq(notes[note])  # Set the frequency for the note
        buzzer.duty(512)          # Set duty cycle (50%)
        time.sleep(0.5)           # Play the note for 0.5 seconds
        buzzer.duty(0)            # Stop the buzzer
    else:
        print(f"Note {note} not found!")

# Main loop
try:
    while True:
        for note, touch in touch_sensors.items():
            touch_value = touch.read()
            if touch_value < threshold:  # If touch detected
                print(f"Playing {note}, Touch Value: {touch_value}")
                play_note(note)
                time.sleep(0.1)  # Short delay to debounce
except KeyboardInterrupt:
    print("Stopping...")
    buzzer.deinit()
# Write your code here :-)
