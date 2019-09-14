import device
from phosphene.signal import *
from phosphene.signalutil import *
from phosphene.graphs import *

class DiscoBall(device.Device):
    def __init__(self, port):
        device.Device.__init__(self, "DiscoBall", port)

    def setupSignal(self, signal):
        def beats(s):
            return numpymap(lambda (a, b): 1 if a > b * 1.414 else 0, zip(s.avg6, s.longavg6)) 
        signal.beats = lift(beats)
        signal.discoball = blend(beats,0.7)

    def graphOutput(self, signal):
        return boopGraph(signal.discoball[:4])

    def redraw(self, signal):
        data = self.truncate(signal.discoball[:4] * 255)
        print data
        self.port.write(self.toByteStream(data))
