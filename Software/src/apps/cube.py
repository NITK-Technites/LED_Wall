from devices.cubelib import rgbemulator as emulator
from devices.cubelib import rgbwireframe as wireframe
from devices.rgbanimations import *

pv = emulator.ProjectionViewer(640,480)
wf = wireframe.Wireframe()
pv.createCube(wf)


start = (0, 0, 0)

def cubeProcess(cube, signal, count):
    start = (0, 0, 0)
    point = (0,0)
    #planeBounce(cube,(count/20)%2+1,count%20)
    colours = [[1,0,0],[0,1,0],[0,0,1]]
    #start = wireframeExpandContractFrames(cube,start,colours[(count/7)%3],count)
    rain(cube,count,2,4,1)
    #colourCube(cube)
    #quadrantColourSwap(cube)
    #time.sleep(.1)
    #point = voxel(cube,count,point)
    #sine_wave(cube,count)
    #pyramids(cube,count)
    #side_waves(cube,count)
    #fireworks(cube,4)
    #technites(cube,count)
    #planeBounce(cube,(count/8)%3,count%8,colours[(count/8)%3])
    cube.redraw(wf, pv)
    return count + 1
