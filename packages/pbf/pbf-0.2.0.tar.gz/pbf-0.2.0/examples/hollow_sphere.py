import os
import psutil

hyperthreading = False

os.environ["OMP_NUM_THREADS"] = str(psutil.cpu_count(logical=hyperthreading))

import math
import time
import shutil
import pbf
import numpy

print(f"OMP_NUM_THREADS={os.environ["OMP_NUM_THREADS"]}")

units = pbf.units


## ======== Path construction ======== 

def generateLevelTrack(r0, r1, time, zlevel, ilayer, pauseTime):

    track = []
    
    # Add contour circles
    def addContour(time, radius):
        track.append(pbf.LaserPosition(xyz=[radius, 0.0, zlevel], power=0, time=time))
        for i in range(1, 51):
            x, y = radius * math.cos(2 * i * math.pi / 50), radius * math.sin(2 * i * math.pi / 50)
            time += math.sqrt((track[-1].xyz[0] - x)**2 + (track[-1].xyz[1] - y)**2) / laserSpeed
            track.append(pbf.LaserPosition(xyz=[x, y, zlevel], power=laserPower, time=time))
        return time + pauseTime
        
            
    if r0 > 0: time = addContour(time, r0)
    if r1 > 0: time = addContour(time, r1)
    
    # Generate coordinates for hatch lines
    def hatchTicks(xmin, xmax):
        return numpy.linspace(xmin, xmax, int((xmax - xmin) / hatchDistance) + 1)[1:-1].tolist()
        
    if r0 > 0 and r1 > 0:
        xvalues = hatchTicks(-r1, -(r0 - hatchDistance / 2)) +                    \
                  hatchTicks(-(r0 + hatchDistance / 2), r0 + hatchDistance / 2) + \
                  hatchTicks(r0 - hatchDistance / 2, r1)
    elif r1 > 0:
        xvalues = hatchTicks(-r1, r1)
    else:
        xvalues = []

    # Add hatch lines (potentially split in two parts)
    def addHatchLine(time, i, x, y0, y1):
        track.append(pbf.LaserPosition(xyz=[x, y0, zlevel], power=0, time=time))
        time += abs(y1 - y0) / laserSpeed
        track.append(pbf.LaserPosition(xyz=[x, y1, zlevel], power=laserPower, time=time))
        return time + pauseTime
        
    for i, x in enumerate(xvalues):
        y = math.sqrt(r1**2 - x**2) - 0.5 * hatchDistance * r1 / math.sqrt(r1**2 - x**2)
        if x <= -r0 or x >= r0:         
            if i % 2 != 0: 
                time = addHatchLine(time, i, x, -y, y)
            else:
                time = addHatchLine(time, i, x, y, -y)
        else:
            y2 = math.sqrt(r0**2 - x**2) + 0.5 * hatchDistance * r0 / math.sqrt(r0**2 - x**2)
            if i % 2 != 0: 
                time = addHatchLine(time, i, x, -y, -y2)
                time = addHatchLine(time, i, x, y2, y)
            else:
                time = addHatchLine(time, i, x, y2, y)
                time = addHatchLine(time, i, x, -y, -y2)
                
    # Flip x and y for odd layers
    if ilayer % 2 != 0:
        for ti in track:
            ti.xyz = [ti.xyz[1], ti.xyz[0], ti.xyz[2]]

    return track

def measureLaserOn(track: list[pbf.LaserPosition]) -> (float, float):
    distance, duration = 0.0, 0.0
    for pos0, pos1 in zip(track[:-1], track[1:]):
        if pos1.power > 0.0:
            diff = [(x1 - x0)**2 for x0, x1 in zip(pos0.xyz, pos1.xyz)]
            distance += math.sqrt(diff[0] + diff[1] + diff[2])
            duration += pos1.time - pos0.time
    return distance, duration

## ======= Process parameters ======== 
material = pbf.makeMaterial("SS316L")
material.regularization = 1

laserD4Sigma = 80 * units.um
laserSpeed = 800.0 * units.mm / units.s
laserPower = 280.0 * units.W

laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.32)

layerThickness = 50 * units.um 
hatchDistance = 80 * units.um

timeBeforeDeposition = 20 * units.ms # Time before new powder layer is added
depositionTimeStep = 4 * units.s     # Length of layer extension (single) time step
timeAfterDeposition = 20 * units.ms   # Time after new powder layer was added
pauseTime = 2 * units.ms             # Time between hatch lines

nlayers = 30
basePlateHeight = 4 * units.mm

domainMin = [-1/2 * units.cm, -1/2 * units.cm, -basePlateHeight]
domainMax = [+1/2 * units.cm, +1/2 * units.cm, layerThickness * nlayers]

radius0 = 1.0 * units.mm
radius1 = 1.5 * units.mm

emissivity = 0.1
convectionCoefficient = 1e-5 * units.W / units.mm ** 2 / units.C

## ====== Simulation parameters ====== 
coarseMesh = True

trefinement = 5 # Temperature grid refinement
srefinement = 6 # Material grid refinement

elementsize = layerThickness / 2 if coarseMesh else coarseMesh / 4
timestep = 0.33 * laserD4Sigma / laserSpeed

filebase = f"outputs/hollow_sphere"
outputInterval = 32

depthSigma = max(0.3 * laserD4Sigma / 4, 0.7 * elementsize)

grid = pbf.createMesh(domainMin, domainMax, elementsize * 2**trefinement, layerThickness)

## =========== Simulation ============
processSimulation = pbf.ProcessSimulation(grid=grid, material=material,
    layerThickness=layerThickness, ambientTemperature=25.0)

tsetup = pbf.ThermalProblem(processSimulation, degree=1)

tstate = pbf.makeThermalState(tsetup, grid, srefinement=srefinement)
info = pbf.stateInfoOutput(filebase + "/stateinfo.csv")
shutil.copy(__file__, filebase + "/" + os.path.basename(__file__))

for ilayer in range(nlayers):
    print(f"Layer {ilayer + 1} / {nlayers}", flush=True)
    zlevel = (ilayer + 1) * layerThickness
    r0Level = math.sqrt(radius0**2 - zlevel**2) if radius0 > zlevel else 0
    r1Level = math.sqrt(radius1**2 - zlevel**2) if radius1 > zlevel else 0

    # Update material grid and compute new temperature in single time step
    tstate = pbf.addNewPowderLayerThermal(tsetup, tstate, deltaT=depositionTimeStep if ilayer > 0 else timestep)
    time0, pauseAfter = tstate.time, (timeAfterDeposition if ilayer != 0 else 0)

    # Generate track for current level (no refinement towards previous layer track)
    laserTrack = generateLevelTrack(r0Level, r1Level, time0 + pauseAfter, zlevel, ilayer, pauseTime)

    # Update thermal problem
    tsetup.clearSources()
    tsetup.addSource(pbf.volumeSource(laserTrack, laserBeam, depthSigma=depthSigma))
    tsetup.setConvectionRadiationBC(emissivity=emissivity, convectionCoefficient=convectionCoefficient)
    tsetup.clearRefinements()
    tsetup.addRefinement(pbf.laserRefinement(laserTrack, 0.4 * laserD4Sigma, laserSpeed, trefinement, nseedpoints=5, cutoffDelay=0.1*units.ms))
    tsetup.addRefinement(pbf.adaptiveRefinement(trefinement, coarsen=1.25, threshold=35 if coarseMesh else 20))

    layerbase = filebase + f"/layer_{ilayer}/timestep"
    tsetup.postprocess = []
    tsetup.addPostprocessor(pbf.thermalVtuOutput(layerbase, interval=outputInterval))
    tsetup.addPostprocessor(info)
    info.ilayer = ilayer

    onDistance, onDuration = measureLaserOn(laserTrack)

    # Run simulation with given dwell time before and after
    duration = (laserTrack[-1].time - time0 if len(laserTrack) else 0.0) + timeBeforeDeposition

    print(f"    Simulated duration : {duration:.3f}s")
    print(f"    Laser on duration  : {onDuration:.3f}s")
    print(f"    Laser on distance  : {onDistance/1000:.3f}m")

    tstate = pbf.computeThermalProblem(tsetup, tstate, timestep, duration, ilayer=ilayer)
    
