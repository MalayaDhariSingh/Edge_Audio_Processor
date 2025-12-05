This is the most important file in the repository. Recruiters will scan this for 30 seconds. Engineers will read it to see if you understand *architecture*.

We need to frame this not as a "Python script," but as a **Prototype for a Robot's Auditory Cortex**.

Create a file named `README.md` and paste this in.

-----

# Cloudless Audio Edge Processor (Helix Prototype)

**Real-time, asynchronous audio pipeline for humanoid auditory perception.**

### 🎯 Mission

To build a highly optimized, low-latency audio pre-processing unit that mimics the "ears" of a humanoid robot. This system captures raw audio, sanitizes it (Noise Gating & Filtering), measures signal quality (SNR), and visualizes the data stream in real-time—all running locally on the edge without cloud dependencies.

### ⚡ Key Features

  * **Asynchronous Pipeline:** Decoupled Input (Driver) and Processing (DSP) using `asyncio` to prevent blocking the main thread.
  * **Spectral Noise Gating:** FFT-based algorithm to silence background noise floor while preserving speech.
  * **Live Telemetry:** Real-time calculation of Signal-to-Noise Ratio (SNR) and Processing Latency (ms).
  * **Thread-Safe Hardware I/O:** Robust bridging between C-level audio drivers and Python's Event Loop.
  * **Visualization Dashboard:** 60FPS dual-waveform rendering for debugging raw vs. processed signals.

-----

### 🛠 Architecture

The system uses a **Producer-Consumer** architecture to ensure zero frame drops during high CPU load.

1.  **The Ear (Hardware Thread):** `sounddevice` captures audio frames via PortAudio (C-Library) and pushes them to a thread-safe queue.
2.  **The Nervous System (Async Loop):** An `asyncio` worker pulls frames, applies math, and handles backpressure.
3.  **The Brain (DSP Logic):**
      * **FFT:** Converts Time Domain $\rightarrow$ Frequency Domain.
      * **Spectral Gating:** Zeros out bins below the dynamic noise threshold.
      * **Low-Pass Filter:** Butterworth filter (Cutoff: 4000Hz) to remove high-frequency artifacts.
4.  **The Eye (Main Thread):** `Matplotlib` visualizes the result via a secondary queue.

-----

### 🚀 Quick Start

**Prerequisites**

  * Python 3.9+
  * PortAudio (System Level Dependency)

<!-- end list -->

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/edge-audio-processor.git
cd edge-audio-processor

# 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Run the System
python main.py
```

-----

### 🎛 Configuration

Tune the robot's ears in `config/audio_settings.yaml`:

```yaml
audio:
  sample_rate: 16000     # Standard for ASR models (Whisper/Kaldi)
  block_size: 1024       # Balance between latency and stability

processing:
  noise_threshold: 2.5   # Adjust based on environment noise floor
```

-----

### 🧠 Engineering Decisions (Why this stack?)

**1. Why Asyncio instead of Threading?**
Python's GIL (Global Interpreter Lock) makes multi-threading CPU-heavy tasks inefficient. By using `asyncio` for the I/O pipeline and `numpy` (C-optimized) for the math, we maximize throughput while keeping the visualization responsive.

**2. Why Spectral Subtraction?**
Standard volume gates clip the start of words. Spectral Subtraction operates in the frequency domain, allowing us to remove constant background hum (like server fans or robot actuators) without destroying the human voice.

**3. Latency vs. Throughput**
The system prioritizes **Real-time Sync**. If the Visualization queue fills up (rendering lag), the pipeline drops visual frames rather than blocking the audio processing. The robot's "hearing" never pauses, even if the "debugger" lags.

-----

### 🤖 Relevance to Figure AI (Helix Team)

This project demonstrates the fundamental requirements for the **Helix Speech** team:

  * **Low-Level Audio Data Manipulation:** Manipulating raw PCM buffers directly.
  * **Edge Optimization:** Running DSP locally, not via an API.
  * **Latency Awareness:** Measuring and optimizing the "Motion-to-Photon" equivalent for audio.
  * **Tooling:** Building internal debuggers to visualize sensor data.

-----

### 📂 Directory Structure

```text
CloudlessEdgeAudio/
├── config/             # YAML configurations
├── src/
│   ├── core/           # DSP Logic, Hardware Drivers, Async Pipeline
│   └── ui/             # Visualization Dashboard
├── main.py             # Application Entry Point
└── requirements.txt
```
