from timeit import default_timer


class Timer(object):
    """ A modified version of the timer written for the scraper.
    :param name: String, name for the timer to help with identification when using multiple timers
    """

    def __init__(self, name):
        self.name = name
        self._start_timer = None
        self._stop_timer = None

    def start(self):
        self._start_timer = default_timer()

    def stop(self):
        self._stop_timer = default_timer()

    @property
    def current(self):
        running_time = default_timer() - self._start_timer
        return running_time
