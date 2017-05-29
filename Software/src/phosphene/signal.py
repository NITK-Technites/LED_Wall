import time

import numpy

from util import indexable

__all__ = [
    'Signal',
    'lift',
    'foldp',
    'perceive',
    'realTimeProcess',
]


class lift:
    """ Annotate an object as lifted """
    def __init__(self, f, t_indexable=None):
        self.f = f
        if hasattr(f, '__call__'):
            self._type = 'lambda'
        elif isinstance(self.f, (list, tuple, numpy.ndarray)):
            self._type = 'iterable'
        else:
            raise ValueError(
                    """You can lift only a function that takes
                       the signal as argument, or an iterable"""
            )

        self.indexable = t_indexable

    def _manifest(self, signal):

        # compute the current value of this lifted
        # function given the current value of the signal

        if self._type == "lambda":
            return self.f(signal)
        elif self._type == "iterable":
            if self.indexable is None or self.indexable:
                # Make the array temporally indexable
                return indexable(self.f, signal.x)
            elif indexable == False:
                return self.f[signal.x]


def foldp(f, init=None):
    """Fold a value over time
    """

    State = lambda: 0         # hack to let me store state
    State.store = init
    State.val = None

    def g(signal):
        val, store = f(signal, State.store)
        State.store = store
        State.val = val
        return val
    return lift(g)


class _WAIT:
    # _WAIT instances are used in the locking
    # mechanism in Signal to avoid recomputation
    # when multiple threads are using a signal
    pass


class Signal:
    """ The Signal abstraction. """
    def __init__(self, Y, sample_rate, max_fps=90):
        self.Y = Y
        self.x = 0
        self.fps = 0
        self.max_fps = max_fps
        self.sample_rate = sample_rate
        self.lifts = {}
        self.t = lift(lambda s: s.time())
        self.A = lift(Y[:,0], True)
        self.cache = {}

    def time(self, t=time.time):
        # this signal's definition of time
        return t()

    def __getattr__(self, k):
        # call the thing that is requred with self
        if self.lifts.has_key(k):
            # Lifted values must have the same value
            # for the same x. Cache them.
            # This also helps in performance e.g. when
            # fft is needed a multiple places

            if self.cache.has_key(k):
                if isinstance(self.cache[k], _WAIT):
                    # Locking mechanism to avoid
                    # redundant computations by threads
                    while isinstance(self.cache[k], _WAIT):
                        pass
                    return self.cache[k][1]
                else:
                    x, val = self.cache[k]
                    if x == self.x:
                        return val

            self.cache[k] = _WAIT()
            val = self.lifts[k]._manifest(self)
            self.cache[k] = (self.x, val)
            return val
        else:
            return self.__dict__[k]

    def __setattr__(self, k, v):
        if isinstance(v, lift):
            self.lifts[k] = v
        else:
            self.__dict__[k] = v

    def set_state(self, x, fps, frames):
        self.x = x
        self.fps = fps
        self.frames = frames

    def clear_data(self, slc):
        self.Y = numpy.delete(self.Y,slc,0)
        self.cache = {}
        self.A = lift(self.Y[:,0],True)

def perceive(processes, signal, max_fps, realTime = False):
    """Let processes perceive the signal

    simulates real-time reading of signals and runs all the functions
    in processes (these functions take the current signal value as
    argument)
    """
    start_time = signal.time()
    call_spacing = 1.0 / max_fps
    sample_count = len(signal.Y)
    prev_x = -1
    x = 0
    frames = 0
    fps = max_fps

    while True:
        tic = signal.time()

        # what should be the current sample?
        x = int((tic - start_time) * signal.sample_rate)
        sample_count = len(signal.Y)
        if not realTime and x >= sample_count:
            break
        while realTime and sample_count-x<1312:
            print "waiting for samples of ", sample_count-x
            time.sleep(0.032)
            sample_count = len(signal.Y)
            continue
        frames += 1

        # approximate current fps
        fps = fps * 0.5 + 0.5 * signal.sample_rate / float(x - prev_x)

        # Advance state of the signal
        signal.set_state(x, fps, frames)

        for p in processes:
                p(signal)     # show processes the signal

        prev_x = x

        toc = signal.time()
        wait = call_spacing - (toc - tic)

        # chill out before looping again
        # FIXME: this assumes that the frame rate varies smoothly
        #        i.e. next frame takes approximately takes the
        #        same time as few frames immediately before it
        if wait > 0:
            time.sleep(wait)

def realTimeProcess(processes,signal,max_fps):
    jumps = signal.sample_rate / max_fps
    jumpsPer1024 = 1024.0 / jumps
    call_spacing = 0.02333/jumpsPer1024
    prev_x = -1
    x = 0
    frames = 0
    fps = max_fps
    while True:
        tic = time.time()
        sample_count = len(signal.Y)
        if sample_count>=44100*30:
            print "Called"
            signal.clear_data(numpy.s_[:-1400:])
            x = 1400
            continue
        if sample_count-x<1312:
            time.sleep(0.001)
            #print "waiting",sample_count-x
            continue
        frames+=1
        fps = fps*0.5 + 0.5 *signal.sample_rate / float(x-prev_x)
        #print sample_count, x, fps, sample_count-x
        #print "time" , sample_count/44100
        signal.set_state(x,fps,frames)
        for p in processes:
            p(signal)

        prev_x = x
        x += jumps

        toc = time.time()
        wait = call_spacing - (toc-tic)
        if wait>0:
            time.sleep(wait)
