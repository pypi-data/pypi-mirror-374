import pbf

units = pbf.units

## ======= Process parameters ======== 
material = pbf.makeMaterial("SS316L")

laserD4Sigma = 100 * units.um
laserSpeed = 800.0 * units.mm / units.s
laserPower = 280.0 * units.W

laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.32)

layerThickness = 50 * units.um 

# These values are not realistic of course
timeBeforeDeposition = 1.1 * units.ms # Time before new powder layer is added
depositionTimeStep = 0.2 * units.ms   # Length of layer extension (single) time step
timeAfterDeposition = 1.1 * units.ms  # Time after new powder layer was added

nlayers = 3
basePlateHeight = 3 * units.mm

domainMin = [0 * units.cm, 0 * units.cm, -basePlateHeight]
domainMax = [1 * units.cm, 1 * units.cm, layerThickness * nlayers]

convectionCoefficient = 1e-5 * units.W / units.mm ** 2 / units.C

## ====== Simulation parameters ====== 

# number of temperature grid and material grid refinement levels
trefinement = 5
srefinement = 6

elementsize = layerThickness / 4
timestep = 0.25 * laserD4Sigma / laserSpeed

# Output file path and time steps inverval to write output files
filebase = "outputs/multilayer"
outputInterval = 8

grid = pbf.createMesh(domainMin, domainMax, elementsize * 2**trefinement, layerThickness)

## ====== Initialize simulation ====== 
processSimulation = pbf.ProcessSimulation(grid=grid, material=material, 
    layerThickness=layerThickness, ambientTemperature=50.0)

tsetup = pbf.ThermalProblem(processSimulation, degree=1)
tsetup.addPostprocessor(pbf.thermalVtuOutput(filebase, interval=outputInterval))
tsetup.setConvectionRadiationBC(emissivity=0.1, convectionCoefficient=convectionCoefficient)
# tsetup.addDirichletBC(pbf.temperatureBC(4, processSimulation.ambientTemperature))

## =========== Simulation ============ 
tstate = pbf.makeThermalState(tsetup, grid, srefinement=srefinement, powderHeight=0.0)

laserTrack = []

for ilayer in range(nlayers):
    print(f"Layer {ilayer + 1} / {nlayers}", flush=True)

    # Update material grid and compute new temperature in single time step
    tstate = pbf.addNewPowderLayerThermal(tsetup, tstate, deltaT=depositionTimeStep)
    
    x0, x1, y, zlevel = 4 * units.mm, 6 * units.mm, 5 * units.mm, (ilayer + 1) * layerThickness
    time0, before, laserTime = tstate.time, (timeBeforeDeposition if ilayer else 0), (x1 - x0) / laserSpeed
    
    # Move to start position without power, followed by a laser stroke 
    laserTrack.append(pbf.LaserPosition(xyz=[x0, y, zlevel], power=0, time=time0 + before))
    laserTrack.append(pbf.LaserPosition(xyz=[x1, y, zlevel], power=laserPower, time=time0 + before + laserTime))

    # Update thermal problem
    refinement = pbf.laserRefinement(laserTrack, laserD4Sigma / 4, laserSpeed, trefinement)

    tsetup.clearSources()
    tsetup.addSource(pbf.volumeSource(laserTrack, laserBeam, depthSigma=10 * units.um))
    tsetup.clearRefinements()
    tsetup.addRefinement(refinement)

    # Run simulation with given dwell time before and after
    duration = before + laserTime + timeAfterDeposition
    
    tstate = pbf.computeThermalProblem(tsetup, tstate, timestep, duration, ilayer=ilayer)
