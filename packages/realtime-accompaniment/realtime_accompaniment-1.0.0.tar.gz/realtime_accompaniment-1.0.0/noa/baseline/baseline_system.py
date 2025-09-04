import warnings

import numpy as np
import librosa as lb

# Custom imports
from noa.offline_noa import OfflineNOA
from noa.baseline.match import align_match
import utils.constants as constants


class BaselineSystem(OfflineNOA):
    """
    Class for running offline baseline systems as if they were real-time systems.
    """

    def __init__(self, *args, eval_type: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.eval_type = eval_type
        print(f"Using baseline system: {self.eval_type}")
        self._precomputed_path = None

    def reset(self):
        super().reset()
        self._precomputed_path = None

    def _compute_path(self, query_features, query_path):
        """
        Compute the path based on the evaluation type.

        Args:
            query_features (np.ndarray): The features of the query audio to be aligned. Should have shape (n_features, n_frames).
            query_path (str): Path to the query audio file.

        Returns:
            path (np.ndarray): shape (N, ) of aligned indices corresponding to the reference frames.
        """
        self.query_features = query_features

        # compute path
        if self.eval_type == "dtw":
            # compute cosine distance matrix
            C = 1 - query_features.T @ self.solo_features

            # [1] is the path
            path = lb.sequence.dtw(
                C=C,
                metric="cosine",
                step_sizes_sigma=constants.DEFAULT_DTW_STEPS,
                weights_mul=constants.DEFAULT_DTW_WEIGHTS,
            )[1]
            path = np.flip(path, axis=0).T  # flip the path to match the query
        elif self.eval_type == "match":
            path = align_match(query_path, self.solo_reference)
        elif self.eval_type == "noa_test":
            offline_noa = OfflineNOA(
                cache_dir="cache",
                solo_reference=self.solo_reference,
                orch_reference=self.orch_reference,
            )
            path = offline_noa.align(query_features, query_path)
            return path  # does not need to be interpolated
        else:
            raise ValueError(f"Invalid evaluation type: {self.eval_type}")

        # path should have shape (2, ) now, with path[0] being the query indices and path[1] being the reference indices
        # we need to interpolate the path to make sure that there is a corresponding reference time for each query time
        path = np.interp(np.arange(query_features.shape[1]), path[0], path[1])
        path = path.astype(int)

        return path

    def align(self, query_features, query_path):
        """
        Align the given query features to the reference features.

        Args:
            query_features (np.ndarray): The features of the query audio to be aligned. Should have shape (n_features, n_frames).
            query_path (str): Path to the query audio file. Note that this is not the query features!

        Returns:
            path (np.ndarray): shape (N, ) of aligned indices corresponding to the reference frames.
        """
        self.reset()
        self._precomputed_path = self._compute_path(
            query_features, query_path
        )  # perform alignment
        pos = 0
        self.query_alpha_history = []

        # go through each frame of the query features
        self.phase = "align"

        for i in range(self.query_features.shape[1]):
            if i == 0:
                print(f"Initial mode: {'orchestra' if self.orchestra else 'solo'}")

            # Check if we are at end of the reference
            if self._check_end_of_reference():
                if self.recording:
                    self.save_audio(query_path)
                print(f"End of reference reached at frame {i}")
                self.phase = "finalize"
                return self.path

            self.progress = i / self.query_features.shape[1]

            # get mode
            if not self.path:
                mode = self._get_and_update_mode(self.current_stream_index)
            else:
                mode = self._get_and_update_mode(self.path[-1])

            # simulate the alignment by popping the front of the precomputed path into the current path
            self.path.append(self._precomputed_path[i])

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
