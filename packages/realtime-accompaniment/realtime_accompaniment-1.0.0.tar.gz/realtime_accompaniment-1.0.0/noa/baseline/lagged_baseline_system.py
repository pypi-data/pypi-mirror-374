import warnings
from noa.baseline.baseline_system import BaselineSystem


class LaggedBaselineSystem(BaselineSystem):
    """
    Class for running offline baseline systems as if they were real-time systems with a lag.
    """

    def __init__(self, *args, lag: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.lag = lag
        self.lag_samples_offline = int(lag / 1000 * self.sr)
        self.lag_feature_frames = int(lag / 1000 * self.sr / self.hop_length)

    def align(self, query_features, query_path):
        """
        Align the given query features to the reference features.

        Args:
            query_features (np.ndarray): The features of the query audio to be aligned. Should have shape (n_features, n_frames).
            query_path (str): Path to the query audio file. Note that this is not the query features!
        """
        self.reset()
        self._precomputed_path = self._compute_path(
            query_features, query_path
        )  # perform alignment
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
                return self.path

            self.progress = i / query_features.shape[1]

            # get mode
            if not self.path:
                mode = self._get_and_update_mode(self.current_stream_index)
            else:
                mode = self._get_and_update_mode(self.path[-1])

            # simulate the alignment by popping the front of the precomputed path into the current path
            self.path.append(self._precomputed_path[i])

            # update alpha
            if (i + 1) % self.alpha_update_frequency == 0:
                new_alpha = self.get_alpha(
                    i - 1 - self.lag_feature_frames, history=self.alpha_lookback
                )
                if (
                    abs(new_alpha - self.current_alpha) > 0.01
                ):  # only update if the change is greater than 1%
                    self.current_alpha = new_alpha
                    self.base_alpha = self.current_alpha

            elif (
                len(self.path) > self.alpha_adjust_max_frame_deviation
                and (i + 1) % self.alpha_adjust_frequency == 0
                and i > self.initial_constant_period_frames
                and not self.orchestra
            ):
                self.adjust_alpha(pos, lag_samples=self.lag_samples_offline)
            self.query_alpha_history.append(self.current_alpha)

            # update TSM if not at end of reference
            if pos <= len(self.tsm.xh):
                Ha = self.update_tsm_orch(pos)
                pos += Ha
            else:
                warnings.warn(
                    "TSM is not enabled or at end of reference, skipping TSM update"
                )
                break

            self.current_stream_index += 1

        if self.recording:
            self.save_audio(query_path)

        self.phase = "finalize"
        return self.path
