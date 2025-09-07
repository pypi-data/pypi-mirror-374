import pbf
import math

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

def rectangleTrack(positions: list[tuple[float, 3]], power: float, speed: float, dwell0: float, dwell1: float):
    track = [pbf.LaserPosition(xyz=positions[0], time=0.0, power=power)]
    duration = lambda p0, p1: math.sqrt(sum([(x1 - x2)**2 for x1, x2 in zip(p0, p1)])) / speed
    
    for p in positions[1:5]:
        track.append(pbf.LaserPosition(xyz=p, time=track[-1].time + duration(track[-1].xyz, p), power=power))
        track.append(pbf.LaserPosition(xyz=p, time=track[-1].time + dwell0, power=0.0))

    for p0, p1 in zip(positions[5::2], positions[6::2]):
        track.append(pbf.LaserPosition(xyz=p0, time=track[-1].time + dwell1, power=0.0))
        track.append(pbf.LaserPosition(xyz=p1, time=track[-1].time + duration(p0, p1), power=power))

    return track

# Process parameters
laserPower = 200.0 * units.W
laserSpeed = 1200.0 * units.mm / units.s
laserD4Sigma = 90 * units.um
layerThickness = 40.0 * units.um
recoaterHeight = 1 * layerThickness

squareLengths = (0.8 * units.mm, 0.8 * units.mm)
trackCenter = (0 * units.mm, ) * 2 + (recoaterHeight, )

positions = rectanglePositions(trackCenter, *squareLengths, hatchDistance=80*units.um)
laserTrack = rectangleTrack(positions, laserPower, laserSpeed, 1 * units.ms, 1 * units.ms)

laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.36)
heatSource = pbf.volumeSource(laserTrack, laserBeam, depthSigma=laserD4Sigma / 4)

domainMin = [-2 * l for l in squareLengths] + [-1 * units.mm]
domainMax = [2 * l for l in squareLengths] + [recoaterHeight]

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
timestep = 0.3 * laserD4Sigma / laserSpeed

outputInterval = 4

# Setup problem
filebase = "outputs/hatched_square"
grid = pbf.createMesh(domainMin, domainMax, elementSize * 2**trefinement, layerThickness)

# Setup process simulation
setup = pbf.ProcessSimulation(grid=grid, material=material, layerThickness=layerThickness, ambientTemperature=25.0)

output = pbf.thermomechanicalVtuOutput(filebase, interval=outputInterval, l2project=True)

# Setup thermal problem
tsetup = pbf.ThermalProblem(setup, degree=1, theta=1)
#tsetup.addPostprocessor(pbf.thermalVtuOutput(filebase, interval=outputInterval, clipAbove=False))
tsetup.addPostprocessor(output)
tsetup.setConvectionRadiationBC(emissivity, convectionCoefficient)
tsetup.addSource(heatSource)
tsetup.addRefinement(pbf.laserRefinement(laserTrack, laserD4Sigma / 4, laserSpeed, trefinement))
tsetup.addDirichletBC(pbf.temperatureBC(4, temperature=setup.ambientTemperature))

# Setup mechanical problem
msetup = pbf.MechanicalProblem(setup, degree=1, quadratureOrderOffset=1)
msetup.addPostprocessor(output)

if mrefinementType >= 1:
    shiftedTrack = [pbf.LaserPosition(xyz=t.xyz[:-1] + [t.xyz[-1] - layerThickness], time=t.time, power=t.power) for t in laserTrack]
    def refinementStrategy(problem, state0, state1):
        refinementPoints = [
            pbf.LaserRefinementPoint(0.0 * units.ms, 0.20 * units.mm, mrefinement + 0.4, 1.0),
            pbf.LaserRefinementPoint(0.4 * units.ms, 0.34 * units.mm, mrefinement + 0.2, 1.0),
            pbf.LaserRefinementPoint(1.0 * units.ms, 0.50 * units.mm, mrefinement + 0.0, 1.0),
            pbf.LaserRefinementPoint(8.0 * units.ms, 0.70 * units.mm, mrefinement - 0.5, 1.0)]
        return pbf.laserTrackPointRefinement(shiftedTrack, refinementPoints, state1.time, state0.basis.maxdegree() + 2)
    msetup.addRefinement(refinementStrategy)
    
if mrefinementType == 1:
    def preventRefinement(setup, state0, state1):
        diff = [0 for _ in state0.mesh.refinementLevels()]
        return pbf.refineAdaptively(state0.mesh, diff, mrefinement)   
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
    msetup.addRefinement(makeRefinementBox(mrefinement - 0, 80 * units.um, 69 * units.um, 75 * units.um))
    msetup.addRefinement(makeRefinementBox(mrefinement - 1, 200 * units.um, 150 * units.um, 200 * units.um))

msetup.addDirichletBC(pbf.dirichletBC(4, 0, value=0.0))
msetup.addDirichletBC(pbf.dirichletBC(4, 1, value=0.0))
msetup.addDirichletBC(pbf.dirichletBC(4, 2, value=0.0))

# Create initial states and start analysis
tstate = pbf.makeThermalState(tsetup, grid, srefinement=srefinement, powderHeight=recoaterHeight)
mstate = pbf.makeMechanicalState(msetup, grid)

tstate, mstate = pbf.computeThermomechanicalProblem(tsetup, msetup, 
    tstate, mstate, timestep, laserTrack[-1].time, rtol=1e-8, maxiter=20)
    
for icoarsen in range(6):
    tstate, mstate = pbf.computeThermomechanicalProblem(tsetup, msetup, tstate, mstate, 
        timestep * 2**icoarsen, 1 * units.ms * 2**icoarsen, rtol=1e-8, maxiter=20)
