# This file is part of the mlhpbf project. License: See LICENSE
import math
import unittest
import pbf

units = pbf.units

class SolidificationBarTest(unittest.TestCase):
    def testHistoryQuadrature(self):
    
        # Two meshes with different refinement
        mesh1 = pbf.makeRefinedGrid([3, 1, 2], lengths=[3.0, 1.0, 2.0])
        mesh2 = pbf.makeRefinedGrid([3, 1, 2], lengths=[3.0, 1.0, 2.0])
        
        mesh1.refine([0, 2, 3, 5])
        mesh2.refine([0, 3, 4])
        
        mesh1.refine([10, 11, 12, 13, 19, 20])
        mesh2.refine([11, 14])
        
        basis1 = pbf.makeHpTrunkSpace(mesh1)
        
        # Piecewise constant function with jump at x = 1.25 (conforming by 
        # mesh union) and y = 7/6 (conforming by top surface partitioning)
        f0 = pbf.scalarField(3, "0.3 if x < 1.25 else 0.7")
        f1 = pbf.scalarField(3, "4.1 if z < 7.0 / 6.0 else -3.8")
        f2 = pbf.scalarField(3, "x * (3 - x) + y * (1 - y) + z * (2 - z)")
        
        f = pbf.scalarField(3, "f0(x, y, z) * f1(x, y, z) + f2(x, y, z)", fields=[f0, f1, f2])
        
        # Integrate function
        quadrature = pbf._quadratureUnionWithHistory(mesh2, 7/6)
        integrand = pbf.functionIntegrand(f)
        
        expectedIntegral = (0.3 * 4.1) * (1.25 * 7/6) - (0.3 * 3.8) * (1.25 * 5/6) + \
                           (0.7 * 4.1) * (1.75 * 7/6) - (0.7 * 3.8) * (1.75 * 5/6) + 14
                         
        computedIntegral = pbf.ScalarDouble(0.7)
        pbf.integrateOnDomain(basis1, integrand, [computedIntegral], quadrature=quadrature)
                         
        self.assertAlmostEqual(computedIntegral.get() - 0.7, expectedIntegral, places=13)
                         
        # # Postprocessing
        # pbf.writeMeshOutput(mesh1, writer=pbf.VtuOutput("mesh1.vtu"), processors=[pbf.functionProcessor(f, "Function")])
        # pbf.writeMeshOutput(mesh2, writer=pbf.VtuOutput("mesh2.vtu"))
        # 
        # order = pbf.relativeQuadratureOrder(3, 1)
        # postmesh = pbf.quadraturePointCellMesh(quadrature, basis1, order)
        # 
        # pbf.writeMeshOutput(mesh1, postmesh=postmesh, writer=pbf.VtuOutput("points.vtu"))
        