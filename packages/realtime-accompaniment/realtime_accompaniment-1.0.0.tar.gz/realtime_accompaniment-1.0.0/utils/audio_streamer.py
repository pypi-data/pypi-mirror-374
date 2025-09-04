from typing import Optional, Callable
import threading
import queue
import numpy as np
import pyaudio
import time
import utils.constants as constants


class AudioStreamer:
    """
    AudioStreamer class handles live audio streaming and processing.
    It uses PyAudio to capture audio input and provides methods to start/stop streaming,
    process audio chunks, and manage the audio queue.
    """

    def __init__(
        self,
        input_device: Optional[int] = None,
        sr: int = constants.DEFAULT_SR,
        chunk_size: int = constants.DEFAULT_CHUNK_SIZE_NOA,
        audio_callback: Optional[Callable] = None,
    ):
        """
        Initialize the AudioStreamer with parameters for live audio streaming.

        Args:
            input_device (int, optional): Audio input device index. If None, uses default device.
            sr (int): Sampling rate for audio processing. Default is 22050.
            chunk_size (int): Size of audio chunks for live streaming. Default is 1024.
            audio_callback (callable, optional): Callback function for audio events (alignment updates, mode changes, etc.).
        """

        self.input_device = input_device
        self.sr = sr
        self.chunk_size = chunk_size
        self.audio_callback = audio_callback

        # Audio streaming state
        self.is_streaming = False
        self.stream = None
        self.audio_thread = None
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()

        # Locks for thread safety
        self._streaming_lock = threading.Lock()
        self._processing_thread_lock = threading.Lock()
        self._stream_lock = threading.Lock()

        # timing
        self.stream_start_t = 0
        self.add_to_queue_t = 0

        # Initialize PyAudio
        self.init_audio()

    def init_audio(self):
        """Initialize PyAudio for live audio streaming."""
        try:
            self.audio = pyaudio.PyAudio()

            # Get device info if specified
            if self.input_device is not None:
                device_info = self.audio.get_device_info_by_index(self.input_device)
                print(f"Using audio device: {device_info['name']}")
            else:
                print("Using default audio input device")

            # Open audio stream (but don't start it yet)
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                start=False,
                rate=self.sr,
                input=True,
                input_device_index=self.input_device,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback_pyaudio,
            )
            print("Opened input stream in AudioStreamer init")

        except Exception as e:
            print(f"Warning: Could not initialize PyAudio: {e}")
            self.audio = None

    def _audio_callback_pyaudio(self, in_data, frame_count, time_info, status):
        """PyAudio callback function for live audio streaming."""

        start_t = time.perf_counter()
        if status:
            print(f"Audio callback status: {status}")

        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)

        # Add to queue for processing
        try:
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            print("Warning: Audio queue is full, dropping audio chunk")

        self.add_to_queue_t += time.perf_counter() - start_t

        return (None, pyaudio.paContinue)

    def start_live_streaming(self, audio_processing_thread):
        """Start live audio streaming and processing."""
        if self.audio is None:
            raise RuntimeError("PyAudio not initialized. Cannot start live streaming.")

        with self._streaming_lock:
            if self.is_streaming:
                print("Live streaming is already active.")
                return

        print("Starting live audio streaming...")

        # Reset state
        self.stop_event.clear()

        try:
            with self._processing_thread_lock:
                self.processing_thread = threading.Thread(target=audio_processing_thread)
                self.processing_thread.daemon = True
                self.processing_thread.start()

            with self._stream_lock:
                self.stream.start_stream()

            with self._streaming_lock:
                self.is_streaming = True

        except Exception as e:
            print(f"Error starting live streaming: {e}")
            self.stop_live_streaming()

    def get_in_lat(self):
        return self.input_latency

    def stop_live_streaming(self):
        """Stop live audio streaming and processing."""
        with self._streaming_lock:
            if not self.is_streaming:
                print("Live streaming is not active.")
                return
            self.is_streaming = False

        print("Stopping live audio streaming...")

        # Set stop event
        self.stop_event.set()

        # Stop and close stream
        with self._stream_lock:
            if self.stream:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()

                # reopen stream for next time
                self.stream = self.audio.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    start=False,
                    rate=self.sr,
                    input=True,
                    input_device_index=self.input_device,
                    frames_per_buffer=self.chunk_size,
                    stream_callback=self._audio_callback_pyaudio,
                )

        # Wait for processing thread to finish
        with self._processing_thread_lock:
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2.0)

        print("Audio streamer stopped.")

    def __del__(self):
        """Cleanup when object is destroyed."""
        with self._stream_lock:
            self.stream = None
        with self._streaming_lock:
            if self.is_streaming:
                self.stop_live_streaming()
        if hasattr(self, "audio") and self.audio:
            self.audio.terminate()
