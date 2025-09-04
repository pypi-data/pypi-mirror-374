Welcome to RealtimeAccompaniment's documentation!
================================================

A real-time musical accompaniment system that listens to live performance and dynamically adjusts orchestral playback speed to stay synchronized with the performer.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   examples
   evaluation
   contributing

Features
--------

* **Real-time Alignment**: Tracks performer position in score using NOA algorithm
* **Dynamic Time-stretching**: Adjusts accompaniment playback speed in real-time
* **Live Audio Streaming**: Processes live audio input for real-time performance
* **Evaluation Framework**: Comprehensive testing and benchmarking tools
* **Multiple Baseline Systems**: Comparison with DTW and MATCH algorithms

Quick Start
-----------

.. code-block:: python

   from noa import NOA
   import librosa as lb

   # Initialize the system
   solo_reference = "path/to/solo_reference.wav"
   orch_reference = "path/to/orchestra_reference.wav"
   
   noa = NOA(
       cache_dir='cache',
       solo_reference=solo_reference,
       orch_reference=orch_reference,
       input_device=1,
       output_device=2,
       recording=True,
       outfile='output.wav'
   )

   # Start real-time accompaniment
   noa.start_live_streaming()
   # ... play your solo ...
   noa.stop_live_streaming()

Installation
-----------

.. code-block:: bash

   pip install realtime-accompaniment

For development installation:

.. code-block:: bash

   git clone https://github.com/yourusername/RealtimeAccompaniment.git
   cd RealtimeAccompaniment
   pip install -e ".[dev]"

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
