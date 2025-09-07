import unittest, math, pbf
from functools import reduce

units = pbf.units

distance = lambda xyz0, xyz1: math.sqrt(reduce(lambda a, b: a + b, [(x1 - x0) ** 2 for x0, x1 in zip(xyz0, xyz1)]))

class BridgeTest(unittest.TestCase):
    def test(self):
        material = pbf.makeMaterial("SS316L")

        # General parameters
        laserD4Sigma = 120 * units.um
        laserSpeed = 1000 * units.mm / units.s
        laserPower = 180 * units.W
        layerThickness = 30 * units.um

        recoaterLevel = 20 * layerThickness
        totalHeight = 30 * layerThickness

        xyz0 = [-0.55 * units.mm, 1.45 * units.mm, recoaterLevel]
        xyz1 = [0.55 * units.mm, 2.55 * units.mm, recoaterLevel]

        dur = distance(xyz0, xyz1) / laserSpeed

        # Set to dur to simulate full benchmark
        simulationTime = 1.7 * dur

        elementSize = 0.14 * laserD4Sigma
        trefinement = 5
        srefinement = 5
        timestep = 0.3 * laserD4Sigma / laserSpeed
        
        laserTrack = [pbf.LaserPosition(xyz=xyz0, time=0.0, power=laserPower),
                      pbf.LaserPosition(xyz=xyz1, time=dur, power=laserPower)]

        laserBeam = pbf.gaussianBeam(sigma=laserD4Sigma / 4, absorptivity=0.32)
        heatSource = pbf.volumeSource(laserTrack, laserBeam, depthSigma=10 * units.um)

        domainMin = [-2.0 * units.mm, 0.0 * units.mm, -1.0 * units.mm]
        domainMax = [2.0 * units.mm, 4.0 * units.mm, totalHeight]

        # Construct part
        circles = pbf.implicitSubtraction(
            [pbf.implicitSphere([0.0, 0.0], 1 * units.mm), pbf.implicitSphere([0.0, 0.0], 0.55 * units.mm)])

        cylinder = pbf.extrude(circles, 0.0, 2 * units.mm, 0)

        translation = [-(1 / math.sqrt(2)) * units.mm, (1 / math.sqrt(2) + 2) * units.mm, 0 * units.mm]
        transformation = pbf.concatenate([pbf.rotation([0.0, 0.0, 1.0], -0.25 * math.pi), pbf.translation(translation)])

        part = pbf.implicitIntersection([
            pbf.implicitTransformation(cylinder, transformation),
            pbf.implicitHalfspace([0.0, 0.0, recoaterLevel - layerThickness], [0.0, 0.0, 1.0])
        ])

        # Setup problem
        rootsize = elementSize * 2 ** trefinement
        grid = pbf.createMesh(domainMin, domainMax, rootsize, layerThickness=layerThickness, zfactor=0.5)

        setup = pbf.ProcessSimulation(grid, material=material)
        setup.setMaterials(air=pbf.makeAir())
        
        tsetup = pbf.ThermalProblem(setup)
        tsetup.addSource(heatSource)

        # Setup custom refinement
        refinementPoints = [
            pbf.LaserRefinementPoint(0.00 * units.ms, 0.18 * units.mm, 5.4, 0.5),
            pbf.LaserRefinementPoint(1.20 * units.ms, 0.24 * units.mm, 3.5, 0.5),
            pbf.LaserRefinementPoint(6.00 * units.ms, 0.40 * units.mm, 2.5, 0.8),
            pbf.LaserRefinementPoint(30.0 * units.ms, 0.90 * units.mm, 1.5, 1.0),
            pbf.LaserRefinementPoint(0.10 * units.s, 1.10 * units.mm, 1.0, 1.0)
        ]

        def refinement(problem, state0, state1): 
            nseedpoints = state0.basis.maxdegree() + 2
            return pbf.laserTrackPointRefinement(laserTrack, refinementPoints, state1.time, nseedpoints)
                
        refinementFunction = pbf.laserTrackPointRefinementFunction(laserTrack, refinementPoints)

        tsetup.addRefinement(refinement)
        
        #out = pbf.thermalVtuOutput("outputs/pbftests/bridge", interval=16, functions=[(refinementFunction, "RefinementLevel")])
        #
        #tsetup.addPostprocessor(out)

        # Compute melt pool dimensions every other step
        meltPoolBoundsList = []

        def meltPoolBoundsAccumulator(mesh):
            points = mesh.points()
            bounds = [[1e50, 1e50, 1e50], [-1e50, -1e50, -1e50]]
            for ipoint in range(int(len(points) / 3)):
                for icoord in range(3):
                    bounds[0][icoord] = min(bounds[0][icoord], points[3 * ipoint + icoord])
                    bounds[1][icoord] = max(bounds[1][icoord], points[3 * ipoint + icoord])
            meltPoolBoundsList.append([max(u - l, 0.0) for l, u in zip(*bounds)])

        tsetup.addPostprocessor(pbf.meltPoolContourOutput(meltPoolBoundsAccumulator, interval=2))

        # Save number of elements and number of dofs every time step
        computedNElementsList, computedMaterialNCellsList, computedNDofList = [], [], []

        def meshDataAccumulator(thermalProblem, tstate):
            computedNElementsList.append(tstate.basis.nelements())
            computedNDofList.append(tstate.basis.ndof())
            computedMaterialNCellsList.append(tstate.history.grid().ncells())

        tsetup.addPostprocessor(meshDataAccumulator)

        # Setup initial state and compute problem
        tstate0 = pbf.makeThermalState(tsetup, grid, powderHeight=recoaterLevel, srefinement=srefinement, part=part)
        tstate1 = pbf.computeThermalProblem(tsetup, tstate0, timestep, simulationTime)

        # Check whether results are consistent with previous versions
        expectedNElementsList = [
            512, 3914, 4159, 4614, 5055, 5279, 5783, 5965, 6357, 6728, 6798, 7225, 7393, 7645, 
            7890, 7897, 8072, 8107, 8324, 8436, 8485, 8597, 8632, 8856, 9017, 9080, 9150, 9220, 
            9269, 9395, 9500, 9472, 9535, 9598, 9605, 9752, 9640, 9689, 9864, 9745, 9906, 9913, 
            9843, 10025, 9815, 9409, 9010, 8611, 8275, 7757, 7512, 7057, 6756, 6497, 5972, 5790, 
            5384, 5153, 4908, 4586, 4502, 4320, 4250, 4117, 3970, 3956, 3802, 3844, 3725, 3648, 
            3627, 3466, 3438, 3368, 3221
        ]

        expectedMaterialNCellsList = [
            187244, 111483, 111553, 111616, 111630, 111693, 111707, 111756, 111840, 111840, 
            111910, 111931, 111966, 112078, 112078, 112148, 112155, 112197, 112302, 112330, 
            112372, 112379, 112407, 112470, 112512, 112540, 112575, 112589, 112666, 112722, 
            112750, 112792, 112813, 112876, 112946, 112988, 113016, 113037, 113100, 113177, 
            113212, 113254, 113261, 113331, 113331, 113331, 113331, 113331, 113331, 113331, 
            113331, 113331, 113331, 113331, 113331, 113331, 113331, 113331, 113331, 113331, 
            113331, 113331, 113331, 113331, 113331, 113331, 113331, 113331, 113331, 113331, 
            113331, 113331, 113331, 113331, 113331
        ]
        
        expectedNDofList = [
            729, 3224, 3439, 3796, 4151, 4336, 4736, 4875, 5181, 5469, 5528, 5853, 5978, 6155, 6354, 
            6364, 6500, 6529, 6677, 6774, 6830, 6902, 6931, 7074, 7217, 7271, 7317, 7381, 7386, 7487, 
            7561, 7543, 7603, 7632, 7651, 7758, 7687, 7721, 7840, 7748, 7869, 7876, 7828, 7945, 7774,
            7451, 7122, 6790, 6512, 6101, 5892, 5534, 5294, 5081, 4679, 4524, 4215, 4039, 3856, 3622, 
            3568, 3429, 3377, 3275, 3168, 3154, 3037, 3073, 2980, 2925, 2907, 2789, 2767, 2712, 2615
        ]
        
        # print(computedMaterialNCellsList)
        # print(pbf.thermalEvaluator(tstate1)([0.0, 2.0, recoaterLevel]))
        # for lst in meltPoolBoundsList:
        #    print(f"[{lst[0]:.8f}, {lst[1]:.8f}, {lst[2]:.8f}],")
           
        assert (len(expectedNElementsList) == len(computedNElementsList))
        assert (len(expectedMaterialNCellsList) == len(computedMaterialNCellsList))
        assert (len(expectedNDofList) == len(computedNDofList))

        for expectedNCells, computedNCells in zip(expectedNElementsList, computedNElementsList):
            assert (expectedNCells == computedNCells)
        for expectedNCells, computedNCells in zip(expectedMaterialNCellsList, computedMaterialNCellsList):
            assert (expectedNCells == computedNCells)
        for expectedNDof, computedNDof in zip(expectedNDofList, computedNDofList):
            assert (expectedNDof == computedNDof)

        expectedBoundsList = [
            [0.0, 0.0, 0.0], 
            [0.11902237, 0.11902237, 0.03523499], [0.15680695, 0.15680695, 0.04634583],
            [0.18926239, 0.18926239, 0.04986145], [0.21861649, 0.21861649, 0.05051697],
            [0.24150848, 0.24150848, 0.05087585], [0.26099777, 0.26099777, 0.05106445],
            [0.27092743, 0.27092743, 0.05078247], [0.27103043, 0.27103043, 0.05055908],
            [0.27167892, 0.27167892, 0.05068359], [0.27375031, 0.27375031, 0.05144897],
            [0.27573395, 0.27573395, 0.05311157], [0.27365112, 0.27365112, 0.05461853],
            [0.28258514, 0.28258514, 0.05434021], [0.30065918, 0.30065918, 0.05225098],
            [0.31966782, 0.31966782, 0.05088501], [0.33171463, 0.33171463, 0.05101685],
            [0.33323669, 0.33323669, 0.05079529], [0.28942108, 0.28942108, 0.05049133],
            [0.27611160, 0.27611160, 0.05075317], [0.27374268, 0.27374268, 0.05064331],
            [0.27105713, 0.27105713, 0.05089417], [0.24149704, 0.24149704, 0.04984497],
            [0.17368698, 0.17368698, 0.03866272], [0.09318542, 0.09318542, 0.01652710],
            [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 
            [0.0, 0.0, 0.0],
        ]

        assert (len(meltPoolBoundsList) == len(expectedBoundsList))

        for computedBounds, expectedBounds in zip(meltPoolBoundsList, expectedBoundsList):
            for computedAxis, expectedAxis in zip(computedBounds, expectedBounds):
                self.assertAlmostEqual(computedAxis, expectedAxis, delta=5e-5)

        temperature = pbf.thermalEvaluator(tstate1)

        self.assertAlmostEqual(temperature([0.0, 2.0, recoaterLevel]), 655.413439, delta=1e-3)
