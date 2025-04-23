import machine
import time
import network
import socket
from array import array

# I2S and WiFi configuration
SCK_PIN = 32
WS_PIN = 25
SD_PIN = 33
SAMPLE_RATE = 16000
BITS_PER_SAMPLE = 16
BUFFER_LENGTH_IN_BYTES = 4096  # Larger buffer for better audio

# WiFi credentials
WIFI_SSID = "wifi ssid"
WIFI_PASSWORD = "wifi password"

# Server details
SERVER_IP = "ip address"  # Make sure this is correct
SERVER_PORT = 5000
SOCKET_TIMEOUT = 10  # Socket timeout in seconds

# Initialize I2S for the INMP441
i2s = machine.I2S(
    0,                      # I2S peripheral number
    sck=machine.Pin(SCK_PIN),
    ws=machine.Pin(WS_PIN),
    sd=machine.Pin(SD_PIN),
    mode=machine.I2S.RX,
    bits=BITS_PER_SAMPLE,
    format=machine.I2S.MONO,
    rate=SAMPLE_RATE,
    ibuf=BUFFER_LENGTH_IN_BYTES
)

# Create an audio buffer
audio_buffer = array('h', [0] * (BUFFER_LENGTH_IN_BYTES // 2))

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"Connecting to {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        max_wait = 20
        while max_wait > 0 and not wlan.isconnected():
            max_wait -= 1
            print("Waiting for connection...")
            time.sleep(1)

    if wlan.isconnected():
        print("Connected to WiFi")
        print(f"Network config: {wlan.ifconfig()}")
        return True
    else:
        print("Failed to connect to WiFi")
        return False

def record_audio(duration_ms=2000):
    """Record audio for a specified duration"""
    print(f"Recording audio for {duration_ms}ms...")

    # Calculate buffer size needed for the duration
    num_samples = (SAMPLE_RATE * duration_ms) // 1000

    # Create a buffer big enough for the full recording
    # Use a list of smaller arrays to avoid memory issues
    chunks = []
    samples_recorded = 0

    # Record until we have enough samples
    start_time = time.ticks_ms()
    while samples_recorded < num_samples:
        # Read a chunk of audio
        try:
            num_bytes_read = i2s.readinto(audio_buffer)
            if num_bytes_read > 0:
                # Store a copy of the buffer
                chunk = array('h', audio_buffer)
                chunks.append(chunk)
                samples_recorded += len(audio_buffer)

                # Print recording progress
                elapsed = time.ticks_ms() - start_time
                print(f"Recording: {elapsed}ms / {duration_ms}ms")
            else:
                print("No audio data read")
                time.sleep(0.01)
        except Exception as e:
            print(f"Error reading audio: {e}")
            break

        # Check if we've exceeded the time
        if (time.ticks_ms() - start_time) > duration_ms + 500:  # Add margin
            print("Recording timed out")
            break

    print(f"Recorded {samples_recorded} samples in {len(chunks)} chunks")
    return chunks

def send_audio_to_server(audio_chunks):
    """Send audio chunks to server"""
    s = None
    try:
        # Calculate total size
        total_size = sum(len(chunk) * 2 for chunk in audio_chunks)  # *2 because each sample is 2 bytes
        print(f"Sending {total_size} bytes of audio...")

        # Create socket connection with timeout
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(SOCKET_TIMEOUT)
        s.connect((SERVER_IP, SERVER_PORT))

        # First send the size of data
        size_data = total_size.to_bytes(4, 'big')
        s.sendall(size_data)

        # Send each chunk
        for chunk in audio_chunks:
            # Convert to bytes
            chunk_bytes = bytearray(chunk)
            s.sendall(chunk_bytes)
            print(f"Sent chunk of {len(chunk_bytes)} bytes")

        # Wait for response with timeout
        print("Waiting for server response...")
        response = s.recv(1024).decode('utf-8')
        print(f"Received response: {response}")
        return response

    except Exception as e:
        print(f"Error sending audio: {e}")
        return None
    finally:
        if s:
            s.close()

def detect_command():
    """Record audio and detect command"""
    # Wait for sound above threshold to start recording
    print("Listening for sound...")
    while True:
        i2s.readinto(audio_buffer)
        energy = sum(abs(audio_buffer[i]) for i in range(len(audio_buffer))) // len(audio_buffer)

        if energy > 400:  # Adjust based on your environment
            print(f"Sound detected (energy: {energy})")

            # Record audio for 2 seconds
            audio_chunks = record_audio(2000)

            # Send to server
            text = send_audio_to_server(audio_chunks)
            if text:
                print(f"Server recognized: {text}")
                if "testing" in text.lower():
                    print("\n*** I hear you loud and clear! ***\n")
                    return True
            break

        time.sleep(0.1)

    return False

# Main program
print("Improved server-side speech recognition")
print("Say 'testing' loud and clear when ready...")

# Connect to WiFi
if connect_wifi():
    try:
        # Main loop
        while True:
            detect_command()
            time.sleep(1)  # Wait before listening again
    except KeyboardInterrupt:
        i2s.deinit()
        print("Program stopped")
else:
    print("Cannot proceed without WiFi connection")
