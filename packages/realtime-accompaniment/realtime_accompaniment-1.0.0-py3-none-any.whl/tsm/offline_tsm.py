from scipy.signal import medfilt
import librosa as lb
import numpy as np
import utils.constants as constants


def tsm_ola_variable(x, sr, t_alpha, alpha, L=220):
    """
    Time stretches the input signal using overlap-add with variable stretch factors.

    Inputs:
    x: input signal
    sr: sample rate
    t_alpha: array of time points (seconds) when stretch factors change
    alpha: array of stretch factors corresponding to t_alpha
    L: frame length (must be even)

    Returns time-stretched signal y
    """
    assert L % 2 == 0, "Frame length must be even."
    Hs = L // 2

    # Convert time points to samples
    t_alpha_samples = [int(t * sr) for t in t_alpha]
    t_alpha_samples.append(len(x))  # Add end of signal as final boundary

    # Initialize
    current_alpha_idx = 0
    curr_offset = 0
    analysis_frames = []

    # Analysis phase
    while curr_offset <= len(x) - L:
        current_alpha = alpha[current_alpha_idx]
        Ha = int(np.round(Hs / current_alpha))

        # Check if next window would cross boundary
        if curr_offset + Ha > t_alpha_samples[current_alpha_idx + 1]:
            current_alpha_idx += 1

        # Extract and store frame
        frame = x[curr_offset : curr_offset + L]
        analysis_frames.append(frame)
        # Advance position
        curr_offset += Ha

    num_frames = len(analysis_frames)
    if num_frames == 0:
        return np.zeros(0)

    analysis_frames = np.array(analysis_frames).T

    # Synthesis phase
    synthesis_frames = analysis_frames * hann_window(L).reshape((-1, 1))
    y = np.zeros(Hs * (num_frames - 1) + L)

    for i in range(num_frames):
        offset = i * Hs
        y[offset : offset + L] += synthesis_frames[:, i]

    return y


def hann_window(L):
    w = 0.5 * (1 - np.cos(2 * np.pi * np.arange(L) / L))
    return w


def tsm_phasevocoder_variable(x, sr, t_alpha, alpha, L=2048):
    """
    Phase‐vocoder time‐scale modification with piecewise constant speed factors.

    Parameters
    ----------
    x : np.ndarray
        Input audio signal (1D array of samples).
    sr : int
        Sampling rate in Hz.
    t_alpha : list of float
    alpha : list of float
        Speed factors corresponding to each segment defined by `t_alpha`.
    L : int, optional
        FFT size and window length (defaults to 2048 samples).

    Returns
    -------
    y : np.ndarray
        Time‐scaled output signal.
    """
    Hs = L // 4
    window = np.hanning(L)  # Hann window of length L

    t_alpha_samples = [int(t * sr) for t in t_alpha] + [len(x)]
    prev_fft = None  # stores the FFT of the previous frame (None for first frame)
    prev_phase = np.zeros(L // 2 + 1)  # half of the size of FFT
    currOffset = 0  # current read pointer in the input x
    seg_idx = 0  # which segment (alpha[seg_idx]) we’re in
    analysisFrames = []

    # precompute nominal angular frequencies for each FFT bin
    omega_nom = np.arange(L // 2 + 1) * 2 * np.pi * sr / L

    # main processing loop
    while currOffset + L <= len(x):  # stop when not enough frame for entire window
        if currOffset >= t_alpha_samples[seg_idx + 1]:
            seg_idx += 1  # if we’ve crossed the next time boundary, increment seg_idx.
        a = alpha[seg_idx]  # the speed factor for this frame.
        Ha = int(
            round(Hs / a)
        )  # Ha length in terms of Hs --> output_length approx input_length * (Ha / Hs)

        # extract, window, and FFT the current frame
        frame = x[currOffset : currOffset + L] * window
        S = np.fft.rfft(frame)

        # estimate IF
        if prev_fft is None:  # nothing for first frame
            w_if = np.zeros_like(omega_nom)
        else:

            dphi = np.angle(S) - np.angle(
                prev_fft
            )  # phase difference between current & previous FFT
            dphi = dphi - omega_nom * (Ha / sr)

            dphi = (dphi + np.pi) % (
                2 * np.pi
            ) - np.pi  # wrap to [-π, π] to undo any 2π jumps
            w_if = omega_nom + dphi * (sr / Ha)  # IF = nom + correction

        prev_phase = prev_phase + w_if * (
            Hs / sr
        )  # accumulates phase after every time boundary

        # build the modified spectrum & inverse FFT back to time domain
        X_mod = np.abs(S) * np.exp(1j * prev_phase)
        frame_mod = np.fft.irfft(X_mod)
        analysisFrames.append(frame_mod)

        # advance pos
        currOffset += Ha
        prev_fft = S

    numFrames = len(analysisFrames)
    analysisFrames = np.array(analysisFrames).T
    den = calc_sum_squared_window(window, Hs)
    synthesisFrames = analysisFrames * window.reshape((-1, 1)) / den.reshape((-1, 1))
    y = np.zeros((Hs * numFrames) + L)

    for i in range(numFrames):
        offset = i * Hs
        y[offset : offset + L] += synthesisFrames[:, i]

    return y


def estimateIF(S, sr, hop_samples):
    """
    Estimates the instantaneous frequencies in a STFT matrix.

    Inputs
    S: the STFT matrix, should only contain the lower half of the frequency bins
    sr: sampling rate
    hop_samples: the hop size of the STFT analysis in samples

    Returns a matrix containing the estimated instantaneous frequency at each time-frequency bin.
    This matrix should contain one less column than S.
    """
    hop_sec = hop_samples / sr
    fft_size = (S.shape[0] - 1) * 2
    w_nom = np.arange(S.shape[0]) * sr / fft_size * 2 * np.pi
    w_nom = w_nom.reshape((-1, 1))
    unwrapped = np.angle(S[:, 1:]) - np.angle(S[:, 0:-1]) - w_nom * hop_sec
    wrapped = (unwrapped + np.pi) % (2 * np.pi) - np.pi
    w_if = w_nom + wrapped / hop_sec
    return w_if


def invert_stft(S, hop_length, window):
    """
    Reconstruct a signal from a modified STFT matrix.

    Inputs
    S: modified STFT matrix
    hop_length: the synthesis hop size in samples
    window: an array specifying the window used for FFT analysis

    Returns a time-domain signal y whose STFT is closest to S in squared error distance.
    """

    L = len(window)

    # construct full stft matrix
    fft_size = (S.shape[0] - 1) * 2
    Sfull = np.zeros((fft_size, S.shape[1]), dtype=np.complex64)
    Sfull[0 : S.shape[0], :] = S
    Sfull[S.shape[0] :, :] = np.conj(np.flipud(S[1 : fft_size // 2, :]))

    # compute inverse FFTs
    frames = np.zeros_like(Sfull)
    for i in range(frames.shape[1]):
        frames[:, i] = np.fft.ifft(Sfull[:, i])
    frames = np.real(frames)  # remove imaginary components due to numerical roundoff

    # synthesis frames
    num = window.reshape((-1, 1))
    den = calc_sum_squared_window(window, hop_length)
    # den = np.square(window) + np.square(np.roll(window, hop_length))
    frames = frames * window.reshape((-1, 1)) / den.reshape((-1, 1))
    # frames = frames * window.reshape((-1,1))

    # reconstruction
    y = np.zeros(hop_length * (frames.shape[1] - 1) + L)
    for i in range(frames.shape[1]):
        offset = i * hop_length
        y[offset : offset + L] += frames[:, i]

    return y


def calc_sum_squared_window(window, hop_length):
    """
    Calculates the denominator term for computing synthesis frames.

    Inputs
    window: array specifying the window used in FFT analysis
    hop_length: the synthesis hop size in samples

    Returns an array specifying the normalization factor.
    """
    assert (
        len(window) % hop_length == 0
    ), "Hop length does not divide the window evenly."

    numShifts = len(window) // hop_length
    den = np.zeros_like(window)
    for i in range(numShifts):
        den += np.roll(np.square(window), i * hop_length)

    return den


def harmonic_percussive_separation(
    x,
    sr=constants.DEFAULT_SR,
    fft_size=constants.DEFAULT_FEATURE_WINDOW,
    hop_length=constants.DEFAULT_HOP_LENGTH,
    lh=6,
    lp=6,
):

    window = hann_window(fft_size)
    X = lb.core.stft(
        x, n_fft=fft_size, hop_length=hop_length, window=window, center=False
    )
    Y = np.abs(X)
    Yh = medfilt(Y, (1, 2 * lh + 1))
    Yp = medfilt(Y, (2 * lp + 1, 1))
    Mh = Yh > Yp
    Mp = np.logical_not(Mh)
    Xh = X * Mh
    Xp = X * Mp
    xh = invert_stft(Xh, hop_length, window)
    xp = invert_stft(Xp, hop_length, window)

    return xh, xp, Xh, Xp


def mix_recordings(x1, x2):
    min_length = min(len(x1), len(x2))
    y = 0.5 * (x1[0:min_length] + x2[0:min_length])
    return y


def tsm_hybrid_variable(x, sr, alpha, t_alpha):
    """
    Inputs:
    x - input signal
    sr - sampling rate
    alpha - a list of stretch factos
    t_alpha - a list of times (in seconds) where the stretch factor, alpha, applies e.g. alpha = [1, 0.5, 2] and t_alpha = [0, 2.5, 6]
    then from 0 to 2.5 secs, alpha = 1, then from 2.5 to 6 secs, alpha = 0.5 and so on.
    """
    if len(alpha) != len(t_alpha):
        raise ValueError("Size of alpha list and time list do not match.")

    xh, xp, _, _ = harmonic_percussive_separation(x)
    xh_stretched = tsm_phasevocoder_variable(xh, sr, t_alpha, alpha)
    xp_stretched = tsm_ola_variable(xp, sr, t_alpha, alpha)
    y = mix_recordings(xh_stretched, xp_stretched)
    return y
