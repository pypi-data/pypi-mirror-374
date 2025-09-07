import unittest
import pbf

units = pbf.units


class MultilayerThermalTest(unittest.TestCase):
    def test(self):
        material = pbf.makeMaterial("SS316L")

        # process parameters
        laserD4Sigma = 0.100 * units.mm
        laserSpeed = 800.0 * units.mm / units.s
        laserPower = 280.0 * units.W
        layerThickness = 50 * units.um
        depositionTime = 0.001 * units.s
        nlayers = 3
        nLayerTracks = 1

        # domain
        basePlateHeight = 0.15 * units.mm

        domainMin = [0 * units.mm, -0.15 * units.mm, -basePlateHeight]
        domainMax = [1 * units.mm, +0.15 * units.mm, layerThickness * nlayers]

        # scan path
        eps = 2.17e-4 * units.mm
        x0 = 0.01 * units.mm + eps
        x1 = 0.98 * units.mm + eps
        y = 0.0 * units.mm - eps
        
        totalTime = (x1 - x0) * nLayerTracks * nlayers / laserSpeed + depositionTime * nlayers
        layerTime = (x1 - x0) * nLayerTracks / laserSpeed
        singleTrackTime = (x1 - x0) / laserSpeed

        # discretization
        trefinement = 2
        srefinement = 3
        
        elementSize = layerThickness
        grid = pbf.createMesh(domainMin, domainMax, elementSize, layerThickness * nlayers)
        timestep = 0.5 * laserD4Sigma / laserSpeed  # 0.2 * laserD4Sigma / laserSpeed

        # laser beam shape
        laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.32)

        # setup process simulation
        setup = pbf.ProcessSimulation(grid=grid, material=material, layerThickness=50 * units.um, ambientTemperature=50.0)
        setup.setMaterials(air=pbf.makeAir())

        # thermal problem definition
        tsetup = pbf.ThermalProblem(setup, degree=1)
        tsetup.addDirichletBC(pbf.temperatureBC(4, setup.ambientTemperature))
        
        # Save number of elements and number of dofs every time step
        computedNElementsList, computedMaterialNCellsList, computedNDofList = [], [], []

        def meshDataAccumulator(thermalProblem, tstate):
            computedNElementsList.append(tstate.basis.nelements())
            computedNDofList.append(tstate.basis.ndof())
            computedMaterialNCellsList.append(tstate.history.grid().ncells())

        tsetup.addPostprocessor(meshDataAccumulator)
        #tsetup.addPostprocessor(pbf.thermalVtuOutput("outputs/pbftests/multilayer", interval=1))
        #tsetup.addPostprocessor(pbf.materialVtuOutput("outputs/pbftests/multilayer", interval=1))

        tstate0 = pbf.makeThermalState(tsetup, grid, srefinement=srefinement)

        # solve problem
        # initialize moving heat source
        laserTrack = [
            pbf.LaserPosition(xyz=[x0, y, 1 * layerThickness], time=0.0, power=0),
            pbf.LaserPosition(xyz=[x0, y, 1 * layerThickness], time=depositionTime, power=laserPower),
            pbf.LaserPosition(xyz=[x1, y, 1 * layerThickness], time=depositionTime + layerTime, power=laserPower),
            pbf.LaserPosition(xyz=[x0, y, 2 * layerThickness], time=depositionTime + layerTime, power=0.0),
            pbf.LaserPosition(xyz=[x0, y, 2 * layerThickness], time=2 * depositionTime + layerTime, power=laserPower),
            pbf.LaserPosition(xyz=[x1, y, 2 * layerThickness], time=2 * depositionTime + layerTime + layerTime, power=laserPower),
            pbf.LaserPosition(xyz=[x0, y, 3 * layerThickness], time=2 * depositionTime + 2 * layerTime, power=0.0),
            pbf.LaserPosition(xyz=[x0, y, 3 * layerThickness], time=3 * depositionTime + 2 * layerTime, power=laserPower),
            pbf.LaserPosition(xyz=[x1, y, 3 * layerThickness], time=3 * depositionTime + 3 * layerTime, power=laserPower)
        ]

        # define heat source
        heatSource = pbf.volumeSource(laserTrack, laserBeam, depthSigma=0.045 * units.mm)
        tsetup.addSource(heatSource)

        # geometric laser refinement
        refinement = pbf.laserRefinement(laserTrack, laserD4Sigma / 4, laserSpeed, trefinement)
        tsetup.addRefinement(refinement)

        # solve thermal problem
        print(f"Integrating thermal problem:", flush=True)
        print(f"    duration        = {totalTime}", flush=True)

        for ilayer in range(nlayers):
            print(f"Layer {ilayer + 1} / {nlayers}", flush=True)

            # We intentionally limit the number of newton iterations here to test the adaptive time step reduction
            tstate = pbf.addNewPowderLayerThermal(tsetup, tstate0, deltaT=depositionTime)
            tstate0 = pbf.computeThermalProblem(tsetup, tstate, timestep, layerTime, ilayer=ilayer, maxiter=8)

        # Check whether results are consistent with previous versions
        expectedNElementsList = [
            720, 720, 2694, 3296, 3870, 4444, 5046, 5592, 6082, 6537, 6929, 7195, 7356, 7510, 
            7692, 7846, 7986, 8140, 8224, 8266, 8112, 7783, 4829, 7020, 7496, 7930, 8378, 8812, 
            9190, 9512, 9799, 10023, 10121, 10114, 10100, 10114, 10114, 10086, 10072, 10086, 
            10086, 9848, 9470, 5760, 6642, 6950, 7237, 7538, 7832, 8084, 8294, 8483, 8623, 
            8679, 8672, 8665, 8672, 8672, 8651, 8644, 8651, 8644, 8504, 8245
        ]   
                 
        expectedMaterialNCellsList = [
            720, 720, 1420, 1595, 1994, 2365, 2659, 2680, 2932, 3219, 3548, 3863, 4171, 
            4269, 4486, 4829, 4829, 5158, 5438, 5704, 5858, 5816, 5816, 6488, 6845, 7076, 
            7132, 7391, 7636, 7958, 8196, 8420, 8679, 8896, 9162, 9428, 9631, 9806, 9974, 
            10198, 10401, 10653, 10548, 10548, 11283, 11633, 11731, 12018, 12298, 12550, 
            12697, 12802, 12935, 13138, 13222, 13334, 13432, 13495, 13565, 13698, 13747, 
            13894, 14020, 13908
        ]
        
        expectedNDofList = [
            1029, 1029, 2679, 3186, 3671, 4170, 4677, 5128, 5541, 5931, 6248, 6458, 6594, 
            6746, 6918, 7065, 7204, 7391, 7495, 7566, 7515, 7288, 5441, 7869, 8291, 8663, 
            9056, 9402, 9692, 9944, 10173, 10329, 10378, 10353, 10344, 10355, 10355, 10333, 
            10322, 10333, 10363, 10211, 9924, 6929, 7757, 8047, 8319, 8602, 8872, 9098, 9290,  
            9467, 9583, 9616, 9598, 9591, 9598, 9598, 9580, 9573, 9580, 9595, 9491, 9264
        ]
        
        # print(computedMaterialNCellsList)
        # print(pbf.thermalEvaluator(tstate0)([1.0, 0.0, basePlateHeight]))
        
        assert (len(expectedNElementsList) == len(computedNElementsList))
        assert (len(expectedMaterialNCellsList) == len(computedMaterialNCellsList))
        assert (len(expectedNDofList) == len(computedNDofList))

        for expectedNElements, computedNElements in zip(expectedNElementsList, computedNElementsList):
            assert (expectedNElements == computedNElements)
            
        for expectedNCells, computedNCells in zip(expectedMaterialNCellsList, computedMaterialNCellsList):
            assert (expectedNCells == computedNCells)
            
        for expectedNDof, computedNDof in zip(expectedNDofList, computedNDofList):
            assert (expectedNDof == computedNDof)

        temperature = pbf.thermalEvaluator(tstate0)

        self.assertAlmostEqual(temperature([1.0, 0.0, basePlateHeight]), 3817.027654534, delta=1e-6)
