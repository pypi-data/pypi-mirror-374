import numpy as np
import utils.constants as constants


def compute_mode_array(
    solo_features,
    orch_features,
    threshold: float = -10,
    time: float = 2.5,
    sr=constants.DEFAULT_SR,
    hop_length=constants.DEFAULT_HOP_LENGTH,
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

    if solo_features is None or orch_features is None:
        raise ValueError("Solo or orchestral features could not be loaded or computed.")

    assert (
        solo_features.shape == orch_features.shape
    ), "Input features must have the same shape."

    med = int(time * sr / hop_length)  # number of frames in the time window

    # sum to get energy + add epsilon to avoid divide by zero
    solo_features_processed = np.sum(solo_features, axis=0) + 1e-9
    orch_features_processed = np.sum(orch_features, axis=0) + 1e-10

    # initialize output array
    op = np.ones(solo_features_processed.shape)
    # default is 1 = piano led

    # apply median filter
    for idx, _ in enumerate(solo_features_processed):
        if np.all(
            10
            * np.log10(
                solo_features_processed[idx : idx + med]
                / orch_features_processed[idx : idx + med]
            )
            < threshold
        ) and idx + med < len(solo_features_processed):
            op[idx : idx + med] = 0

        elif np.all(
            10
            * np.log10(
                solo_features_processed[idx : idx + med]
                / orch_features_processed[idx : idx + med]
            )
            > -threshold
        ) and idx + med < len(solo_features_processed):
            op[idx : idx + med] = 2

    return op
