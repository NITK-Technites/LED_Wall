import serial
import numpy
import math
from device import Device
from cubelib import rgbemulator as emulator
from cubelib import rgbwireframe as wireframe
from rgbanimations import *
import time
import threading

# A class for the RGBcube
# TODO : 
# Add RGB value dimension to the layer - DONE.
# Convert the ByteStream function to send proper data- DONE. 
# Proper animations.
 
#Sending each layer of red first followed by green and then blue. 1 frame -25bytes.

class RGBCube(Device):
    def __init__(self, port, dimension=4, emulator=False):
        Device.__init__(self, "RGBCube", port)
        self.array = numpy.array([[[\
                [0]*3]*dimension]*dimension]*dimension, dtype='bool')
        self.dimension = dimension
        self.emulator = emulator
        self.name = "RGBCube"

    def set_led(self, x, y, z, level=[1,1,1]):
        self.array[x][y][z] = level

    def get_led(self, x, y, z):
        return self.array[x][y][z]

    def takeSignal(self, signal):
        pass

    def toByteStream(self):
        # 16 bits per layer, 0 bits waste. 
        # Note : Bytes to be read in reverse order.
 
        bytesPerLayer = int(math.ceil((self.dimension**2) / 8.0)) #4**2/8 = 2
        discardBits = bytesPerLayer * 8 - self.dimension**2 # 2*8 - 4**2 = 0
        bts = []
        for i in range(0,3):
            #3 bytearrays - bts[0] - red stream, bts[1] green stream, bts[2] - blue
            bts.append(bytearray(bytesPerLayer*self.dimension)) #2*4 3times
        pos = 0
        mod = 0
        for layer in self.array:
            mod = discardBits
            for row in layer:
                for bit in row:
                    for i in range(0,3):
                        if bit[i]: bts[i][pos] |= 1 << mod
                        else: bts[i][pos] &= ~(1 << mod)
                    mod += 1
                    if mod == 8:
                        mod = 0
                        pos += 1
        return bts

    def redraw(self, wf=None, pv=None):
        if self.emulator:
            wf.setVisible(emulator.findIndexArray(self.array))
            pv.run()

    def sendData(self):
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

def setupEmulator():
    pv = emulator.ProjectionViewer(640,480)
    wf = wireframe.Wireframe()
    pv.createCube(wf)
    return (pv,wf) 
if __name__ == "__main__":
    cube = RGBCube("/dev/ttyACM1",4,True)
    pv = emulator.ProjectionViewer(640,480)
    wf = wireframe.Wireframe()
    pv.createCube(wf)
    count = 0
    start = (0, 0, 0)
    point = (0,0)
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
    t = threading.Thread(target=sendingThread)
    t.start()
    
    count =0
    colorNumber = 0
    fillCube(cube,off)
    while True:
        #randomFillCube(cube,count)
        colours = [[1,0,0],[0,1,0],[0,0,1]]
        #wireframeCubeCenter(cube,count%(cube.dimension),colours[(count/4)%3])
        #colourCube(cube)
        #start = wireframeExpandContractFrames(cube,start,colours[(count/7)%3],count)
        #fillOneByOne(cube,count%65,colours[2])
        #rain(cube,count,2,4,1)
        #quadrantColourSwap(cube)
        planeBounce(cube,(count/8)%3,count%8,colours[(count/8)%3])
        #fillOneByOne(cube,count,colours[count%3])
        cube.redraw(wf,pv)
        time.sleep(1)
        """
        if count==64:
            count=0
            colorNumber=(colorNumber+1)%3
        """
        count += 1
