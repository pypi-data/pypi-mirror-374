import subprocess
import tempfile
import os
import pickle
import numpy as np
import utils.constants as constants


def align_match(
    wav1_path,
    wav2_path,
    outfile=None,
    sr=constants.DEFAULT_SR,
    hop=constants.DEFAULT_HOP_LENGTH,
    output_path=None,
    timeout=1200,  # seconds
):
    """
    Calls the java PerformanceMatcher to align two audio files.

    Args:
        wav1_path (str): path to first wav file
        wav2_path (str): path to second wav file
        outfile (str): path to save output pickle file
        sr (int): sample rate
        hop (int): hop size
        output_path (str): temp file for java output (optional)
        timeout (int): maximum time in seconds to allow the process to run. Default is 20 minutes.
    """

    # Use temp file if no output_path given (auto cleanup)
    if output_path is None:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        output_path = tmp_file.name
        tmp_file.close()
    else:
        tmp_file = None

    cmd = [
        "java",
        "-cp",
        "noa/baseline/match-0.9.4.jar",  # replace with your own path
        "at.ofai.music.match.PerformanceMatcher",
        "-b",
        "-G",
        "-q",
        "-os",
        output_path,
        wav1_path,
        wav2_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"PerformanceMatcher timed out after {timeout} seconds.")
        if tmp_file:
            try:
                os.remove(output_path)
            except Exception as e:
                print(f"Could not delete temp file: {e}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"PerformanceMatcher failed with error: {e}")
        if tmp_file:
            try:
                os.remove(output_path)
            except Exception as ex:
                print(f"Could not delete temp file: {ex}")
        return None

    path = parse_match_file(output_path, sr, hop)

    # Check if the path is valid (not None, has expected shape, not empty)
    if (
        path is None
        or not isinstance(path, np.ndarray)
        or path.size == 0
        or path.shape[0] != 2
    ):
        print("Invalid or empty alignment path returned from PerformanceMatcher.")
        path = None

    if tmp_file:
        try:
            os.remove(output_path)
        except Exception as e:
            print(f"Could not delete temp file: {e}")

    if path is not None and outfile:
        with open(outfile, "wb") as f:
            pickle.dump(path, f)

    return path


def parse_match_file(
    output_path="output_path.txt",
    sr=constants.DEFAULT_SR,
    hop=constants.DEFAULT_HOP_LENGTH,
):
    """
    Parses the output file from PerformanceMatcher.

    Returns:
        path (np.ndarray): shape (2, N) of aligned indices
    """
    try:
        path = np.loadtxt(output_path)
        path = np.fliplr(path.T * (sr / hop)).astype(int)
        return path
    except Exception as e:
        print(f"Error parsing output: {e}")
        return None
