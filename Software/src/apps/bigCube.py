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
    #start = wireframeExpandContract(cube,start)
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
    cube.redraw(wf, pv)
    return count + 1
