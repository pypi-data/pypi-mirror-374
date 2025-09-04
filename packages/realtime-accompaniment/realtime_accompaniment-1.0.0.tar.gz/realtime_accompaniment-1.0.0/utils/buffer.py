import numpy as np
import threading
from contextlib import contextmanager
from typing import Optional, Union
import warnings

class AudioBufferError(Exception):
    """Custom exception for AudioBuffer operations."""
    pass


class AudioBuffer:
    """
    A thread-safe circular buffer for storing audio samples. Allows appending, reading, peeking, and clearing samples.
    Supports overwriting old samples when the buffer is full if specified.
    """
    
    def __init__(self, max_frames: int, num_channels: int = 1, dtype=np.float32, 
                 overwrite: bool = False, raise_on_full: bool = True):
        """
        Initialize the AudioBuffer with a specified maximum number of frames, number of channels, data type, and overwrite option.
        
        Args:
            max_frames (int): Maximum number of frames to store in the buffer.
            num_channels (int): Number of audio channels. Default is 1 (mono).
            dtype (data-type): Data type of the audio samples. Default is np.float32.
            overwrite (bool): If True, overwrite old samples when the buffer is full. Default is False.
            raise_on_full (bool): If True, raise exception when buffer is full (when overwrite=False). 
                                If False, print warning. Default is True.
        """
        if max_frames <= 0:
            raise ValueError("max_frames must be positive")
        if num_channels <= 0:
            raise ValueError("num_channels must be positive")
            
        self.max_frames = max_frames
        self.num_channels = num_channels
        self.dtype = dtype
        self.overwrite = overwrite
        self.raise_on_full = raise_on_full

        # Initialize the buffer
        self.buffer = np.zeros((max_frames, num_channels), dtype=dtype)
        self.write_ptr = 0
        self.read_ptr = 0
        self.size = 0

        # Thread-safe access
        self.lock = threading.RLock()  # Use RLock for nested locking support

    @contextmanager
    def _lock_context(self):
        """Context manager for thread-safe operations."""
        self.lock.acquire()
        try:
            yield
        finally:
            self.lock.release()

    def _normalize_samples(self, samples):
        """Convert samples to the correct dtype and shape."""
        samples = np.asarray(samples, dtype=self.dtype)
        if samples.ndim == 1:
            samples = samples[:, np.newaxis]
        elif samples.ndim > 2:
            raise ValueError("Samples must be 1D or 2D array")
            
        if samples.shape[1] != self.num_channels:
            raise ValueError(f"Channel mismatch: expected {self.num_channels}, got {samples.shape[1]}")
        
        return samples

    def append(self, samples):
        """
        Append samples to the buffer using optimized bulk operations.
        
        Args:
            samples (array-like): Audio samples to append to the buffer.
            
        Raises:
            ValueError: If the number of channels in samples does not match the buffer's num_channels.
            AudioBufferError: If buffer is full and overwrite=False and raise_on_full=True.
        """
        samples = self._normalize_samples(samples)
        
        # Ensure we only keep the last max_frames samples if more are provided
        num_samples = samples.shape[0]
        if num_samples > self.max_frames:
            warnings.warn(f"Provided {num_samples} samples, but buffer can only hold {self.max_frames}. "
                          "Truncating to the last max_frames samples.")
            samples = samples[-self.max_frames:]
            num_samples = self.max_frames

        if num_samples == 0:
            return

        with self._lock_context():
            if not self.overwrite and self.size + num_samples > self.max_frames:
                excess = (self.size + num_samples) - self.max_frames
                if self.raise_on_full:
                    raise AudioBufferError(f"Buffer full. Cannot append {num_samples} samples. "
                                         f"Available space: {self.max_frames - self.size}")
                else:
                    print(f"Warning: Buffer full. Dropping {excess} samples.")
                    num_samples = self.max_frames - self.size
                    if num_samples <= 0:
                        return
                    samples = samples[:num_samples]

            # Optimized bulk copy with wraparound handling
            samples_written = 0
            while samples_written < num_samples:
                if self.size == self.max_frames and self.overwrite:
                    # Advance read pointer when overwriting
                    samples_to_overwrite = min(num_samples - samples_written, self.max_frames)
                    self.read_ptr = (self.read_ptr + samples_to_overwrite) % self.max_frames
                    self.size = max(0, self.size - samples_to_overwrite)

                # Calculate how many samples we can write before wrapping
                remaining_space_linear = self.max_frames - self.write_ptr
                samples_to_write = min(num_samples - samples_written, remaining_space_linear)
                
                # Bulk copy
                end_idx = self.write_ptr + samples_to_write
                sample_start = samples_written
                sample_end = samples_written + samples_to_write
                
                self.buffer[self.write_ptr:end_idx] = samples[sample_start:sample_end]
                
                # Update pointers
                self.write_ptr = (self.write_ptr + samples_to_write) % self.max_frames
                self.size = min(self.size + samples_to_write, self.max_frames)
                samples_written += samples_to_write

    def read(self, num_samples: int) -> Optional[np.ndarray]:
        """
        Read and remove samples from the buffer using optimized bulk operations.
        
        Args:
            num_samples (int): Number of samples to read from the buffer.
            
        Returns:
            np.ndarray or None: Array of samples read from the buffer, or None if empty.
        """
        if num_samples <= 0:
            return None
            
        with self._lock_context():
            if self.size == 0:
                return None
                
            # Clamp to available samples
            actual_samples = min(num_samples, self.size)
            output = np.zeros((actual_samples, self.num_channels), dtype=self.dtype)
            
            # Optimized bulk read with wraparound handling
            samples_read = 0
            while samples_read < actual_samples:
                # Calculate how many samples we can read before wrapping
                remaining_samples_linear = min(
                    actual_samples - samples_read,
                    self.max_frames - self.read_ptr,
                    self.size
                )
                
                if remaining_samples_linear <= 0:
                    break
                
                # Bulk copy
                end_idx = self.read_ptr + remaining_samples_linear
                output_start = samples_read
                output_end = samples_read + remaining_samples_linear
                
                output[output_start:output_end] = self.buffer[self.read_ptr:end_idx]
                
                # Update pointers
                self.read_ptr = (self.read_ptr + remaining_samples_linear) % self.max_frames
                self.size -= remaining_samples_linear
                samples_read += remaining_samples_linear
            
            return output if output.shape[0] > 0 else None

    def peek(self, num_samples: int, offset: int = 0) -> Optional[np.ndarray]:
        """
        Peek at samples in the buffer without removing them.
        
        Args:
            num_samples (int): Number of samples to peek at.
            offset (int): Offset from the current read position. Default is 0.
            
        Returns:
            np.ndarray or None: Array of samples peeked from the buffer, or None if empty.
        """
        if num_samples <= 0:
            return None
            
        with self._lock_context():
            if self.size == 0 or offset >= self.size:
                return None
                
            # Clamp to available samples
            actual_samples = min(num_samples, self.size - offset)
            if actual_samples <= 0:
                return None
                
            output = np.zeros((actual_samples, self.num_channels), dtype=self.dtype)
            
            # Start from read_ptr + offset
            peek_ptr = (self.read_ptr + offset) % self.max_frames
            
            # Optimized bulk peek with wraparound handling
            samples_peeked = 0
            while samples_peeked < actual_samples:
                remaining_samples_linear = min(
                    actual_samples - samples_peeked,
                    self.max_frames - peek_ptr
                )
                
                end_idx = peek_ptr + remaining_samples_linear
                output_start = samples_peeked
                output_end = samples_peeked + remaining_samples_linear
                
                output[output_start:output_end] = self.buffer[peek_ptr:end_idx]
                
                peek_ptr = (peek_ptr + remaining_samples_linear) % self.max_frames
                samples_peeked += remaining_samples_linear
            
            return output

    def pop(self) -> np.ndarray:
        """
        Remove and return the oldest sample from the buffer.
        
        Returns:
            np.ndarray: The oldest sample removed from the buffer.
            
        Raises:
            AudioBufferError: If the buffer is empty.
        """
        with self._lock_context():
            if self.size == 0:
                raise AudioBufferError("Buffer is empty. Cannot pop samples.")

            sample = self.buffer[self.read_ptr].copy()
            self.read_ptr = (self.read_ptr + 1) % self.max_frames
            self.size -= 1
            return sample

    def push_front(self, samples):
        """
        Add samples to the front of the buffer (before current read position).
        Useful for "un-reading" samples.
        
        Args:
            samples (array-like): Audio samples to add to the front.
            
        Raises:
            AudioBufferError: If there's not enough space and overwrite=False.
        """
        samples = self._normalize_samples(samples)
        num_samples = samples.shape[0]
        
        if num_samples == 0:
            return
            
        with self._lock_context():
            if not self.overwrite and self.size + num_samples > self.max_frames:
                if self.raise_on_full:
                    raise AudioBufferError(f"Not enough space to push {num_samples} samples to front")
                else:
                    warnings.warn("Not enough space. Truncating to available space.")
                    num_samples = self.max_frames - self.size
                    samples = samples[:num_samples]
                    
            # Move read pointer backwards
            self.read_ptr = (self.read_ptr - num_samples) % self.max_frames
            
            # Handle overwriting if necessary
            if self.overwrite and self.size + num_samples > self.max_frames:
                excess = (self.size + num_samples) - self.max_frames
                self.write_ptr = (self.write_ptr - excess) % self.max_frames
                self.size = self.max_frames - num_samples
            
            # Write samples at new read position
            write_pos = self.read_ptr
            for i in range(num_samples):
                self.buffer[write_pos] = samples[i]
                write_pos = (write_pos + 1) % self.max_frames
                
            self.size = min(self.size + num_samples, self.max_frames)

    def resize(self, new_max_frames: int, preserve_data: bool = True):
        """
        Resize the buffer. Optionally preserve existing data.
        
        Args:
            new_max_frames (int): New maximum number of frames.
            preserve_data (bool): Whether to preserve existing data. Default is True.
            
        Raises:
            ValueError: If new_max_frames is not positive.
        """
        if new_max_frames <= 0:
            raise ValueError("new_max_frames must be positive")
            
        with self._lock_context():
            if not preserve_data:
                # Simple case: just recreate buffer
                self.buffer = np.zeros((new_max_frames, self.num_channels), dtype=self.dtype)
                self.max_frames = new_max_frames
                self.write_ptr = 0
                self.read_ptr = 0
                self.size = 0
                return
                
            # Preserve data case
            if self.size == 0:
                # No data to preserve
                self.buffer = np.zeros((new_max_frames, self.num_channels), dtype=self.dtype)
                self.max_frames = new_max_frames
                return
                
            # Read all current data
            current_data = self.peek(self.size)
            
            # Create new buffer
            self.buffer = np.zeros((new_max_frames, self.num_channels), dtype=self.dtype)
            self.max_frames = new_max_frames
            self.write_ptr = 0
            self.read_ptr = 0
            self.size = 0
            
            # Restore data (may truncate if new buffer is smaller)
            if current_data is not None:
                self.append(current_data)

    def clear(self):
        """Clear the buffer by resetting pointers and size."""
        with self._lock_context():
            self.write_ptr = 0
            self.read_ptr = 0
            self.size = 0

    def get_length(self) -> int:
        """Get the current number of samples in the buffer."""
        with self._lock_context():
            return self.size

    def get_capacity(self) -> int:
        """Get the maximum capacity of the buffer."""
        return self.max_frames

    def get_free_space(self) -> int:
        """Get the number of free frames in the buffer."""
        with self._lock_context():
            return self.max_frames - self.size

    def is_full(self) -> bool:
        """Check if the buffer is full."""
        with self._lock_context():
            return self.size == self.max_frames

    def is_empty(self) -> bool:
        """Check if the buffer is empty."""
        with self._lock_context():
            return self.size == 0
            
    def get_usage_ratio(self) -> float:
        """Get the buffer usage as a ratio (0.0 to 1.0)."""
        with self._lock_context():
            return self.size / self.max_frames if self.max_frames > 0 else 0.0

    def to_array(self) -> np.ndarray:
        """
        Return all buffer contents as a contiguous array without removing data.
        
        Returns:
            np.ndarray: All samples in the buffer in order.
        """
        with self._lock_context():
            if self.size == 0:
                return np.array([]).reshape(0, self.num_channels)
            return self.peek(self.size)

    def __len__(self) -> int:
        """Return the current number of samples in the buffer."""
        return self.get_length()

    def __bool__(self) -> bool:
        """Return True if buffer is not empty."""
        return not self.is_empty()

    def __repr__(self) -> str:
        """String representation of the buffer."""
        return (f"AudioBuffer(size={self.size}/{self.max_frames}, "
                f"channels={self.num_channels}, dtype={self.dtype}, "
                f"overwrite={self.overwrite})")

    def __enter__(self):
        """Context manager entry."""
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.lock.release()