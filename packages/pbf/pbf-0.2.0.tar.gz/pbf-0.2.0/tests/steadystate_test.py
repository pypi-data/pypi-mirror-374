import math
import unittest, pbf

units = pbf.units

class SteadyStateTest(unittest.TestCase):
    def test(self):
        IN625 = pbf.makeMaterial("IN625")

        laserD4Sigma = 85 * units.um
        laserSpeed = 960 * units.mm / units.s
        laserPower = 285 * units.W
        absorptivity = 0.54
    
        position = 1.3 * units.mm
        elementSize = 20 * units.um

        laserTrack = [
            pbf.LaserPosition(xyz=[position, 0.0 * units.mm, 0.0], time=-1.0, power=laserPower),
            pbf.LaserPosition(xyz=[position, 0.0 * units.mm, 0.0], time=0.0, power=laserPower)
        ]

        # Setup beam shape
        laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=absorptivity)
        heatSource = pbf.surfaceSource(laserTrack, laserBeam)

        # Setup problem
        domainMin = [0.0 * units.mm, -0.3 * units.mm, -0.24 * units.mm]
        domainMax = [1.5 * units.mm, 0.3 * units.mm, 0.0]

        filebase = "outputs/pbftests/steadystate"
        grid = pbf.createMesh(domainMin, domainMax, elementSize, 0.0)
    
        # setup process simulation
        setup = pbf.ProcessSimulation(grid=grid, material=IN625)

        tsetup = pbf.ThermalProblem(setup)
        tsetup.addDirichletBC(pbf.temperatureBC(1, setup.ambientTemperature))
        tsetup.addSource(heatSource)
        tsetup.addPostprocessor(pbf.meltPoolBoundsPrinter())
        #tsetup.addPostprocessor(pbf.thermalVtuOutput(filebase))

        tstate = pbf.makeThermalState(tsetup, grid)
        tstate = pbf.computeSteadyStateThermal(tsetup, tstate, [laserSpeed, 0, 0], qoffset=2)

        T = pbf.thermalEvaluator(tstate)
        
        self.assertAlmostEqual(T([1.0, 0.0, 0.0]), 2280.469517, delta=1e-3)
        self.assertAlmostEqual(T([0.1, 0.0, 0.0]), 1071.352689, delta=1e-3)
        self.assertAlmostEqual(T([0.7, 0.1, -0.1]), 456.71292194, delta=1e-3)
        self.assertAlmostEqual(pbf.norm(tstate.dofs), 97823.642543, delta=1e-3)
