from librosa.onset import onset_detect
from librosa import load
import numpy as np
import soundfile as sf
import utils.constants as constants


def detect_onsets(
    audio_path,
    hop_length=constants.DEFAULT_HOP_LENGTH,
    sr=constants.DEFAULT_SR,
    units="frames",
    delta=0.01,
    pre_max=5,
    post_max=5,
    pre_avg=10,
    post_avg=10,
    wait=0,
    backtrack=False,
):
    """Detect onsets in an audio file using librosa.

    Args:
        audio_path (str): Path to the audio file.
        hop_length (int): Hop length in samples.
        sr (int): Sample rate.
        units (str): Units of the onsets. Can be 'frames', 'seconds', or 'samples'.
        delta (float): Threshold offset for onset detection. Lower values are more sensitive.
        pre_max (int): Number of preceding frames for local maximum.
        post_max (int): Number of following frames for local maximum.
        pre_avg (int): Number of preceding frames for moving average.
        post_avg (int): Number of following frames for moving average.
        wait (int): Minimum number of frames between onsets.
        backtrack (bool): If True, backtracks detected onsets to the nearest preceding minimum.

    Returns:
        onsets (array-like): Onset times in frames, seconds, or samples.
    """
    y, sr = load(audio_path, sr=sr)
    onsets = onset_detect(
        y=y,
        sr=sr,
        hop_length=hop_length,
        delta=delta,
        pre_max=pre_max,
        post_max=post_max,
        pre_avg=pre_avg,
        post_avg=post_avg,
        wait=wait,
        backtrack=backtrack,
    )
    if units == "frames":
        return onsets
    elif units == "seconds":
        return onsets * hop_length / sr
    elif units == "samples":
        return onsets * hop_length
    else:
        raise ValueError(f"Invalid units: {units}")


def _generate_click(sr, duration=0.01, freq=1000):
    """Generate a short click sound.

    Args:
        sr (int): Sample rate.
        duration (float): Duration of the click in seconds.
        freq (int): Frequency of the click in Hz.
    """
    t = np.linspace(0, duration, int(sr * duration), False)
    click = 0.5 * np.sin(2 * np.pi * freq * t)
    # Apply a short fade-out to avoid clicks
    fade_len = int(0.002 * sr)
    if fade_len > 0:
        click[-fade_len:] *= np.linspace(1, 0, fade_len)
    return click


def overlay_onsets(audio_path, onset_times=None, outfile=None, sr=22050):
    """Overlay onsets on an audio file.

    Args:
        audio_path (str): Path to the audio file.
        onset_times (array-like): Onset times in seconds.
        outfile (str): Path to the output file.
        sr (int): Sample rate.
    """
    y, sr = load(audio_path, sr=sr)
    click = _generate_click(sr)

    y_overlay = np.copy(y)
    if onset_times is None:
        onset_times = detect_onsets(audio_path, sr=sr, units="seconds")

    for onset_time in onset_times:
        onset_sample = int(onset_time * sr)
        end_sample = onset_sample + len(click)
        if end_sample < len(y_overlay):
            y_overlay[onset_sample:end_sample] += click
        else:
            # If click would go past end, truncate
            y_overlay[onset_sample:] += click[: len(y_overlay) - onset_sample]

    if outfile:
        sf.write(outfile, y_overlay, sr)


def merge_solo_and_orchestra_onsets(solo_onsets, orchestra_onsets):
    """Merge solo and orchestra onsets, returning sorted unique onsets.

    Args:
        solo_onsets (array-like): Onset times in frames.
        orchestra_onsets (array-like): Onset times in frames.
    """
    # Use np.union1d for sorted unique merge
    return np.union1d(solo_onsets, orchestra_onsets)
