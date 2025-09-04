import pickle


def get_config(preset):
    """
    Get the configuration for a given preset.
    
    Returns:
        solo_reference (str): Path to the solo reference audio file.
        orch_reference (str): Path to the orchestral reference audio file.
        query (str): Path to the query audio file.
    """
    with open("cfg/presets.pkl", "rb") as f:
        d = pickle.load(f)
    solo_reference = d[preset]["solo_reference"]
    orch_reference = d[preset]["orch_reference"]
    query = d[preset]["query"]
    return solo_reference, orch_reference, query


def get_presets():
    """
    Get the list of presets.
    """
    with open("cfg/presets.pkl", "rb") as f:
        d = pickle.load(f)
    return list(d.keys())
