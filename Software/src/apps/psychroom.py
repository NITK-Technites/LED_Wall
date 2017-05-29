#
# This script plays an mp3 file and communicates via serial.Serial
# with devices in the Technites psychedelic room to visualize the
# music on them.
#
# It talks to 4 devices
#   WaterFall -- tubes with LEDs and flying stuff fanned to music
#   DiscoBall -- 8 60 watt bulbs wrapped in colored paper
#   LEDWall   -- a 4 channel strip of LED
#                this time it was the LED roof instead :p
#   LEDCube   -- a 10x10x10 LED cube - work on this is still on
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


# Setup devices with their corresponding device files

devs = [
        #Waterfall("/dev/ttyACM5"),
        #DiscoBall("/dev/ttyACM8"),
        LEDWall("/dev/ttyACM0")
        ]

pygame.init()
surface = display.set_mode((640, 480))

if len(sys.argv) < 2:
    print "Usage: %s file.mp3" % sys.argv[0]
    sys.exit(1)
else:
    fPath = sys.argv[1]

sF, data = audio.read(fPath)

import serial

signal = Signal(data, sF)

signal.A = lift((data[:,0] + data[:,1]) / 2, True)
signal.beats = lift(lambda s: numpymap(lambda (a, b): 1 if a > b * 1.414 else 0, zip(s.avg8, s.longavg8)))

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

cube = RGBCube("/dev/ttyACM2",4)

def cubeUpdate(signal):
    if signal.beats[0] or signal.beats[1] or signal.beats[2] or signal.beats[3]:
        CubeState.count = cubeProcess(cube, signal, CubeState.count)

def graphsProcess(s):
    display.update()

processes = [graphsProcess, devices, cubeUpdate]

signal.relthresh = 1.66

soundObj = audio.makeSound(sF, data)
    # make a pygame Sound object from the data

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
t = Thread(target=sendingThread)
t.start()

# run setup on the signal
signalutil.setup(signal)
soundObj.play()                      # start playing it. This is non-blocking
perceive(processes, signal, 36)      # perceive your signal.
