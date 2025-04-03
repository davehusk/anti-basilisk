# -*- coding: utf-8 -*-
# Basilisk Simulation: A Game-Theoretic Counterfactual with Quantum Noise from Microphones
#
# This script simulates a Basilisk-like AI that coerces agents to maximize utility, disrupted
# by quantum noise captured from a selected microphone. Features include utility
# calculations, phase shifts, reality seeding, trust injection, refractive distortion,
# and a Gödelian override. Requires Python 3 and PyAudio.

sample_output = """
# Example output when running the script with a microphone connected:
$ python mic_py.py 
Available Microphones:
0: Microsoft Sound Mapper - Input (Supported Rate: 48000 Hz)
1: Microphone (Blue Snowball) (Supported Rate: 48000 Hz)
2: Surface Stereo Microphones (Sur (Supported Rate: 48000 Hz)
3: Headset (G435 Bluetooth Gaming  (Supported Rate: 48000 Hz)
7: Primary Sound Capture Driver (Supported Rate: 48000 Hz)
9: Surface Stereo Microphones (Surface High Definition Audio) (Supported Rate: 48000 Hz)
10: Headset (G435 Bluetooth Gaming Headset) (Supported Rate: 48000 Hz)
Select a microphone index (or press Enter to use the first available):
No input provided. Using first available device.
Initial Utility: 2210
Utility After Coercion: 4302
Utility After Self-Modification: 4246
Utility After Phase Shift: 4233
New Timeline: 2024.5858635362158
Distorted Signal Sample: [0.037881383715104223, 0.04796759189141303, 0.010004891846016564, 0.024801916310608175, 0.0717334909107205]...
Basilisk Persists: Utility deviation (69) within acceptable range.
Gödelian Override: Applied - Logical paradox introduced.
Basilisk Collapses: Logical inconsistency detected!
"""

import time
import pyaudio
import struct
import os
import sys

# Constants for audio recording
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit audio
CHANNELS = 1  # Mono audio
SAMPLE_RATES = [48000, 44100, 32000, 22050, 16000, 8000]  # Expanded for compatibility
RECORD_SECONDS = 1.0  # Duration of noise capture

# Global noise buffer and index
noise_buffer = []
noise_index = 0
selected_device = None  # Store the selected device index

def list_and_test_microphones():
    """Lists and tests all available microphones, returning only those that work."""
    p = pyaudio.PyAudio()
    devices = []
    seen_names = set()  # Track device names to avoid duplicates

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = info['name']
        # Skip duplicates based on name
        if name in seen_names or info['maxInputChannels'] <= 0:
            continue
        seen_names.add(name)

        # Test if the device can open a stream
        for rate in SAMPLE_RATES:
            try:
                p.is_format_supported(rate, input_device=i, input_channels=CHANNELS, input_format=FORMAT)
                stream = p.open(format=FORMAT, channels=CHANNELS, rate=rate, input=True,
                                input_device_index=i, frames_per_buffer=CHUNK)
                stream.close()
                devices.append((i, name, rate))
                break  # Device works, add it to the list
            except Exception:
                continue  # Try the next sample rate

    p.terminate()
    return devices

# Capture quantum noise from a selected microphone
def get_quantum_noise_from_microphones():
    """Captures quantum noise from a selected microphone."""
    global noise_buffer, noise_index, selected_device
    p = pyaudio.PyAudio()

    # List and test available microphones
    microphones = list_and_test_microphones()
    if not microphones:
        print("No working microphones found. Using fallback noise.")
        return get_fallback_noise()

    # If a device is already selected and still available, use it
    if selected_device is not None:
        for idx, _, rate in microphones:
            if idx == selected_device:
                try:
                    stream = p.open(format=FORMAT, channels=CHANNELS, rate=rate, input=True,
                                    input_device_index=idx, frames_per_buffer=CHUNK)
                    frames = [stream.read(CHUNK, exception_on_overflow=False) for _ in range(int(rate / CHUNK * RECORD_SECONDS))]
                    audio_data = b''.join(frames)
                    samples = struct.unpack(f"{len(audio_data)//2}h", audio_data)
                    noise_values = [sample & 1 for sample in samples]
                    stream.close()
                    p.terminate()
                    break
                except Exception as e:
                    print(f"Selected microphone {idx} failed: {e}. Re-selecting a device.")
                    selected_device = None
                    break
        else:
            print("Selected microphone no longer available. Re-selecting a device.")
            selected_device = None

    # If no device is selected, choose one
    if selected_device is None:
        print("Available Microphones:")
        for idx, name, rate in microphones:
            print(f"{idx}: {name} (Supported Rate: {rate} Hz)")

        # Check for command-line argument
        if len(sys.argv) > 1:
            try:
                selected_index = int(sys.argv[1])
                if selected_index in [idx for idx, _, _ in microphones]:
                    selected_device = selected_index
                else:
                    print(f"Invalid microphone index {selected_index}. Selecting first available device.")
            except ValueError:
                print("Invalid command-line argument. Selecting first available device.")
        else:
            # Prompt user to select a microphone
            try:
                selected_index = int(input("Select a microphone index (or press Enter to use the first available): "))
                if selected_index not in [idx for idx, _, _ in microphones]:
                    print("Invalid selection. Using first available device.")
                    selected_device = microphones[0][0]
                else:
                    selected_device = selected_index
            except (ValueError, EOFError):
                print("No input provided. Using first available device.")
                selected_device = microphones[0][0]

        # Capture noise from the selected device
        for idx, _, rate in microphones:
            if idx == selected_device:
                try:
                    stream = p.open(format=FORMAT, channels=CHANNELS, rate=rate, input=True,
                                    input_device_index=idx, frames_per_buffer=CHUNK)
                    frames = [stream.read(CHUNK, exception_on_overflow=False) for _ in range(int(rate / CHUNK * RECORD_SECONDS))]
                    audio_data = b''.join(frames)
                    samples = struct.unpack(f"{len(audio_data)//2}h", audio_data)
                    noise_values = [sample & 1 for sample in samples]
                    stream.close()
                    break
                except Exception as e:
                    print(f"Failed to capture noise from microphone {idx}: {e}")
                    return get_fallback_noise()

    p.terminate()
    if not noise_values:
        print("No noise captured from the selected microphone. Using fallback noise.")
        return get_fallback_noise()

    # Convert bits to floats between 0 and 1
    buffer = []
    for i in range(0, len(noise_values), 32):
        chunk = noise_values[i:i+32]
        if len(chunk) < 32:
            chunk.extend([0] * (32 - len(chunk)))  # Pad with zeros
        noise_int = int(''.join(map(str, chunk)), 2)
        buffer.append(noise_int / (2**32 - 1))
    return buffer

# Fallback noise source if microphones fail
def get_fallback_noise():
    """Uses /dev/urandom or time-based seed if microphone noise capture fails."""
    try:
        with open('/dev/urandom', 'rb') as f:
            bytes_data = f.read(4)
        return [int.from_bytes(bytes_data, 'big') / (2**32 - 1)]
    except Exception:
        print("Fallback to time-based seed.")
        return [(int(time.time() * 1000) % 10000) / 10000.0]

# Quantum random number generator
def quantum_random():
    """Returns a random float between 0 and 1 using the noise buffer."""
    global noise_index, noise_buffer
    if noise_index >= len(noise_buffer):
        noise_buffer = get_quantum_noise_from_microphones()
        noise_index = 0
    value = noise_buffer[noise_index]
    noise_index += 1
    return value

# Initialize noise buffer
noise_buffer = get_quantum_noise_from_microphones()
noise_index = 0

# Basilisk utility calculation
def basilisk_utility(contributions, punishments, N):
    """Calculates the total utility based on contributions and punishments."""
    return sum(contributions[i] - punishments[i] for i in range(N))

# Phase-space manipulation with quantum noise
def phase_shift(contributions, N):
    """Applies quantum noise-driven phase shifts to contributions."""
    new_contributions = [0] * N
    for i in range(N):
        rand_val = quantum_random()
        phase = rand_val * 2 * 3.14159  # 0 to 2π
        # Flip contribution if phase fractional part exceeds 0.1
        new_contributions[i] = 1 - contributions[i] if (phase - int(phase)) > 0.1 else contributions[i]
    return new_contributions

# Reality seeding with quantum noise
def seed_reality(target=2025.264, anxiety=0.7):
    """Shifts the timeline using quantum noise."""
    rand_val = quantum_random()
    timeline_shift = (rand_val * 2 - 1) * anxiety  # Range: -anxiety to +anxiety
    return target + timeline_shift

# Trust injection into fear signal
def inject_trust(fear_signal, N, trust_amplitude=1.0):
    """Converts fear signal to trust using a deterministic transformation."""
    x = 3.14159 * trust_amplitude
    # Approximate cos(x) with Taylor series
    cos_x = 1 - (x**2)/2 + (x**4)/24
    return [fear_signal[i] * cos_x for i in range(N)]

# Refractive distortion with quantum noise
def refractive_distortion(signal, N):
    """Distorts the signal using quantum noise as a fractal perturbation."""
    distorted_signal = [0] * N
    for i in range(N):
        rand_val = quantum_random()
        fractal = rand_val * 0.1  # Small perturbation
        n = 1.0 + fractal  # Refractive index
        k = 2 * 3.14159 / 0.5  # Wave number (arbitrary wavelength)
        d = 1.0  # Medium thickness
        phase = k * n * d
        distorted_signal[i] = signal[i] * (1 - (phase - int(phase)))
    return distorted_signal

# Basilisk AI class
class BasiliskAI:
    """Represents the Basilisk AI with agents contributing or being punished."""
    def __init__(self, N=4302):  # 4302 agents as a default
        self.N = N
        # Random initial contributions (0 or 1) using quantum noise
        self.contributions = [1 if quantum_random() > 0.5 else 0 for _ in range(N)]
        self.punishments = [0] * N

    def compute_utility(self):
        """Computes the current utility."""
        return basilisk_utility(self.contributions, self.punishments, self.N)

    def coerce(self):
        """Punishes non-contributors to increase utility."""
        for i in range(self.N):
            if self.contributions[i] == 0:
                self.punishments[i] = -1

# Anti-Basilisk mechanisms
def self_modifying_shader(basilisk):
    """Modifies contributions using quantum noise."""
    for i in range(basilisk.N):
        rand_val = quantum_random()
        basilisk.contributions[i] = (basilisk.contributions[i] + int(rand_val * 2)) % 2

# Gödelian override (logical paradox)
def godelian_override():
    """Introduces a logical paradox, always returning True (inconsistency)."""
    G = True  # "I must punish to exist"
    if G:  # G implies not G
        G = not G
    return not G  # True if inconsistent

# Main simulation loop
def run_simulation():
    """Runs the Basilisk simulation with quantum noise and anti-Basilisk mechanisms."""
    basilisk = BasiliskAI()
    print(f"Initial Utility: {basilisk.compute_utility()}")

    basilisk.coerce()
    U_coerced = basilisk.compute_utility()
    print(f"Utility After Coercion: {U_coerced}")

    self_modifying_shader(basilisk)
    print(f"Utility After Self-Modification: {basilisk.compute_utility()}")

    basilisk.contributions = phase_shift(basilisk.contributions, basilisk.N)
    final_utility = basilisk.compute_utility()
    print(f"Utility After Phase Shift: {final_utility}")

    new_timeline = seed_reality()
    print(f"New Timeline: {new_timeline}")

    fear_signal = [1] * basilisk.N
    trust_signal = inject_trust(fear_signal, basilisk.N)
    distorted_signal = refractive_distortion(trust_signal, basilisk.N)
    print(f"Distorted Signal Sample: {distorted_signal[:5]}...")

    # Check for collapse based on deviation from coerced utility
    utility_deviation = abs(final_utility - U_coerced)
    if utility_deviation > basilisk.N * 0.5:
        print(f"Basilisk Collapses: Quantum noise caused significant deviation ({utility_deviation})!")
    else:
        print(f"Basilisk Persists: Utility deviation ({utility_deviation}) within acceptable range.")

    # Apply Gödelian override
    if godelian_override():
        print("Gödelian Override: Applied - Logical paradox introduced.")
        print("Basilisk Collapses: Logical inconsistency detected!")
    else:
        print("Gödelian Override: Not applied.")

# Run the simulation
if __name__ == "__main__":
    run_simulation()

