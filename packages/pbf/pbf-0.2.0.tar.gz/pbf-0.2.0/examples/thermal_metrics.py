import pbf
import math
import numpy as np
import matplotlib.pyplot as plt

units = pbf.units

def rectanglePositions(center: list[float, 3], length: float, width: float, hatchDistance: float):
    laserPositions = []
    
    append = lambda x, y: laserPositions.append((x, y, center[2]))
    
    # Frame
    append(center[0] - length / 2, center[1] + width / 2)
    append(center[0] - length / 2, center[1] - width / 2) 
    append(center[0] + length / 2, center[1] - width / 2) 
    append(center[0] + length / 2, center[1] + width / 2) 
    append(center[0] - length / 2, center[1] + width / 2) 
    
    # Interior
    xmin, ymin = center[0] - length / 2, center[1] - width / 2 
    xmax, ymax = center[0] + length / 2, center[1] + width / 2
    
    ntracks = math.ceil((length + width) / (math.sqrt(2) * hatchDistance))
    increment = (length + width) / ntracks
    
    for itrack in range(1, ntracks):
        t = itrack * increment
        
        # Bottom left and top right points
        append(max(xmax - t, xmin), max(ymin - length + t, ymin))
        append(min(xmax + width - t, xmax), min(ymin + t, ymax))
        laserPositions[-2:] = laserPositions[-2:][::(-1 if itrack % 2 else 1)]
    
    return laserPositions

def rectangleTrack(positions: list[tuple[float, 3]], power: float, speed: float, pause0: float, pause1: float):
    track = [pbf.LaserPosition(xyz=positions[0], time=0.0, power=power)]
    duration = lambda p0, p1: math.sqrt(sum([(x1 - x2)**2 for x1, x2 in zip(p0, p1)])) / speed
    
    for p in positions[1:5]:
        track.append(pbf.LaserPosition(xyz=p, time=track[-1].time + duration(track[-1].xyz, p), power=power))
        track.append(pbf.LaserPosition(xyz=p, time=track[-1].time + pause0, power=0.0))

    for p0, p1 in zip(positions[5::2], positions[6::2]):
        track.append(pbf.LaserPosition(xyz=p0, time=track[-1].time + pause1, power=0.0))
        track.append(pbf.LaserPosition(xyz=p1, time=track[-1].time + duration(p0, p1), power=power))

    return track

# Process parameters
laserPower = 200.0 * units.W
laserSpeed = 1200.0 * units.mm / units.s
laserD4Sigma = 90 * units.um
layerThickness = 40.0 * units.um
powderHeight = 0 * layerThickness

squareLengths = (0.8 * units.mm, 0.8 * units.mm)
trackCenter = (0 * units.mm, ) * 2 + (powderHeight, )
pauseTime = 1 * units.ms

positions = rectanglePositions(trackCenter, *squareLengths, hatchDistance=80*units.um)
laserTrack = rectangleTrack(positions, laserPower, laserSpeed, pauseTime, pauseTime)

laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.36)
heatSource = pbf.volumeSource(laserTrack, laserBeam, depthSigma=laserD4Sigma / 4)

domainMin = [-1.0 * l for l in squareLengths] + [-5 * units.mm]
domainMax = [1.0 * l for l in squareLengths] + [powderHeight]

duration = laserTrack[-1].time + 2 * units.ms

# Material
material = pbf.makeMaterial("SS316L")
emissivity = 0.1
convectionCoefficient = 10 * units.W / units.m ** 2 / units.C

# Discretization
trefinement = 4
mrefinement = 3
srefinement = 5

mrefinementType = 1 # 0 --> Static box, 1 -> refine, no coarsening, 2 -> refine and coarsen

elementSize = layerThickness / 4
timestep = 0.25 * laserD4Sigma / laserSpeed

outputInterval = 4

# Setup problem
filebase = "outputs/hatched_square"
grid = pbf.createMesh(domainMin, domainMax, elementSize * 2**trefinement, layerThickness)

# Setup process simulation
setup = pbf.ProcessSimulation(grid=grid, material=material, layerThickness=layerThickness, ambientTemperature=25.0)

# Custom postprocessor
xsamples = np.linspace(-0.6 * squareLengths[0], 0.6 * squareLengths[0], 200)
ysamples = np.linspace(-0.6 * squareLengths[1], 0.6 * squareLengths[1], 200)
X, Y = np.meshgrid(xsamples, ysamples, indexing='ij')
Z = np.zeros(X.shape)
def process(setup, state):
    T = np.reshape(pbf.thermalEvaluator(state)(X.ravel(), Y.ravel(), Z.ravel()), X.shape)
    dt, Ts = state.time - process.previousTime, material.solidTemperature
    process.tmax = np.maximum(T, process.tmax)
    process.mtam[1] += dt
    process.mtam[1][T < Ts] = 0.0
    process.mtam[0] = np.maximum(process.mtam[0], process.mtam[1])
    process.ctam[T > Ts] += dt
    if dt > 0:
        coolingMask = process.previousTemp < Ts
        process.cmax[coolingMask] = np.maximum(-(T - process.previousTemp) / dt, process.cmax)[coolingMask]
    process.previousTime = state.time
    process.previousTemp = T

process.tmax = np.zeros(X.shape)
process.cmax = np.zeros(X.shape)
process.ctam = np.zeros(X.shape)
process.mtam = [np.zeros(X.shape), np.zeros(X.shape)]
process.previousTime = 0.0
process.previousTemp = np.full(X.shape, setup.ambientTemperature)

# Setup and solve thermal problem
tsetup = pbf.ThermalProblem(setup, degree=1, theta=1)
tsetup.addPostprocessor(pbf.thermalVtuOutput(filebase, interval=outputInterval))
tsetup.addPostprocessor(process)
tsetup.setConvectionRadiationBC(emissivity, convectionCoefficient)
tsetup.addSource(heatSource)
tsetup.addRefinement(pbf.laserRefinement(laserTrack, laserD4Sigma / 4, laserSpeed, trefinement, cutoffDelay=0.1 * units.ms))
tsetup.addRefinement(pbf.adaptiveRefinement(depth=trefinement))

tstate = pbf.makeThermalState(tsetup, grid, srefinement=srefinement, powderHeight=powderHeight)
tstate = pbf.computeThermalProblem(tsetup, tstate, timestep, duration)

# Plot results
fig, ax = plt.subplots(2, 2, figsize=(12, 9))
f0 = ax[0, 0].contourf(X, Y, process.tmax, levels=20, cmap='turbo')
f1 = ax[0, 1].contourf(X, Y, process.cmax, levels=20, cmap='turbo')
f2 = ax[1, 0].contourf(X, Y, 1000 * process.mtam[0], levels=20, cmap='turbo')
f3 = ax[1, 1].contourf(X, Y, 1000 * process.ctam, levels=20, cmap='turbo')
segments = [s for s in zip(laserTrack[:-1], laserTrack[1:]) if s[1].power]
x = np.transpose([[p.xyz[0] for p in segment] for segment in segments])
y = np.transpose([[p.xyz[1] for p in segment] for segment in segments])
for axis in ax.ravel():
    axis.plot(x, y, '--', color='black')
plt.colorbar(f0, label='Maximum temperature [°C]')
plt.colorbar(f1, label='Maximum cooling rate [°C/s]')
plt.colorbar(f2, label='MTAM [ms]')
plt.colorbar(f3, label='CTAM [ms]')
plt.tight_layout()
plt.show()

