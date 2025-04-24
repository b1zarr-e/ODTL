import sounddevice as sd
import queue
import sys
import json
import requests
from vosk import Model, KaldiRecognizer

# ESP32 Wi-Fi connection info - replace with your ESP32's IP address
ESP32_IP = '192.168.4.1'  
ESP32_URL = f"http://{ESP32_IP}/control"

# Path to your downloaded Vosk model
model_path = 'vosk-model-small-en-us-0.15'
sample_rate = 16000
q = queue.Queue()

# Audio callback - required by sounddevice
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# Load the model and start recognition
model = Model(model_path)
recognizer = KaldiRecognizer(model, sample_rate)

# Start audio stream
with sd.RawInputStream(samplerate=sample_rate, blocksize=8000, dtype='int16',
                      channels=1, callback=callback):
    print("Listening for command... (Ctrl+C to stop)")
    
    try:
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get("text", "")
                
                if text:
                    print("You said:", text)
                    
                    # Send command to ESP32 if "light" is detected
                    if "expand" in text.lower():
                        print("Sending command to ESP32...")
                        try:
                            response = requests.get(f"{ESP32_URL}?command=LIGHT_ON", timeout=5)
                            print(f"ESP32 response: {response.text} (Status: {response.status_code})")
                        except Exception as e:
                            print(f"Error communicating with ESP32: {e}")

                    elif "contract" in text.lower() or "contact" in text.lower():
                        print("Sending command to ESP32...")
                        try:
                            response = requests.get(f"{ESP32_URL}?command=LIGHT_OFF", timeout=5)
                            print(f"ESP32 response: {response.text} (Status: {response.status_code})")
                        except Exception as e:
                            print(f"Error communicating with ESP32: {e}")

                    elif "exit" in text.lower():
                        print("Sending command to ESP32...")
                        try:
                            response = requests.get(f"{ESP32_URL}?command=LIGHT_HOLD", timeout=5)
                            print(f"ESP32 response: {response.text} (Status: {response.status_code})")
                        except Exception as e:
                            print(f"Error communicating with ESP32: {e}")

                    elif "left" in text.lower():
                        print("Sending command to ESP32...")
                        try:
                            response = requests.get(f"{ESP32_URL}?command=MOVE_LEFT", timeout=5)
                            print(f"ESP32 response: {response.text} (Status: {response.status_code})")
                        except Exception as e:
                            print(f"Error communicating with ESP32: {e}")

                    elif "right" in text.lower():
                        print("Sending command to ESP32...")
                        try:
                            response = requests.get(f"{ESP32_URL}?command=MOVE_RIGHT", timeout=5)
                            print(f"ESP32 response: {response.text} (Status: {response.status_code})")
                        except Exception as e:
                            print(f"Error communicating with ESP32: {e}")
                    elif "middle" in text.lower():
                        print("Sending command to ESP32...")
                        try:
                            response = requests.get(f"{ESP32_URL}?command=MOVE_MID", timeout=5)
                            print(f"ESP32 response: {response.text} (Status: {response.status_code})")
                        except Exception as e:
                            print(f"Error communicating with ESP32: {e}")
                        
    except KeyboardInterrupt:
        print("\nProgram stopped")
