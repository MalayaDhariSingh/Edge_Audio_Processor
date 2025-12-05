import asyncio
import queue
import time
import yaml
import numpy as np
from src.core.dsp import DSPUtils

class AudioPipeline:
    def __init__(self, audio_queue: asyncio.Queue, plot_queue: queue.Queue):
        """
        Manages the data flow: Audio Queue -> DSP -> Plot Queue
        """
        self.audio_queue = audio_queue
        self.plot_queue = plot_queue
        self.config = self._load_config()
        self.is_running = False

    def _load_config(self):
        try:
            with open("config/audio_settings.yaml", "r") as f:
                return yaml.safe_load(f)['processing']
        except Exception:
            return {"noise_threshold": 0.02}

    async def run(self):
        """
        The main async worker loop.
        """
        print(">>> Pipeline: Processing Worker Started")
        self.is_running = True
        
        while self.is_running:
            # 1. Wait for raw audio from the hardware driver
            # This 'await' yields control back to the loop if queue is empty
            raw_data = await self.audio_queue.get()
            
            # Flatten to 1D array for processing
            raw_flat = raw_data.flatten()

            # 2. Performance Monitoring (Latency)
            start_time = time.perf_counter()

            # 3. Apply DSP (The "Brain")
            # A. Clean the audio (Noise Gating)
            fft_data = np.fft.rfft(raw_flat)
            max_fft_mag = np.max(np.abs(fft_data))
            print(f"FFT Max: {max_fft_mag:.4f} | Threshold: {self.config['noise_threshold']}")
            gated_data = DSPUtils.spectral_subtraction(
                raw_flat, 
                threshold=self.config['noise_threshold']
            )
            clean_data = DSPUtils.low_pass_filter(gated_data, cutoff=4000)
            # B. Measure Quality (SNR)
            snr_value = DSPUtils.calculate_snr(raw_flat)
            
            # Calculate total processing time in milliseconds
            latency_ms = (time.perf_counter() - start_time) * 1000

            # 4. Package for UI
            # We use a Dictionary as a "Data Transfer Object" (DTO)
            packet = {
                "raw": raw_flat,
                "clean": clean_data,
                "snr": snr_value,
                "latency": latency_ms
            }

            # 5. Send to Visualizer (Non-blocking)
            # If the UI is slow and the queue is full, we DROP the frame.
            # This prevents the audio processing from lagging behind real-time.
            try:
                self.plot_queue.put_nowait(packet)
            except queue.Full:
                pass # Dropping frame to maintain real-time sync

            # Mark task as done in the queue
            self.audio_queue.task_done()

    def stop(self):
        self.is_running = False