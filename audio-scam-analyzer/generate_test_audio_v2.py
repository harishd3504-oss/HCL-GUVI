import wave
import struct

# Create a 1-second silence WAV file
sample_rate = 44100
duration = 1.0
num_frames = int(duration * sample_rate)

with wave.open('test_call.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
    wav_file.setframerate(sample_rate)
    
    # Write silence (0)
    data = struct.pack('<' + ('h' * num_frames), *([0] * num_frames))
    wav_file.writeframes(data)

print("Created test_call.wav")
