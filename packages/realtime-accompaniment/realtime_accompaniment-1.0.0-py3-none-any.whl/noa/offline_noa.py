import warnings

import numpy as np
import librosa as lb

from tsm.tsm import TSM
from noa.alignment._numba import compute_cosine_distance
from noa.noa import NOA
from utils.numeric import round_alpha


class OfflineNOA(NOA):
    """
    OfflineNOA class for performing NOA on pre-recorded audio files.
    """

    def __init__(self, *args, **kwargs) -> None:
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
            steps (np.ndarray): Array defining the steps for alignment. Default is [[1, 1, 2], [1, 2, 1]]. First step must be (1,1) to initialize alignment.
            weights (np.ndarray): Weights for the steps. Default is [1, 1, 2].
            noa_update_function (callable): Function to update the alignment row. Default is update_alignment_row_numba.
        """
        # initialize phase and progress
        self.phase = "init"
        self.progress = 0
        self.query_features = None  # to be initialized in align()

        super().__init__(*args, streaming=False, **kwargs)

        # load orch reference
        if self.tsm_enabled:
            if self.save_solo:
                audio_data = self.solo_audio
            else:
                audio_data = self.orch_audio
            # Use the parent class method to properly handle both audio files and pickle files
            if hasattr(self, "orch_audio") and self.orch_audio is not None:
                self.tsm = TSM(
                    sr=self.sr,
                    audio_data=audio_data,
                    recording=self.recording,
                    playback=False,
                    cache_dir=self.cache_dir,
                    save_cache=self.save_cache,
                )

    def reset(self):
        """Reset the alignment state."""
        self._get_and_update_mode(0)  # Initialize mode
        self.current_stream_index = 0
        self.path = []  # Store full path for alignment
        self.ref_length = self.orch_features.shape[1]
        self.total_alignment_time = 0.0
        self.get_alpha_time = 0.0
        self.adjust_alpha_time = 0.0
        self.append_elapsedtime = 0.0
        self.total_tsm_runtime = 0.0
        self.frame_count = 0

        max_query_length = (
            2 * self.ref_length
        )  # Allow for some flexibility in query length
        self.D = np.full((max_query_length, self.ref_length), np.inf, dtype=np.float32)
        self.B = np.full((max_query_length, self.ref_length), -1, dtype=np.int32)

        self.window_offset = 0

        self.orchestra = True
        self.current_alpha = 1.0
        self.base_alpha = 1.0

        self.alpha_history = []
        self.deviation_history = []

        self.progress = 0
        self.phase = "feature"

    def align(self, query_features, query_path):
        """
        Align the given query features to the reference features.

        Args:
            query_features (np.ndarray): The features of the query audio to be aligned. Should have shape (n_features, n_frames).
            query_path (str): Path to the query audio file. Note that this is not the query features!

        Returns:
            path (np.ndarray): shape (N, ) of aligned indices corresponding to the reference frames.
        """
        self.reset()  # Reset the alignment state
        self.query_features = np.ascontiguousarray(query_features, dtype=np.float32)
        pos = 0
        self.query_alpha_history = []

        # go through each frame of the query features
        self.phase = "align"

        for i in range(query_features.shape[1]):
            if i == 0:
                print(f"Initial mode: {'orchestra' if self.orchestra else 'solo'}")

            # Check if we are at end of the reference
            if self._check_end_of_reference():
                if self.recording:
                    self.save_audio(query_path)
                print(f"End of reference reached at frame {i}")
                self.phase = "finalize"
                return self.path

            self.progress = i / query_features.shape[1]

            # get mode
            if not self.path:
                mode = self._get_and_update_mode(self.current_stream_index)
            else:
                mode = self._get_and_update_mode(self.path[-1])

            if mode:  # Orchestra mode
                self._update_alignment_row_orchestra()
            else:  # Solo mode
                costs = compute_cosine_distance(
                    query_features[:, i], self.solo_features
                )
                self._update_alignment_row_solo(self.current_stream_index, costs)

            # update the alpha value
            self._update_alpha(pos)

            # update TSM
            if self.tsm_enabled and pos < len(self.tsm.xh):
                Ha = self.update_tsm_orch(pos)
                pos += Ha
            else:
                warnings.warn(
                    f"TSM is not enabled or at end of reference, skipping TSM update. Current query time: {i*self.hop_length/self.sr}."
                )
                break

            self.current_stream_index += 1

        if self.recording:
            self.save_audio(query_path)

        self.phase = "finalize"
        return self.path

    def update_tsm_orch(self, pos):
        """Update the TSM orchestral playback.

        Args:
            pos (int): The current position in the TSM playback.
        """

        # compute reference frame index
        ref_frame = int(pos / self.hop_length)

        # find the closest smaller query frame corresponding to the reference frame
        query_frame = self._find_query_frame(ref_frame)

        # update the TSM alpha
        try:
            self.tsm.alpha = self.query_alpha_history[query_frame]
        except IndexError:
            if len(self.query_alpha_history) > 0:
                self.tsm.alpha = self.query_alpha_history[-1]
                warnings.warn(
                    f"No alpha history for query frame {query_frame}, using last alpha"
                )
            else:
                self.tsm.alpha = 1.0
                warnings.warn(
                    f"No alpha history for query frame {query_frame}, using 1.0"
                )

        self.alpha_history.append(round_alpha(self.tsm.alpha, self.hop_length))

        # perform TSM
        Ha, tsm_out = self.tsm.update_stream(pos, stream=None)

        # append the TSM output to the orchestra output buffer
        if self.recording:
            audio_size = len(tsm_out)
            self.y_orchestra_out[
                self.y_orchestra_pos : self.y_orchestra_pos + audio_size
            ] = tsm_out

            # update the TSM position and the orchestra output position
            self.y_orchestra_pos += audio_size

        return Ha
