# Notes on NOA System

## Offline NOA

### Alignment Algorithm (v0.3)

## Lagged Offline NOA

The Lagged Offline NOA system extends the standard offline alignment to simulate the effect of system latency (lag) in a controlled, offline setting. This is useful for benchmarking and evaluating how alignment and time-stretching algorithms perform under realistic latency conditions, similar to those encountered in real-time systems.

### Key Parameters
- `lag` (default: 500 ms): The amount of lag to simulate, specified in milliseconds. This lag is applied both to the audio (in samples) and to the feature frames used for alignment.
- `lag_samples_offline`: The lag in audio samples, computed as `lag / 1000 * sr` (where `sr` is the sample rate).
- `lag_feature_frames`: The lag in feature frames, computed as `lag / 1000 * sr / hop_length` (where `hop_length` is the feature extraction hop size).

### Implementation Details
- The `LaggedOfflineNOA` class (see `lagged_offline_noa.py`) inherits from `OfflineNOA` and overrides the alignment process to account for lag.
- During initialization, the lag is converted to both sample and feature frame units and stored as `self.lag_samples_offline` and `self.lag_feature_frames`.
- In the `align()` method, the main alignment loop is modified so that the time-stretch factor α is computed using a history window that is offset by the lag (`i - 1 - self.lag_feature_frames`). This means the system bases its tempo estimation on past information, as would be the case in a real-time system with lag.
- When updating the TSM position, the system ensures that it does not process audio beyond the available (lagged) input by checking `pos <= len(self.tsm.xh) - self.tsm.L - self.lag_samples_offline`.
- The rest of the alignment logic (mode detection, cost computation, path update) follows the standard offline approach, but all updates are effectively delayed by the simulated lag.

## Latency Testing

The goal of latency testing is to measure the input, output, and round-trip latency of the audio subsystem. These measurements are used to compensate for lag in real-time system.

### Implementation Details
- The `LatencyTester` class (see `utils/latency_tester.py`) provides methods to measure and report audio latency using the PyAudio library.
- Upon initialization, the class can automatically run a round-trip latency test, or tests can be triggered manually.

#### Key Methods
- `list_audio_devices()`: Returns a list of available input and output devices, including their indices, names, channel counts, and sample rates.
- `print_device_list()`: Prints a formatted list of all available audio devices for easy selection.
- `test_input_latency()`: Measures and reports the input latency as reported by PyAudio for the selected input device.
- `test_output_latency()`: Measures and reports the output latency as reported by PyAudio for the selected output device.
- `test_round_trip_latency()`: Measures and reports the sum of input and output latency, providing an estimate of the total round-trip delay.

#### Example Usage
```python
from utils.latency_tester import LatencyTester
from utils.audio import list_audio_devices

list_audio_devices() # List available audio devices
tester = LatencyTester(input_device_index=1, output_device_index=2, sr=22050)
tester.test_input_latency()  # Measure input latency
tester.test_output_latency()  # Measure output latency
tester.test_round_trip_latency()  # Measure round-trip latency
```

#### Notes
- The measured latencies are those reported by the underlying audio driver via PyAudio, and may not include all sources of system or processing delay.
  - Pyaudio estimates the processing delay.
- The round-trip latency is especially useful for simulating and compensating for real-world lag in both offline and online alignment systems.
- The `LatencyTester` is integrated into the real-time NOA system to automatically measure and account for device latency during initialization.

## Online NOA

## Time Stretch Factor (α) Calculation

The Time Stretch Factor (α) determines the playback speed of the orchestral reference. Specifically, 1/α is the speed factor; for example, an α of 2 means the audio is played at 50% speed. The NOA module computes α in real time, and this value is then used by the TSM (Time-Scale Modification) module to adjust orchestral playback.

There are two main components to α calculation: regression estimation and catchup update.

### Regression (v0.1)

**Goal:**  
Estimate the local tempo ratio between the soloist and the orchestral reference over a recent window of time, providing a smooth, robust value for α.

**Key Parameters:**
- `history` (default: 100): Number of previous alignment points (frames) to consider for regression.
- `default_alpha` (default: 1.0): Fallback α value if insufficient history is available.
- `max_timewarp_factor`: Maximum allowed value for α (prevents extreme time-stretching).
- `initial_constant_period_frames`: For the first N frames, α is fixed at 1.0.

**Implementation Details:**
- The function `get_alpha(i, history, default_alpha)` computes α at alignment index `i` by performing a linear regression over the most recent `history` points in the alignment path.
- The regression estimates the local slope (tempo ratio) between the query (solo) and reference (orchestra) times.
- If insufficient history is available (e.g., at the start), α defaults to 1.0.
- The result is clamped to the range [1/`max_timewarp_factor`, `max_timewarp_factor`].
- The α value is updated at a frequency set by `alpha_update_frequency`.

**Relevant Code:**
```python
# noa.py

def get_alpha(self, i, history=100, default_alpha=1.0):
    if i <= self.initial_constant_period_frames:
        return 1.0
    # ... regression logic using self.path ...
```

### Catchup Update (v0.1)

**Goal:**  
Dynamically adjust α to correct for accumulated alignment drift or lag, ensuring the orchestral playback stays in sync with the soloist.

**Key Parameters:**
- `alpha_adjust_sensitivity`: Controls how aggressively α is adjusted in response to deviation.
- `alpha_adjust_max_scale` / `alpha_adjust_min_scale`: Bounds for scaling α during catchup.
- `alpha_adjust_frequency`: How often the catchup adjustment is applied.
- `lag_samples`: Number of samples to compensate for system latency.

**Implementation Details:**
- The function `adjust_alpha(pos, lag_samples)` computes the deviation between the current solo position and the aligned reference position.
- This deviation is mapped through a sigmoid function (for smoothness) and scaled to adjust α within preset bounds.
- The adjusted α is then used for TSM playback, helping the system "catch up" if it falls behind or gets ahead.
- This catchup update is applied at a frequency set by `alpha_adjust_frequency`, but only after the initial constant period.

**Relevant Code:**
```python
# noa.py

def adjust_alpha(self, pos, lag_samples=0):
    # Compute deviation between solo and reference
    # Map deviation to scale factor using sigmoid
    # Adjust self.current_alpha accordingly
```

## TSM

### Phase Vocoder

**Goal:**  
The Phase Vocoder is used to time-stretch the harmonic component of the audio without affecting its pitch. It enables smooth, high-quality time-scale modification by manipulating the phase information in the frequency domain.

**Key Parameters:**
- `L`: Window length for STFT (Short-Time Fourier Transform).
- `Hs`: Synthesis hop size (output frame advance).
- `Ha`: Analysis hop size (input frame advance, depends on α).
- `window`: Window function (e.g., Hanning window).
- α: Time stretch factor (ratio of output speed to input speed).
- `sr`: Sample rate.

**Implementation details:**
- The input audio is first separated into harmonic and percussive components.
- The harmonic component is processed using the phase vocoder:
  - The audio is windowed and transformed into the frequency domain using the STFT.
  - The phase vocoder modifies the phase of each frequency bin to account for the time-stretch factor, ensuring phase continuity and minimizing artifacts.
  - The processed frames are then transformed back to the time domain and overlap-added to reconstruct the output.

### OLA

**Goal:**  
The Overlap-Add (OLA) method is used to time-stretch the percussive component of the audio. OLA is simple and effective for transient, percussive sounds, where phase coherence is less critical.

**Key Parameters:**
- `L_ola`: Window length for OLA.
- `Hs_ola`: Synthesis hop size for OLA.
- `ratio`: Number of OLA frames per phase vocoder frame.
- `window`: Window function (e.g., Hanning window).

**Implementation details:**
- The percussive component is processed using OLA:
  - The audio is divided into overlapping frames.
  - Each frame is windowed and then overlap-added at the appropriate position in the output buffer.
  - The number of frames and their positions are determined by the time-stretch factor.

### Applying TSM in Simulated Online Setting

In the simulated online setting, TSM is applied as part of the alignment process using the `OfflineNOA` class (see `offline_noa.py`).

- **Initialization:**
  - When an `OfflineNOA` object is created, it checks if TSM is enabled (`self.tsm_enabled`).
  - If enabled, it loads the orchestral reference audio and creates a `TSM` object (`self.tsm`), passing the orchestral audio data.

- **During Alignment:**
  - The `align()` method processes the entire query (solo) features in a loop.
  - At each step, it updates the current time-stretch factor α using `get_alpha()` or `adjust_alpha()`.
  - If there is enough audio left, it calls `self.update_tsm_orch(pos)` to apply TSM to the orchestral audio at the current position.
  - `update_tsm_orch(pos)` sets the TSM’s α and calls `self.tsm.update_stream(...)` to generate the time-stretched output for the current chunk.
  - The output is not streamed in real time, but processed and optionally saved for later evaluation or playback.

**Key Points:**
- TSM is applied frame-by-frame as the alignment proceeds, using the computed α values.
- The process is in simulated real-time, i.e. the audio chunks are streamed into the TSM chunk by chunk as the alignment is being processed.
- The output can be saved for later analysis or listening.

### Applying TSM in Online Setting

In the online (real-time) setting, TSM is applied using the `NOA` class (see `noa.py`).

- **Initialization:**
  - When a `NOA` object is created with streaming enabled, it loads the orchestral audio and creates a `TSM` object (`self.tsm`).
  - It also sets up audio streaming infrastructure for real-time input and output.

- **During Live Streaming:**
  - The system starts two threads: one for processing incoming audio and alignment, and one for TSM playback (`_tsm_playback_thread`).
  - In the TSM playback thread, it repeatedly:
    - Updates the current α (using `get_alpha()` and `adjust_alpha()` as needed).
    - Calls `update_tsm_orch(self.pos, stream)` to apply TSM to the orchestral audio at the current position.
    - Writes the time-stretched output directly to the audio output stream in real time.
  - The TSM output is played back to the user as the system aligns the live solo input to the orchestral reference.

**Key Points:**
- TSM is applied in real time, chunk by chunk, as the alignment and audio input proceed.
- The output is streamed directly to the speakers (or output device) for live accompaniment.
- The α values are updated dynamically based on the alignment between the live soloist and the orchestral reference.

## Evaluation Method

**Goal**: We want to find a way to automatically evaluate our system without manual annotation/listening.

Our evaluation method involves the steps outlined below:

1. Given the _solo reference_ $S_{\rm ref}$, automatically generate time-scale modified _query file_ $S_M$ ($M$ for modified).
2. Perform NOA alignment with $S_M$ as the input to generate a sequence of time stretch factors α.
3. Use the time stretch factors to reconstruct another time-scale modified version of the reference $S_{\rm tsm}$. We call this the _reconstructed query_. In an ideal world $S_{\rm tsm}$ should be exactly the same as $S_M$.
4. We find all note onset times in the orchestra reference and solo reference. Since both $S_{\rm ref}-S_M$ and $S_{\rm ref}-S_{\rm tsm}$ are one-to-one matchings, we can map the reference onset times to query and reconstructed query onset times. We filter out the times that correspond to orchestra-only sections.
5. We calculate the difference between the onset times in the query and the reconstructed query. We call this the _reconstruction error_.
6. We can plot the reconstruction error over time to visualize where our errors are concentrated at. Alternatively, we can aggregate the errors and create error rate plots.

#### Key Difference between $S_M$ and $S_{\rm tsm}$

$S_M$ is the _query audio_, which is the input to the NOA system. $S_{\rm tsm}$ is the _reconstructed query audio_, which is the output to the real-time accompaniment (RTA) system.

Normally the RTA output is a time-scale modified orchestra reference $O_{\rm tsm}$. To construct $O_{\rm tsm}$, we use the time stretch factors that the NOA alignment produces and apply them on the original orchestra reference $O_{\rm ref}$. Our goal is to characterize how _in sync_ $O_{\rm tsm}$ is with $S_M$. However, since we know that $S_{\rm ref}$ and $O_{\rm ref}$ are perfectly synchronzied (and thus $S_{\rm tsm}$ and $O_{\rm tsm}$), characterizing how much $S_{\rm tsm}$ is in sync with $S_M$ is equivalent to chracterizing how much $O_{\rm tsm}$ is in sync with $S_M$!

### Automataic Query Generation

To evaluate our system, we need a way to generate query files _en masse_. To do this, we developed a system that could take a solo reference and a list of α values and time scale modify it to create a new query.  This will replace our old system of manual audio modifications an annotations.

There are multiple ways we could generate the list of alpha values. We currently have two methods:

(1) Completely random. The alpha values are completely random chosen within a range $[α_{\rm min}, α_{\rm max}]$;

(2) Random walk. The alpha values are generated as a sequence; the difference between eacfh element and the previous element in the sequence can be at most $Δα$.

$α_{\rm min}, α_{\rm max}$, and $Δα$ are system parameters.

### Alignment

The evaluation system works on online/offline RTA since both systems output a list of α values used during TSM. We will benchmark our results on lagged offline RTA.

The way we get the list of α values during alignment is we append α to a list of α histories at every feature frame. This way we will get a list of α values where the $i$-th element of the list indicate the α value at time $t = i \times \frac{\rm hop}{\rm sr}$.

#### Evaluating against Baseline Systems

For baseline systems, we decided to go with offline global DTW and MATCH (java implementation)

However, these systems are run offline, meaning that we run the alignment algorithm on a pair of feature files/audio files to get an alignment path. To simulate online alpha calculation, we interpolate the aligned paths so that there is one corresponding reference frame for every feature frame. Then, we process the query frames one by one in a simulated online fashion, calculating alpha in the same way that we would in online/simulated online NOA.

Currently we do not have ways to deal with solo or orchestra mode with the baselines. We are looking at ways to distinguish between these two modes in our baseline evaluations.

### Query Reconstruction

To reconstruct the query, we apply the sequence of alpha values (time-stretch factors) obtained from the alignment to the solo reference audio. This is done using the same time-scale modification (TSM) process used to generate the original query, but now using the alpha values estimated by the system rather than the ground truth.

- **Implementation:**  
  The reconstruction is typically performed frame-by-frame, applying each alpha to the corresponding segment of the solo reference. This is implemented in `utils/evaluation.py` (see `generate_stsm_evaluation`).

- **Goal:**  
  If the alignment and TSM are perfect, the reconstructed query ($S_{\rm tsm}$) should be identical to the generated query ($S_M$).

- **Pseudocode:**
  ```python
  for i, alpha in enumerate(alphas):
      # Apply TSM to solo reference using alpha
      reconstructed_chunk = tsm(solo_reference_chunk, alpha)
      reconstructed_query.append(reconstructed_chunk)
  ```

### Onset Detection

Sampling every frame while evaluating the system is not the best way, becuase frames have no musical meanings. Instead, we decided to evaluate the system on orchestra and solo onsets. This is because in an ideal world, the onsets for solo and orchestra should be perfectly synced up, but we don't care that much about the middle of notes. Even if the middle of a long note is messed up in the middle, there is no difference from an audience/a performer's perspective.

We call `librosa.onset.onset_detect` for onset detection. The algorithm is not perfect; it sometimes misses weak onsets. We're still experimenting with hyperparameters.

### Error Calculation

The reconstruction error quantifies how well the system can reproduce the timing of the generated query using the time-stretch factors estimated by the alignment. The process is as follows:

1. **Extract time arrays:**  
   - For each generated query $S_M$, record the time array $t_\text{mod}$ (the time of each frame in the modified query).
   - For each reconstructed query $S_\text{tsm}$, record the time array $t_\text{tsm}$ (the time of each frame in the reconstructed query).

2. **Compute reconstruction error:**  
   - For each frame $i$, compute the reconstruction error:
     $$
     {\rm Reconstruction Error}_i = |t_{{\rm mod},i} - t_{{\rm tsm},i}|
     $$
   - This gives a per-frame error curve over time.

3. **Aggregate error statistics:**  
   - To summarize performance, aggregate the errors across all frames and all generated queries.
   - Compute the percentage of frames where the error is below various thresholds (e.g., 200 ms, 1 s, 2 s).