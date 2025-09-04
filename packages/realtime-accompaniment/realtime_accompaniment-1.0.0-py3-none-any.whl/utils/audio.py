import numpy as np
from scipy.io.wavfile import write
from utils.latency_tester import LatencyTester
import utils.constants as constants


def writeStereo(filename, stereo_audio, sr=constants.DEFAULT_SR):
    """
    Input: filename - path of where the file will be saved in
    stereo_audio - (Lx2) where 2 is the number of channels
    sr - sampling rate
    """
    scaled = np.int16(stereo_audio.T)
    write(filename, sr, scaled)


def makeStereo(y1, y2):
    """Input: y1 - audio time domain signal 1
    y2 - audio time domain signal 2
    Output: Stereo audio of y1 on the left and y2 on the right ear."""
    length = min(len(y1), len(y2))

    stereo_audio = np.array([y1[0:length] * 32767, y2[0:length]])
    return stereo_audio


def list_audio_devices():
    """List available audio input and output devices."""
    latency_tester = LatencyTester(
        test_on_init=False
    )  # use test_on_init=False to avoid latency test
    latency_tester.print_device_list()
