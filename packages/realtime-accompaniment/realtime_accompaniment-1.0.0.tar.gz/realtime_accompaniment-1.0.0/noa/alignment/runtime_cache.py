import numpy as np
import utils.constants as constants


class AlphaCache:
    """Cache for alpha values.

    This class is used to cache the alpha values for the runtime alignment.

    Args:
        history (int): The number of previous locations to consider for calculating the alpha value.
    """

    def __init__(self, history=constants.DEFAULT_ALPHA_LOOKBACK):
        """Initialize the cache.

        Args:
            history (int): The number of previous locations to consider for calculating the alpha value.
        """
        self.history = history
        self.x = np.arange(-history + 1, 1, dtype=np.float64)  # query
        self.sum_x = np.sum(self.x)
        self.sum_x2 = np.sum(self.x * self.x)
