import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import queue
import numpy as np
import yaml

class AudioVisualizer:
    def __init__(self, plot_queue):
        """
        Real-time Audio Dashboard.
        Args:
            plot_queue: Thread-safe queue containing processed audio packets.
        """
        self.plot_queue = plot_queue
        self.config = self._load_config()
        self.block_size = self.config['audio']['block_size']
        
        # Setup Figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.suptitle('Helix Audio Sensor Debugger', fontsize=16)
        
        # Setup Plot 1: Raw Input
        self.x = np.arange(self.block_size)
        self.line_raw, = self.ax1.plot(self.x, np.zeros(self.block_size), color='#ff4b4b', lw=1)
        self.ax1.set_ylim(-1.0, 1.0)
        self.ax1.set_xlim(0, self.block_size)
        self.ax1.set_ylabel('Amplitude')
        self.ax1.set_title('Raw Microphone Input')
        self.ax1.grid(True, linestyle='--', alpha=0.5)

        # Setup Plot 2: Cleaned Output (DSP)
        self.line_clean, = self.ax2.plot(self.x, np.zeros(self.block_size), color='#2ecc71', lw=1)
        self.ax2.set_ylim(-1.0, 1.0)
        self.ax2.set_xlim(0, self.block_size)
        self.ax2.set_ylabel('Amplitude')
        self.ax2.set_title('DSP Output (Spectral Gating)')
        self.ax2.grid(True, linestyle='--', alpha=0.5)

        # Setup Metrics Text
        self.text_metrics = self.ax1.text(
            0.02, 0.95, "", 
            transform=self.ax1.transAxes, 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
            verticalalignment='top'
        )

    def _load_config(self):
        with open("config/audio_settings.yaml", "r") as f:
            return yaml.safe_load(f)

    def update_plot(self, frame):
        """
        Called by Matplotlib animation loop.
        """
        try:
            # Get the LATEST packet.
            # If the queue has 5 items, we want the newest one, 
            # so we drain the queue to avoid "display lag".
            packet = None
            while not self.plot_queue.empty():
                packet = self.plot_queue.get_nowait()
            
            if packet is None:
                return self.line_raw, self.line_clean, self.text_metrics

            # Update Lines
            self.line_raw.set_ydata(packet['raw'])
            self.line_clean.set_ydata(packet['clean'])
            
            # Update Text
            snr = packet['snr']
            latency = packet['latency']
            
            self.text_metrics.set_text(
                f"SNR: {snr:.2f} dB\n"
                f"Latency: {latency:.2f} ms\n"
                f"Status: {'CRITICAL' if snr < 5 else 'GOOD'}"
            )

            return self.line_raw, self.line_clean, self.text_metrics

        except Exception as e:
            # Keep running even if a frame fails
            return self.line_raw, self.line_clean, self.text_metrics

    def start(self):
        """Starts the blocking UI loop"""
        print(">>> Visualizer: Starting UI Loop")
        ani = FuncAnimation(
            self.fig, 
            self.update_plot, 
            interval=30,  # 30ms refresh
            blit=True     # Critical for performance
        )
        plt.show()