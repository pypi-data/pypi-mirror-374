import os
import re
import shutil
import pickle
import hashlib
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import librosa as lb

from utils.evaluation import generate_query
from utils import mode_detection
import utils.constants as constants
from utils.cache_utils import load_cache, store_cache

from noa.offline_noa import OfflineNOA
from noa.lagged_offline_noa import LaggedOfflineNOA
from noa.baseline.baseline_system import BaselineSystem
from noa.baseline.lagged_baseline_system import LaggedBaselineSystem


def get_t_from_alpha(
    alphas,
    dt=1,
    sr=constants.DEFAULT_SR,
    hop=constants.DEFAULT_HOP_LENGTH,
    convert_to_int=True,
):
    """
    Integrates the alphas to get the frames.

    Input: alphas (np.array) - Array of alphas
    dt (int) - time step in frames
    convert_to_int (bool) - whether to convert the expected hop sizes to integers
    """
    if convert_to_int:
        expected_has = [int(hop / alpha) for alpha in alphas]
    else:
        expected_has = [hop / alpha for alpha in alphas]
    t_array = np.cumsum(expected_has) * dt / sr

    # move everything to the right by 1 and add a 0 at the beginning
    t_array = np.concatenate(([0], t_array[:-1]))
    return t_array


def plot_times(t_tsm, t_ref):
    """
    Plot the times of the TSM'd result vs. the original reference.

    Args:
        t_tsm (np.array): Times of the TSM'd result
        t_ref (np.array): Times of the original reference
    """
    plt.figure()
    plt.plot(t_ref, t_tsm, ".-")
    plt.xlabel(r"$t_\text{ref}$ (s)")
    plt.ylabel(r"$t_\text{TSM}$ (s)")
    plt.title("Times of TSM'd result vs. original reference")
    plt.show()


def generate_smod_evaluation(
    orch_ref,
    solo_ref,
    num_iterations=10,
    hop=constants.DEFAULT_HOP_LENGTH,
    sr=constants.DEFAULT_SR,
    eval_mode="continuous",
    global_alpha=1,
    outfile_name=None,
    save_dir="evaluation_output/",
    plot_each=True,
    max_alpha_change=0.1,
    use_cache=False,
):
    """
    Generate the queries for evaluation for a given piece and returns the original reference times.

    Args:
        orch_ref (str): Path to the orchestra reference audio file.
        solo_ref (str): Path to the solo reference audio file.
        num_iterations (int): Number of iterations/queries to generate.
        hop (int): Hop length for time conversion.
        sr (int): Sample rate for time conversion.
        outfile_name (str): Base name for the output files. e.g., 'bach'.
        save_dir (str): Directory to save generated files.
        plot_each (bool): Whether to plot each iteration.


    Returns:
        smod_eval_info: Dictionary containing results for each iteration.
    """
    # Deletes the file if it exists already to make sure it resets correctly
    if os.path.exists("evaluation_output") and not use_cache:
        shutil.rmtree("evaluation_output")

    if use_cache:
        # Cache logic
        cache_dir = "cache/eval"

        # Use file paths and all params for cache key
        cache_key_tuple = (
            str(orch_ref),
            str(solo_ref),
            num_iterations,
            hop,
            sr,
            eval_mode,
            outfile_name,
            save_dir,
            max_alpha_change,
        )
        cache_key_bytes = str(cache_key_tuple).encode("utf-8")
        cache_key = hashlib.md5(cache_key_bytes).hexdigest()
        cached = load_cache(cache_dir, cache_key, "smod_eval.pkl")
        if cached is not None:
            return cached

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # load audio files and extract chroma features
    orch, _ = lb.load(orch_ref, sr=sr, mono=True)
    solo, _ = lb.load(solo_ref, sr=sr, mono=True)
    orch_feat = lb.feature.chroma_cqt(
        y=orch,
        sr=sr,
        hop_length=hop,
        norm=None,
        window=constants.DEFAULT_FEATURE_WINDOW,
    )
    solo_feat = lb.feature.chroma_cqt(
        y=solo,
        sr=sr,
        hop_length=hop,
        norm=None,
        window=constants.DEFAULT_FEATURE_WINDOW,
    )

    # compute mode array
    mode_array = mode_detection.compute_mode_array(solo_feat, orch_feat)

    # generate SM for each iteration
    smod_eval_info = {}
    for iter in range(num_iterations):
        filename = f"{save_dir}{outfile_name}[{iter}].wav"

        if os.path.exists(filename):
            save = False
        else:
            save = True

        _, alphas = generate_query.generate_SM(
            solo,
            mode_array=mode_array,
            save=save,
            filename=filename,
            global_alpha=global_alpha,
            plot=plot_each,
            seed=iter,
            eval_mode=eval_mode,
            max_alpha_change=max_alpha_change,
        )

        # convert alphas to time
        t_ref = get_t_from_alpha(alphas, sr=sr, hop=hop, convert_to_int=True)
        f_ref = t_ref * sr / hop
        f_mod = np.arange(len(alphas))
        t_mod = np.array(f_mod) * hop / sr
        smod_eval_info[iter] = {
            "alphas": alphas,
            "f_ref": f_ref,
            "f_mod": f_mod,
            "t_ref": t_ref,
            "t_mod": t_mod,
        }
        if plot_each:
            plot_times(t_mod, t_ref)
        print(f"Iteration {iter +1} is complete!")

    if use_cache:
        # Store in cache
        store_cache(cache_dir, cache_key, (smod_eval_info, mode_array), "smod_eval.pkl")
    return smod_eval_info, mode_array


def generate_stsm_evaluation(
    smod_eval_info,
    eval_system="noa",
    smod_ref="evaluation_output/",
    cache_dir="cache",
    solo_ref=None,
    orch_ref=None,
    alpha_adjust_sensitivity=constants.DEFAULT_ALPHA_ADJUST_SENSITIVITY,
    alpha_lookback=constants.DEFAULT_ALPHA_LOOKBACK,
    alpha_adjust_max_scale=constants.DEFAULT_ALPHA_ADJUST_MAX_SCALE,
    alpha_update_frequency=constants.DEFAULT_ALPHA_UPDATE_FREQUENCY,
    alpha_adjust_frequency=constants.DEFAULT_ALPHA_ADJUST_FREQUENCY,
    plot_each=True,
    recording=False,
    lag=0,
    use_cache=False,
    *args,
    **kwargs,
):
    """
    Generate Stsm evaluation data and plots for a given reference directory.

    Args:
        smod_eval_info (dict): Dictionary containing results for a specific query
        eval_system (str): Evaluation system to use.
        smod_ref (str): Path to the Smod .wav files.
        cache_dir (str): Path to cache of song.
        solo_ref (str): Path to the solo reference audio file.
        orch_ref (str): Path to the orchestra reference audio file.
        alpha_adjust_sensitivity (float): Sensitivity of alpha adjustment.
        alpha_lookback (int): Lookback for alpha adjustment.
        alpha_adjust_max_scale (float): Maximum scale for alpha adjustment.
        alpha_update_frequency (int): Frequency of alpha update.
        alpha_adjust_frequency (int): Frequency of alpha adjustment.
        plot_each (bool): Whether to plot each iteration.
        recording (bool): Whether to generate a recording.
        lag (int): Lag in milliseconds.

    Returns:
        stsm_eval_info: Dictionary containing results for each iteration.
    """

    # create the output directory if it doesn't exist
    if not os.path.exists("tsm_output"):
        os.makedirs("tsm_output")

    if use_cache:
        # Cache logic
        eval_cache_dir = "cache/eval"

        # Use directory, file list, and params for cache key
        try:
            file_list = tuple(sorted(os.listdir(smod_ref)))
        except Exception:
            file_list = ()
        cache_key_tuple = (
            str(smod_ref),
            file_list,
            str(cache_dir),
            str(solo_ref),
            str(orch_ref),
            plot_each,
            lag,
        )
        cache_key_bytes = str(cache_key_tuple).encode("utf-8")
        cache_key = hashlib.md5(cache_key_bytes).hexdigest()
        cached = load_cache(eval_cache_dir, cache_key, "stsm_eval.pkl")
        if cached is not None:
            return cached

    # generate stsm evaluation info
    stsm_eval_info = {}
    for idx, filename in enumerate(os.listdir(smod_ref)):
        # since the files are named like "bach0.wav", "bach1.wav", etc.
        # we can get the file number by finding the digits in the filename
        file_num = int(re.findall(r"\[(\d+)\]", filename)[0])

        # set up noa
        if lag == 0:
            outfile_name = f"tsm_output/{filename[:-7]}TSM[{file_num}].wav"
            if eval_system == "noa":
                system = OfflineNOA(
                    cache_dir=cache_dir,
                    solo_reference=solo_ref,
                    orch_reference=orch_ref,
                    feature_extractor=lb.feature.chroma_stft,
                    alpha_adjust_max_scale=alpha_adjust_max_scale,
                    alpha_update_frequency=alpha_update_frequency,
                    alpha_adjust_frequency=alpha_adjust_frequency,
                    alpha_adjust_sensitivity=alpha_adjust_sensitivity,
                    alpha_lookback=alpha_lookback,
                    enable_tsm=True,
                    recording=recording,
                    outfile=outfile_name,
                    save_solo=False,
                )
            else:
                system = BaselineSystem(
                    cache_dir=cache_dir,
                    solo_reference=solo_ref,
                    orch_reference=orch_ref,
                    feature_extractor=lb.feature.chroma_stft,
                    alpha_adjust_max_scale=alpha_adjust_max_scale,
                    alpha_update_frequency=alpha_update_frequency,
                    alpha_adjust_frequency=alpha_adjust_frequency,
                    alpha_adjust_sensitivity=alpha_adjust_sensitivity,
                    alpha_lookback=alpha_lookback,
                    enable_tsm=True,
                    recording=recording,
                    outfile=outfile_name,
                    save_solo=False,
                    eval_type=eval_system,
                )
        else:
            outfile_name = f"tsm_output/{filename[:-7]}TSM[{file_num}]_lag{lag}.wav"
            if eval_system == "noa":
                system = LaggedOfflineNOA(
                    cache_dir=cache_dir,
                    solo_reference=solo_ref,
                    orch_reference=orch_ref,
                    feature_extractor=lb.feature.chroma_stft,
                    alpha_adjust_max_scale=alpha_adjust_max_scale,
                    alpha_update_frequency=alpha_update_frequency,
                    alpha_adjust_frequency=alpha_adjust_frequency,
                    alpha_adjust_sensitivity=alpha_adjust_sensitivity,
                    alpha_lookback=alpha_lookback,
                    enable_tsm=True,
                    recording=recording,
                    outfile=outfile_name,
                    lag=lag,
                )
            else:
                system = LaggedBaselineSystem(
                    cache_dir=cache_dir,
                    solo_reference=solo_ref,
                    orch_reference=orch_ref,
                    feature_extractor=lb.feature.chroma_stft,
                    alpha_adjust_max_scale=alpha_adjust_max_scale,
                    alpha_update_frequency=alpha_update_frequency,
                    alpha_adjust_frequency=alpha_adjust_frequency,
                    alpha_adjust_sensitivity=alpha_adjust_sensitivity,
                    alpha_lookback=alpha_lookback,
                    enable_tsm=True,
                    recording=recording,
                    outfile=outfile_name,
                    lag=lag,
                    eval_type=eval_system,
                )

        # load query
        query = smod_ref + filename
        audio, _ = lb.load(query, sr=constants.DEFAULT_SR)
        query_feature = lb.feature.chroma_stft(
            y=audio,
            sr=constants.DEFAULT_SR,
            hop_length=constants.DEFAULT_HOP_LENGTH,
            center=False,
        )

        # align query
        system.align(query_feature, query)

        # get alpha values
        alphas, _ = system.get_alpha_tref()
        alphas = np.array(alphas)

        t_mod = (
            np.arange(len(alphas)) * constants.DEFAULT_HOP_LENGTH / constants.DEFAULT_SR
        )

        t_tsm = get_t_from_alpha(
            alphas, sr=system.sr, hop=system.hop_length, convert_to_int=True
        )
        f_tsm = t_tsm * system.sr / system.hop_length
        stsm_eval_info[file_num] = {
            "t_mod": t_mod,
            "t_tsm": t_tsm,
            "f_tsm": np.array(f_tsm),
            "alphas": alphas,
        }
        min_length = min(len(t_tsm), len(t_mod))
        if plot_each:
            plot_times(t_tsm[0:min_length], t_mod[0:min_length])
        print(f"Iteration {idx + 1} is complete!")

    if use_cache:
        # Store in cache
        store_cache(eval_cache_dir, cache_key, stsm_eval_info, "stsm_eval.pkl")
    return stsm_eval_info


def generate_batch_stsm_evaluation(
    smod_eval_info,
    *args,
    mode_array,
    param_name,
    param_values,
    eval_mode=None,
    eval_system="noa",
    save_dir="evaluation_results",
    outfile_name=None,
    save_results=False,
    **kwargs,
):
    """
    Generate batch Stsm evaluation data and plots for a given reference directory,
    sweeping over a parameter (e.g., lag, alpha_sensitivity, etc.).

    Args:
        smod_eval_info: Smod evaluation info.
        *args, **kwargs: Arguments to pass to generate_stsm_evaluation.
        mode_array: Mode array.
        param_name (str): Name of the parameter to sweep (must match argument in generate_stsm_evaluation).
            Possible values: "lag", "alpha_adjust_sensitivity", "alpha_lookback", "alpha_adjust_max_scale", "alpha_update_frequency", "alpha_adjust_frequency".
        param_values (iterable): Values to sweep for the parameter.
        eval_mode (str): Evaluation mode.
        save_dir (str): Directory to save the results.
        outfile_name (str): Name of the output file.
        save_results (bool): Whether to save the results.

    Returns:
        stsm_eval_info_list: List of stsm_eval_info dicts for each parameter value. Contains raw timestamps.
        err_dict_list: List of error dicts for each parameter value.
    """
    # check if the eval mode is provided if save_results is True
    if save_results:
        assert (
            eval_mode is not None
        ), "Eval mode must be provided if save_results is True"

    # check if the parameter name is valid
    param_name = param_name.lower()
    if param_name not in [
        "lag",
        "alpha_adjust_sensitivity",
        "alpha_lookback",
        "alpha_adjust_max_scale",
        "alpha_update_frequency",
        "alpha_adjust_frequency",
    ]:
        raise ValueError(
            f"Invalid parameter name: {param_name}. Possible values: 'lag', 'alpha_adjust_sensitivity', 'alpha_lookback', 'alpha_adjust_max_scale', 'alpha_update_frequency', 'alpha_adjust_frequency'."
        )

    filtered_info_list = []

    for a in param_values:
        print(f"Sweeping {param_name} to {a}")

        # Build kwargs for generate_stsm_evaluation, setting the swept parameter
        eval_kwargs = dict(kwargs)  # copy user kwargs
        eval_kwargs["smod_eval_info"] = smod_eval_info
        eval_kwargs["eval_system"] = eval_system
        eval_kwargs[param_name] = a

        # Always set plot_each to False unless user overrides
        # We don't want a million plots!
        eval_kwargs.setdefault("plot_each", False)

        stsm_eval_info = generate_stsm_evaluation(*args, **eval_kwargs)

        # filter to include only results for solo mode
        filtered_info = filter_eval_info(smod_eval_info, stsm_eval_info, mode_array)
        filtered_info_list.append(filtered_info)

    # optionally save the results to pickle files
    if save_results:
        # create the directories if they don't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        if not os.path.exists(f"{save_dir}/{eval_system}"):
            os.makedirs(f"{save_dir}/{eval_system}")
        if not os.path.exists(f"{save_dir}/{eval_system}/{outfile_name}"):
            os.makedirs(f"{save_dir}/{eval_system}/{outfile_name}")

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filtered_info_list_file = f"{save_dir}/{eval_system}/{outfile_name}/{param_name}_{eval_mode}_evaluation_results_{current_time}.pkl"
        with open(filtered_info_list_file, "wb") as f:
            pickle.dump(filtered_info_list, f)
        print("-" * 100)
        print(f"Saved evaluation results to {filtered_info_list_file}!")
        print("-" * 100)

    return filtered_info_list


def get_digits_in_order(dir="evaluation_output/"):
    """Get file number as `os` orders them."""
    digits_in_order = []
    file_list = os.listdir(dir)
    for file in file_list:
        # file num is enclosed in []
        file_num = re.findall(r"\[(\d+)\]", file)[0]
        digits_in_order.append(int(file_num))
    return digits_in_order


def filter_eval_info(
    smod_eval_info,
    stsm_eval_info,
    mode_array,
    digits_in_order=None,
    hop=constants.DEFAULT_HOP_LENGTH,
    sr=constants.DEFAULT_SR,
):
    """
    Filter the evaluation info to only include the solo sections.

    Args:
        smod_eval_info: Smod evaluation info.
        stsm_eval_info: Stsm evaluation info.
        mode_array: Mode array.
        digits_in_order: Digits in order.
    """
    err_dict = {}
    if digits_in_order is None:
        digits_in_order = get_digits_in_order()

    # Iterate through each file index in order
    for i in digits_in_order:
        # Retrieve relevant arrays for this file
        ground_truth_alpha = smod_eval_info[i]["alphas"]
        t_ref = smod_eval_info[i]["t_ref"]
        applied_alpha = stsm_eval_info[i]["alphas"]
        t_tsm = stsm_eval_info[i]["t_tsm"]

        # filter out non-solo sections
        max_len = min(
            len(mode_array),
            len(t_ref),
            len(t_tsm),
            len(ground_truth_alpha),
            len(applied_alpha),
        )
        solo_indices = [idx for idx in range(max_len) if mode_array[idx] != 0]

        t_ref_solo = [t_ref[idx] for idx in solo_indices]
        t_tsm_solo = [t_tsm[idx] for idx in solo_indices]
        ground_truth_alpha_solo = [ground_truth_alpha[idx] for idx in solo_indices]
        applied_alpha_solo = [applied_alpha[idx] for idx in solo_indices]

        # save the results for this file
        err_dict[i] = {
            "t_ref_solo": t_ref_solo,
            "t_tsm_solo": t_tsm_solo,
            "ground_truth_alpha_solo": ground_truth_alpha_solo,
            "applied_alpha_solo": applied_alpha_solo,
        }

    return err_dict


def agg_err(thresholds, err_dict):
    """
    Aggregate the error rates for a given set of thresholds.

    Args:
        thresholds: Thresholds to compute error rates for.
        err_dict: Error dictionary.
    """

    # compute the error rate for each threshold
    aggregate_errs = []
    for idx in err_dict.keys():
        # Calculate absolute error between t_mod_solo and t_tsm_solo
        y = np.abs(
            np.array(err_dict[idx]["t_ref_solo"])
            - np.array(err_dict[idx]["t_tsm_solo"])
        )
        aggregate_errs.extend(y)

    # compute the error rate for each threshold
    err_rate = []
    for threshold in thresholds:
        count = 0
        for e in aggregate_errs:
            if e < threshold:
                count += 1
        err_rate.append(count / len(aggregate_errs) * 100)

    return err_rate


def agg_err_batch(thresholds, err_dict_list, param_values):
    """
    Aggregate the error rates for a given set of thresholds.

    Args:
        thresholds: Thresholds to compute error rates for.
        err_dict_list: List of error dictionaries.
        param_values: List of parameter values.

    Returns:
        errors: Dictionary of error rates for each parameter value.
    """
    errors = {}
    for idx, a in enumerate(param_values):
        err_dict = err_dict_list[idx]
        err_rate = agg_err(thresholds, err_dict)
        errors[a] = err_rate
    return errors


def plot_heatmap(
    errors,
    param_name,
    param_values,
    thresholds,
    threshold_step,
    step,
    eval_mode,
    save_plot=False,
    config=None,
):
    """
    Plot a heatmap of the error rates vs. the parameter values.

    Args:
        errors: Dictionary of error rates for each parameter value.
        param_name: Name of the parameter.
        param_values: List of parameter values.
        thresholds: List of thresholds for the error rates.
        threshold_step: Step size for the thresholds.
        step: Step size for the parameter values.
        eval_mode: Evaluation mode.
        save_plot: Whether to save the plot.
    """
    len_a = len(param_values)
    len_t = len(thresholds)
    mp = np.empty((len_a, len_t))

    for idx, value in enumerate(param_values):
        mp[idx, :] = errors[value]

    plt.figure(figsize=(10, 6))
    im = plt.imshow(
        mp,
        aspect="auto",
        origin="lower",
        extent=[0, mp.shape[1] * threshold_step, 0, mp.shape[0] * step],
        cmap="tab20c",
    )

    plt.colorbar(im, label="Accuracy rate (%)")
    plt.xlabel("Threshold (s)")
    plt.ylabel(param_name)
    plt.xlim()
    plt.title(
        f"Heatmap of Accuracy Rate vs. {param_name}\n{eval_mode.capitalize()} Mode"
    )
    if save_plot:
        assert config is not None, "Config must be provided if save_plot is True"
        plt.savefig(f"heatmap_{config}_{param_name}_{eval_mode}.png")
    else:
        plt.show()
