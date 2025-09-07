import pbf

IN625 = pbf.makeMaterial("IN625")
# IN625 = pbf.readMaterialFile("materials/IN625.json")

units = pbf.units

laserD4Sigma = 170 * units.um
laserSpeed = 800.0 * units.mm / units.s
laserPower = 280.0 * units.W
domainHeight = 0.5 * units.mm

x0 = 0.25 * units.mm
x1 = 0.75 * units.mm
dur = (x1 - x0) / laserSpeed

elementSize = 0.12 * laserD4Sigma
timestep = 0.2 * laserD4Sigma / laserSpeed
nrefinements = 2

laserTrack1 = [pbf.LaserPosition(xyz=[0.5 * units.mm, x0, domainHeight], time=0.0, power=laserPower),
               pbf.LaserPosition(xyz=[0.5 * units.mm, x1, domainHeight], time=dur, power=laserPower)]

laserTrack2 = [pbf.LaserPosition(xyz=[x0, 0.5 * units.mm, domainHeight], time=0.0, power=laserPower),
               pbf.LaserPosition(xyz=[x1, 0.5 * units.mm, domainHeight], time=dur, power=laserPower)]

laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.32)
heatSource1 = pbf.volumeSource(laserTrack1, laserBeam, depthSigma=0.045)
# heatSource2 = pbf.volumeSource(laserTrack2, laserBeam, depthSigma=0.045)

domainMin = [0.0 * units.mm, 0 * units.mm, -0.3 * units.mm]
domainMax = [1.0 * units.mm, 1 * units.mm, domainHeight]

filebase = "outputs/stldomain"
grid = pbf.createMesh(domainMin, domainMax, elementSize * 2 ** nrefinements)

# setup process simulation
setup = pbf.ProcessSimulation(grid, material=IN625)

tsetup = pbf.ThermalProblem(setup)
tsetup.addPostprocessor(pbf.thermalVtuOutput(filebase))
tsetup.addPostprocessor(pbf.materialVtuOutput(filebase))
# tsetup.addDirichletBC(pbf.temperatureBC(4, tsetup.ambientTemperature))
tsetup.addSource(heatSource1)
# tsetup.addSource(heatSource2)

refinement1 = pbf.laserRefinement(laserTrack1, laserD4Sigma / 4, laserSpeed, nrefinements)
# refinement2 = pbf.laserRefinement(laserTrack2, laserD4Sigma/4, laserSpeed, nrefinements)

tsetup.addRefinement(refinement1)
# tsetup.addRefinement(refinement2)

# Initialize material
triangulation = pbf.readStl("stldomain.stl")

scale = pbf.scaling([0.05 * units.mm, 0.05 * units.mm, 0.05 * units.mm])
move = pbf.translation([0.5 * units.mm, 0.5 * units.mm, 0.25 * units.mm])

domain = pbf.rayIntersectionDomain(triangulation)
domain = pbf.implicitTransformation(domain, pbf.concatenate([scale, move]))

# Setup initial state and run simulation
tstate0 = pbf.makeThermalState(tsetup, grid, part=domain, srefinement=3, powderHeight=domainHeight)

pbf.computeThermalProblem(tsetup, tstate0, timestep, dur)  # 3 * dur)
