#
# This script takes realtime input using pyaudio and communicates via serial.Serial
# with devices in the Technites psychedelic room to visualize the
# music on them.
#
## It talks to 4 devices
#   WaterFall -- tubes with LEDs and flying stuff fanned to music
#   DiscoBall -- 8 60 watt bulbs wrapped in colored paper
#   LEDWall   -- a 6 channel 6-strip of LED's with 2 woofers and 8 bulbs.
#   The woofers had 4 rings of LEDs arranged one inside another.
#   Bulbs were just 8 bulbs arranged in a circle.
#   LEDCube   -- a 4x4x4 RGB LED cube
#
# the script also has a sloppy pygame visualization of the fft and
# beats data
#

import sys
import time
import scipy
import pygame
from pygame import display
from pygame.draw import *

import pathsetup # this module sets up PYTHONPATH for all this to work

from devices.discoball import DiscoBall
from devices.waterfall import Waterfall
from devices.ledwall import LEDWall
from devices.cube import Cube
from devices.rgbcube import RGBCube

import phosphene
from phosphene import audio, signalutil, util
from phosphene.util import *
from phosphene.signal import *
from phosphene.dsp import *
from phosphene.graphs import *
from phosphene.signalutil import *
from cube import cubeProcess

#from phosphene import cube
from threading import Thread
import numpy
import pyaudio


# Setup devices with their corresponding device files

devs = [
        #Waterfall("/dev/ttyACM5"),
        #DiscoBall("/dev/ttyACM8"),
        LEDWall("/dev/ttyACM0")
        ]

pygame.init()
surface = display.set_mode((640, 480))

import serial

data = numpy.zeros((0,2))
sF = 44100
signal = Signal(data, sF)

signal.A = lift((data[:,0] + data[:,1]) / 2, True)
signal.beats = lift(lambda s: numpymap(lambda (a, b): 1 if a > b * 1.414 else 0, zip(s.avg8, s.longavg8)))

def initRecording(sig):
    p = pyaudio.PyAudio()
    def callback(in_data, frame_count, time_info, status):
        newSamples = numpy.fromstring(in_data,dtype=numpy.int16)
        sig.Y = numpy.append(sig.Y,zip(newSamples[::2],newSamples[1::2]),0)
        sig.A = lift((sig.Y[:,0] + sig.Y[:,1]) / 2, True)
        return (in_data,pyaudio.paContinue)
    stream = p.open(channels=2,
                    format=pyaudio.paInt16,
                    frames_per_buffer=1024,
                    rate=44100,
                    input=True,
                    input_device_index=3, #change input_device_index depending on the sound card
                    stream_callback=callback,
                    )
    return stream

for d in devs:
    d.setupSignal(signal)

def devices(s):
    #threads = []
    for d in devs:
        if d.isConnected:
            def f():
                d.redraw(s)
            #t = Thread(target=f)
            #threads.append(t)
            #t.start()
            f()

    #for t in threads:
    #    t.join(timeout=2)
    #    if t.isAlive():
    #        d.isUnresponsive()

    surface.fill((0, 0, 0))
    graphsGraphs(filter(
        lambda g: g is not None,
        [d.graphOutput(signal) for d in devs]))(surface, (0, 0, 640, 480))

CubeState = lambda: 0
CubeState.count = 0

cube = RGBCube("/dev/ttyACM1",4)

def cubeUpdate(signal):
    if signal.beats[0] or signal.beats[1] or signal.beats[2] or signal.beats[3]:
        CubeState.count = cubeProcess(cube, signal, CubeState.count)

def graphsProcess(s):
    display.update()

processes = [graphsProcess, devices, cubeUpdate]

signal.relthresh = 1.66

def sendingThread():
    while True:
        bs = cube.toByteStream()
        cube.port.write("S")
        print "Wrote S"
        readValue = cube.port.read()
        print readValue 
        for j in range(0,4):
            for i in range(0,3):
                cube.port.write(chr(bs[i][2*j]))
                print "wrote", bs[i][2*j]
                #time.sleep(0.0001)
                cube.port.write(chr(bs[i][2*j+1]))
                print "wrote", bs[i][2*j+1]
                #time.sleep(0.0001)
#t = Thread(target=sendingThread)
#t.start()

# run setup on the signal
signalutil.setup(signal)
stream = initRecording(signal)
print "Recording initiated..processing starting"
realTimeProcess(processes, signal, 90) # perceive your signal.
#t.join()
