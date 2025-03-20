import random
import time
import cv2
import pyaudio
import numpy as np
import wave
import pygame
import serial
import threading
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk
import os

class HorrorGame:
    def __init__(self, serial_port='/dev/ttyUSB0', baud_rate=115200):
        # Initialize serial connection to ESP32
        try:
            self.ser = serial.Serial(serial_port, baud_rate, timeout=1)
            print("Connected to ESP32")
        except Exception as e:
            print(f"Failed to connect to ESP32: {e}")
            print("Running in standalone mode")
            self.ser = None
            
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Questions bank with flags for special questions and answer options
        self.questions = [
            {
                "text": "Do you remember locking your door tonight?", 
                "special": False,
                "options": ["Yes", "No"]
            },
            {
                "text": "Can you hear that noise?", 
                "special": False,
                "options": ["Yes", "What noise?"]
            },
            {
                "text": "Have you noticed the shadows moving?", 
                "special": False,
                "options": ["Yes", "No"]
            },
            {
                "text": "Are you alone?", 
                "special": True, 
                "trigger": "camera",
                "warning": "H I D E"
            },
            {
                "text": "Do you feel like you're being watched?", 
                "special": True, 
                "trigger": "camera",
                "warning": "H I D E"
            },
            {
                "text": "Did you hear that whisper?", 
                "special": True, 
                "trigger": "microphone",
                "options": ["Yes", "IT CAN HEAR YOU"]
            },
            {
                "text": "Was that a footstep behind you?", 
                "special": True, 
                "trigger": "microphone",
                "options": ["Yes", "IT CAN HEAR YOU"]
            },
            {
                "text": "Do you believe in ghosts?", 
                "special": False,
                "options": ["Yes", "No"]
            },
            {
                "text": "Would you know if something followed you home?", 
                "special": False,
                "options": ["Yes", "No"]
            },
            {
                "text": "Can you feel the temperature dropping?", 
                "special": False,
                "options": ["Yes", "No"]
            },
            {
                "text": "What's that standing in the corner of your room?", 
                "special": True, 
                "trigger": "camera",
                "warning": "D O N ' T  M O V E"
            },
            {
                "text": "Did you catch that shadow moving?", 
                "special": True, 
                "trigger": "microphone",
                "options": ["Yes", "IT CAN HEAR YOU"]
            },
        ]
        
        # Jumpscare resources
        self.jumpscare_image_path = 'jumpscare.png'  # Replace with your image
        self.jumpscare_sound = 'screeching-sound-effect-312866.mp3'  # Replace with your sound file
        
        # Initialize tkinter for fullscreen jumpscare
        self.root = None
        self.tk_thread = None
        
        # Audio detection settings
        self.audio_threshold = 1000  # Adjust based on testing
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        
        # Video detection settings
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Game state
        self.running = False
        self.current_question = None
        self.user_choice = None
        
    def start_game(self):
        """Start the horror game"""
        self.running = True
        print("\n" + "="*50)
        print("HORROR GAME INITIATED")
        print("="*50 + "\n")
        time.sleep(2)
        print("The game will ask you questions...")
        time.sleep(1)
        print("Answer truthfully... or else.")
        time.sleep(2)
        
        try:
            # Create a shuffled copy of questions to go through
            game_questions = random.sample(self.questions, len(self.questions))
            
            for question in game_questions:
                if not self.running:
                    break
                    
                self.current_question = question
                
                # Display the question with a slow typing effect
                self.type_text(self.current_question["text"])
                
                # Handle the question based on its type
                if self.current_question["special"]:
                    if self.current_question["trigger"] == "camera":
                        self.handle_camera_question()
                    elif self.current_question["trigger"] == "microphone":
                        self.handle_microphone_question()
                else:
                    self.handle_normal_question()
                
                # Wait between questions
                time.sleep(random.uniform(2, 4))
                
        except KeyboardInterrupt:
            print("\nGame terminated by user")
        finally:
            self.cleanup()
    
    def type_text(self, text):
        """Display text with creepy typing effect"""
        print("\n")
        for char in text:
            print(char, end='', flush=True)
            time.sleep(random.uniform(0.05, 0.15))
        print("\n")
    
    def handle_normal_question(self):
        """Handle a normal question with yes/no options"""
        options = self.current_question.get("options", ["Yes", "No"])
        
        # Display options
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        # Get user choice
        while True:
            try:
                choice = input("\nEnter your choice (1 or 2): ")
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    self.user_choice = options[choice_num - 1]
                    print(f"You chose: {self.user_choice}")
                    break
                else:
                    print(f"Please enter a number between 1 and {len(options)}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def handle_camera_question(self):
        """Handle a camera-based question"""
        print("\nPress Enter to continue...")
        input()
        
        # Display warning
        warning = self.current_question.get("warning", "H I D E")
        self.type_text(warning)
        
        # Start camera in a separate thread
        camera_thread = threading.Thread(target=self._camera_check)
        camera_thread.daemon = True
        camera_thread.start()
        
        # Wait for detection period
        time.sleep(3)  # 3 second window to hide
    
    def handle_microphone_question(self):
        """Handle a microphone-based question"""
        options = self.current_question.get("options", ["Yes", "IT CAN HEAR YOU"])
        
        # Display options
        for option in options:
            print(f"- {option}")
        
        print("\nListening...")
        
        # Start listening in a separate thread
        mic_thread = threading.Thread(target=self._listen_for_sound)
        mic_thread.daemon = True
        mic_thread.start()
        
        # Wait for detection period
        time.sleep(3)  # 3 second window of silence
    
    def _camera_check(self):
        """Internal method to check camera feed for faces"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Could not open camera")
            return
            
        # Check for 3 seconds
        end_time = time.time() + 3
        detected = False
        
        while time.time() < end_time and not detected:
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # If face detected, trigger jumpscare
            if len(faces) > 0:
                detected = True
                self.trigger_jumpscare("I SEE YOU")
        
        # Release the camera
        cap.release()
    
    def _listen_for_sound(self):
        """Internal method to listen for sounds above threshold"""
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        # Listen for 3 seconds
        end_time = time.time() + 3
        detected = False
        
        while time.time() < end_time and not detected:
            data = np.frombuffer(stream.read(self.chunk), dtype=np.int16)
            if np.abs(data).mean() > self.audio_threshold:
                detected = True
                self.trigger_jumpscare("I HEARD YOU")
        
        # Close the stream
        stream.stop_stream()
        stream.close()
    
    def trigger_jumpscare(self, message):
        """Display jumpscare image and play sound"""
        # Log the jumpscare event
        print(f"\n!!! JUMPSCARE TRIGGERED: {message} !!!")
        
        # Notify ESP32 if connected
        if self.ser:
            self.ser.write(b'JUMPSCARE\n')
        
        # Play jumpscare sound in a separate thread
        sound_thread = threading.Thread(target=self._play_jumpscare_sound)
        sound_thread.daemon = True
        sound_thread.start()
        
        # Display jumpscare image using tkinter for guaranteed fullscreen
        if self.tk_thread and self.tk_thread.is_alive():
            # Don't create a new window if one is already active
            return
            
        self.tk_thread = threading.Thread(target=self._show_fullscreen_jumpscare, args=(message,))
        self.tk_thread.daemon = True
        self.tk_thread.start()
        
        # Wait for jumpscare window to close
        if self.tk_thread:
            self.tk_thread.join(timeout=2.5)  # Wait up to 2.5 seconds
        
    def _play_jumpscare_sound(self):
        """Play jumpscare sound"""
        try:
            pygame.mixer.music.load(self.jumpscare_sound)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing jumpscare sound: {e}")
    
    def _show_fullscreen_jumpscare(self, message):
        """Show jumpscare image in fullscreen mode using tkinter"""
        try:
            # Create a new tkinter window
            root = tk.Tk()
            root.attributes('-fullscreen', True)  # Make it fullscreen
            root.attributes('-topmost', True)  # Make it appear on top of all windows
            root.overrideredirect(True)  # Remove window decorations
            
            # Load jumpscare image
            if os.path.exists(self.jumpscare_image_path):
                # Get screen dimensions
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                
                # Load and resize the image to fit the screen
                image = Image.open(self.jumpscare_image_path)
                image = image.resize((screen_width, screen_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Create a label with the image
                label = tk.Label(root, image=photo)
                label.image = photo  # Keep a reference to prevent garbage collection
                label.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                print(f"Jumpscare image not found: {self.jumpscare_image_path}")
                
                # Create a plain black screen with text if image is missing
                label = tk.Label(root, text=message, font=("Arial", 72), fg="red", bg="black")
                label.place(relx=0.5, rely=0.5, anchor='center')
            
            # Function to close the window after 2 seconds
            def close_window():
                root.destroy()
                
            # Schedule window to close after 2 seconds
            root.after(2000, close_window)
            
            # Start the main loop
            root.mainloop()
                
        except Exception as e:
            print(f"Error displaying jumpscare: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        # Close serial connection if open
        if self.ser:
            self.ser.close()
            
        # Terminate audio
        self.audio.terminate()
        
        # Close any OpenCV windows
        cv2.destroyAllWindows()
        
        # Note: We don't check the root window here anymore
        # Instead, we let each tk window clean itself up
        print("\nThe game has ended...or has it?")

if __name__ == "__main__":
    # Adjust the serial port based on your system
    # Windows: 'COM3' (or other COM port)
    # Linux: '/dev/ttyUSB0' or '/dev/ttyACM0'
    # Mac: '/dev/cu.usbserial-*'
    
    serial_port = '/dev/ttyUSB0'  # Change this to match your ESP32 connection
    
    game = HorrorGame(serial_port=serial_port)
    game.start_game()
