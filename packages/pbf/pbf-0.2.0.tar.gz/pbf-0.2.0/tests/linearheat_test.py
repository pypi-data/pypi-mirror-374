# This file is part of the mlhpbf project. License: See LICENSE

import mlhp
import unittest
import pbf

def makeRefinement(position0, position1, time):
    sourcePosition = [(x1 - x0) * time + x0 for x0, x1 in zip(position0, position1)]
    
    refinement1Radii = [0.096, 0.048, 0.048]
    refinement2Radii = [0.052, 0.016, 0.016]

    center1 = [sourcePosition[0] - 0.6 * refinement1Radii[0]] + sourcePosition[1:]
    center2 = [sourcePosition[0] - 0.3 * refinement2Radii[0]] + sourcePosition[1:]
    
    domain1 = mlhp.implicitEllipsoid(center1, refinement1Radii)
    domain2 = mlhp.implicitEllipsoid(center2, refinement2Radii)
    
    refinement1 = mlhp.refineInsideDomain(domain1, 1)
    refinement2 = mlhp.refineInsideDomain(domain2, 2)
    
    return mlhp.refinementOr([refinement1, refinement2])
    
class LinearHeatTest(unittest.TestCase):
    def test_1(self):
        
        # Material setup
        capacity = 1.0
        conductivity = 0.008
        
        material = pbf.makeMaterial("SS316L")
        material.density = pbf.temperatureFunction(1.0)
        material.specificHeatCapacity = pbf.temperatureFunction(capacity)
        material.heatConductivity = pbf.temperatureFunction(conductivity)
        
        # Computational domain and time discretization
        lengths = [1.0, 0.4, 0.1]
        
        grid = pbf.createMesh([0.0] * 3, lengths, 0.1)

        duration = 1.0
        nsteps = 24
        dt = duration / nsteps 
        
        sourceSigma = 0.02
        
        position0 = [0.2, lengths[1] / 2.0, lengths[2]]         
        position1 = [0.8, lengths[1] / 2.0, lengths[2]]
        
        analytical = mlhp.makeAmLinearSolution(position0, position1, duration,
            capacity, conductivity, sourceSigma, duration / 10.0, 0.0)         

        # Configure problem
        setup = pbf.ProcessSimulation(grid=grid, material=material, ambientTemperature=0.0)
        setup.setMaterials(powder=material)

        tsetup = pbf.ThermalProblem(setup, degree=2, theta=0.5)
        tsetup.addSource(("VolumeSource", lambda tbounds: analytical.source))
        tsetup.addRefinement(lambda problem, state0, state1: makeRefinement(position0, position1, state1.time))
        
        # Boundary condition
        tsetup.addDirichletBC(pbf.temperatureBC(0, analytical.solution)) # left
        tsetup.addDirichletBC(pbf.temperatureBC(1, analytical.solution)) # right
        tsetup.addDirichletBC(pbf.temperatureBC(2, analytical.solution)) # front
        tsetup.addDirichletBC(pbf.temperatureBC(3, analytical.solution)) # back 
        tsetup.addDirichletBC(pbf.temperatureBC(4, analytical.solution)) # bottom
        
        # Laser source
        # Gather values for error check
        def countDofs(thermalProblem, tstate):
            countDofs.count += tstate.basis.ndof()
        
        def integrateNorms(thermalProblem, tstate):
            l2ErrorIntegrand = mlhp.l2ErrorIntegrand(tstate.dofs, mlhp.sliceLast(analytical.solution, tstate.time))            
            l2Integrals = mlhp.makeScalars(3)
            mlhp.integrateOnDomain(tstate.basis, l2ErrorIntegrand, l2Integrals)
            factor = dt if tstate.index < nsteps else dt / 2.0
            integrateNorms.L2 = [E + factor * Ec.get() for E, Ec in zip(integrateNorms.L2, l2Integrals)]
            
        countDofs.count = 0
        integrateNorms.L2 = [0.0, 0.0, 0.0]
        
        tsetup.addPostprocessor(pbf.thermalVtuOutput("outputs/pbftests/linearheat2"))
        tsetup.addPostprocessor(countDofs)
        tsetup.addPostprocessor(integrateNorms)
        
        # Simulate       
        tstate0 = pbf.makeThermalState(tsetup, grid, powderHeight=lengths[1])
        tstate1 = pbf.computeThermalProblem(tsetup, tstate0, dt, duration, rtol=1e-10, lsolver_rtol=1e-10)
        
        # Compare to reference values
        self.assertEqual(countDofs.count, 15921)
        self.assertAlmostEqual(integrateNorms.L2[0], 2.7311908312**2, delta=2e-6)
        self.assertAlmostEqual(integrateNorms.L2[1], 2.7530527887**2, delta=2e-8)
        self.assertAlmostEqual(integrateNorms.L2[2], 0.0735319739**2, delta=2e-8)
        self.assertAlmostEqual(integrateNorms.L2[2] / integrateNorms.L2[1], 0.0267092495**2, delta=2e-8)
        
        # # With: tstate1.basis = mlhp.makeHpTrunkSpace(tstate1.mesh, mlhp.LinearGrading([thermalProblem.degree]*3))
        # self.assertEqual(countDofs.count, 33436 + 353)
        # self.assertAlmostEqual(integrateNorms.L2[0], 2.7342053949**2, delta=2e-6) # 1e-8 with projection integration
        # self.assertAlmostEqual(integrateNorms.L2[1], 2.7532175961**2, delta=1e-8)
        # self.assertAlmostEqual(integrateNorms.L2[2], 0.0644606778**2, delta=1e-7)
        # self.assertAlmostEqual(integrateNorms.L2[2] / integrateNorms.L2[1], 0.0234128526**2, delta=1e-7)
        
