import random


def get_classification():
    """
    This function is actually a webhook in which a more fancy classifier can
    be used.
    """

    # Return a random classification
    return random.randint(0, 1)
