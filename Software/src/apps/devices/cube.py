import serial
import numpy
import math
from device import Device
from cubelib import emulator
from cubelib import mywireframe as wireframe
from animations import *
import time
import threading

# A class for the cube
#TODO:Fix up animations to add the new pv variable.

class Cube(Device):
    def __init__(self, port, dimension=10, emulator=False):
        Device.__init__(self, "Cube", port)
        self.array = numpy.array([[\
                [0]*dimension]*dimension]*dimension, dtype='bool')
        self.dimension = dimension
        self.emulator = emulator
        self.name = "Cube"

    def set_led(self, x, y, z, level=1):
        self.array[x][y][z] = level

    def get_led(self, x, y, z):
        return self.array[x][y][z]

    def takeSignal(self, signal):
        pass

    def toByteStream(self):
        # 104 bits per layer, last 4 bits waste.
 
        bytesPerLayer = int(math.ceil(self.dimension**2 / 8.0))
        discardBits = bytesPerLayer * 8 - self.dimension**2
        bts = bytearray(bytesPerLayer*self.dimension)

        pos = 0
        mod = 4

        for layer in self.array:
            for row in layer:
                for bit in row:
                    if bit: bts[pos] |= 1 << mod
                    else: bts[pos] &= ~(1 << mod)

                    mod += 1

                    if mod == 8:
                        mod = 0
                        pos += 1
                        
        return bts

    def redraw(self, wf=None, pv=None):
        if self.emulator:
            wf.setVisible(emulator.findIndexArray(self.array))
            pv.run()

if __name__ == "__main__":
    cube = Cube("/dev/ttyACM1",10,True)
    pv = emulator.ProjectionViewer(640,480)
    wf = wireframe.Wireframe()
    pv.createCube(wf)
    count = 0
    start = (0, 0, 0)
    point = (0,0)
    fillCube(cube,0)
    #cube.redraw()
    #time.sleep(100)
    def sendingThread():
        while True:
            cube.port.write("S")
            bs = cube.toByteStream()
            #time.sleep(0.01)
            cube.port.write("L")
            print "wrote L"
            ack = cube.port.read(size=1)
            print "Ack recieved", ack
            for i in range(0, 130):
                if i%13==0:
                    cube.port.write("S")
                    print "Wrote S"
                    ack = cube.port.read(size=1)
                    print "Ack recieved", ack
                    #time.sleep(0.01)
                cube.port.write(chr(bs[i]))
                print "wrote", bs[i]

    t = threading.Thread(target=sendingThread)
    t.start()
    while True:
        #wireframeCube(cube,(1,1,1),(9,9,9))
        if count==0:
            fillCube(cube, 0)
            cube.redraw(wf,pv)
            count+=1
            continue
        #planeBounce(cube,(count/20)%2+1,count%20)
        #planeBounce(cube,1,count)
        #start = wireframeExpandContract(cube,start)
        #rain(cube,count,5,10)
	#drawFunc(cube,lambda x,y:x**2+y**2,count)
        #point = voxel(cube,count,point)
	#sine_wave(cube,count)
	#pyramids(cube,count)
	#side_waves(cube,count)
	#fireworks(cube,4)
        #technites(cube, count)
        #setPlane(cube,1,(counter/100)%10,1)
        #setPlane(cube,2,0,1)
	#stringPrint(cube,'TECHNITES',count)
        #moveFaces(cube)
        #cube.set_led(0,0,0)
        #cube.set_led(0,0,1)
        #dotTest(cube,count-10)
        #setPlane(cube,1,(count-1)%cube.dimension,0)
        #setPlane(cube,1,count%cube.dimension)
        #cube.set_led(0,0,3)
        fillCube(cube,count%2)
        cube.redraw(wf,pv)
        count += 1
	time.sleep(.1)
