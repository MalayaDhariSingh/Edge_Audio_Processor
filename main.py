import asyncio
import queue
import threading
import sys
from src.core.audio_stream import AudioStream
from src.core.pipeline import AudioPipeline
from src.ui.visualizer import AudioVisualizer

def start_background_loop(loop):
    """Runs the asyncio loop in a separate thread."""
    asyncio.set_event_loop(loop)
    loop.run_forever()

def main():
    # 1. Setup Data Channels (Queues)
    # audio_queue: Hardware -> Pipeline (Async)
    # plot_queue:  Pipeline -> Visualizer (Thread-safe standard Queue)
    audio_queue = asyncio.Queue(maxsize=100)
    plot_queue = queue.Queue(maxsize=100)

    # 2. Setup Async Environment
    loop = asyncio.new_event_loop()

    # 3. Initialize Components
    try:
        # Hardware Driver
        mic_stream = AudioStream(loop, audio_queue)
        
        # Processing Logic
        pipeline = AudioPipeline(audio_queue, plot_queue)
        
        # Visualization
        visualizer = AudioVisualizer(plot_queue)

    except Exception as e:
        print(f"Initialization Failed: {e}")
        return

    # 4. Launch Background Threads
    # Start the Async Loop in a background thread so it doesn't block the UI
    t = threading.Thread(target=start_background_loop, args=(loop,), daemon=True)
    t.start()

    # Schedule the Pipeline to run on that loop
    asyncio.run_coroutine_threadsafe(pipeline.run(), loop)

    # 5. Start Hardware
    mic_stream.start()

    # 6. Start UI (This BLOCKS the Main Thread until window is closed)
    print(">>> System Online. Close graph window to exit.")
    try:
        visualizer.start()
    except KeyboardInterrupt:
        pass

    # 7. Cleanup (When window closes)
    print(">>> Shutting down...")
    mic_stream.stop()
    pipeline.stop()
    loop.call_soon_threadsafe(loop.stop)
    t.join(timeout=1.0)
    print(">>> Shutdown Complete.")

if __name__ == "__main__":
    main()