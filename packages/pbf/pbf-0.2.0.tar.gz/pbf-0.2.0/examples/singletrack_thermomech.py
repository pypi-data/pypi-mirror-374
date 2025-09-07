import pbf

units = pbf.units

steel = pbf.makeMaterial("SS316L")

# D86 approximately 80 um
emissivity = 0.1
convectionCoefficient = 10 * units.W / units.m ** 2 / units.C

# process parameters
laserD4Sigma = 90 * units.um
laserSpeed = 1200.0 * units.mm / units.s
laserPower = 200.0 * units.W
layerThickness = 40.0 * units.um

# One layer of powder above base plate (set to zero for bare plate)
recoaterHeight = 1 * layerThickness

x0 = 0.2 * units.mm
x1 = 0.6 * units.mm

printingTime = (x1 - x0) / laserSpeed

trefDepth = 3
mrefDepth = 2
matDepth = 4

mrefinementType = 2 # 0 --> Static box, 1 -> refine, no coarsening, 2 -> refine and coarsen

elementSize = layerThickness / 8
timestep = 0.2 * laserD4Sigma / laserSpeed

interval = 1

# Setup problem
laserTrack = [pbf.LaserPosition(xyz=[x0, 0.0, recoaterHeight], time=1.0 * units.s, power=laserPower),
              pbf.LaserPosition(xyz=[x1, 0.0, recoaterHeight], time=1.0 * units.s + printingTime, power=laserPower)]

laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.32)
heatSource = pbf.volumeSource(laserTrack, laserBeam, depthSigma=laserD4Sigma / 4)

domainMin = [x0 - 0.4 * units.mm, -0.4 * units.mm, -0.3 * units.mm]
domainMax = [x1 + 0.4 * units.mm, +0.4 * units.mm, recoaterHeight]

filebase = "outputs/singletrack_thermomechanical"
grid = pbf.createMesh(domainMin, domainMax, elementSize * 2**trefDepth, layerThickness)

trefinement = pbf.laserRefinement(laserTrack, laserD4Sigma / 4, laserSpeed, trefDepth)

# Setup process simulation
setup = pbf.ProcessSimulation(grid=grid, material=steel, layerThickness=layerThickness, ambientTemperature=25.0)

output = pbf.thermomechanicalVtuOutput(filebase, interval=interval)

# Setup thermal problem
tsetup = pbf.ThermalProblem(setup, degree=1, theta=1)
tsetup.addPostprocessor(pbf.meltPoolBoundsPrinter())
tsetup.addPostprocessor(output)
tsetup.setConvectionRadiationBC(emissivity, convectionCoefficient)
tsetup.addSource(heatSource)
tsetup.addRefinement(trefinement)
tsetup.addDirichletBC(pbf.temperatureBC(4, temperature=setup.ambientTemperature))
tsetup.setConvectionRadiationBC(1e-1, 1e-5)

# Setup mechanical problem
msetup = pbf.MechanicalProblem(setup, degree=1, quadratureOrderOffset=1)
msetup.addPostprocessor(output)

if mrefinementType >= 1:
    shiftedTrack = [pbf.LaserPosition(xyz=t.xyz[:-1] + [t.xyz[-1] - layerThickness], time=t.time, power=t.power) for t in laserTrack]
    def refinementStrategy(problem, state0, state1):
        refinementPoints = [# delay, sigma (refinement width), depth (maximum refinement depth), zfactor
            pbf.LaserRefinementPoint(0.00 * units.ms, laserD4Sigma + 0.01 * units.mm, mrefDepth + 0.4, 1.0),
            pbf.LaserRefinementPoint(0.60 * units.ms, laserD4Sigma + 0.07 * units.mm, mrefDepth - 0.5, 1.0),
            pbf.LaserRefinementPoint(6.00 * units.ms, laserD4Sigma + 0.40 * units.mm, mrefDepth - 1.5, 1.0),
            pbf.LaserRefinementPoint(30.0 * units.ms, laserD4Sigma + 0.90 * units.mm, mrefDepth - 2.5, 1.0),
            pbf.LaserRefinementPoint(0.10 * units.s,  laserD4Sigma + 1.10 * units.mm, mrefDepth - 3.0, 1.0)]
        return pbf.laserTrackPointRefinement(shiftedTrack, refinementPoints, state1.time, state0.basis.maxdegree() + 2)
    msetup.addRefinement(refinementStrategy)
    
if mrefinementType == 1:
    def preventRefinement(setup, state0, state1):
        diff = [0 for _ in state0.mesh.refinementLevels()]
        return pbf.refineAdaptively(state0.mesh, diff, mrefDepth)   
    msetup.addRefinement(preventRefinement)
    
if mrefinementType == 0:
    def makeRefinementBox(depth, dx, dy, dz):
        def refinement(msetup, mstate0, mstate1):
            depth, dx, dy, dz = refinement.parameters
            refinementMin = [x0 - dx, -dy, recoaterHeight - dz]
            refinementMax = [x1 + dx, +dy, recoaterHeight]
            return pbf.refineInsideDomain(pbf.implicitCube(refinementMin, refinementMax), depth)
        refinement.parameters = [depth, dx, dy, dz]
        return refinement
    msetup.addRefinement(makeRefinementBox(mrefDepth - 0, 80 * units.um, 69 * units.um, 75 * units.um))
    msetup.addRefinement(makeRefinementBox(mrefDepth - 1, 200 * units.um, 150 * units.um, 200 * units.um))

msetup.addDirichletBC(pbf.dirichletBC(4, 0, value=0.0))
msetup.addDirichletBC(pbf.dirichletBC(4, 1, value=0.0))
msetup.addDirichletBC(pbf.dirichletBC(4, 2, value=0.0))

tstate0 = pbf.makeThermalState(tsetup, grid, srefinement=matDepth)
mstate0 = pbf.makeMechanicalState(msetup, grid)

for pp in tsetup.postprocess:
    pp(tsetup, tstate0)
for pp in msetup.postprocess:
    pp(msetup, mstate0)


# deposit a layer of powder material
tstate0 = pbf.addNewPowderLayerThermal(tsetup, tstate0, deltaT=1.0 * units.s)
mstate0 = pbf.addNewPowderLayerMechanical(msetup, mstate0, deltaT=1.0 * units.s)

for pp in tsetup.postprocess:
    pp(tsetup, tstate0)
for pp in msetup.postprocess:
    pp(msetup, mstate0)

# solve single-track thermomechanical problem with a layer of powder
dur = 2 * printingTime
for icoarsen in range(4):
    tstate0, mstate0 = pbf.computeThermomechanicalProblem(tsetup, msetup, tstate0, mstate0, timestep, dur, rtol=1e-8, maxiter=20)
    timestep, dur = 2 * timestep, 2 * dur
