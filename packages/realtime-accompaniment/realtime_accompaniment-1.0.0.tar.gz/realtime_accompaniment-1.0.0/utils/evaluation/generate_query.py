import numpy as np
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
import utils.constants as constants
from tsm.tsm import online_tsm


def generate_SM(
    audio_data,
    mode_array,
    eval_mode="continuous",
    max_tsm_factor=constants.DEFAULT_MAX_TSM_FACTOR,
    max_alpha_change=0.1,
    global_alpha=1,
    initial_constant_period=constants.DEFAULT_INITIAL_CONSTANT_PERIOD,
    sr=constants.DEFAULT_SR,
    hop=constants.DEFAULT_HOP_LENGTH,
    save=True,
    filename=None,
    plot=False,
    seed=0,
):
    """Randomly generates modified query. Saves to file.

    Inputs:
    audio_data: audio data to be modified
    mode_array: mode array of the reference audio
    eval_mode: mode of evaluation
    max_tsm_factor: maximum TSM factor
    max_alpha_change: maximum amount that alpha is allowed to change
    global_alpha: global alpha value
    initial_constant_period: initial constant period
    sr: sample rate
    hop: hop size
    save: bool, saves modified signal to file
    filename: filename for saved file
    plot: bool, plots alphas
    seed: seed for random number generator

    Returns:
    frames: list of query frames at which the alphas are applied
    alphas: list of alphas applied during TSM
    """
    np.random.seed(seed)
    orch_mode = 0 in mode_array
    frames_in_audio = len(audio_data) // hop
    initial_constant_period_frames = int(initial_constant_period * sr / hop)

    frames = np.arange(frames_in_audio)  # all frames in audio

    # create list of frame idx for alpha change
    if eval_mode != "continuous":
        frame_change_idx, orch_start_idx = create_frame_change_idx_no_walk(
            initial_constant_period_frames, frames_in_audio, orch_mode, mode_array
        )

    elif eval_mode == "continuous":
        # changes every frame
        frame_change_idx = frames

    # time array for TSM
    t_alpha = frame_change_idx * hop / sr

    # create alpha lists to go into TSM
    if eval_mode == "random":
        alphas_tsm = generate_alpha_random(
            max_tsm_factor, frame_change_idx, orch_mode, orch_start_idx
        )

    elif eval_mode == "segmented":
        alphas_tsm = generate_alpha_segmented(
            max_tsm_factor,
            max_alpha_change,
            frame_change_idx,
            orch_mode,
            orch_start_idx,
        )

    elif eval_mode == "constant":
        alphas_tsm = np.full((frame_change_idx.shape), global_alpha)

        if orch_mode:
            np.put(alphas_tsm, orch_start_idx, 1)

        alphas_tsm[0] = 1.0

    elif eval_mode == "continuous":
        alphas_tsm = generate_alpha_continuous(
            max_tsm_factor,
            max_alpha_change,
            frames,
            initial_constant_period_frames,
            mode_array,
        )

        alphas = alphas_tsm

    if eval_mode != "continuous":
        # expand to have every ref frame
        f_diff = np.diff(np.append(frame_change_idx, frames_in_audio))
        alphas = np.repeat(alphas_tsm, f_diff)

    if save:
        # offline TSM
        # audio_modified = tsm_hybrid_variable(audio_data, sr, alphas_tsm, t_alpha)

        # online TSM
        audio_modified, actual_alphas, actual_times = online_tsm(
            sr, audio_data, alphas, hop
        )

        audio_modified = np.int16(
            audio_modified / np.max(np.abs(audio_modified)) * 32767
        )

        write(filename, sr, audio_modified)
        print(f"Saved constructed query to {filename}.")

    if plot:
        plot_alpha(frames, alphas, hop, sr, eval_mode)

    # return frame and alpha list that contain every frame in the recording
    return frames, np.array(actual_alphas)


def generate_alpha_continuous(
    max_tsm_factor, max_alpha_change, frames, initial_constant_period_frames, mode_array
):

    min_tsm_factor = 1 / max_tsm_factor
    m = max_alpha_change / 15 + 1  # QUESTION: why 15?
    k = 1

    alphas_tsm = np.ones(frames.shape)
    last = alphas_tsm[0]

    # lower and upper bounds are determined by the max and min TSM factors
    log_alpha_lower_bound = np.emath.logn(m, min_tsm_factor)
    log_alpha_upper_bound = np.emath.logn(m, max_tsm_factor)

    for f, alpha_tsm in enumerate(alphas_tsm):
        if (f > initial_constant_period_frames) and (mode_array[f] != 0):
            # log of most recent alpha value
            log_alpha_last = np.emath.logn(m, last)

            # get lower and upper bounds for new alpha value
            # this means that alpha_{t+1} is between alpha_{t} / m and alpha_{t} * m
            lower_log = max(log_alpha_lower_bound, log_alpha_last - k)
            upper_log = min(log_alpha_upper_bound, log_alpha_last + k)

            # uniformly sample new alpha value between lower and upper bounds
            new_alpha_log = np.random.uniform(lower_log, upper_log)

            alphas_tsm[f] = m**new_alpha_log
            last = m**new_alpha_log

        else:
            last = alpha_tsm

    return alphas_tsm


def generate_alpha_segmented(
    max_tsm_factor, max_alpha_change, frame_change_idx, orch_mode, orch_start_idx
):
    """
    Generate alpha values for segmented evaluation mode. In this mode, the alpha values are constant
    for each segment of the reference audio.

    Args:
        max_tsm_factor: maximum TSM factor
        max_alpha_change: maximum amount that alpha is allowed to change
        frame_change_idx: frame indices at which the alpha values change
        orch_mode: whether the reference audio is in orchestra mode
        orch_start_idx: frame indices at which the orchestra mode starts

    Returns:
        alphas_tsm: array of alpha values
    """

    min_tsm_factor = 1 / max_tsm_factor
    m = max_alpha_change + 1
    k = 1

    alphas_tsm = [1]
    # lower and upper bounds are determined by the max and min TSM factors
    log_alpha_lower_bound = np.emath.logn(m, min_tsm_factor)
    log_alpha_upper_bound = np.emath.logn(m, max_tsm_factor)

    for i in range(len(frame_change_idx) - 1):
        if orch_mode and ((i + 1) in orch_start_idx):
            new_alpha = 1.0
        else:
            last = alphas_tsm[-1]

            # log of most recent alpha value
            log_alpha_last = np.emath.logn(m, last)

            # get lower and upper bounds for new alpha value
            lower_log = max(log_alpha_lower_bound, log_alpha_last - k)
            upper_log = min(log_alpha_upper_bound, log_alpha_last + k)

            # uniformly sample new alpha value between lower and upper bounds
            new_alpha_log = np.random.uniform(lower_log, upper_log)

            # convert back to linear scale
            new_alpha = m**new_alpha_log

        alphas_tsm.append(new_alpha)

    alphas_tsm = np.array(alphas_tsm)

    return alphas_tsm


def generate_alpha_random(max_tsm_factor, frame_change_idx, orch_mode, orch_start_idx):
    """
    Generate alpha values for random evaluation mode. In this mode, the alpha values are randomly
    sampled from a uniform distribution between the min and max TSM factors for each segment.

    Args:
        max_tsm_factor: maximum TSM factor
        frame_change_idx: frame indices at which the alpha values change
        orch_mode: whether the reference audio is in orchestra mode
        orch_start_idx: frame indices at which the orchestra mode starts
    """

    min_tsm_factor = 1 / max_tsm_factor

    alphas_tsm_log = np.random.uniform(
        np.log(min_tsm_factor), np.log(max_tsm_factor), size=len(frame_change_idx) - 1
    )

    alphas_tsm = np.exp(alphas_tsm_log)

    # add 1 to the beginning for initial constant period
    alphas_tsm = np.append(np.array([1]), alphas_tsm)

    # replace orchestra sections with 1
    if orch_mode:
        np.put(alphas_tsm, orch_start_idx, 1)

    return alphas_tsm


def find_orch_start_end(mode_array):
    """
    Find the start and end indices of the orchestra sections in the mode array.

    Args:
        mode_array: mode array of the reference audio

    Returns:
        starts: array of start indices of the orchestra sections
        ends: array of end indices of the orchestra sections
    """
    starts = np.array([])
    ends = np.array([])

    for idx, e in enumerate(mode_array):
        if (e == 0 and idx == len(mode_array) - 1) or (
            e == 0 and mode_array[idx + 1] != 0
        ):
            ends = np.append(ends, idx)
        elif (e == 0 and idx == 0) or (e == 0 and mode_array[idx - 1] != 0):
            starts = np.append(starts, idx)

    if len(starts) != len(ends):
        raise ValueError("Orchestra starts and ends do not match in size.")

    return starts, ends


def remove_between(frame_change_idx, starts, ends):
    """
    Remove the frames between the start and end indices of the orchestra sections.

    Args:
        frame_change_idx: frame indices at which the alpha values change
        starts: array of start indices of the orchestra sections
        ends: array of end indices of the orchestra sections

    Returns:
        frame_change_idx: frame indices at which the alpha values change
        start_idx: array of start indices of the orchestra sections
    """
    start_o = starts[0]
    end_o = ends[0]
    to_remove = []
    num_o = len(starts)
    o_count = 0

    for idx, f in enumerate(frame_change_idx):
        if (f > start_o) and (f < end_o):
            to_remove.append(idx)
        elif (f > end_o) and (o_count < num_o - 1):
            o_count += 1
            start_o = starts[o_count]
            end_o = ends[o_count]

    frame_change_idx = np.delete(frame_change_idx, to_remove).astype(int)

    # save idx for starts of orch sections
    start_idx = []

    for idx, f in enumerate(frame_change_idx):
        if f in starts:
            start_idx.append(idx)

    return frame_change_idx, start_idx


def create_frame_change_idx_no_walk(
    initial_constant_period_frames, frames_in_audio, orch_mode, mode_array
):

    frame_change_idx = np.random.randint(
        low=initial_constant_period_frames,
        high=frames_in_audio,
        size=np.random.randint(10, 100),
    )
    frame_change_idx = np.append(0, frame_change_idx)

    # find locations of orchestra mode
    if orch_mode:
        starts, ends = find_orch_start_end(mode_array)

        # add locations to frame_change_idxs
        if 0 in starts:
            frame_change_idx = np.append(frame_change_idx, np.append(starts[1:], ends))
        else:
            frame_change_idx = np.append(frame_change_idx, np.append(starts, ends))

        frame_change_idx.sort()
        frame_change_idx = np.unique(frame_change_idx)

        # remove locations that are between starts and ends
        frame_change_idx, orch_start_idx = remove_between(
            frame_change_idx, starts, ends
        )

    else:
        frame_change_idx.sort()
        frame_change_idx = np.unique(frame_change_idx)

        orch_start_idx = None

    return frame_change_idx, orch_start_idx


def plot_alpha(frames, alphas, hop, sr, eval_mode):
    plt.figure()

    if eval_mode == "continuous":
        plt.plot(frames * hop / sr, alphas, ",", color="lightgreen")

    else:
        plt.plot(frames * hop / sr, alphas, "s", markersize=1, color="lightgreen")

    plt.title(f"Alpha Values\nMode = {eval_mode}")
    plt.xlabel("time (s)")
    plt.ylabel("alpha")
    plt.show()
