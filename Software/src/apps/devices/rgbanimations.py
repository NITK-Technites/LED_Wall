import numpy
import random
import time

from cubelib import rgbwireframe
from cubelib import rgbemulator

# TODO:
# shiftPlane(axis, plane, delta)
#   moves the plane along the axis by delta steps, if it exceeds dimensions, just clear it out, don't rotate.
# swapPlanes(axis1, plane1, axis2, plane2)
# rain should set random LEDs on the first plane (not a lot of them)
#   and shift the plane along that axis by one step---Fixed
#   and shift the plane along that axis by one step
# Convert all animations to RGB.   
#
# THINK:
#   The python code keeps sending a 125 byte string to redraw the
#   cube as often as it can, this contains 1000 bit values that the MSP
#   handles. Now, in our code we have been using time.sleep() a lot.
#   We probably can have a counter that each of these functions uses to
#   advance its steps, and then increment / decrement that
#   counter according to music

off = [0,0,0] #Value to be passed to turn off a set of leds.

colourDict = {'red':[1,0,0], 'green':[0,1,0],'blue':[0,0,1],'rg':[1,1,0],'gb':[0,1,1],'rb':[1,0,1],'rgb':[1,1,1],'off':[0,0,0]}
            
def wireframeCubeCenter(cube,size,colours):
    if size % 2 == 1:
            size = size+1

    half = size/2
    start = cube.dimension/2 - half
    end = cube.dimension/2 + half - 1
    print start, end, colours
    for x in xrange(0,cube.dimension):
        for y in xrange(0,cube.dimension):
            for z in xrange(0,cube.dimension):
                cube.set_led(x,y,z,off)

    for x in (start,end):
        for y in (start,end):
            for z in xrange(start,end+1):
                cube.set_led(x,y,z,colours)
                cube.set_led(x,z,y,colours)
                cube.set_led(z,x,y,colours)

def wireframeCube(cube,START,END,colours):
    x0,y0,z0 = START
    x1,y1,z1 = END
    print "start:",START,"end:",END
    for x in xrange(0,cube.dimension):
        for y in xrange(0,cube.dimension):
                for z in xrange(0,cube.dimension):
                        cube.set_led(x,y,z,off)
    for x in (x0,x1):
        for y in (y0,y1):
            if z0<z1:
                for z in xrange(z0,z1+1):
                    cube.set_led(x,y,z,colours)
            else:
                for z in xrange(z1,z0+1):
                    cube.set_led(x,y,z,colours)
    for x in (x0,x1):
        for z in (z0,z1):
            if y0<y1:
                for y in xrange(y0,y1+1):
                    cube.set_led(x,y,z,colours)
            else:
                for y in xrange(y1,y0+1):
                    cube.set_led(x,y,z,colours)
    for y in (y0,y1):
        for z in (z0,z1):
            if x0<x1:
                for x in xrange(x0,x1+1):
                    cube.set_led(x,y,z,colours)
            else:
                for x in xrange(x1,x0+1):
                    cube.set_led(x,y,z,colours)

def solidCubeCenter(cube,size,colours):
    if size % 2 == 1:
        size = size+1

    half = size/2 
    start = cube.dimension/2 - half
    end = cube.dimension/2 + half
    for i in xrange(start,end):
        for j in xrange(start,end):
            for k in xrange(start,end):
                cube.set_led(i,j,k,colours)

def solidCube(cube,START,END,colours):
    x0,y0,z0 = START
    x1,y1,z1 = END
    for i in xrange(min(x0,x1),max(x0,x1)+1):
        for j in xrange(min(y0,y1),max(y0,y1)+1):
            for k in xrange(min(z0,z1),max(z0,z1)+1):
                cube.set_led(i,j,k,colours)

def setPlane(cube,axis,x,level):
    plane = level
    if len(level)==3:
        plane = numpy.array([[level]*10]*10, dtype=bool)
    if axis == 1:
        for i in xrange(0,cube.dimension):
            for j in xrange(0,cube.dimension):
                cube.set_led(x,i,j,plane[i][j])
    elif axis == 2:
        for i in xrange(0,cube.dimension):
            for j in xrange(0,cube.dimension):
                cube.set_led(i,x,j,plane[i][j])
    else:
        for i in xrange(0,cube.dimension):
            for j in xrange(0,cube.dimension):
                cube.set_led(i,j,x,plane[i][j])

def shiftPlane(cube,axis,plane,delta):
    if axis == 1:
        for i in xrange(0,cube.dimension):
	    for j in xrange(0,cube.dimension):
                try:
                    cube.set_led(plane+delta,i,j,cube.get_led(plane,i,j))
                    cube.set_led(plane,i,j,0)
                except:
                    cube.set_led(plane,i,j,0)
    elif axis == 2:
        for i in xrange(0,cube.dimension):
	    for j in xrange(0,cube.dimension):
                try:
                    cube.set_led(i,plane+delta,j,cube.get_led(i,plane,j))
                    cube.set_led(i,plane,j,0)
                except: 
                    cube.set_led(i,plane,j,0)
    else:
        for i in xrange(0,cube.dimension):
            for j in xrange(0,cube.dimension):
		try:
	            cube.set_led(i,j,plane+delta,cube.get_led(i,j,plane))
                    cube.set_led(i,j,plane,0)
                except:
		    cube.set_led(i,j,plane,0)

def randPlane(cube,minimum,maximum):
    array = numpy.array([[[0]*3]*cube.dimension]*cube.dimension,dtype = 'bool')
    for i in xrange(minimum,maximum):
        x = random.choice([i for i in xrange(0,cube.dimension)]) 
        y = random.choice([i for i in xrange(0,cube.dimension)])   
        colourKey = random.choice(colourDict.keys())
        array[x][y] = colourDict[colourKey]
    return array

def wireframeExpandContract(cube,start,colour,wf,pv):
    """Draws 2*cube.dimension frames. Need to fix to draw only 1"""
    (x0, y0, z0) = start

    for i in xrange(0,cube.dimension):
        j = cube.dimension - i - 1
        if(x0 == 0):
            if(y0 == 0 and z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0+i,z0+i),colour)
            elif(y0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0+i,z0-i),colour)
            elif(z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0-i,z0+i),colour)
            else:
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0-i,z0-i),colour)
        else:
            if(y0 == 0 and z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0+i,z0+i),colour)
            elif(y0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0+i,z0-i),colour)
            elif(z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0-i,z0+i),colour)
            else:
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0-i,z0-i),colour)
        time.sleep(0.08)
        cube.redraw(wf,pv)    
    max_coord = cube.dimension - 1
    corners = [0,max_coord]
    x0 = random.choice(corners)
    y0 = random.choice(corners)
    z0 = random.choice(corners)
    for j in xrange(0,cube.dimension):
        i = cube.dimension - j - 1
        if(x0 == 0):
            if(y0 == 0 and z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0+i,z0+i),colour)
            elif(y0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0+i,z0-i),colour)
            elif(z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0-i,z0+i),colour)
            else:
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0-i,z0-i),colour)
        else:
            if(y0 == 0 and z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0+i,z0+i),colour)
            elif(y0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0+i,z0-i),colour)
            elif(z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0-i,z0+i),colour)
            else:
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0-i,z0-i),colour)                 
        time.sleep(0.08)
        cube.redraw(wf,pv)    
    return (x0, y0, z0) # return the final coordinate

def rain(cube,counter,minimum,maximum,axis=3):
    shiftCube(cube,axis,1)
    setPlane(cube,axis,cube.dimension-1,randPlane(cube,minimum,maximum))
    
def planeBounce(cube,axis,counter,colour):
    i = counter%8
    if i:
        if i<4:          #to turn off the previous plane
            setPlane(cube,axis,i-1,off)
        elif i>4:
            setPlane(cube,axis,8-i,off)
    if i<4:
        setPlane(cube,axis,i,colour)
    elif i>4:
        setPlane(cube,axis,7-i,colour)
      
def square(cube,size,translate=(0,0)):
    x0,y0 = translate
    array = numpy.array([[0]*cube.dimension] * cube.dimension)
    for i in xrange(0,size):
	    for j in xrange(0,size):
	        array[i+x0][j+y0] = 1
    return array

def distance(point1,point2):
    x0,y0 = point1
    x1,y1 = point2
    return numpy.sqrt((x0-x1)**2 + (y0-y1)**2)

def circle(cube,radius,translate=(0,0)):
    x1,y1 = translate
    array = numpy.array([[0]*cube.dimension] * cube.dimension)
    for i in xrange(0,2*radius):
        for j in xrange(0,2*radius):
	    if distance((i,j),(radius,radius))<=radius:
		array[i+x1][j+y1] = 1
    return array

def fillCube(cube,level=[1,1,1]):
    for x in xrange(0,cube.dimension):
	    for y in xrange(0,cube.dimension):
	        for z in xrange(0,cube.dimension):
		        cube.set_led(x,y,z,level)
    
def voxel(cube,counter,point):
     x,y = point
     if(counter==0):
         fillCube(cube,0)
	 for x in xrange(0,cube.dimension):
            for y in xrange(0,cube.dimension):
    	        cube.set_led(x,y,random.choice([0,cube.dimension-1]))    
     if counter%9==0:
         x = random.choice([i for i in xrange(0,cube.dimension)])
         y = random.choice([i for i in xrange(0,cube.dimension)])
     if cube.get_led(x,y,counter%9)==1:
	     cube.set_led(x,y,counter%9+1)
	     cube.set_led(x,y,counter%9,0)
     else:
         cube.set_led(x,y,8-(counter%9))
         cube.set_led(x,y,9-(counter%9),0)
     return (x,y)

def shiftCube(cube,axis,delta):
      for x in xrange(0,cube.dimension):
        for y in xrange(0,cube.dimension):
            for z in xrange(0,cube.dimension-1):
                if axis == 3:
                    cube.set_led(x,y,z,cube.get_led(x,y,z+delta))
                    cube.set_led(x,y,z+delta,off)
                elif axis == 2:
                    cube.set_led(x,z,y,cube.get_led(x,z+delta,y))
                    cube.set_led(x,y,z+delta,off)
                elif axis == 1:
                    cube.set_led(z,x,y,cube.get_led(z+delta,x,y))
                    cube.set_led(z+delta,x,y,off)

def pyramids(cube,counter,axis = 3):
    if(counter%20 <cube.dimension):
        size = counter%10 + 1
        setPlane(cube,axis,cube.dimension-1,square(cube,counter%10 + 1,((cube.dimension-counter%10-1)/2,(cube.dimension-counter%10-1)/2)))
        shiftCube(cube,axis,1)
    else:
	size = 9 - (counter-10)%10
	translate = (cube.dimension - size)/2
        setPlane(cube,axis,cube.dimension-1,square(cube,size,(translate,translate)))
	shiftCube(cube,axis,1)
    time.sleep(0)
    print "counter = ",counter,"size=",size

def sine_wave(cube,counter):
    fillCube(cube,0)
    center = (cube.dimension-1)/2.0
    for x in xrange(0,cube.dimension):
	for y in xrange(0,cube.dimension):
            dist = distance((x,y),(center,center))
	    cube.set_led(x,y,int(counter%10+numpy.sin(dist+counter)))

def side_waves(cube,counter):
    fillCube(cube,0)
    origin_x=4.5;
    origin_y=4.5;
    for x in xrange(0,cube.dimension):
	for y in xrange(0,cube.dimension):
            origin_x=numpy.sin(counter);
            origin_y=numpy.cos(counter);
            z=int(numpy.sin(numpy.sqrt(((x-origin_x)*(x-origin_x))+((y-origin_y)*(y-origin_y))))+counter%10);
            cube.set_led(x,y,z);

def fireworks(cube,n):
    origin_x = 3;
    origin_y = 3;
    origin_z = 3;
    #Particles and their position, x,y,z and their movement,dx, dy, dz
    origin_x = random.choice([i for i in xrange(0,4)])
    origin_y = random.choice([i for i in xrange(0,4)])
    origin_z = random.choice([i for i in xrange(0,4)])
    origin_z +=5;
    origin_x +=2;
    origin_y +=2;
    particles = [[None for _ in xrange(6)] for _ in range(n)]
    #shoot a particle up in the air value was 600+500
    for e in xrange(0,origin_z):
        cube.set_led(origin_x,origin_y,e,1);
	time.sleep(.05+.02*e);
        cube.redraw()
	fillCube(cube,0)
    for f in xrange(0,n):
        #Position
        particles[f][0] = origin_x
	particles[f][1] = origin_y
	particles[f][2] = origin_z
	rand_x = random.choice([i for i in xrange(0,200)])
	rand_y = random.choice([i for i in xrange(0,200)])
	rand_z = random.choice([i for i in xrange(0,200)])

	try:
	    #Movement
            particles[f][3] = 1-rand_x/100.0  #dx
            particles[f][4] = 1-rand_y/100.0  #dy
            particles[f][5] = 1-rand_z/100.0  #dz
	except:
	    print "f:",f
    #explode
    for e in xrange(0,25):
        slowrate = 1+numpy.tan((e+0.1)/20)*10
        gravity = numpy.tan((e+0.1)/20)/2
        for f in xrange(0,n):
            particles[f][0] += particles[f][3]/slowrate
            particles[f][1] += particles[f][4]/slowrate
            particles[f][2] += particles[f][5]/slowrate;
            particles[f][2] -= gravity;
            cube.set_led(int(particles[f][0]),int(particles[f][1]),int(particles[f][2]))
    time.sleep(1000)
def randomFillCube(cube,counter):
    colour = counter%3
    if colour == 0:
        fillCube(cube,[1,0,0])
    elif colour == 1:
        fillCube(cube,[0,1,0])
    else:
        fillCube(cube,[0,0,1])

def colourCube(cube):
    r = random.choice([0,1]) 
    g = random.choice([0,1])
    b = random.choice([0,1])
    if (r,g,b) is (0,0,0):
        r=1
    fillCube(cube,[r,g,b])

def fillOneByOne(cube,count,colour):
    count = count%64
    if count == 0:
        fillCube(cube,off)
    x = count/16
    y = (count/4)%4
    z = count%4
    if count>0:
        prevx = (count-1)/16
        prevy = ((count-1)/4)%4
        prevz = (count-1)%4
        cube.set_led(prevx,prevy,prevz,off)
    cube.set_led(x,y,z,colour)

def quadrantColourSwap(cube):
    shuffledColorKeys = random.sample(colourDict.keys(),len(colourDict))
    quadrantSize = cube.dimension/2-1
    corners = [(x,y,z) for x in [0,cube.dimension-1] for y in [0,cube.dimension-1] for z in [0,cube.dimension-1]]
    colour =0
    for x,y,z in corners:
        if x == cube.dimension-1:
            newx = x-quadrantSize
        else:
            newx = x+quadrantSize
        if y == cube.dimension-1:
            newy = y-quadrantSize
        else:
            newy = y+quadrantSize
        if z == cube.dimension-1:
            newz = z-quadrantSize
        else:
            newz = z+quadrantSize
        solidCube(cube,(x,y,z),(newx,newy,newz),colourDict[shuffledColorKeys[colour]])
        colour+=1

def wireframeExpandContractFrames(cube,start,colour,frame):
    """Frame 0 decide start"""
    (x0, y0, z0) = start
    frame = frame/3
    frame = frame%7
    if frame==0:
        fillCube(cube,[0,0,0])
    if frame<4:
        i = frame%4
        j = cube.dimension - i - 1
        if(x0 == 0):
            if(y0 == 0 and z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0+i,z0+i),colour)
            elif(y0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0+i,z0-i),colour)
            elif(z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0-i,z0+i),colour)
            else:
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0-i,z0-i),colour)
        else:
            if(y0 == 0 and z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0+i,z0+i),colour)
            elif(y0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0+i,z0-i),colour)
            elif(z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0-i,z0+i),colour)
            else:
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0-i,z0-i),colour)
    if frame ==4:
        max_coord = cube.dimension - 1
        corners = [0,max_coord]
        x0 = random.choice(corners)
        y0 = random.choice(corners)
        z0 = random.choice(corners)
    if frame>=4:
        i = cube.dimension - (frame-3)%4 - 1
        if(x0 == 0):
            if(y0 == 0 and z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0+i,z0+i),colour)
            elif(y0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0+i,z0-i),colour)
            elif(z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0-i,z0+i),colour)
            else:
                wireframeCube(cube,(x0,y0,z0),(x0+i,y0-i,z0-i),colour)
        else:
            if(y0 == 0 and z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0+i,z0+i),colour)
            elif(y0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0+i,z0-i),colour)
            elif(z0 == 0):
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0-i,z0+i),colour)
            else:
                wireframeCube(cube,(x0,y0,z0),(x0-i,y0-i,z0-i),colour)                 
    return (x0, y0, z0) # return the start/end coordinate
