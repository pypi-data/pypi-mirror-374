import math
import unittest, pbf

units = pbf.units

class AMB201802Test(unittest.TestCase):
    def test(self):
        IN625 = pbf.makeMaterial("IN625")

        ## Parameters from 2022 space-time paper 
        #density = 8440.0 * units.kg / ( units.m * units.m * units.m )
        #cp  = 4.05e-1 * units.J / ( units.g * units.C )
        #dcp = 2.47e-4 * units.J / ( units.g * units.C )
        #k = 9.50e-2 * units.W / ( units.cm * units.C )
        #dk = 1.50e-4 * units.W / ( units.cm * units.C )
        #IN625.density = pbf.temperatureFunction([0.0], [density], extrapolate="constant")
        #IN625.specificHeatCapacity = pbf.temperatureFunction([0.0, 1290.0], [cp, cp + 1290.0 * dcp], extrapolate="constant")
        #IN625.heatConductivity = pbf.temperatureFunction([0.0, 1290.0], [k, k + 1290.0 * dk], extrapolate="constant")
        #IN625.latentHeatOfFusion = 2.8e5 * units.J / units.kg

        # General parameters
        laserD4Sigma = 170 * units.um
        laserSpeed = 800 * units.mm / units.s
        laserPower = 179.2 * units.W

        x0 = 2.004 * units.cm
        x1 = 0.604 * units.cm
        
        dur = abs( x1 - x0 ) / laserSpeed
        
        # Set to dur to simulate full benchmark
        simulationTime = 10.0 / 256.0 * dur
        
        elementSize = 0.38 * laserD4Sigma
        refinement = 5
        timestep = 0.322 * laserD4Sigma / laserSpeed

        laserTrack = [pbf.LaserPosition(xyz=[x0, 0.0, 0.0], time=0.0, power=laserPower),
                      pbf.LaserPosition(xyz=[x1, 0.0, 0.0], time=dur, power=laserPower)]

        laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.34)
        heatSource = pbf.volumeSource(laserTrack, laserBeam, depthSigma=0.28 * laserD4Sigma / 4)

        domainMin = [0.0 * units.mm, -24.82 * units.mm / 2.0, -3.18 * units.mm]
        domainMax = [24.08 * units.mm, 24.82 * units.mm / 2.0, 0.0]

        filebase = "outputs/pbftests/amb2018-02"
        grid = pbf.createMesh(domainMin, domainMax, elementSize * 2**refinement, zfactor=0.5)

        # Setup problem
        setup = pbf.ProcessSimulation(grid=grid, material=IN625)

        tsetup = pbf.ThermalProblem(setup)
        tsetup.addSource(heatSource) 
        
        # Setup custom refinement
        refinementPoints = [
            pbf.LaserRefinementPoint(0.00*units.ms, 0.18*units.mm, 5.4, 0.5),
            pbf.LaserRefinementPoint(1.20*units.ms, 0.24*units.mm, 3.5, 0.5),
            pbf.LaserRefinementPoint(6.00*units.ms, 0.40*units.mm, 2.5, 0.8),
            pbf.LaserRefinementPoint(30.0*units.ms, 0.90*units.mm, 1.5, 1.0),
            pbf.LaserRefinementPoint(0.10*units.s,  1.10*units.mm, 1.0, 1.0)]
            
        refinement = lambda problem, state0, state1: pbf.laserTrackPointRefinement(laserTrack, 
            refinementPoints, state1.time, state0.basis.maxdegree() + 2)
        refinementFunction = pbf.laserTrackPointRefinementFunction(laserTrack, refinementPoints)     
        
        tsetup.degree = 3
        tsetup.addRefinement(refinement)
        tsetup.addPostprocessor(pbf.thermalVtuOutput(filebase, interval=20, functions=[(refinementFunction, "RefinementLevel")]))
        
        # Compute melt pool dimensions every other step
        meltPoolBoundsList = []
        def meltPoolBoundsAccumulator(mesh):
            points = mesh.points( )
            bounds = [[1e50, 1e50, 1e50], [-1e50, -1e50, -1e50]]
            for ipoint in range(int(len(points)/3)):
                for icoord in range(3):
                    bounds[0][icoord] = min(bounds[0][icoord], points[3*ipoint + icoord])
                    bounds[1][icoord] = max(bounds[1][icoord], points[3*ipoint + icoord])
            meltPoolBoundsList.append([max(u - l, 0.0) for l, u in zip(*bounds)])
            
        tsetup.addPostprocessor(pbf.meltPoolContourOutput(meltPoolBoundsAccumulator, interval=2))
        
        # Save number of elements and number of dofs every time step
        computedNElementsList, computedNDofList = [], []
        
        def meshDataAccumulator(thermalProblem, tstate):
            computedNElementsList.append(tstate.basis.nelements( ))
            computedNDofList.append(tstate.basis.ndof( ))
        
        tsetup.addPostprocessor(meshDataAccumulator)
        
        # Setup initial state and compute problem
        tstate0 = pbf.makeThermalState(tsetup, grid)
        tstate1 = pbf.computeThermalProblem(tsetup, tstate0, timestep, simulationTime)
        
        # Check whether results are consistent with previous versions
        expectedNElementsList = [432, 586, 600, 614, 614, 642, 656, 670, 656, 670, 670]
        expectedNDofList = [4186, 4964, 5047, 5130, 5130, 5296, 5379, 5462, 5379, 5462, 5462]
        
        assert(len(expectedNElementsList) == len(computedNElementsList))
        assert(len(expectedNDofList) == len(computedNDofList))
        
        for expectedNCells, computedNCells in zip(expectedNElementsList, computedNElementsList):
            assert(expectedNCells == computedNCells)
        for expectedNDof, computedNDof in zip(expectedNDofList, computedNDofList):
            assert(expectedNDof == computedNDof)
        
        #for lst in meltPoolBoundsList:
        #    print(f"[{lst[0]:.8f}, {lst[1]:.8f}, {lst[2]:.8f}],")
        
        expectedBoundsList = [
            [0.00000000, 0.00000000, 0.00000000],
            [0.13455653, 0.11612283, 0.02559100],
            [0.21289602, 0.12814098, 0.03172269],
            [0.27481131, 0.12782537, 0.03245700],
            [0.31846219, 0.12800211, 0.03242465],
            [0.32368278, 0.12832403, 0.03232437],
        ]
        
        assert(len(meltPoolBoundsList) == len(expectedBoundsList))
            
        for computedBounds, expectedBounds in zip(meltPoolBoundsList, expectedBoundsList):
            for computedAxis, expectedAxis in zip(computedBounds, expectedBounds):
                self.assertAlmostEqual(computedAxis, expectedAxis, delta=1e-5)
        
        temperature = pbf.thermalEvaluator(tstate1)
        
        self.assertAlmostEqual(temperature([19.53,  0.03, 0.0]), 2107.15374625, delta=3e-3)
        self.assertAlmostEqual(temperature([19.86, -0.07, 0.0]), 747.265450021, delta=1e-3)
        self.assertAlmostEqual(temperature([13.0,   5.0,  0.0]), 25.0000001707, delta=1e-5)
