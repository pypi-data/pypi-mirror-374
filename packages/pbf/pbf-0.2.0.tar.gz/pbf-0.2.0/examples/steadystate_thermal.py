import pbf 
import numpy as np
import matplotlib.pyplot as plt

units = pbf.units

material = pbf.makeMaterial("SS316L")
material.regularization = 2

# Laser parameters
laserSpeed = 960 * units.mm / units.s
laserPower = 150 * units.W
absorptivity = 0.4

pixelsize = 4 * units.um
npixels = 50

# Create grid for beam shape evaluation
x = np.linspace(-pixelsize * npixels / 2, pixelsize * npixels / 2, npixels)
X, Y = np.meshgrid(x, x, indexing='ij')

# # Gaussian shape
# laserD4Sigma = 80 * units.um
# pixels = np.exp(-(X**2 + Y**2) / (2 * (laserD4Sigma / 4)**2))

# Ring shape
ringSigma, ringRadius = 15 * units.um, 60 * units.um
pixels = np.exp(-(np.sqrt(X**2 + Y**2) - ringRadius)**2 / (2 * ringSigma**2))

# Normalize intensity and create heat source
pixels = pixels / (np.sum(pixels) * pixelsize**2)
laserBeam = pbf.beamShapeFromPixelMatrix(absorptivity * pixels, pixelsize)

laserTrack = [
    pbf.LaserPosition(xyz=[0.0, 0.0, 0.0], time=-1.0, power=laserPower),
    pbf.LaserPosition(xyz=[0.0, 0.0, 0.0], time=1.0, power=laserPower)
]

heatSource = pbf.surfaceSource(laserTrack, laserBeam)
#heatSource = pbf.volumeSource(laserTrack, laserBeam, depthSigma=14*units.um)

plt.contourf(1e3 * X, 1e3 * Y, pixels)
plt.colorbar(label='Normalized intensity')
plt.show()

# Setup problem
domainMin = [-600 * units.um, -250 * units.um, -200 * units.um]
domainMax = [200 * units.um, 250 * units.um, 0.0]

elementSize = 14 * units.um

filebase = "outputs/steadystate"
grid = pbf.createMesh(domainMin, domainMax, elementSize, layerThickness=0.0, zfactor=0.8)

# Setup process simulation
setup = pbf.ProcessSimulation(grid=grid, material=material)

tsetup = pbf.ThermalProblem(setup)
tsetup.addDirichletBC(pbf.temperatureBC(1, setup.ambientTemperature))
tsetup.addSource(heatSource)
tsetup.addPostprocessor(pbf.meltPoolBoundsPrinter())
#tsetup.addPostprocessor(pbf.thermalVtuOutput(filebase))
#tsetup.addPostprocessor(pbf.meltPoolContourOutput(filebase))

# When the nonlinear iterations fail to converge we can try the following:
# - Further increase material.regularization to spread the phase change over a larger temperature range
# - Refine the mesh (smaller element size, reduce domain size, or introduce local refinement)
# - Increase qoffset, which specifies the number of quadrature points per quadrature cell. More
#   specifically, qoffset = 1 means polynomial degree of the shape functions (setup.degree) plus 1.
# - Increase treedepth, which defines quadrature grid refinement depth towards the melt pool boundary
tstate = pbf.makeThermalState(tsetup, grid)
tstate = pbf.computeSteadyStateThermal(tsetup, tstate, [laserSpeed, 0, 0], qoffset=1, treedepth=3)

# Plot result
evaluator = pbf.thermalEvaluator(tstate)

x = np.linspace(-600 * units.um, 120 * units.um, 180)
y = np.linspace(-120 * units.um, 120 * units.um, 60)
z = np.linspace(-240 * units.um, 0 * units.um, 60)
meltingRange = [material.solidTemperature, material.liquidTemperature]

X1, Y1 = np.meshgrid(x, y)
X2, Z2 = np.meshgrid(x, z)
T1 = np.reshape(evaluator(X1.ravel(), Y1.ravel(), np.full(X1.size, tstate.history.topSurface)), X1.shape)
T2 = np.reshape(evaluator(X2.ravel(), np.zeros(X2.size), Z2.ravel()), X2.shape)

T1[T1 > meltingRange[1]] = meltingRange[1] # Comment this out to see the 
T2[T2 > meltingRange[1]] = meltingRange[1] # temperature in the melt pool

colorIntervals = np.linspace(min(min(T1.flat), min(T2.flat)), max(max(T1.flat), max(T2.flat)), 20)
contourLines = [600, 800, 1000, meltingRange[0]]

fig, ax = plt.subplots(2, 1, figsize=(12, 6))
ax[0].contourf(X1, Y1, T1, cmap='turbo', levels=colorIntervals)
ax[0].contour(X1, Y1, T1, levels=contourLines, colors='black')
ax[0].set_aspect('equal')
ax[1].contourf(X2, Z2, T2, cmap='turbo', levels=colorIntervals)
ax[1].contour(X2, Z2, T2, levels=contourLines, colors='black')
ax[1].set_aspect('equal')
plt.show()
