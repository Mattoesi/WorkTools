import time
import pyaudiowpatch as pyaudio

TEST_SECONDS = 3
CHUNK = 1024
FORMAT = pyaudio.paInt16

p = pyaudio.PyAudio()

loopback_devices = []
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get("isLoopbackDevice"):
        loopback_devices.append(dev)

print("Loopback devices found:")
for dev in loopback_devices:
    print(f'{dev["index"]}: {dev["name"]} | rate={int(dev["defaultSampleRate"])} | channels={dev["maxInputChannels"]}')

print("\nPlay audio now on the device you want to test...\n")

for dev in loopback_devices:
    idx = dev["index"]
    rate = int(dev["defaultSampleRate"])
    channels = int(dev["maxInputChannels"])

    print(f"Testing device {idx}: {dev['name']}")

    frames = []
    try:
        stream = p.open(
            format=FORMAT,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=idx,
            frames_per_buffer=CHUNK,
            start=False
        )

        stream.start_stream()
        start = time.time()

        while time.time() - start < TEST_SECONDS:
            available = stream.get_read_available()
            if available >= CHUNK:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            else:
                time.sleep(0.01)

        stream.stop_stream()
        stream.close()

        total_bytes = sum(len(f) for f in frames)
        print(f"  Frames: {len(frames)} | Bytes: {total_bytes}")

    except Exception as e:
        print(f"  ERROR: {e}")

p.terminate()