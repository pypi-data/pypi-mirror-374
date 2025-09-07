# This file is part of the mlhpbf project. License: See LICENSE
import math
import unittest, pbf

units = pbf.units


class SolidificationBarTest(unittest.TestCase):

    def stressEvaluator(self, msetup, mstate, tstate, iComponent, xyz):
        temperature, materialAdapter = pbf.thermalEvaluator(tstate), pbf.iternalMaterialAdapter(tstate.history,
                                                                                        msetup.simulation.materials)
        processors = [pbf.mechanicalPostprocessor(["Stress"], mstate.dofs, mstate.history, temperature, materialAdapter)]
        local = mstate.mesh.mapBackwards(xyz)

        if len(local) == 0:
            raise ValueError(f"No element at coordinates {xyz}")

        ielement, rst = local[0]
        partition = pbf.CellMeshPartition(index=ielement, points=rst)
        postmesh = pbf.customCellMesh(ndim=3, partitions=[partition])
        writer = pbf.dataAccumulator()
        pbf.basisOutput(mstate.basis, postmesh, writer, processors)

        return writer.data()[0][iComponent]

    def refineTowardsMaterialInterface(self, depth, functionInterface, *, nseedpoints=None):
        def refinement(problem, state0, state1):
            interface = pbf.sliceLast(pbf.scalarField(ndim=4, func=functionInterface), state1.time)
            nseedpoints_ = refinement.nseedpoints if refinement.nseedpoints is not None else problem.degree + 2
            return pbf.refineWithLevelFunction(interface, nseedpoints_)

        refinement.depth = depth
        refinement.nseedpoints = nseedpoints

        return refinement

    def refineTowardsBoundaryFunction(self, depth, boundaryFunction, *, nseedpoints=None):
        def refinement(problem, state0, state1):
            nseedpoints_ = refinement.nseedpoints if refinement.nseedpoints is not None else problem.degree + 2
            return pbf.refineWithLevelFunction(pbf.scalarField(ndim=3, func=boundaryFunction), nseedpoints_)

        refinement.depth = depth
        refinement.nseedpoints = nseedpoints

        return refinement

    def test(self):
        def blend(function, factor, T0, T1):
            return pbf.blendMaterialFunction(function, pbf.linearMaterialBlending(T0, T1), factor * function(20.0)[0])

        # Material setup
        material = pbf.Material()
        material.initialized = True
        material.density = pbf.temperatureFunction(7200 * units.kg / units.m ** 3)
        material.specificHeatCapacity = pbf.temperatureFunction(680 * units.J / units.kg)
        material.heatConductivity = pbf.temperatureFunction(34 * units.W / units.m /  units.C)
        alpha = material.heatConductivity(20)[0] /(material.specificHeatCapacity(20)[0] * material.density(20)[0])
        material.solidTemperature = 1490 * units.C * units.C
        material.annealingTemperature = 1490 * units.C * units.C
        material.liquidTemperature = 1490 * units.C + 1 * units.C
        Tw, Ti, Tm = 1362 * units.C, 1550 * units.C, material.annealingTemperature
        material.latentHeatOfFusion = 272e3 * units.J / units.kg

        CoTE = 8.46354e-5 * 1 / units.C

        E = 40.0 * units.GPa
        yieldStress0 = 40.0 * units.MPa
        poissonRatio = 0.35
        material.poissonRatio = pbf.temperatureFunction(poissonRatio)
        material.plasticModelSelector = 0.0
        material.hardening = pbf.temperatureFunction(0.0)

        def liquidMechanicalProperty(function, factor):
            blending = pbf.linearMaterialBlending(material.annealingTemperature, material.solidTemperature , flip=True)
            return pbf.blendMaterialFunction(function, blending, factor * function(20.0)[0])

        material.youngsModulus = liquidMechanicalProperty(pbf.temperatureFunction(E), 1e-8)
        material.thermalExpansionCoefficient = pbf.temperatureFunction(CoTE)

        linearBlending = pbf.linearMaterialBlending(Tw, Tm, flip=True)
        material.yieldStress = pbf.blendMaterialFunction(pbf.temperatureFunction(yieldStress0), linearBlending, 0.0)

        # Analytical solution
        lmbda = 0.330825295611989
        xhat1 = 0.45487188
        xhat2 = 0.21570439
        m = f"( 1.0 - {poissonRatio} ) * {yieldStress0} / ({CoTE} * {E} * ({Tm} - {Tw}) )"
        D = f"1 / erf({lmbda})"

        X = f"2 * {lmbda} * sqrt({alpha} * x[3])"
        left = f"{Tw} + ({Tm} - {Tw}) * erf (x / sqrt(4 * {alpha} * x[3])) / erf ({lmbda})"
        right = f"{Ti} + ({Tm} - {Ti}) * erfc(x / sqrt(4 * {alpha} * x[3])) / erfc({lmbda})"
        solutionThermal = pbf.scalarField(ndim=4, func=f"{left} if x < {X} else {right}")

        xhat = f"(x / (2 * {lmbda} * sqrt({alpha} * x[3])))"
        stressfactor = f"({CoTE} * {E} * ({Tm} - {Tw}) ) / ( 1.0 - {poissonRatio})"
        left = f"({m} * ({D} * erf ({lmbda} * {xhat}) - 1))"
        elastic = (f"({m} * (1 - {D} * erf({lmbda} * {xhat1})) + {D} * (erf({lmbda} * {xhat1}) - erf({lmbda} * {xhat})) "
                   f"- 2 / sqrt({math.pi}) * {D} * (1 - {m}) * {lmbda} * {xhat1} * exp(-({lmbda} * {xhat1})**2) * log ({xhat1} / {xhat}))")
        right = f"{m} * (1 - {D} * erf ({lmbda} * {xhat}) )"
        # ORIGINAL SOLUTION WITH GENERALIZED PLAIN STRAIN BC ###########################################################
        # solutionMechanical = pbf.scalarField(ndim=4,
        #                                      func=f"({left} * {stressfactor}) if {xhat} < {xhat2} else  ({elastic} * {stressfactor}) if ({xhat} >= {xhat2} "
        #                                           f"and  {xhat} <= {xhat1}) else ({right} * {stressfactor}) if  ({xhat} > {xhat1} and"
        #                                           f" {xhat} <= 1) else 0")
        # SOLUTION WITH HOMOGENEOUS DIRICHLET BC #######################################################################
        solutionMechanical = pbf.scalarField(ndim=4,
                                             func=f"({right} * {stressfactor}) if {xhat} <= 1 else 0")

        # Problem setup
        lengths = [8.0 * units.mm, 0.4 * units.mm, 0.4 * units.mm]
        grid = pbf.makeGrid([16, 1, 1], lengths)

        setup = pbf.ProcessSimulation(grid)
        setup.setMaterials(baseplate=material, structure=material, air=material, powder=material)
        setup.ambientTemperature = Ti

        refDepth = 2
        interfaceFunction = f"{refDepth} * exp(-(x-{X})**2 / 0.8**2)"
        leftFaceFunction = f"{refDepth} * exp(- x**2 / 1**2)"

        out = pbf.thermomechanicalVtuOutput("outputs/pbftests/thermoelastoplasticbar",
        functions=[( solutionMechanical, "Analytical Mechanical"), ( solutionThermal, "Analytical Thermal"), (pbf.scalarField(ndim=4,
                                             func=interfaceFunction), "RefinementIndicator")], materialRefinement=False,
                                            clipAbove=False)

        # Setup thermal problem
        tsetup = pbf.ThermalProblem(setup)
        tsetup.degree = 3
        tsetup.addDirichletBC(pbf.temperatureBC(0, Tw))
        tsetup.addDirichletBC(pbf.temperatureBC(1, solutionThermal))
        tsetup.addPostprocessor(out)
        tsetup.addRefinement(self.refineTowardsMaterialInterface(refDepth, interfaceFunction, nseedpoints=13))

        # Setup mechanical problem
        msetup = pbf.MechanicalProblem(setup, degree=3, quadratureOrderOffset=1)
        msetup.addDirichletBC(pbf.dirichletBC(0, 0))
        msetup.addDirichletBC(pbf.dirichletBC(2, 1))
        msetup.addDirichletBC(pbf.dirichletBC(3, 1))
        msetup.addDirichletBC(pbf.dirichletBC(4, 2))
        msetup.addDirichletBC(pbf.dirichletBC(5, 2))
        msetup.addPostprocessor(out)
        msetup.addRefinement(self.refineTowardsMaterialInterface(refDepth, interfaceFunction, nseedpoints=5))
        msetup.addRefinement(self.refineTowardsBoundaryFunction(refDepth, leftFaceFunction, nseedpoints=5))

        # Solution
        tstate0 = pbf.makeThermalState(tsetup, grid, powderHeight=lengths[0])
        mstate0 = pbf.makeMechanicalState(msetup, grid, powderHeight=lengths[0])
        tstate1, mstate1 = pbf.computeThermomechanicalProblem(tsetup, msetup, tstate0, mstate0, 0.1 * units.s,
                                                              1 * units.s, atol=1e-6, rtol=1e-8, maxiter=20)

        # Compare result to analytical solution
        tol = 1e-1
        nsamples = 100
        expected = [2.643311623, 0.232632659, 0.153387138, 0.494741346, 0.592891177, 0.512063330, 0.460000091, 0.169827559, 
                    0.089832209, 0.352397177, 0.727338763, 0.724410800, 0.424886426, 0.366844092, 0.798293028, 0.700731493, 
                    0.641207409, 1.387964259, 0.756477564, 0.803059329, 0.356509421] + [0.0] * 79
        
        for i in range(nsamples):
            xyzt = [(i + 1) * lengths[0] / nsamples, lengths[1] / 2, lengths[2] / 2, tstate1.time]
            sigmaZZ = self.stressEvaluator(msetup, mstate1, tstate1, 2, xyzt[:-1])
            error = abs(sigmaZZ - solutionMechanical(xyzt))
            #print(f"{error:.9f}, ", end='')
            self.assertLess(error, expected[i] + tol, msg="Difference above tolerance")
