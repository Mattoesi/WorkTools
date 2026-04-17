import time
import wave
import queue
import pyaudiowpatch as pyaudio

DEVICE_INDEX = 20
CHUNK = 1024
FORMAT = pyaudio.paInt16
RECORD_SECONDS = 5
OUTPUT_FILE = "loopback_test.wav"

audio_queue = queue.Queue()
frames = []

p = pyaudio.PyAudio()
device_info = p.get_device_info_by_index(DEVICE_INDEX)

RATE = int(device_info["defaultSampleRate"])
CHANNELS = int(device_info["maxInputChannels"])

print("Using device:", device_info["name"])
print("Sample rate:", RATE)
print("Channels:", CHANNELS)

callback_calls = 0

def callback(in_data, frame_count, time_info, status):
    global callback_calls
    callback_calls += 1
    if in_data:
        audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=CHUNK,
    stream_callback=callback
)

print("Recording...")
stream.start_stream()

start = time.time()
while time.time() - start < RECORD_SECONDS:
    while not audio_queue.empty():
        frames.append(audio_queue.get())
    time.sleep(0.01)

stream.stop_stream()
stream.close()

sample_width = p.get_sample_size(FORMAT)
p.terminate()

total_bytes = sum(len(f) for f in frames)
print("Callback calls:", callback_calls)
print("Frames captured:", len(frames))
print("Total bytes captured:", total_bytes)

if total_bytes == 0:
    print("No audio data captured. WAV file will be empty.")
else:
    with wave.open(OUTPUT_FILE, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(sample_width)
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    print("Done recording.")
    print(f"Saved to {OUTPUT_FILE}")