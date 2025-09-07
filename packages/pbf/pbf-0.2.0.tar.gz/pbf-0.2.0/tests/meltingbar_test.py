# This file is part of the mlhpbf project. License: See LICENSE

import unittest, pbf

units = pbf.units


class MeltingBarTest(unittest.TestCase):
    def refineTowardsMaterialInterface(self, depth, functionInterface, *, nseedpoints=None):
        def refinement(problem, state0, state1):
            interface = pbf.sliceLast(pbf.scalarField(ndim=4, func=functionInterface), state1.time)
            nseedpoints_ = refinement.nseedpoints if refinement.nseedpoints is not None else problem.degree + 2
            return pbf.refineWithLevelFunction(interface, nseedpoints_)

        refinement.depth = depth
        refinement.nseedpoints = nseedpoints

        return refinement
    def test(self):
        # Material setup
        material = pbf.Material()
        material.initialized = True
        material.density = pbf.temperatureFunction(4510 * units.kg / units.m ** 3)
        material.specificHeatCapacity = pbf.temperatureFunction(520 * units.J / units.kg)
        material.heatConductivity = pbf.temperatureFunction(16 * units.W / units.m)
        material.solidTemperature = 1670 * units.C - 1 * units.C
        material.liquidTemperature = 1670 * units.C + 1 * units.C
        material.latentHeatOfFusion = 325e3 * units.J / units.kg

        # Analytical solution
        Ts, Tl, Tm = 1500 * units.C, 2000 * units.C, 1670 * units.C
        lmbda = 0.388150542167233
        alpha = 6.8224e-06 * units.m ** 2 / units.s

        front = f"2 * {lmbda} * sqrt({alpha} * x[3])"
        left = f"{Tl} - ({Tl} - {Tm}) * erf (x / sqrt(4 * {alpha} * x[3])) / erf ({lmbda})"
        right = f"{Ts} + ({Tm} - {Ts}) * erfc(x / sqrt(4 * {alpha} * x[3])) / erfc({lmbda})"
        solution = pbf.scalarField(ndim=4, func=f"{left} if x < {front} else {right}")

        refDepth = 3
        interfaceFunction = f"{refDepth} * exp(-(x-{front})**2 / 10**2)"

        # Problem setup
        lengths = [100.0 * units.mm, 1.0 * units.mm, 1.0 * units.mm]
        grid = pbf.makeGrid([25, 1, 1], lengths)

        setup = pbf.ProcessSimulation(grid)
        setup.setMaterials(baseplate=material, structure=material, air=material, powder=material)
        setup.ambientTemperature = Ts

        out = pbf.thermalVtuOutput("outputs/pbftests/meltingbar", functions=[(solution, "Analytical")], interval=20)

        tsetup = pbf.ThermalProblem(setup)
        tsetup.degree = 3
        tsetup.addDirichletBC(pbf.temperatureBC(0, Tl))
        tsetup.addDirichletBC(pbf.temperatureBC(1, solution))
        tsetup.addPostprocessor(out)
        tsetup.addRefinement(self.refineTowardsMaterialInterface(refDepth, interfaceFunction, nseedpoints=5))

        # Solution
        tstate0 = pbf.makeThermalState(tsetup, grid, powderHeight=lengths[-1])
        tstate1 = pbf.computeThermalProblem(tsetup, tstate0, deltaT=1.0 * units.s, duration=100 * units.s, rtol=1e-8, lsolver_rtol=1e-10)

        # Compare result to analytical solution
        evaluator = pbf.thermalEvaluator(tstate1)

        expected = [0.000000, 0.023614, 0.047265, 0.070951, 0.094722, 0.118595, 0.142589, 0.166728, 0.191027, 0.215510,
                    0.240187, 0.265086, 0.290238, 0.315695, 0.341546, 0.367955, 0.395211, 0.423823, 0.454675, 0.489283,
                    0.530431, 0.131938, 0.154419, 0.176801, 0.198685, 0.220012, 0.240748, 0.260872, 0.280367, 0.299223,
                    0.317428, 0.334973, 0.351842, 0.368029, 0.383518, 0.398303, 0.412366, 0.425698, 0.438318, 0.450142,
                    0.461235, 0.471556, 0.481128, 0.489881, 0.497874, 0.505074, 0.511504, 0.517111, 0.521948, 0.525991,
                    0.529263, 0.531729, 0.533434, 0.534367, 0.534550, 0.533965, 0.532650, 0.530605, 0.527851, 0.524388,
                    0.520245, 0.515432, 0.509969, 0.503870, 0.497158, 0.489849, 0.481963, 0.473523, 0.464545, 0.455053,
                    0.445062, 0.434603, 0.423687, 0.412339, 0.400571, 0.388421, 0.375889, 0.363004, 0.349773, 0.336234,
                    0.322384, 0.308248, 0.293832, 0.279170, 0.264256, 0.249110, 0.233736, 0.218165, 0.202386, 0.186417,
                    0.170257, 0.153935, 0.137437, 0.120777, 0.103953, 0.086989, 0.069870, 0.052609, 0.035201, 0.017670]

        for i in range(100):
            xyzt = [i * units.mm, 0.5 * units.mm, 0.5 * units.mm, tstate1.time]
            error = evaluator(xyzt[:-1]) - solution(xyzt)
            self.assertAlmostEqual(evaluator(xyzt[:-1]) - solution(xyzt), expected[i], delta=0.002)
