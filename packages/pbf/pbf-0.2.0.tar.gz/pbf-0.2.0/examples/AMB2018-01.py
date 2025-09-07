import os
import psutil

hyperthreading = False

os.environ["OMP_NUM_THREADS"] = str(psutil.cpu_count(logical=hyperthreading))

import math
import time
import shutil
import pbf

print(f"OMP_NUM_THREADS={os.environ["OMP_NUM_THREADS"]}")

units = pbf.units

def createAMB201801Path(ilayer: int, layerThickness: float, timeOffset: float = 0.0) -> list[pbf.LaserPosition]:

    z = (ilayer + 1) * layerThickness
    hatchSpacing = 100.0 * units.um

    contourPower = 100.0 * units.W
    infillPower = 195.0 * units.W

    contourSpeed = 900.0 * units.mm / units.s
    infillSpeed = 800.0 * units.mm / units.s

    track = []

    def addPart(partX: float, partY: float):
        def moveLaser(x: float, y: float, dt: float = 0.0, power: float = 0.0):
            xyz = (x * units.mm + partX, y * units.mm + partY, z)
            time = timeOffset if not len(track) else track[-1].time + dt
            track.append(pbf.LaserPosition(xyz=xyz, time=time, power=power))

        def moveSpeed(x: float, y: float, speed: float, power: float):
            xy = (x * units.mm + partX, y * units.mm + partY)
            dist = math.sqrt((track[-1].xyz[0] - xy[0])**2 + (track[-1].xyz[1] - xy[1])**2)
            moveLaser(x, y, dist / speed, power)

        # Create x-intervals depending on z-level
        intervals = []
        intervalLaserOffRight = []
        intervalLaserOffLeft = []

        if z < 7.0 * units.mm - 1e-2 * units.um:
            o = min(7.0 - z, 2.0)

            intervals = [[0.0, 5.0],
                [ 5.0 + o,  7.5], [ 7.5 + o, 12.0], [12.0 + o, 19.0],
                [19.0 + o, 21.5], [21.5 + o, 26.0], [26.0 + o, 33.0],
                [33.0 + o, 35.5], [35.5 + o, 40.0], [40.0 + o, 47.0],
                [47.0 + o, 49.5], [49.5 + o, 54.0], [54.0 + o, 72.5]]

            intervalLaserOffRight = [6.7 * units.ms, 7.9 * units.ms, 2.3 * units.ms,
                4.8 * units.ms, 4.8 * units.ms, 4.8 * units.ms, 4.8 * units.ms, 4.8 * units.ms,
                4.8 * units.ms, 4.8 * units.ms, 4.8 * units.ms, 4.8 * units.ms, 4.8 * units.ms]

            intervalLaserOffLeft = [21.2 * units.ms, 22.6 * units.ms, 22.6 * units.ms,
                22.6 * units.ms, 22.6 * units.ms, 22.6 * units.ms, 22.6 * units.ms, 22.6 * units.ms,
                22.6 * units.ms, 22.6 * units.ms,  7.9 * units.ms,  4.8 * units.ms,  2.3 * units.ms]

        elif z <= 12.0 * units.mm:
            intervals = [[0.0, 72.5]]
            intervalLaserOffRight = [6.7 * units.ms]
            intervalLaserOffLeft = [21.2 * units.ms]

        elif z <= 12.5 * units.mm + 0.01 * units.um:
            for i in range(11):
                intervals.push_back((7.0 * j, 7.0 * j + 1.0))

            intervalLaserOffRight = [6.7 * units.ms] * 11
            intervalLaserOffLeft = [6.7 * units.ms] * 11

        # Contour
        for x0, x1 in intervals:
            moveLaser(x0, 0.0, 10.0 * units.ms)
            moveSpeed(x1, 0.0, contourSpeed, contourPower)

            if(x1 > 72.0):
                moveSpeed(75.0, 2.5, contourSpeed, contourPower)

            moveSpeed(x1, 5.0, contourSpeed, contourPower)
            moveSpeed(x0, 5.0, contourSpeed, contourPower)
            moveSpeed(x0, 0.0, contourSpeed, contourPower)

        trimHatchLines = 0 * hatchSpacing

        # Odd infill
        if (ilayer + 1) % 2:
            for i in range(50):
                for j2 in range(len(intervals)):
                    j = j2 if i % 2 else len(intervals) - j2 - 1
                    x0, x1 = intervals[j]

                    if x1 > 72.0:
                        x1 += 2.5 - abs(2.5 - i * hatchSpacing) - 0.3 * hatchSpacing

                    if (x1 - x0) > 2.2 * hatchSpacing:
                        x0 += trimHatchLines
                        x1 -= trimHatchLines

                        if i % 2 == 0:
                            x0, x1 = x1, x0

                        laserOff = intervalLaserOffRight[j] if i % 2 else intervalLaserOffLeft[j2]

                        moveLaser(x0, 5.0 - i * hatchSpacing, laserOff)
                        moveSpeed(x1, 5.0 - i * hatchSpacing, infillSpeed, infillPower)

        # Even infill
        else:
            for x0, x1 in intervals:
                x1 = 75.0 * units.mm - 0.4 * hatchSpacing if x1 > 72.0 * units.mm else x1

                laserOff = 8.0 * units.ms
                nspaces = math.floor((x1 - x0) / hatchSpacing)
                space = (x1 - x0) / nspaces

                for i in range(1, nspaces):
                    wedge = x0 + i * space > 72.5 * units.mm

                    offset = 2.5 * units.mm - abs(75.0 * units.mm - x0 - i * space) + \
                        1.3 * trimHatchLines if wedge else trimHatchLines

                    if 5.0 - 2.0 * offset > 0.1 * hatchSpacing:
                        laserOff = 21.3 * units.ms if wedge else 6.7 * units.ms

                        moveLaser(x0 + i * space, offset if i % 2 else 5.0 - offset, laserOff)
                        moveSpeed(x0 + i * space, 5.0 - offset if i % 2 else offset, infillSpeed, infillPower)

    addPart(21.74 * units.mm, 17.03 * units.mm)
    #addPart(21.24 * units.mm, 37.03 * units.mm)
    #addPart(20.74 * units.mm, 57.03 * units.mm)
    #addPart(20.34 * units.mm, 77.03 * units.mm)

    return track

def measureLaserOn(track: list[pbf.LaserPosition]) -> (float, float):
    distance, duration = 0.0, 0.0
    for pos0, pos1 in zip(track[:-1], track[1:]):
        if pos1.power > 0.0:
            diff = [(x1 - x0)**2 for x0, x1 in zip(pos0.xyz, pos1.xyz)]
            distance += math.sqrt(diff[0] + diff[1] + diff[2])
            duration += pos1.time - pos0.time
    return distance, duration


#def laserRefinement(laserTrack, laserSigma, laserSpeed, depth):
#    def refinement(problem, state0, state1):
#        refinementPoints = [# delay, sigma (refinement width), depth (maximum refinement depth), zfactor
#            pbf.LaserRefinementPoint(0.0  * units.ms, 4 * laserSigma + 65 * units.um, depth + 0.49, 0.6),  # 5.49
#            pbf.LaserRefinementPoint(0.3  * units.ms, 4 * laserSigma + 120 * units.um, depth + 0.49, 0.6), # 5.49
#            pbf.LaserRefinementPoint(0.31 * units.ms, 4 * laserSigma + 150 * units.um, depth - 0.51, 0.8), # 4.49
#            pbf.LaserRefinementPoint(2.50 * units.ms, 4 * laserSigma + 200 * units.um, depth - 0.60, 1.0), # 4.4
#            pbf.LaserRefinementPoint(2.51 * units.ms, 4 * laserSigma + 200 * units.um, depth - 1.51, 1.0), # 3.49
#            pbf.LaserRefinementPoint(8.00 * units.ms, 4 * laserSigma + 400 * units.um, depth - 1.60, 1.0), # 3.4
#            pbf.LaserRefinementPoint(8.04 * units.ms, 4 * laserSigma + 500 * units.um, depth - 2.51, 1.0), # 2.49
#            pbf.LaserRefinementPoint(64.0 * units.ms, 4 * laserSigma + 600 * units.um, depth - 2.60, 1.0), # 2.4
#            pbf.LaserRefinementPoint(64.1 * units.ms, 4 * laserSigma + 700 * units.um, depth - 3.51, 1.0), # 1.49
#            pbf.LaserRefinementPoint(0.50 * units.s, 4 * laserSigma + 1000 * units.um, depth - 3.60, 1.0), # 1.4
#            pbf.LaserRefinementPoint(0.51 * units.s, 4 * laserSigma + 1000 * units.um, depth - 4.51, 1.0)
#            ] # 0.49
#        return pbf.laserTrackPointRefinement(laserTrack, refinementPoints, state1.time, state0.basis.maxdegree() + 2)
#    refinement.laserTrack = laserTrack
#    refinement.laserSigma = laserSigma
#    refinement.laserSpeed = laserSpeed
#    refinement.depth = depth
#    return refinement


## ======= Process parameters ========
material = pbf.makeMaterial("IN625")

laserFWHM = 50 * units.um
laserD4Sigma = pbf.convertBeamDiameter(laserFWHM, "FWHM", "D4Sigma")
laserSpeed = 800.0 * units.mm / units.s
laserPower = 280.0 * units.W
depthSigma = 0.3 * laserD4Sigma / 4

laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.35)

layerThickness = 20 * units.um

timeBeforeDeposition = 20 * units.ms # Time before new powder layer is added
depositionTimeStep = 10 * units.s    # Length of layer extension (single) time step
timeAfterDeposition = 5 * units.ms   # Time after new powder layer was added

nlayers = 200
basePlateHeight = 8 * units.mm # 12.7 * units.mm

#domainMin = [0.0 * units.mm, 0.0 * units.mm, -basePlateHeight]
#domainMax = [100.0 * units.mm, 100.0 * units.mm, layerThickness * nlayers]

domainMin = [20.5 * units.mm, 16 * units.mm, -basePlateHeight]
domainMax = [97.0 * units.mm, 23 * units.mm, layerThickness * nlayers]

emissivity = 0.1
convectionCoefficient = 1e-5 * units.W / units.mm**2 / units.C

## ====== Simulation parameters ======

trefinement = 6 # Temperature grid refinement
srefinement = 6 # Material grid refinement

elementsize = layerThickness
timestep = 1/2 * laserD4Sigma / laserSpeed

filebase = f"outputs/AMB2018-01"
outputInterval = 128

grid = pbf.createMesh(domainMin, domainMax, elementsize * 2**trefinement, layerThickness)

## =========== Simulation ============
processSimulation = pbf.ProcessSimulation(grid=grid, material=material,
    layerThickness=layerThickness, ambientTemperature=25.0)

tsetup = pbf.ThermalProblem(processSimulation, degree=1)
tsetup.setConvectionRadiationBC(emissivity=emissivity, convectionCoefficient=convectionCoefficient)

tstate = pbf.makeThermalState(tsetup, grid, srefinement=srefinement)
info = pbf.stateInfoOutput(filebase + "/stateinfo.csv")
shutil.copy(__file__, filebase + "/" + os.path.basename(__file__))

for ilayer in range(nlayers):
    print(f"Layer {ilayer + 1} / {nlayers}", flush=True)
    zlevel = (ilayer + 1) * layerThickness

    # Update material grid and compute new temperature in single time step
    tstate = pbf.addNewPowderLayerThermal(tsetup, tstate, deltaT=depositionTimeStep if ilayer > 0 else timestep)
    time0, pauseAfter = tstate.time, (timeAfterDeposition if ilayer != 0 else 0)

    # Generate track for current level (no refinement towards previous layer track)
    laserTrack = createAMB201801Path(ilayer, layerThickness=layerThickness, timeOffset=time0 + pauseAfter)

    # Update thermal problem
    tsetup.clearSources()
    tsetup.addSource(pbf.volumeSource(laserTrack, laserBeam, depthSigma=depthSigma))
    tsetup.clearRefinements()
    tsetup.addRefinement(pbf.laserRefinement(laserTrack, 0.4 * laserD4Sigma, laserSpeed, trefinement, cutoffDelay=0.1*units.ms))
    tsetup.addRefinement(pbf.adaptiveRefinement(trefinement, coarsen=1.25, threshold=20))

    layerbase = filebase + f"/layer_{ilayer}/timestep"
    tsetup.postprocess = []
    tsetup.addPostprocessor(pbf.thermalVtuOutput(layerbase, interval=outputInterval))
    #tsetup.addPostprocessor(pbf.materialVtuOutput(layerbase, interval=outputInterval))
    tsetup.addPostprocessor(info)
    info.ilayer = ilayer

    onDistance, onDuration = measureLaserOn(laserTrack)

    # Run simulation with given dwell time before and after
    duration = (laserTrack[-1].time - time0 if len(laserTrack) else 0.0) + timeBeforeDeposition

    print(f"    Simulated duration : {duration:.3f}s")
    print(f"    Laser on duration  : {onDuration:.3f}s")
    print(f"    Laser on distance  : {onDistance/1000:.3f}m")

    tstate = pbf.computeThermalProblem(tsetup, tstate, timestep, duration, ilayer=ilayer)
    
