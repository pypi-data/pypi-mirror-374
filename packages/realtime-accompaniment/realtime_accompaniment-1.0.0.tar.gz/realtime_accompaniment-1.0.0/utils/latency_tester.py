### UTILITY FUNCTIONS FOR LATENCY MEASUREMENT ###

from typing import Dict, List
import pyaudio
import utils.constants as constants


class LatencyTester:
    """
    LatencyTester class for testing the latency of input and output audio streams as well as processing time.
    """

    def __init__(
        self,
        input_device_index: int = None,
        output_device_index: int = None,
        sr: int = constants.DEFAULT_SR,
        test_on_init: bool = True,
    ):
        """
        Initialize the LatencyTester class.

        Args:
            input_device_index: int, the index of the input device to use.
            output_device_index: int, the index of the output device to use.
            sr: int, sampling rate for audio testing. Default is 22050.
        """
        self.input_device_index = input_device_index
        self.output_device_index = output_device_index
        self.sr = sr
        self.input_latency = None
        self.output_latency = None
        self.round_trip_latency = None

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Run Test
        if test_on_init:
            self.test_round_trip_latency()  # run test on initialization

    def list_audio_devices(self) -> Dict[str, List[Dict]]:
        """
        List all available audio devices with their capabilities.

        Returns:
            Dict containing 'input' and 'output' device lists
        """
        devices = {"input": [], "output": []}

        for i in range(self.audio.get_device_count()):
            try:
                info = self.audio.get_device_info_by_index(i)
                device_info = {
                    "index": i,
                    "name": info["name"],
                    "max_input_channels": info["maxInputChannels"],
                    "max_output_channels": info["maxOutputChannels"],
                    "default_sample_rate": info["defaultSampleRate"],
                    "host_api": info["hostApi"],
                }

                if info["maxInputChannels"] > 0:
                    devices["input"].append(device_info)
                if info["maxOutputChannels"] > 0:
                    devices["output"].append(device_info)

            except Exception as e:
                print(f"Error getting device {i} info: {e}")

        return devices

    def print_device_list(self):
        """Print a formatted list of available audio devices."""
        devices = self.list_audio_devices()

        print("Available Audio Devices:")
        print("=" * 80)

        print("\nINPUT DEVICES:")
        print("-" * 40)
        for device in devices["input"]:
            print(f"Index {device['index']}: {device['name']}")
            print(
                f"  Channels: {device['max_input_channels']}, Sample Rate: {device['default_sample_rate']}"
            )
            print()

        print("\nOUTPUT DEVICES:")
        print("-" * 40)
        for device in devices["output"]:
            print(f"Index {device['index']}: {device['name']}")
            print(
                f"  Channels: {device['max_output_channels']}, Sample Rate: {device['default_sample_rate']}"
            )
            print()

    def test_input_latency(self) -> float:
        """
        Test input latency by fetching the PyAudio reported value only.

        Returns:
            input_latency: float, the input latency in seconds
        """
        print("Testing input latency ...")
        try:
            stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sr,
                input=True,
                input_device_index=self.input_device_index,
            )
            input_latency = stream.get_input_latency()
            print(f"PyAudio reported input latency: {input_latency:.4f} seconds")
            stream.close()
            self.input_latency = input_latency
            return input_latency
        except Exception as e:
            print(f"Error testing input latency: {e}")
            return {}

    def test_output_latency(self) -> float:
        """
        Test output latency by fetching the PyAudio reported value only.

        Returns:
            output_latency: float, the output latency in seconds
        """
        print("Testing output latency ...")
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sr,
                output=True,
                output_device_index=self.output_device_index,
            )
            output_latency = stream.get_output_latency()
            print(f"PyAudio reported output latency: {output_latency:.4f} seconds")
            stream.close()
            self.output_latency = output_latency
            return output_latency
        except Exception as e:
            print(f"Error testing output latency: {e}")
            return {}

    def test_round_trip_latency(self) -> float:
        """
        Test round-trip latency by summing PyAudio input and output reported values only.

        Returns:
            round_trip_latency: float, the round-trip latency in seconds
        """
        print("Testing round-trip latency ...")
        try:
            input_stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sr,
                input=True,
                input_device_index=self.input_device_index,
            )
            output_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sr,
                output=True,
                output_device_index=self.output_device_index,
            )
            input_latency = input_stream.get_input_latency()
            output_latency = output_stream.get_output_latency()
            total_latency = input_latency + output_latency
            print(
                f"PyAudio reported total latency: {total_latency:.4f}s (input: {input_latency:.4f}s + output: {output_latency:.4f}s)"
            )
            input_stream.close()
            output_stream.close()
            self.input_latency = input_latency
            self.output_latency = output_latency
            self.round_trip_latency = total_latency
            return total_latency
        except Exception as e:
            print(f"Error testing round-trip latency: {e}")
            return {}

    def __del__(self):
        """Cleanup when object is destroyed."""
        if hasattr(self, "audio") and self.audio:
            self.audio.terminate()
