# standard library imports
import pickle
import time
import threading
import queue
import warnings
from typing import Optional, Callable
import os

# other imports
import numpy as np
import librosa as lb
import matplotlib.pyplot as plt
import pyaudio

# Import custom modules
from noa.alignment._numba import (
    compute_cosine_distance,
    update_alignment_row_numba,
    _get_alpha_numba,
    calc_scale_from_deviation,
)
from noa.alignment.runtime_cache import AlphaCache
from utils.audio import writeStereo, makeStereo
from utils.audio_streamer import AudioStreamer
from utils.buffer import AudioBuffer
from utils.numeric import round_alpha
from utils.latency_tester import LatencyTester
from utils.mode_detection import compute_mode_array
import utils.constants as constants
from utils.cache_utils import generate_cache_key, load_cache, store_cache

from tsm.tsm import TSM


class NOA:
    """
    OnlineNOA class implements the Online NOA algorithm for real-time audio accompaniment.
    It processes a reference recording and extracts features, allowing for real-time accompaniment
    based on the NOA algorithm with support for both file input and live audio streaming.
    """

    def __init__(
        self,
        # cache parameters
        cache_dir: str = "cache",
        save_cache: bool = True,
        solo_reference: str = None,
        orch_reference: str = None,
        # audio parameters
        sr: int = constants.DEFAULT_SR,
        hop_length: int = constants.DEFAULT_HOP_LENGTH,
        feature_window: int = constants.DEFAULT_FEATURE_WINDOW,
        feature_extractor: callable = lb.feature.chroma_stft,
        noa_update_function: callable = update_alignment_row_numba,
        steps: np.ndarray = constants.DEFAULT_DTW_STEPS.T,
        weights: np.ndarray = constants.DEFAULT_DTW_WEIGHTS,
        buffer_size: int = 10 * 60 * constants.DEFAULT_SR,
        window_size: int = 1000,
        # Live audio parameters
        input_device: Optional[int] = None,
        output_device: Optional[int] = None,
        chunk_size: int = constants.DEFAULT_CHUNK_SIZE_NOA,
        audio_callback: Optional[Callable] = None,
        voice_mode: bool = False,
        alpha_lookback: int = constants.DEFAULT_ALPHA_LOOKBACK,
        alpha_update_frequency: int = constants.DEFAULT_ALPHA_UPDATE_FREQUENCY,
        alpha_adjust_frequency: int = constants.DEFAULT_ALPHA_ADJUST_FREQUENCY,
        max_timewarp_factor: float = constants.DEFAULT_MAX_TIMEWARP_FACTOR,
        alpha_adjust_sensitivity: float = constants.DEFAULT_ALPHA_ADJUST_SENSITIVITY,
        alpha_adjust_max_scale: float = constants.DEFAULT_ALPHA_ADJUST_MAX_SCALE,
        enable_tsm: bool = True,
        save_solo: bool = False,
        initial_constant_period: float = constants.DEFAULT_INITIAL_CONSTANT_PERIOD,
        additional_latency: float = 0.0,
        streaming: bool = True,
        # recording parameters
        recording: bool = False,
        outfile: str = None,
        warnings_on: bool = True,
    ) -> None:
        """
        Initialize the NOA class with a reference recording and parameters for the NOA algorithm.

        Args:
            cache_dir (str): Directory to save/load precomputed features. If cache_dir is not specified, solo_reference and orch_reference must be provided as file paths or precomputed feature files.
            save_cache (bool): Whether to save precomputed features to cache. Default is True.
            solo_reference (str): Path to the solo reference audio file or to the pickle file containing precomputed features.
            orch_reference (str): Path to the orchestral reference audio file or to the pickle file containing precomputed features.
            sr (int): Sampling rate for audio processing. Default is 22050.
            hop_length (int): Number of samples between successive frames. Default is 512. Must be a divisor of feature_window.
            feature_window (int): Feature window size. Default is 2048.
            feature_extractor (callable): Function to extract features from audio. Default is librosa's chroma_stft.
            noa_update_function (callable): Function to update the alignment row. Default is update_alignment_row_numba.
            steps (np.ndarray): Array defining the steps for alignment. Default is [[1, 1, 2], [1, 2, 1]]. First step must be (1,1) to initialize alignment.
            weights (np.ndarray): Weights for the steps. Default is [1, 1, 2].
            buffer_size (int): Size of the buffer for processing audio chunks. Default is sets it to 10 minutes.
            window_size (int): Size of the sliding window for alignment matrices to limit memory usage.
            input_device (int, optional): Audio input device index. If None, uses default device.
            chunk_size (int): Size of audio chunks for live streaming. Default is 1024.
            audio_callback (callable, optional): Callback function for audio events (alignment updates, mode changes, etc.).
            alpha_lookback (int): Number of frames to look back for alpha updates. Default is 10.
            alpha_update_frequency (int): Frequency of alpha updates. Default is 10.
            max_timewarp_factor (float): Maximum time warp factor for TSM. Default is 2.0.
            enable_tsm (bool): Whether to enable time-stretching for orchestral playback. Default is True.
            initial_constant_period (float): Initial period of constant alignment speed before updates begin. Default is 10.0 seconds.
            additional_latency (float): Additional latency in seconds. Default is 0.0.
            streaming (bool): Whether to enable live streaming. Default is True.
            rercording (bool): Whether to record the solo and orchestral output. Default is False.
            outfile (str): Output file path for recording.
            warnings_on (bool): Whether to enable warnings. Default is True.
        """
        # Convert to contiguous arrays for numba optimization
        self.dn = np.ascontiguousarray(steps[0], dtype=np.int32)
        self.dm = np.ascontiguousarray(steps[1], dtype=np.int32)
        self.dw = np.ascontiguousarray(weights, dtype=np.float32)
        assert (
            self.dn[0] == 1 and self.dm[0] == 1
        ), "First step must be (1,1) to initialize alignment."

        # Initialize caching variables
        self.cache_dir = cache_dir
        self.save_cache = save_cache
        self.solo_reference = solo_reference
        self.orch_reference = orch_reference
        # check if at least one of cache_dir and references is provided
        if not (self.cache_dir or (self.solo_reference and self.orch_reference)):
            raise ValueError(
                "Either cache_dir or both solo_reference and orch_reference must be provided."
            )

        # Initialize audio parameters
        self.sr = sr
        self.hop_length = hop_length
        self.feature_window = feature_window
        assert (
            self.feature_window % self.hop_length == 0
        ), "feature_window must be a multiple of hop_length."
        self.feature_extractor = feature_extractor

        # Initialize TSM parameters
        self.max_timewarp_factor = max_timewarp_factor
        self.orchestra = True
        self.solo_only = False
        self.initial_constant_period_frames = int(
            initial_constant_period * sr / hop_length
        )

        # Initialize NOA parameters
        self.noa_update_function = noa_update_function
        self.voice_mode = voice_mode
        self.warnings_on = warnings_on

        # Initialize recording parameters
        self.recording = recording
        self.streaming = streaming
        self.save_solo = save_solo
        self.output_device = output_device

        # Locks for thread safety - Define lock hierarchy to prevent deadlocks
        # Order: _buffer_lock -> _path_lock -> _history_lock -> _alpha_lock
        self._buffer_lock = threading.Lock()
        self._path_lock = threading.Lock()
        self._history_lock = threading.Lock()
        self._alpha_lock = threading.Lock()

        # Initialize common attributes
        self.window_size = window_size
        self.buffer_size = buffer_size

        # Initialize streamer
        if self.streaming:
            self.buffer = AudioBuffer(buffer_size)

            print("Initializing input audio stream")
            # Initialize audio streamer
            self.audio_streamer = AudioStreamer(
                input_device=input_device,
                chunk_size=chunk_size,
                audio_callback=audio_callback,
            )

            self.audio_callback = audio_callback

            self.latency_tester = LatencyTester(
                input_device_index=input_device,
                output_device_index=output_device,
                sr=sr,
            )

            # Predictive lag compensation: compute lag in frames
            self.additional_latency = additional_latency
            total_latency = (
                self.latency_tester.round_trip_latency + self.additional_latency
            )
            self.lag_samples = int(total_latency * self.sr)

            # Pre-allocate reusable arrays
            self._audio_chunk_buffer = np.empty(self.feature_window, dtype=np.float32)
            self._feature_buffer = None

        # compute mode array
        if hasattr(self, "voice_mode") and self.voice_mode:
            self._compute_mode_array(
                time=0.5
            )  # in voice mode, there are more frequent mode changes
        else:
            self._compute_mode_array(time=2.5)

        if (2 in self.mode_array) or self.save_solo:
            self._load_solo_audio()

        # Initialize TSM for orchestral playback
        self.tsm_enabled = enable_tsm

        # Initialize TSM variables
        if self.tsm_enabled:
            self.current_alpha = 1.0

            assert alpha_lookback > 1, "alpha_lookback must be greater than 1."
            self.alpha_lookback = alpha_lookback
            self._alpha_cache = AlphaCache(
                history=alpha_lookback
            )  # cache values for alpha computation

            assert (
                alpha_update_frequency > 0
            ), "alpha_update_frequency must be greater than 0."

            self.alpha_update_frequency = alpha_update_frequency
            self.alpha_adjust_frequency = alpha_adjust_frequency
            self.base_alpha = 1.0
            self.alpha_history = []
            self.t_ref = np.arange(len(self.mode_array)) * self.hop_length / self.sr
            self.deviation_history = []

            # Alpha adjustment parameters (tune as needed)
            self.alpha_adjust_sensitivity = alpha_adjust_sensitivity
            self.alpha_adjust_max_scale = alpha_adjust_max_scale
            self.alpha_adjust_min_scale = 2 - alpha_adjust_max_scale
            self.alpha_adjust_max_frame_deviation = 1
            self.alpha_update_counter = 0

            self._load_orchestral_audio()

            # Initialize TSM for live streaming
            if self.streaming:
                if self.save_solo:
                    audio_data = self.solo_audio
                else:
                    audio_data = self.orch_audio

                # Initialize TSM with orchestral audio
                self.tsm = TSM(
                    sr=self.sr,
                    audio_data=audio_data,
                    recording=self.recording,
                    cache_dir=self.cache_dir,
                    save_cache=self.save_cache,
                )

                self.tsm_thread = None

        # Initialize recording variables
        if self.recording:
            self.y_orchestra_out = np.empty(self.max_length)
            self.y_orchestra_pos = 0
            self.outfile = outfile
            if self.streaming:
                self.y_solo_out = np.empty(self.max_length)
                self.y_solo_pos = 0

        # Load and preprocess reference features
        self.load_reference_features()

        # Pre-normalize reference features for faster cosine distance computation
        self._preprocess_reference_features()

        # Initialize other parameters
        self.reset()

        # Add lock timeout to prevent indefinite waiting
        self._lock_timeout = 1.0  # 1 second timeout for lock acquisitions

    def _acquire_locks_safely(self, *locks):
        """Safely acquire multiple locks in the correct order to prevent deadlocks."""
        acquired_locks = []
        try:
            for lock in locks:
                if lock.acquire(timeout=self._lock_timeout):
                    acquired_locks.append(lock)
                else:
                    # Release all acquired locks if we can't acquire the next one
                    for acquired_lock in reversed(acquired_locks):
                        acquired_lock.release()
                    raise TimeoutError(
                        f"Failed to acquire lock within {self._lock_timeout} seconds"
                    )
            return acquired_locks
        except Exception as e:
            # Release any acquired locks on exception
            for acquired_lock in reversed(acquired_locks):
                acquired_lock.release()
            raise e

    def _release_locks(self, locks):
        """Release multiple locks in reverse order."""
        for lock in reversed(locks):
            lock.release()

    def _check_locks_available(self):
        """Check if all locks are available (not locked by current thread)."""
        return {
            "buffer_lock_available": not self._buffer_lock.locked(),
            "path_lock_available": not self._path_lock.locked(),
            "history_lock_available": not self._history_lock.locked(),
            "alpha_lock_available": not self._alpha_lock.locked(),
        }

    def list_audio_devices(self):
        """List available audio input and output devices."""
        self.latency_tester.print_device_list()

    def set_input_device(self, device_index: int):
        """Set the input device."""
        self.audio_streamer.input_device = device_index
        self.audio_streamer.init_audio()  # reinitialize audio streamer
        self.latency_tester.input_device_index = device_index
        self.latency_tester.test_input_latency()  # rerun input latency test

    def set_output_device(self, device_index: int):
        """Set the output device."""
        self.output_device = device_index
        self.latency_tester.output_device_index = device_index
        self.latency_tester.test_output_latency()  # rerun output latency test

    def _preprocess_reference_features(self):
        """Preprocess reference features for optimized distance computation."""
        # Ensure features are contiguous and float32 for numba
        self.solo_features = np.ascontiguousarray(self.solo_features, dtype=np.float32)
        self.orch_features = np.ascontiguousarray(self.orch_features, dtype=np.float32)

        # Pre-allocate feature buffer
        self._feature_buffer = np.empty(self.solo_features.shape[0], dtype=np.float32)

    def load_reference_features(self):
        """Load or compute features for the solo and orchestral reference audio files."""
        # Store original paths for TSM
        self.original_solo_reference = self.solo_reference
        self.original_orch_reference = self.orch_reference

        # Load solo audio and compute hash key
        if isinstance(self.solo_reference, str) and self.solo_reference.endswith(
            ".pkl"
        ):
            with open(self.solo_reference, "rb") as f:
                self.solo_features = pickle.load(f)
            self.solo_cache_key = None
        else:
            solo_audio, _ = lb.load(self.solo_reference, sr=self.sr)
            self.solo_cache_key = generate_cache_key(solo_audio)
            self.solo_features = load_cache(
                self.cache_dir,
                self.solo_cache_key,
                f"{self.feature_extractor.__name__}_features.pkl",
            )

            if self.solo_features is None:
                self.solo_features = self.feature_extractor(
                    y=solo_audio, sr=self.sr, hop_length=self.hop_length
                )
                if self.save_cache:
                    store_cache(
                        self.cache_dir,
                        self.solo_cache_key,
                        self.solo_features,
                        f"{self.feature_extractor.__name__}_features.pkl",
                    )

        # Load orch audio and compute hash key
        if isinstance(self.orch_reference, str) and self.orch_reference.endswith(
            ".pkl"
        ):
            with open(self.orch_reference, "rb") as f:
                self.orch_features = pickle.load(f)
            self.orch_cache_key = None
        else:
            orch_audio, _ = lb.load(self.orch_reference, sr=self.sr)
            self.orch_cache_key = generate_cache_key(orch_audio)
            self.orch_features = load_cache(
                self.cache_dir,
                self.orch_cache_key,
                f"{self.feature_extractor.__name__}_features.pkl",
            )
            if self.orch_features is None:
                self.orch_features = self.feature_extractor(
                    y=orch_audio, sr=self.sr, hop_length=self.hop_length
                )
                if self.save_cache:
                    store_cache(
                        self.cache_dir,
                        self.orch_cache_key,
                        self.orch_features,
                        f"{self.feature_extractor.__name__}_features.pkl",
                    )

    def _load_orchestral_audio(self):
        """Load orchestral reference audio for TSM playback."""
        try:
            # Use original audio file path if available (for TSM), otherwise use current reference
            orch_audio_path = getattr(
                self, "original_orch_reference", self.orch_reference
            )

            if orch_audio_path and not orch_audio_path.endswith(".pkl"):
                self.orch_audio, _ = lb.load(orch_audio_path, sr=self.sr)
                self.max_length = len(self.orch_audio) * 2
                print(
                    f"Loaded orchestral audio: {len(self.orch_audio)/self.sr:.2f} seconds"
                )
            else:
                if self.warnings_on:
                    warnings.warn(
                        "Warning: TSM requires orchestral reference as audio file, not pickle"
                    )
                self.tsm_enabled = False
        except Exception as e:
            print(f"Error loading orchestral audio: {e}")
            self.tsm_enabled = False

    def _load_solo_audio(self):
        """Load solo reference audio for playback if orchestra is silent at beginning."""
        try:
            if self.solo_reference and not self.solo_reference.endswith(".pkl"):
                self.solo_audio, _ = lb.load(self.solo_reference, sr=self.sr)
                self.solo_audio = self.solo_audio * 32767  # convert to int
                print(f"Loaded solo audio: {len(self.solo_audio)/self.sr:.2f} seconds")

                # get initial tempo
                tempo, _ = lb.beat.beat_track(
                    y=self.solo_audio[
                        : int(self.initial_constant_period_frames * self.hop_length)
                    ],
                    sr=self.sr,
                )  # get initial tempo during constant period

                # if tempo is 0, it means piano is not active during constant period
                if tempo != 0:
                    print(f"Initial tempo: {int(tempo)} BPM")
                else:
                    print("Piano not active during constant period.")
            else:
                if self.warnings_on:
                    warnings.warn(
                        "Warning: Solo-only mode requires solo reference as audio file, not pickle"
                    )
        except Exception as e:
            print(f"Error loading solo reference audio: {e}")

    def reset(self):
        """Reset the alignment state."""

        # check if the input audio device is still available
        if self.streaming and self.audio_streamer.audio is not None:
            device_info = self.audio_streamer.audio.get_device_info_by_index(
                self.audio_streamer.input_device
            )
            assert device_info is not None, "Input audio device not available"

        # reset audio streamer
        if self.streaming:
            try:
                with self._buffer_lock:
                    self.buffer.clear()
            except Exception as e:
                print(f"Warning: Failed to clear buffer in reset: {e}")
        self.total_audio_samples = 0
        self.current_stream_index = 0
        self._get_and_update_mode(0)  # Initialize mode
        try:
            with self._path_lock:
                self.path = []  # Store full path for alignment
        except Exception as e:
            print(f"Warning: Failed to reset path in reset: {e}")

        # Initialize alignment matrices with windowing
        self.ref_length = self.orch_features.shape[1]

        # Use sliding window approach to limit memory usage
        max_query_length = min(2 * self.ref_length, self.window_size)
        self.D = np.full((max_query_length, self.ref_length), np.inf, dtype=np.float32)
        self.B = np.full((max_query_length, self.ref_length), -1, dtype=np.int32)

        # Keep track of window offset
        self.window_offset = 0

        self.orchestra = True
        self.solo_only = False

        # Reset alpha and history values following lock hierarchy
        try:
            with self._alpha_lock:
                self.current_alpha = 1.0
                self.base_alpha = 1.0
        except Exception as e:
            print(f"Warning: Failed to reset alpha values: {e}")

        try:
            with self._history_lock:
                self.alpha_history = []
                self.query_alpha_history = []  # Track alpha values for each query frame
                self.t_ref = np.arange(len(self.mode_array)) * self.hop_length / self.sr
                self.deviation_history = []
        except Exception as e:
            print(f"Warning: Failed to reset history values: {e}")

        self.pos = 0

        # time tracking for performance measurement
        self.total_feature_extraction_time = 0.0
        self.total_alignment_time = 0.0
        self.adjust_alpha_time = 0.0
        self.get_alpha_time = 0.0
        self.tsm_t = 0.0
        self.overall_latency = 0.0
        self.tsm_pos_sec = 0.0
        self.queue_time = 0.0
        self.frame_count = 0

        if self.recording:
            self.y_orchestra_out = np.empty(self.max_length)
            self.y_orchestra_pos = 0

            if self.streaming:
                self.y_solo_out = np.empty(self.max_length)
                self.y_solo_pos = 0

        # Clear audio queue
        if self.streaming:
            while not self.audio_streamer.audio_queue.empty():
                try:
                    self.audio_streamer.audio_queue.get_nowait()
                except queue.Empty:
                    break

    def _get_and_update_mode(self, i: int) -> bool:
        """Determine the mode (orchestra/solo) at the given index."""
        # record the previous mode to detect changes
        prev_mode = self.orchestra if i != 0 else None

        # Determine mode based on the index
        if self.mode_array[i] != 0:  # solo mode
            self.orchestra = False
            if self.mode_array[i] == 2:  # solo_only mode
                self.solo_only = True
        else:  # orchestra mode
            self.orchestra = True
            self.solo_only = False

        # If the mode has changed, print a message and call callback
        if i != 0 and prev_mode is not None and prev_mode != self.orchestra:
            mode_msg = f"Mode switched to {'orchestra' if self.orchestra else 'solo'} at reference time {i * self.hop_length / self.sr:.2f} seconds."
            print(mode_msg)

            # Call callback if provided and there is an audio_streamer attribute
            if hasattr(self, "audio_streamer") and self.audio_streamer.audio_callback:
                self.audio_streamer.audio_callback(
                    {
                        "event": "mode_change",
                        "mode": "orchestra" if self.orchestra else "solo",
                        "reference_time": i * self.hop_length / self.sr,
                        "message": mode_msg,
                    }
                )

        return self.orchestra

    def _get_chroma_cqt_features(self) -> tuple:
        """
        Compute or load chroma CQT features for the solo and orchestral references.
        """
        # Use hash-based cache
        if self.cache_dir:
            # Load solo chroma CQT
            if isinstance(self.solo_reference, str) and self.solo_reference.endswith(
                ".pkl"
            ):
                with open(self.solo_reference, "rb") as f:
                    solo_audio = pickle.load(f)
                solo_cache_key = None
            else:
                solo_audio, _ = lb.load(self.solo_reference, sr=self.sr)
                solo_cache_key = generate_cache_key(solo_audio)
            solo_features_chroma_cqt = load_cache(
                self.cache_dir, solo_cache_key, "chroma_cqt_features.pkl"
            )

            # Load orch chroma CQT
            if isinstance(self.orch_reference, str) and self.orch_reference.endswith(
                ".pkl"
            ):
                with open(self.orch_reference, "rb") as f:
                    orch_audio = pickle.load(f)
                orch_cache_key = None
            else:
                orch_audio, _ = lb.load(self.orch_reference, sr=self.sr)
                orch_cache_key = generate_cache_key(orch_audio)
            orch_features_chroma_cqt = load_cache(
                self.cache_dir, orch_cache_key, "chroma_cqt_features.pkl"
            )

            if (
                solo_features_chroma_cqt is not None
                and orch_features_chroma_cqt is not None
            ):
                return solo_features_chroma_cqt, orch_features_chroma_cqt

        # If not cached, compute
        if (
            isinstance(self.solo_reference, str)
            and self.solo_reference.endswith(".pkl")
            and isinstance(self.orch_reference, str)
            and self.orch_reference.endswith(".pkl")
        ):
            raise ValueError(
                "Cannot compute chroma CQT features from a pickle file. Please provide an audio file."
            )

        y_solo, _ = lb.load(self.solo_reference, sr=self.sr)
        y_orch, _ = lb.load(self.orch_reference, sr=self.sr)

        solo_features_chroma_cqt = lb.feature.chroma_cqt(
            y=y_solo,
            sr=self.sr,
            hop_length=self.hop_length,
            norm=None,
            window=self.feature_window,
        )
        orch_features_chroma_cqt = lb.feature.chroma_cqt(
            y=y_orch,
            sr=self.sr,
            hop_length=self.hop_length,
            norm=None,
            window=self.feature_window,
        )

        # Save features to cache if specified
        if self.save_cache and self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            solo_cache_key = generate_cache_key(y_solo)
            orch_cache_key = generate_cache_key(y_orch)
            store_cache(
                self.cache_dir,
                solo_cache_key,
                solo_features_chroma_cqt,
                "chroma_cqt_features.pkl",
            )
            store_cache(
                self.cache_dir,
                orch_cache_key,
                orch_features_chroma_cqt,
                "chroma_cqt_features.pkl",
            )

        return solo_features_chroma_cqt, orch_features_chroma_cqt

    def _compute_mode_array(
        self, threshold: float = -10, time: float = 2.5
    ) -> np.ndarray:
        """
        Computes the mode given two chroma features.

        Args:
            solo_features (np.ndarray): Reference chroma features.
            orch_features (np.ndarray): Accompaniment chroma features.
            threshold (float): Threshold in dB for switching modes. Default is -10 dB.
            time (float): Time window in seconds to consider for mode switching. Default is 5 seconds.

        Returns:
            np.ndarray: Array indicating mode (1 for solo, 0 for orchestra) for each frame.
        """
        solo_features, orch_features = self._get_chroma_cqt_features()

        op = compute_mode_array(
            solo_features, orch_features, threshold, time, self.sr, self.hop_length
        )
        self.mode_array = op
        return op

    def switch_mode(self):
        """Switch between orchestra and solo mode."""
        self.orchestra = not self.orchestra

    def set_mode(self, mode: bool):
        """
        Set the mode explicitly. True for orchestra mode, False for solo mode.
        """
        self.orchestra = mode

    def _audio_processing_thread(self):
        """Thread function for processing audio from the queue."""
        while not self.audio_streamer.stop_event.is_set():
            try:
                # Get audio data from queue with timeout
                start_t = time.perf_counter()
                audio_data = self.audio_streamer.audio_queue.get(timeout=0.1)
                self.queue_time = time.perf_counter() - start_t

                # Process the audio chunk
                self.add_audio_chunk(audio_data)

                # Call callback with alignment update if provided
                if self.audio_callback and self.path:
                    self.audio_callback(
                        {
                            "event": "alignment_update",
                            "query_time": self.current_stream_index
                            * self.hop_length
                            / self.sr,
                            "reference_time": (
                                self.path[-1] * self.hop_length / self.sr
                                if self.path
                                else 0
                            ),
                            "mode": "orchestra" if self.orchestra else "solo",
                        }
                    )

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in audio processing thread: {e}")
                import traceback

                traceback.print_exc()

    def _tsm_playback_thread(self):
        """Thread function for TSM orchestral playback."""
        if not self.tsm_enabled or self.orch_audio is None:
            return

        try:
            # Initialize PyAudio for output
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sr,
                output=True,
                output_device_index=self.output_device,
            )
            print("Opened output audio stream in tsm_playback_thread")

            # Call callback for TSM start
            if self.audio_callback:
                self.audio_callback(
                    {
                        "event": "tsm_playback_start",
                        "message": "TSM orchestral playback started",
                    }
                )

            while (
                not self.tsm.stop_event.is_set()
                and self.pos <= len(self.tsm.xh) - self.tsm.L
            ):
                Ha = self.update_tsm_orch(self.pos, stream)
                self.pos += Ha

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Call callback for TSM end
            if self.audio_callback:
                self.audio_callback(
                    {
                        "event": "tsm_playback_end",
                        "message": "TSM orchestral playback ended",
                    }
                )

        except Exception as e:
            print(f"Error in TSM playback thread: {e}")
            if self.audio_callback:
                self.audio_callback(
                    {"event": "tsm_error", "message": f"TSM playback error: {e}"}
                )

    def update_tsm_orch(self, pos, stream=None):
        """Update the TSM orchestral playback.

        Args:
            pos (int): The current position in the TSM playback.
            stream (pyaudio.Stream, optional): The output stream for TSM playback. Defaults to None.

        Returns:
            int: The number of frames to advance in the TSM playback.
        """
        # Predictive lag compensation: play ahead by lag_samples
        if hasattr(self, "lag_samples"):
            predictive_pos = pos + self.lag_samples
        else:
            predictive_pos = pos

        # compute reference frame index
        ref_frame = int(pos / self.hop_length)

        # find the closest smaller query frame corresponding to the reference frame
        query_frame = self._find_query_frame(ref_frame)

        # update the TSM alpha using reverse lookup
        alpha_value = 1.0  # default value
        try:
            with self._history_lock:
                try:
                    alpha_value = self.query_alpha_history[query_frame]
                except IndexError:
                    if len(self.query_alpha_history) > 0:
                        alpha_value = self.query_alpha_history[-1]
                        if self.warnings_on:
                            warnings.warn(
                                f"No alpha history for query frame {query_frame}, using last alpha"
                            )
                    else:
                        alpha_value = 1.0
                        if self.warnings_on:
                            warnings.warn("No alphas have been computed yet, using 1.0")

                self.alpha_history.append(round_alpha(alpha_value, self.hop_length))
        except Exception as e:
            print(f"Warning: Failed to acquire history lock in update_tsm_orch: {e}")
            # Continue with default alpha value

        # Set TSM alpha outside of lock to avoid potential deadlocks
        self.tsm.alpha = alpha_value

        Ha, orch_out = self.tsm.update_stream(predictive_pos, stream)

        # if in initial constant period and solo_only mode, stream reference solo out
        if self.streaming:
            if (
                self.solo_only
                and int(pos / self.hop_length) < self.initial_constant_period_frames
            ):
                stream.write(self.solo_audio[pos : pos + Ha].astype(np.int16).tobytes())
            else:
                stream.write(orch_out.astype(np.int16).tobytes())

        self.tsm_t = self.tsm.tsm_elapsed_t
        self.frame_count += 1
        if self.recording:
            audio_size = len(orch_out)
            self.y_orchestra_out[
                self.y_orchestra_pos : self.y_orchestra_pos + audio_size
            ] = orch_out
            self.y_orchestra_pos += audio_size
        return Ha

    def _find_query_frame(self, ref_frame):
        """Find the closest smaller query frame corresponding to the reference frame"""
        if ref_frame == 0:
            return 0

        # Acquire path lock to safely read the path
        try:
            with self._path_lock:
                # Safety check for empty path
                if not self.path:
                    if self.warnings_on:
                        warnings.warn(
                            f"Path is empty, cannot find query frame for reference frame {ref_frame}"
                        )
                    return 0

                # Cache path data to prevent race conditions
                path_length = len(self.path)
                path_data = (
                    self.path.copy()
                )  # Make a local copy to prevent race conditions

                # Search for the closest smaller query frame
                query_frame = 0  # Default to first frame
                search_start = min(
                    path_length - 1, 100
                )  # Search at most 100 frames back

                for i in range(
                    path_length - 1, max(-1, path_length - search_start - 1), -1
                ):
                    if path_data[i] <= ref_frame:
                        query_frame = i
                        break
                else:  # if no query frame is found, use the last query frame
                    if self.warnings_on:
                        warnings.warn(
                            f"No query frame found for reference frame {ref_frame}, using last query frame"
                        )
                    query_frame = path_length - 1

                # Safety check to ensure query_frame is within bounds
                query_frame = max(0, min(query_frame, path_length - 1))

                return query_frame
        except Exception as e:
            print(f"Warning: Failed to acquire path lock in _find_query_frame: {e}")
            return 0

    def add_audio_chunk(self, audio: np.ndarray):
        """Add an audio chunk to the buffer and update the alignment."""
        # Ensure input is float32 for consistency
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        if self.recording:
            self.y_solo_out[self.y_solo_pos : self.y_solo_pos + len(audio)] = audio
            self.y_solo_pos += len(audio)

        # Add to buffer with timeout to prevent deadlocks
        try:
            with self._buffer_lock:
                self.buffer.append(audio)
        except Exception as e:
            print(f"Warning: Failed to add audio chunk to buffer: {e}")
            return

        self.total_audio_samples += audio.shape[0]

        self._update_alignment_stream()

    def start_live_streaming(self, reset: bool = True):
        """Start live audio streaming and processing."""
        if self.audio_streamer.is_streaming:
            print("Live streaming is already active.")
            return

        # Reset state if specified
        if reset:
            self.reset()

        # Start the audio streamer
        print("Starting input processing...")
        self.audio_streamer.start_live_streaming(self._audio_processing_thread)

        # Reset TSM state
        if self.tsm_enabled:
            self.tsm.stop_event.clear()
            self.alpha_update_counter = 0
            self.current_alpha = 1.0

        # Start TSM playback thread
        print("Starting TSM orchestral playback thread...")
        if self.tsm_enabled:
            self.tsm_thread = threading.Thread(target=self._tsm_playback_thread)
            self.tsm_thread.daemon = True
            self.tsm_thread.start()

        print("Live streaming started successfully!")

    def stop_live_streaming(self):
        """Stop live audio streaming and processing."""

        # Stop the audio streamer
        if self.streaming:
            # Stop TSM first
            if self.tsm_enabled and self.tsm_thread:
                print("Stopping TSM orchestral playback...")
                self.tsm.stop_event.set()
                if self.tsm_thread.is_alive():
                    self.tsm_thread.join(timeout=2.0)
            self.audio_streamer.stop_live_streaming()

        # Process any remaining audio in buffer with timeout
        try:
            # Use threading with timeout to prevent infinite waiting
            def process_remaining_audio():
                try:
                    self.end_stream()
                except Exception as e:
                    print(f"Error in end_stream: {e}")

            process_thread = threading.Thread(target=process_remaining_audio)
            process_thread.daemon = True
            process_thread.start()

            # Wait for processing with shorter timeout
            process_thread.join(timeout=5.0)

            if process_thread.is_alive():
                if self.warnings_on:
                    warnings.warn(
                        "Timeout while processing remaining audio. Some data may be lost."
                    )

        except Exception as e:
            print(f"Warning: Error while processing remaining audio: {e}")

        print("Live streaming stopped.")

    def _compute_feature_row(self) -> Optional[np.ndarray]:
        """Compute the feature row for the current audio chunk in the buffer and remove it from the buffer."""
        start_time = time.perf_counter()

        audio_chunk = self.buffer.peek(self.feature_window).flatten()
        if audio_chunk is None:
            return None

        # Copy to pre-allocated buffer to avoid repeated allocations
        np.copyto(self._audio_chunk_buffer[: len(audio_chunk)], audio_chunk)

        # Use the pre-allocated buffer
        if len(audio_chunk) < self.feature_window:
            self._audio_chunk_buffer[len(audio_chunk) :] = 0

        # Extract features directly into buffer
        if self.feature_extractor == lb.feature.chroma_stft:
            features = self.feature_extractor(
                y=self._audio_chunk_buffer,
                sr=self.sr,
                hop_length=self.hop_length,
                n_fft=self.feature_window,
                center=False,
            )
        else:
            features = self.feature_extractor(
                y=self._audio_chunk_buffer, sr=self.sr, hop_length=self.hop_length
            )

        # Copy to pre-allocated feature buffer
        np.copyto(self._feature_buffer, features[:, 0])

        self.total_feature_extraction_time += (
            time.perf_counter() - start_time
        )  # Measure feature extraction time
        return self._feature_buffer

    def get_alpha(
        self,
        i,
        history: int = constants.DEFAULT_ALPHA_LOOKBACK,
        default_alpha: float = 1.0,
    ) -> float:
        """
        Calculate the alpha (playback speed factor) value based on the path and desired history window.

        Args:
            i (int): The current index in the path for which to calculate the alpha value.
            history (int): The number of previous locations to consider for calculating the alpha value.
            default_alpha (float): The default alpha value to return if not enough history is available.

        Returns:
            float: The calculated alpha value.
        """
        start_t = time.perf_counter()

        # first 10 seconds of playback is 1.0x speed
        if i <= self.initial_constant_period_frames:
            return 1.0

        # check if cache is initialized and matches the history
        if not hasattr(self, "_alpha_cache") or self._alpha_cache.history != history:
            # Create a new cache if not already initialized
            self._alpha_cache = AlphaCache(history=history)
        alpha = _get_alpha_numba(
            self.path,
            i,
            history=history,
            default_alpha=default_alpha,
            max_timewarp_factor=self.max_timewarp_factor,
            x=self._alpha_cache.x,
            sum_x=self._alpha_cache.sum_x,
            sum_x2=self._alpha_cache.sum_x2,
        )
        self.get_alpha_time += time.perf_counter() - start_t

        return alpha

    def _update_alignment_stream(self):
        """
        Update the alignment based on the current buffer state and the current mode. Applies to during streaming.
        """
        while True:
            # Check buffer size using thread-safe method
            buffer_size = self.buffer.get_length()
            if buffer_size < self.feature_window:
                break

            self._update_alignment()

    def save_audio(self, query_path=None):
        """Save the audio to a file.

        Args:
            query_path (str, optional): The path to the query audio. Defaults to None.
        """
        if query_path:  # system is given a query path if it is simulated realtime
            self.y_solo_out, _ = lb.core.load(query_path, sr=self.sr)
        else:
            total_output_latency = (
                self.latency_tester.output_latency + self.additional_latency
            )
            self.y_solo_out = self.y_solo_out[
                int(total_output_latency * self.sr) :
            ]  # clip to remove lag in recording

        self.y_orchestra_out = self.y_orchestra_out[: self.y_orchestra_pos]

        comp_audio = makeStereo(self.y_solo_out, self.y_orchestra_out)
        writeStereo(self.outfile, comp_audio, self.sr)
        print(f"Saved recording to {self.outfile}.")

    def end_stream(self):
        """
        Finish alignment after streaming ends.
        """
        max_iterations = 100  # Reduced safety limit to prevent long waits
        iteration_count = 0

        while self.buffer.get_length() > 0 and iteration_count < max_iterations:
            try:
                self._update_alignment()
                iteration_count += 1
            except Exception as e:
                if self.warnings_on:
                    warnings.warn(f"Error during end_stream processing: {e}")
                break

        if iteration_count >= max_iterations:
            if self.warnings_on:
                warnings.warn(
                    "Maximum iterations reached in end_stream. Some audio may not be processed."
                )

        if self.recording:
            self.save_audio()

    def _update_sliding_window(self):
        """
        Slide the alignment window to manage memory usage.
        """
        current_row = self.current_stream_index - self.window_offset
        if current_row >= self.D.shape[0] - 1:
            self._slide_window()
            current_row = self.current_stream_index - self.window_offset
        return current_row

    ### ALPHA FUNCTIONS ####
    def adjust_alpha(self, pos: int, lag_samples: int = 0):
        """Adjust the alpha value based on the current path length and history.

        Args:
            pos (int): The current position in the path.
            lag_samples (int, optional): The number of frames to lag. Defaults to 0.
        """
        start_t = time.perf_counter()

        # adjust for lag
        curr_frame = int(
            round((pos - lag_samples) / self.hop_length)
        )  # in feature frames

        # Get path information and calculate deviation in a single lock acquisition
        deviation = 0
        try:
            with self._path_lock:
                if curr_frame >= 0:
                    latest_frame = int(
                        max(0, len(self.path) - (lag_samples / self.hop_length) - 1)
                    )  # in feature frames
                    deviation = curr_frame - self.path[latest_frame]
        except Exception as e:
            print(f"Warning: Failed to acquire path lock in adjust_alpha: {e}")
            return

        # Update deviation history
        try:
            with self._history_lock:
                self.deviation_history.append(deviation)
        except Exception as e:
            print(f"Warning: Failed to acquire history lock in adjust_alpha: {e}")
            return

        scale = calc_scale_from_deviation(
            deviation, self.alpha_adjust_sensitivity, self.alpha_adjust_max_scale
        )

        # Update alpha value
        try:
            with self._alpha_lock:
                self.current_alpha = scale * self.base_alpha
                self.current_alpha = np.clip(
                    self.current_alpha,
                    1 / self.max_timewarp_factor,
                    self.max_timewarp_factor,
                )  # make sure that current alpha is still within range
        except Exception as e:
            print(f"Warning: Failed to acquire alpha lock in adjust_alpha: {e}")
            return

        self.adjust_alpha_time += time.perf_counter() - start_t

    def _update_alpha(self, pos):
        """Update the alpha value based on the current path length and history."""
        # Get path information in a single lock acquisition to avoid deadlocks
        path_len = 0
        idx = 0
        try:
            with self._path_lock:
                path_len = len(self.path)
                if path_len > 0:
                    idx = path_len - 1
        except Exception as e:
            print(f"Warning: Failed to acquire path lock in _update_alpha: {e}")
            return

        if self.tsm_enabled and path_len > 0:
            self.alpha_update_counter += 1
            if self.alpha_update_counter >= self.alpha_update_frequency:
                new_alpha = self.get_alpha(idx, history=self.alpha_lookback)
                try:
                    with self._alpha_lock:
                        if (
                            abs(new_alpha - self.current_alpha) > 0.01
                        ):  # only update if the change is greater than 1%
                            self.current_alpha = new_alpha
                            self.base_alpha = self.current_alpha
                            if hasattr(self, "audio_callback") and self.audio_callback:
                                self.audio_callback(
                                    {
                                        "event": "alpha_update",
                                        "alpha": self.current_alpha,
                                        "message": f"Alpha updated to {self.current_alpha:.3f}",
                                    }
                                )
                except Exception as e:
                    print(f"Warning: Failed to acquire alpha lock: {e}")
                    return
                self.alpha_update_counter = 0
            elif (
                path_len - 1 > self.initial_constant_period_frames
                and (self.alpha_update_counter % self.alpha_adjust_frequency == 0)
                and not self.orchestra
                and path_len > self.alpha_adjust_max_frame_deviation
            ):
                self.adjust_alpha(pos)

        # Append current alpha to query_alpha_history for reverse lookup
        try:
            with self._history_lock:
                self.query_alpha_history.append(self.current_alpha)
        except Exception as e:
            print(f"Warning: Failed to acquire history lock in _update_alpha: {e}")
            return

    ### UPDATE FUNCTIONS ####
    def _update_path(self, current_row):
        """
        Update the alignment path based on the current mode and buffer state.
        """
        if self.current_stream_index == 0:
            print(f"Initial mode: {'orchestra' if self.orchestra else 'solo'}")

        start_time = time.perf_counter()

        # Acquire locks safely using the helper method
        try:
            acquired_locks = self._acquire_locks_safely(
                self._buffer_lock, self._path_lock
            )

            try:
                if self.orchestra:  # orchestra mode
                    self._update_alignment_row_orchestra()
                else:  # solo mode
                    # Compute feature row and update alignment atomically
                    row_feature = self._compute_feature_row()
                    if row_feature is None:
                        raise ValueError(
                            "Buffer does not have enough data to compute feature row."
                        )

                    # Use optimized cost computation
                    costs = compute_cosine_distance(row_feature, self.solo_features)
                    self._update_alignment_row_solo(current_row, costs)

                # Remove the first hop_length frame after processing (consistent for both modes)
                self.buffer.read(self.hop_length)

            finally:
                # Release locks in reverse order
                self._release_locks(acquired_locks)

        except Exception as e:
            print(f"Warning: Failed to update alignment: {e}")
            return

        self.total_alignment_time += (
            time.perf_counter() - start_time
        )  # Measure alignment time

        # Update alpha for this query frame - call outside of any locks to prevent deadlocks
        if self.tsm_enabled:
            self._update_alpha(self.pos)

        self.current_stream_index += 1

    def _check_end_of_reference(self):
        """Check if the end of the reference audio has been reached and handle accordingly."""
        if self.path and self.path[-1] >= self.ref_length - 1:
            end_msg = f"Reached the end of the reference audio at query time {self.current_stream_index * self.hop_length / self.sr:.2f}s. No further alignment updates will be made."
            print(end_msg)

            # Call callback if provided
            if hasattr(self, "audio_streamer") and self.audio_streamer.audio_callback:
                self.audio_streamer.audio_callback(
                    {
                        "event": "alignment_complete",
                        "message": end_msg,
                        "query_time": self.current_stream_index
                        * self.hop_length
                        / self.sr,
                    }
                )

            if hasattr(self, "buffer"):
                self.buffer.clear()  # Clear buffer since no further updates are needed
            return True  # end of reference

    def _update_alignment(self):
        """
        Update the alignment based on the current buffer state and the current mode.
        """
        start_time = time.perf_counter()

        # Check if we need to slide the window
        current_row = self._update_sliding_window()

        # Check if we are at end of the reference
        if self._check_end_of_reference():
            return

        # Determine the current mode
        if not self.path:
            self._get_and_update_mode(self.current_stream_index)
        else:
            self._get_and_update_mode(self.path[-1])

        self.total_alignment_time += (
            time.perf_counter() - start_time
        )  # Measure alignment time

        # Update alignment based on mode
        self._update_path(current_row)

    def _slide_window(self):
        """Slide the alignment window to manage memory usage."""
        # Shift window by half its size
        shift = self.D.shape[0] // 2

        # Ensure shift is valid
        if shift <= 0:
            return

        # shift data
        self.D = np.roll(self.D, -shift, axis=0)
        self.B = np.roll(self.B, -shift, axis=0)

        # Clear the upper half (which now contains old data)
        self.D[shift:] = np.inf
        self.B[shift:] = -1

        # Update window offset
        self.window_offset += shift

    def _update_alignment_row_orchestra(self):
        """
        Update the alignment row for orchestra mode.
        """
        # Note: This method should be called with _path_lock already held
        if self.current_stream_index == 0:  # First row initialization
            start_time = time.perf_counter()

            self.path.append(0)
            self.D[0, 0] = 0

            self.total_alignment_time += time.perf_counter() - start_time
        else:
            start_time = time.perf_counter()

            prev_i, prev_j = len(self.path) - 1, self.path[-1]
            new_i, new_j = prev_i + 1, prev_j + 1

            if new_j < self.ref_length:
                self.path.append(new_j)
                # Use windowed indices for matrix access
                windowed_prev_i = prev_i - self.window_offset
                windowed_new_i = new_i - self.window_offset
                self.D[windowed_new_i, new_j] = self.D[windowed_prev_i, prev_j]
                self.B[windowed_new_i, new_j] = 0
            self.total_alignment_time += time.perf_counter() - start_time

    def _update_alignment_row_solo(self, i: int, costs: np.ndarray):
        """
        Update the alignment row for solo mode.

        Args:
            i (int): Index of the current stream (solo or orchestra).
            costs (np.ndarray): Cost array for the current feature row.
        """
        # Note: This method should be called with _path_lock already held
        if self.current_stream_index == 0:
            start_time = time.perf_counter()
            self.path.append(0)
            self.D[0, 0] = costs[0]
            self.total_alignment_time += time.perf_counter() - start_time
        else:
            start_time = time.perf_counter()
            # Use numba-optimized function
            best_j = self.noa_update_function(
                i,
                None,
                costs,
                self.D,
                self.B,
                self.dn,
                self.dm,
                self.dw,
                self.ref_length,
            )
            self.path.append(best_j)
            self.total_alignment_time += time.perf_counter() - start_time

    def skip(self, skip_time: float):
        """Skip the audio to a specific time.

        Args:
            time (float): The time to skip to in seconds.
        """

        # reset NOA state
        self.reset()

        # Clamp time
        skip_time = max(0, min(skip_time, self.ref_length * self.hop_length / self.sr))

        # update indices
        self.current_stream_index = int(
            skip_time * self.hop_length / self.sr
        )  # update NOA position
        self.pos = int(skip_time * self.sr)  # update TSM position

        # update buffer first (lower in hierarchy)
        if hasattr(self, "buffer"):
            try:
                with self._buffer_lock:
                    self.buffer.clear()
            except Exception as e:
                print(f"Warning: Failed to clear buffer in skip: {e}")

        # update path (higher in hierarchy)
        try:
            with self._path_lock:
                self.path = list(np.arange(self.current_stream_index))
        except Exception as e:
            print(f"Warning: Failed to update path in skip: {e}")

        # update mode
        self._get_and_update_mode(self.current_stream_index)
        self.D[0, 0] = 0

        # call callback if provided
        if hasattr(self, "audio_streamer") and self.audio_streamer.audio_callback:
            self.audio_streamer.audio_callback(
                {"event": "skip", "time": skip_time, "query_time": skip_time}
            )
        print(f"Skipped to {skip_time:.2f} seconds")

    ### INFO FUNCTIONS ####
    def get_current_alignment_info(self) -> dict:
        """Get detailed information about current alignment state."""
        return {
            "streaming_active": (
                self.audio_streamer.is_streaming
                if hasattr(self, "audio_streamer") and self.audio_streamer
                else False
            ),
            "current_mode": (
                "orchestra" if getattr(self, "orchestra", False) else "solo"
            ),
            "total_audio_samples": getattr(self, "total_audio_samples", False),
            "processed_samples": (
                min(
                    self.current_stream_index * self.hop_length,
                    self.total_audio_samples,
                )
                if hasattr(self, "current_stream_index")
                and hasattr(self, "hop_length")
                and hasattr(self, "total_audio_samples")
                else False
            ),
            "current_query_time": (
                self.current_stream_index * self.hop_length / self.sr
                if hasattr(self, "current_stream_index")
                and hasattr(self, "hop_length")
                and hasattr(self, "sr")
                else False
            ),
            "current_reference_time": (
                self.path[-1] * self.hop_length / self.sr
                if hasattr(self, "path")
                and self.path
                and hasattr(self, "hop_length")
                and hasattr(self, "sr")
                else 0
            ),
            "buffer_usage (%)": (
                self.buffer.size / self.buffer.max_frames * 100
                if hasattr(self, "buffer")
                and hasattr(self.buffer, "size")
                and hasattr(self.buffer, "max_frames")
                else False
            ),
            "window_offset": getattr(self, "window_offset", False),
            "feature_extraction_time": getattr(
                self, "total_feature_extraction_time", False
            ),
            "alignment_time": getattr(self, "total_alignment_time", False),
            "audio_queue_size": (
                self.audio_streamer.audio_queue.qsize()
                if hasattr(self, "audio_streamer")
                and hasattr(self.audio_streamer, "audio_queue")
                else 0
            ),
            "tsm_enabled": getattr(self, "tsm_enabled", False),
            "current_alpha": getattr(
                self, "current_alpha", 1.0
            ),  # default to 1.0 if not set
            "query_alpha_history_length": (
                len(self.query_alpha_history)
                if hasattr(self, "query_alpha_history")
                else 0
            ),
            "tsm_active": (
                self.tsm_thread.is_alive()
                if hasattr(self, "tsm_thread") and self.tsm_thread
                else False
            ),
        }

    def print_current_alignment_info(self):
        """Print detailed information about the current alignment state."""
        # Get current alignment info
        if not self.path:
            print("No alignment has been performed yet.")
            return
        info = self.get_current_alignment_info()

        print("-" * 50)
        print("Current Alignment State:")
        print("-" * 50)
        print(f"Streaming Active: {info['streaming_active']}")
        print(f"Mode: {info['current_mode']}")
        print(f"Total Audio Samples: {info['total_audio_samples']}")
        print(f"Processed Samples: {info['processed_samples']}")

        if info["current_query_time"] > 3600:  # Convert to hours if over 3600 seconds
            hours = int(info["current_query_time"] // 3600)
            minutes = int((info["current_query_time"] % 3600) // 60)
            seconds = info["current_query_time"] % 60
            print(
                f"Current Query Time: {hours} hours {minutes} minutes {seconds:.2f} seconds"
            )
        elif info["current_query_time"] > 60:  # Convert to minutes if over 60 seconds
            minutes = int(info["current_query_time"] // 60)
            seconds = info["current_query_time"] % 60
            print(f"Current Query Time: {minutes} minutes {seconds:.2f} seconds")
        else:
            print(f"Current Query Time: {info['current_query_time']:.2f} seconds")

        if (
            info["current_reference_time"] > 3600
        ):  # Convert to hours if over 3600 seconds
            hours = int(info["current_reference_time"] // 3600)
            minutes = int((info["current_reference_time"] % 3600) // 60)
            seconds = info["current_reference_time"] % 60
            print(
                f"Current Reference Time: {hours} hours {minutes} minutes {seconds:.2f} seconds"
            )
        elif (
            info["current_reference_time"] > 60
        ):  # Convert to minutes if over 60 seconds
            minutes = int(info["current_reference_time"] // 60)
            seconds = info["current_reference_time"] % 60
            print(f"Current Reference Time: {minutes} minutes {seconds:.2f} seconds")
        else:
            print(
                f"Current Reference Time: {info['current_reference_time']:.2f} seconds"
            )

        print(f"Buffer Usage: {info['buffer_usage (%)']:.2f}%")
        print(f"Audio Queue Size: {info['audio_queue_size']}")
        print(f"Window Offset: {info['window_offset']}")

        if info["tsm_enabled"]:
            print("TSM Enabled: Yes")
        else:
            print("TSM Enabled: No")

        if info["tsm_active"]:
            print("TSM is active.")
        else:
            print("TSM is not active.")

        print(f"Current Alpha: {info['current_alpha']:.2f}")
        print(f"Query Alpha History Length: {info['query_alpha_history_length']}")

        if (
            info["feature_extraction_time"] > 60
        ):  # Convert to minutes if over 60 seconds
            minutes = int(info["feature_extraction_time"] // 60)
            seconds = info["feature_extraction_time"] % 60
            print(f"Feature Extraction Time: {minutes} minutes {seconds} seconds")
        else:
            print(f"Feature Extraction Time: {info['feature_extraction_time']} seconds")

        if info["alignment_time"] > 60:  # Convert to minutes if over 60 seconds
            minutes = int(info["alignment_time"] // 60)
            seconds = info["alignment_time"] % 60
            print(f"Alignment Time: {minutes} minutes {seconds} seconds")
        else:
            print(f"Alignment Time: {info['alignment_time']} seconds")

        print("-" * 50)

    def get_alpha_tref(self):
        """Returns alpha history and corresponding times"""
        return self.alpha_history, self.t_ref

    def get_query_alpha_history(self):
        """Returns query alpha history for debugging and analysis"""
        return self.query_alpha_history

    #### PLOTTING FUNCTIONS ####
    def plot_alignment(self):
        """Plot the current alignment path."""
        if not self.path:
            print("No alignment path available to plot.")
            return

        path_array = np.array(self.path)
        plt.figure(figsize=(10, 10))
        plt.plot(
            path_array * self.hop_length / self.sr,
            np.arange(len(path_array)) * self.hop_length / self.sr,
            marker="o",
            linestyle="-",
            color="b",
            markersize=3,
        )
        plt.title("Alignment Path")
        plt.xlabel("Reference Time (s)")
        plt.ylabel("Query Time (s)")
        plt.grid()
        plt.show()

    def plot_alpha(self, alpha_true=None, t_start=None, t_end=None):
        plt.plot(
            np.arange(len(self.alpha_history)) * self.hop_length / self.sr,
            np.array(self.alpha_history),
            ".",
            label="TSM Alpha",
        )
        if alpha_true:
            plt.hlines(
                alpha_true,
                t_start,
                t_end,
                colors="lightgreen",
                linewidths=3,
                label="True",
            )
        plt.title(
            f"Alpha Values\nAlpha update = {self.alpha_update_frequency}\nAlpha adjust = {self.alpha_adjust_frequency}"
        )
        plt.xlabel("time (s)")
        plt.ylabel("alpha")
        plt.legend()
        plt.show()

    def plot_query_alpha_history(self):
        """Plot the query alpha history for debugging"""
        if not self.query_alpha_history:
            print("No query alpha history available to plot.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(
            np.arange(len(self.query_alpha_history)) * self.hop_length / self.sr,
            np.array(self.query_alpha_history),
            ".",
            label="Query Alpha History",
            markersize=2,
        )
        plt.title("Query Alpha History")
        plt.xlabel("Query Time (s)")
        plt.ylabel("Alpha")
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_devs(self):
        plt.plot(self.deviation_history, ".")
        plt.ylabel("Deviation (frames)")
        plt.show()

    def plot_mode(self):
        plt.plot(
            np.arange(len(self.mode_array)) * self.hop_length / self.sr,
            self.mode_array,
            ".",
            color="green",
            markersize=1,
        )
        plt.title("Mode Array")
        plt.xlabel("time (s)")
        plt.yticks([0, 1], ["Orchestra Led", "Piano Led"])
        plt.show()
