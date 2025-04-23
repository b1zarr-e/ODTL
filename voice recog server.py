import socket
import speech_recognition as sr
import struct
import numpy as np
import wave
import io
import os
import time
import traceback

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000       # Port to listen on
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2  # 16-bit audio

# Create debug directory if it doesn't exist
DEBUG_DIR = "audio_debug"
os.makedirs(DEBUG_DIR, exist_ok=True)

def save_debug_audio(audio_data, filename):
    """Save audio data to WAV file for debugging"""
    filepath = os.path.join(DEBUG_DIR, filename)
    
    # Convert from int16 to bytes if needed
    if isinstance(audio_data[0], int):
        byte_data = b''.join(struct.pack('<h', sample) for sample in audio_data)
    else:
        byte_data = audio_data
    
    # Create WAV file
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(SAMPLE_WIDTH)  # 16-bit
        wf.setframerate(SAMPLE_RATE)  # Sample rate
        wf.writeframes(byte_data)
    
    print(f"Debug audio saved to {filepath}")
    return filepath

def process_audio(audio_data):
    """Process audio data with multiple recognition methods"""
    print(f"Processing {len(audio_data)} bytes of audio...")
    
    # Save raw audio for debugging
    timestamp = int(time.time())
    save_debug_audio(audio_data, f"raw_audio_{timestamp}.wav")
    
    # Convert bytes to int16 array if needed
    if not isinstance(audio_data[0], int):
        # If we have bytes, convert to int16 array
        int_data = []
        for i in range(0, len(audio_data), 2):
            if i+1 < len(audio_data):
                sample = struct.unpack('<h', audio_data[i:i+2])[0]
                int_data.append(sample)
        audio_data = int_data
    
    # Normalize audio (adjust volume)
    max_val = max(abs(x) for x in audio_data)
    if max_val > 0:
        scale_factor = 32767 / max_val  # Scale to full 16-bit range
        audio_data = [int(x * scale_factor) for x in audio_data]
    
    # Convert back to bytes for AudioData
    byte_data = b''.join(struct.pack('<h', sample) for sample in audio_data)
    
    # Save processed audio for debugging
    save_debug_audio(byte_data, f"processed_audio_{timestamp}.wav")
    
    # Create recognizer
    recognizer = sr.Recognizer()
    
    # Try multiple recognition systems
    results = []
    
    # Create AudioData object from processed audio
    audio = sr.AudioData(byte_data, SAMPLE_RATE, SAMPLE_WIDTH)
    
    # Try Google speech recognition
    try:
        text = recognizer.recognize_google(audio)
        results.append(f"Google: {text}")
    except sr.UnknownValueError:
        results.append("Google: Could not understand audio")
    except sr.RequestError as e:
        results.append(f"Google error: {e}")
    
    # Try Sphinx (offline) if available
    try:
        text = recognizer.recognize_sphinx(audio)
        results.append(f"Sphinx: {text}")
    except sr.UnknownValueError:
        results.append("Sphinx: Could not understand audio")
    except (sr.RequestError, AttributeError) as e:
        results.append(f"Sphinx not available: {e}")
    
    # Join all results
    full_result = " | ".join(results)
    print(f"Recognition results: {full_result}")
    
    # Extract the best result
    for result in results:
        if ":" in result and "Could not understand" not in result and "error" not in result:
            best_result = result.split(":", 1)[1].strip()
            return best_result
    
    return "Could not understand audio"

def main():
    # Create socket server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        
        print(f"Server listening on {HOST}:{PORT}...")
        print(f"Local IP: {socket.gethostbyname(socket.gethostname())}")
        
        while True:
            print("Waiting for connection...")
            # Wait for a connection
            client_socket, client_address = server_socket.accept()
            print(f"Connected to {client_address}")
            
            try:
                # Set a timeout on client socket
                client_socket.settimeout(10)  
                
                # Receive the data size first (4 bytes)
                size_bytes = client_socket.recv(4)
                if not size_bytes:
                    print("No data received")
                    continue
                    
                data_size = struct.unpack('>I', size_bytes)[0]
                print(f"Expecting {data_size} bytes of audio data")
                
                # Now receive the actual audio data
                audio_data = b''
                bytes_received = 0
                
                while bytes_received < data_size:
                    chunk = client_socket.recv(min(1024, data_size - bytes_received))
                    if not chunk:
                        break
                    audio_data += chunk
                    bytes_received += len(chunk)
                    print(f"Received {bytes_received}/{data_size} bytes")
                
                # Process the audio and get text
                text = process_audio(audio_data)
                print(f"Recognized: {text}")
                
                # Send result back to client
                client_socket.sendall(text.encode('utf-8'))
                
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                try:
                    client_socket.sendall("Error processing audio".encode('utf-8'))
                except:
                    pass
            finally:
                print("Closing client connection")
                client_socket.close()
    
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
