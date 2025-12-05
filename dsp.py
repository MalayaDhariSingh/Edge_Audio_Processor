import numpy as np
from scipy.signal import butter, lfilter

class DSPUtils:
    """
    Digital Signal Processing Toolkit.
    Stateless functions for audio manipulation.
    """
    @staticmethod
    def low_pass_filter(data, cutoff=3000, fs=16000, order=5):
        """
        Removes frequencies above 'cutoff'. 
        Human voice is mostly below 3000Hz. Noise is often above.
        """
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = lfilter(b, a, data)
        return y.astype(np.float32)

    @staticmethod
    def calculate_snr(audio_chunk: np.ndarray) -> float:
        """
        Calculates Signal-to-Noise Ratio (SNR) in Decibels (dB).
        
        Logic:
        1. Calculate Signal Power (Mean Square).
        2. Estimate Noise Floor (using 10th percentile as a heuristic).
        3. Compute Logarithmic ratio.
        """
        # Avoid modification of original data
        data = np.array(audio_chunk, dtype=np.float32)
        
        signal_power = np.mean(data ** 2)
        
        # Safety check for absolute silence
        if signal_power < 1e-9:
            return 0.0
        
        # In a real streaming buffer, we would track the noise floor over time.
        # For this 'stateless' chunk processor, we assume the quietest 10% 
        # of samples in this frame represent the background noise.
        noise_floor = np.percentile(np.abs(data), 10) ** 2
        
        if noise_floor < 1e-9:
            noise_floor = 1e-9 # Prevent division by zero
            
        snr = 10 * np.log10(signal_power / noise_floor)
        return float(snr)

    @staticmethod
    def spectral_subtraction(audio_chunk: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """
        Applies a basic FFT-based Noise Gate.
        
        Process:
        Time Domain -> FFT -> Frequency Domain -> Threshold Mask -> IFFT -> Time Domain
        """
        # 1. Convert to Frequency Domain
        # rfft is faster for real-valued inputs (like audio)
        fft_data = np.fft.rfft(audio_chunk)
        
        # 2. Compute Magnitude (Volume of each frequency bin)
        magnitude = np.abs(fft_data)
        
        # 3. Create a Mask (The Gate)
        # If frequency magnitude < threshold, zero it out.
        mask = magnitude > threshold
        
        # 4. Apply Mask
        filtered_fft = fft_data * mask
        
        # 5. Convert back to Time Domain
        clean_audio = np.fft.irfft(filtered_fft)
        
        # 6. Length Correction (FFT padding sometimes changes length slightly)
        return clean_audio[:len(audio_chunk)].astype(np.float32)

    @staticmethod
    def measure_latency(start_time: float, end_time: float) -> float:
        """Returns latency in milliseconds"""
        return (end_time - start_time) * 1000