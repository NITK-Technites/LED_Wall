import device
from phosphene.signal import *
import scipy, numpy
from phosphene.graphs import barGraph
import math
from phosphene import signalutil
from phosphene.util import *
""" The LEDWall is a device which composed of a 6*6 square of led strips.
    Attached to it were 2 "woofers" which had 4 rings of leds 
    and 4 "pillars" which had 6 rings of leds. The LEDWall was used as an equaliser while the
    woofers and the pillars responded to beats. """

class LEDWall(device.Device):
    def __init__(self, port):
        device.Device.__init__(self, "LEDWall", port)

    def setupSignal(self, signal):
        def LEDWall(s):
            lights = [s.avg6[i] * 150 / max(0.5, s.longavg6[i]) \
                            for i in range(0, 6)]

            lights.reverse()
            return lights
        
        def beats(s):
            return numpymap(lambda (a, b): 1 if a > b * 1.3 else 0, zip(s.avg6, s.longavg6))
        signal.woofers = signalutil.blend(beats, 0.7) #Beats
        signal.ledwall = lift(LEDWall) 

    def graphOutput(self, signal):
        return barGraph(self.truncate(signal.ledwall) / 255.0)

    def redraw(self, signal):
        payload = self.toByteStream(signal.ledwall,signal.woofers)
        self.port.write("S") #Start
        ack = self.port.read(size=1) #Ack
        self.port.write(payload) #Data - First byte - woofers.

    def toByteStream(self,array,wooferArray):
        data = []
        bts = bytearray(6)
        LEVELS = 6
        beatVal  = wooferArray[1]
        #Writing 0 to the woofers for now.
        def woofByteStream(val,pos,mod):
                n = int(math.ceil(val*4))
                if val<0.5:
                    n=0
                print val,n,bts[pos]
                for i in range(0,n):
                    bts[pos] |= (1<<(mod+i))
                    print bts[pos]
        def pillarByteStream(val,pos, mod):
            n = int(math.ceil(val*6))
            if val<0.5:
                n=0
            print val,n,bts[pos]
            for i in range(0,n):
                bts[pos] |= (1<<(mod+i))
                print bts[pos]
        pillarByteStream(beatVal,0, 0) #pillar data - 1st 2 bits slack, next 6 pillar data.        
        woofByteStream(beatVal,1, 4) #Woofers first 4 bits of 2nd byte
        
        def group(val):
            div = 85.34 #512/6
            if val < 5:
                return [0 for i in range(0,LEVELS)]
            n = min(6,int(math.ceil(val/div))) #Number of levels to be lit. (0-6)
            return [1 for i in range(0,n)] + [0 for i in range(0,6-n)]
        #Convert into a nested array. 6 values with 6 values inside.
        for value in array:
            data.append(group(value))
        #Now convert into Bytes.
        #First 4 bits is for pillar and is set earlier.
        pos = 1
        mod = 4
        for channel in data:
            for strip in channel:
                if strip: bts[pos] |= (1 << (7 - mod))
                else: bts[pos] &= (~(1<<(7 - mod)))
                mod += 1
                if mod == 8:
                    mod = 0
                    pos+=1
        return bts
