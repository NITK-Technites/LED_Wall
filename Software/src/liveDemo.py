import sys
import pdb
import pygame
from pygame import display
from pygame.draw import *
import scipy
import time
import numpy as np
import pyaudio

from phosphene import audio, util, signalutil, signal
from phosphene.graphs import barGraph, boopGraph, graphsGraphs

from threading import Thread

# initialize PyGame
SCREEN_DIMENSIONS = (640, 480)
pygame.init()
surface = display.set_mode(SCREEN_DIMENSIONS)
data = np.zeros((0,2)) #HACK
sF = 44100
sig = signal.Signal(data, sF)

def beats(s):
    """ Extract beats in the signal in 4 different
        frequency ranges """

    # quick note: s.avg4 is a decaying 4 channel fft
    #             s.longavg4 decays at a slower rate
    # beat detection huristic:
    #       beat occured if s.avg4 * threshold > s.longavg4

    threshold = 1.7
    return util.numpymap(
            lambda (x, y): 1 if x > threshold * y else 0,
            zip(s.avg4 * threshold, s.longavg4))

# Lift the beats
sig.beats = signal.lift(beats)
# not sure if this can be called sustain.
# blend gives a decay effect
sig.sustain = signalutil.blend(beats, 0.7)

def graphsProcess(s):
    # clear screen
    surface.fill((0, 0, 0))
    # draw a decaying fft differential and the beats in the full
    # pygame window.
    graphsGraphs([
        barGraph(s.avg12rel / 10),
        boopGraph(s.beats),
        boopGraph(s.sustain)
    ])(surface, (0, 0) + SCREEN_DIMENSIONS)
    # affect the window
    display.update()

def repl():
    """ call this function to give you a pdb shell
        while the program is running. You will be
        dropped in the current context. """

    def replFunc():
        pdb.set_trace()

    replThread = Thread(target=replFunc)
    replThread.start()
#repl()

def initRecording(sig):
    p = pyaudio.PyAudio()
    def callback(in_data, frame_count, time_info, status):
        nextTime = time.time()
        newSamples = np.fromstring(in_data,dtype=np.int16)
        sig.Y = np.append(sig.Y,zip(newSamples[::2],newSamples[1::2]),0)
        sig.A = signal.lift((sig.Y[:,0] + sig.Y[:,1]) / 2, True)
        startTime = nextTime
        return (in_data,pyaudio.paContinue)
    startTime = time.time()
    stream = p.open(channels=2,
                    format=pyaudio.paInt16,
                    frames_per_buffer=1024,
                    rate=44100,
                    input=True,
                    input_device_index=3, #change input_device_index depending on the sound card
                    stream_callback=callback,
                    )
    return stream
# apply utility "lift"s -- this sets up signal.avgN and longavgN variables
signalutil.setup(sig)
# perceive signal at 90 fps (or lesser when not possible)
stream = initRecording(sig)
signal.realTimeProcess([graphsProcess], sig, 90)
