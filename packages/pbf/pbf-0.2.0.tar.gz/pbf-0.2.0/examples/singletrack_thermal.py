import pbf

units = pbf.units

material = pbf.makeMaterial("SS316L")

laserD4Sigma = 85 * units.um
laserSpeed = 960 * units.mm / units.s
laserPower = 280 * units.W
layerThickness = 50.0 * units.um

# One layer of powder above base plate (set to zero for bare plate)
recoaterHeight = 1 * layerThickness

x0 = 0.0 * units.mm
x1 = 2.0 * units.mm

laserOn = (x1 - x0) / laserSpeed
duration = laserOn + 2 * units.ms

trefinement = 6
srefinement = trefinement + 1

elementSize = 2**trefinement * layerThickness / 4
timestep = 0.3 * laserD4Sigma / laserSpeed

laserTrack = [pbf.LaserPosition(xyz=[x0, 0.0, recoaterHeight], time=0.0, power=laserPower),
              pbf.LaserPosition(xyz=[x1, 0.0, recoaterHeight], time=laserOn, power=laserPower)]

laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.5)
heatSource = pbf.volumeSource(laserTrack, laserBeam, depthSigma=20 * units.um)

domainMin = [x0 - 1 * units.mm, -1 * units.mm, -0.5 * units.mm]
domainMax = [x1 + 1 * units.mm, +1 * units.mm, recoaterHeight]

filebase = "outputs/singletrack_thermal"
outputInterval = 8

grid = pbf.createMesh(domainMin, domainMax, elementSize, layerThickness)

# setup process simulation
setup = pbf.ProcessSimulation(grid=grid, material=material)

# setup thermal problem
tsetup = pbf.ThermalProblem(setup)
tsetup.addPostprocessor(pbf.thermalVtuOutput(filebase, interval=outputInterval))
tsetup.addPostprocessor(pbf.meltPoolBoundsPrinter())
tsetup.addRefinement(pbf.adaptiveRefinement(depth=trefinement, threshold=10))
tsetup.addRefinement(pbf.laserIntensityRefinement(depth=trefinement, threshold=800*units.W/units.mm**2, nseedpoints=6))
tsetup.addSource(heatSource)
#tsetup.addPostprocessor(pbf.materialVtuOutput(filebase))
#tsetup.addDirichletBC(pbf.temperatureBC(4, setup.ambientTemperature))

tstate0 = pbf.makeThermalState(tsetup, grid, srefinement=srefinement, powderHeight=recoaterHeight)
tstate1 = pbf.computeThermalProblem(tsetup, tstate0, timestep, duration)