import sounddevice as sd
import numpy as np
import asyncio
import yaml
import sys

class AudioStream:
    def __init__(self, loop, audio_queue):
        """
        Initializes the Audio Input Stream.
        
        Args:
            loop: The asyncio event loop (Main Thread).
            audio_queue: The queue to push audio data into.
        """
        self.loop = loop
        self.queue = audio_queue
        self.config = self._load_config()
        self.stream = None

    def _load_config(self):
        """Loads audio settings from yaml"""
        try:
            with open("config/audio_settings.yaml", "r") as f:
                data = yaml.safe_load(f)
                return data['audio']
        except FileNotFoundError:
            print("Error: config/audio_settings.yaml not found.")
            sys.exit(1)

    def audio_callback(self, indata, frames, time_info, status):
        """
        This runs in a background thread by the OS Audio Driver.
        WE CANNOT BLOCK HERE.
        """
        if status:
            print(f"Audio Input Status: {status}")

        # CRITICAL: We must copy() indata. 
        # The driver reuses this memory buffer for the next chunk immediately.
        # If we don't copy, we get garbage data later.
        data_copy = indata.copy()

        # Thread-Safety: Schedule the 'put' operation on the main event loop
        self.loop.call_soon_threadsafe(
            self.queue.put_nowait, 
            data_copy
        )

    def start(self):
        """Starts the hardware stream"""
        print(f"Starting Audio Stream: {self.config['sample_rate']}Hz")
        self.stream = sd.InputStream(
            channels=self.config['channels'],
            samplerate=self.config['sample_rate'],
            blocksize=self.config['block_size'],
            dtype=self.config['dtype'],
            callback=self.audio_callback
        )
        self.stream.start()

    def stop(self):
        """Stops the hardware stream"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("Audio Stream Stopped.")