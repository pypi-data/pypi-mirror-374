# This file is part of the mlhpbf project. License: See LICENSE
import os 
import sys

try:
    # mlhp.py script folder
    path = os.path.abspath(os.path.dirname(sys.argv[0]))

    # Try to open path/mlhpPythonPath containing the python module path. This
    # file is written as post build command after compiling pymlhpcore.
    with open(os.path.join(path, 'mlhpPythonPath'), 'r') as f:
        sys.path.append(os.path.normpath(f.read().splitlines()[0]))

except IOError:
    pass

import mlhp
import math
import time

from pymlhpbf import *
from dataclasses import dataclass

vtudefault = "RawBinaryCompressed"


class units:
    mm = 1.0
    m = 1e3 * mm
    cm = 10.0 * mm
    um = 1e-3 * mm
    s = 1.0
    ms = 1e-3 * s
    g = 1.0
    kg = 1e3 * g
    N = 1.0
    kN = 1e3 * N
    J = N * m
    kJ = 1e3 * J
    W = J / s
    kW = 1e3 * W
    C = 1.0
    Pa = N / (m * m)
    MPa = 1e6 * Pa
    GPa = 1e9 * Pa
    Hz = 1.0
    kHz = 1e3 * Hz


def beamShapeFromPixelMatrix(values, pixelsize, npixels=None):
    if isinstance(values, list) or (hasattr(values, "shape") and len(values.shape) == 1):
        if npixels is None:
            raise ValueError("When passing pixel values as list, npixels must be specified")
        data = mlhp.DoubleVector(values)
        shape = npixels
    elif hasattr(values, "shape") and hasattr(values, "ravel"):
        if len(values.shape) != 2:
            raise ValueError("Pixel data dimension too high")
        data = mlhp.DoubleVector(values.ravel())
        shape = values.shape
    else:
        raise ValueError("Pixel data must be passed as list or as 2D numpy array")

    cellsize = [pixelsize] * 2 if isinstance(pixelsize, (float, int)) else list(pixelsize)

    if not isinstance(cellsize, list) or len(cellsize) != 2:
        raise ValueError("pixelsize must be a scalar value or a list of scalar values.")

    lengths = [dx * nx for dx, nx in zip(cellsize, shape)]

    return scalarFieldFromVoxelData(data, shape, lengths, origin=[-l / 2 for l in lengths], outside=0.0)


def volumeSource(track, beamShape, depthSigma=1.0):
    def create(timeBounds):
        return internalVolumeSource(filterTrack(create.track, timeBounds=timeBounds), create.beamShape, create.depthSigma)
    create.track = track
    create.beamShape = beamShape
    create.depthSigma = depthSigma
    return "VolumeSource", create


def surfaceSource(track, beamShape):
    def create(timeBounds):
        return internalSurfaceSource(filterTrack(create.track, timeBounds=timeBounds), create.beamShape)
    create.track = track
    create.beamShape = beamShape
    return "SurfaceSource", create


# Pass single value or interpolate using two lists of temperatures and values.
# extrapolate can be "constant", "linear", or "polynomial".
def temperatureFunction(temperatures=None, values=None, degree=1, extrapolate="constant"):
    if values is None:
        if not isinstance(temperatures, float): raise ValueError("Single value must be of type float.")
        return mlhp.constantInterpolation([0.0], [temperatures])

    extrapolateStr = "default" if extrapolate.lower() == "polynomial" else extrapolate
    if degree == 1:
        return mlhp.linearInterpolation(temperatures, values, extrapolateStr)
    else:
        return mlhp.splineInterpolation(temperatures, values, degree, extrapolateStr)


def makeMaterial(name: str):
    material = Material()
    material.name = name
    material.initialized = True
    
    def applyUnits(values, units):
        for i in range(len(values)):
            values[i] = values[i] * units
            
    def defineTemperatures(annealing, solid, liquid):
        material.annealingTemperature = annealing
        material.solidTemperature = solid
        material.liquidTemperature = liquid
    
    if name == "IN625":
        # [1] https://www.specialmetals.com/documents/technical-bulletins/inconel/inconel-alloy-625.pdf
        # [2] https://dx.doi.org/10.1007/s10765-019-2490-8 
        # https://doi.org/10.1007/BF01563797
        
        # Density at 1000 using thermal expansion: 8440 / (1 + 3 * 13.8e-6 * 1000)
        rhoT = [-1000, 0, 1000, 2000]
        rhoV = [8550, 8448, 8100, 7900]
        rhoD = [0, -348/1000, -348/1000, 0]
        
        # Specific heat according to [1]
        sphcT = [-1000, 0, 1000, 2000]
        sphcV = [320, 404.8, 650.2, 750]
        sphcD = [0, 245.3/1000, 245.3/1000, 0]
        
        # Heat conductivity following [2]
        condT = [-800, 0, 1300, 2200]
        condV = [4, 9, 31.7, 38]
        condD = [0, 17.5/1000, 17.5/1000, 0]
        
        texpT = [93, 204, 316, 427, 538, 649, 760, 871, 982, 1100, 1300]
        texpV = [12.8e-6, 13.1e-6, 13.3e-6, 13.7e-6, 14.0e-6, 14.8e-6, 15.3e-6, 15.8e-6, 16.2e-6, 16.5e-6, 16.8e-6]
        ystrT = [21, 93, 204, 316, 427, 538, 649, 760, 871, 1040, 1150]
        ystrV = [493, 479, 443, 430, 424, 423, 422, 415, 386, 31, 15]
        EmodT = [21, 93, 204, 316, 427, 538, 649, 760, 871]
        EmodV = [207.5, 204.1, 197.9, 191.7, 185.5, 178.6, 170.3, 160.6, 147.5]
        nuT, nuV = EmodT, [0.278, 0.280, 0.286, 0.290, 0.295, 0.305, 0.321, 0.340, 0.336]
        hardT, hardV = [0.0], [0.0]
        
        defineTemperatures(annealing=870 * units.C, solid=1290 * units.C, liquid=1350 * units.C)
        material.latentHeatOfFusion = 2.8e5 * units.J / units.kg
        
    elif name == "IN718":
        # https://www.specialmetals.com/documents/technical-bulletins/inconel/inconel-alloy-725.pdf
        # https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=3cfe53e3a1212efd66eca53a87e37774fa5ba49e
        # https://iopscience.iop.org/article/10.1088/1742-6596/1382/1/012175/pdf
        rhoT = [-800, 0, 1000, 2000]
        rhoV = [8300, 8176.7, 7842, 7700]
        rhoD = [0, -334.7/1000, -334.7/1000, 0]
        
        sphcT = [-800, 0, 950, 2000]
        sphcV = [360, 425, 614, 690]
        sphcD = [0, 189/1000, 189/1000, 0]

        condT = [-800, 0, 1000, 2300]
        condV = [6, 10.2, 25.5, 33]
        condD = [0, 15.3/1000, 15.3/1000, 0]
        
        texpT, texpV, ystrT, ystrV, EmodT, EmodV, nuT, nuV, hardT, hardV = [[0.0]] * 10
            
        defineTemperatures(annealing=870 * units.C, solid=1260 * units.C, liquid=1340 * units.C)
        material.latentHeatOfFusion = 2.1e5 * units.J / units.kg

    elif name == "SS316L":
        # Probably from "Recommended Values of Thermophysical Properties for Selected Commercial Alloys"?
        rhoT = [-800, 0.0, 1300, 2400]
        rhoV = [8100, 7965, 7323, 7000]
        rhoD = [0, -425/1000, -550/1000, 0]
        
        sphcT = [-800, 0, 1300, 2000]
        sphcV = [450, 494.5, 667.4, 710]
        sphcD = [0, 133/1000, 133/1000, 0]
        
        condT = [-800, 0, 1300, 2200]
        condV = [8.5, 12.97, 31.55, 36]
        condD = [0, 17.5/1000, 12.7/1000, 0]
        
        # Only minor modification at high temperatures
        texpT = [-0.15, 26.85, 76.85, 126.85, 226.85, 326.85, 426.85, 526.85, 626.85, 726.85, 826.85, 
                 926.85, 1026.85, 1126.85, 1226.85]
        texpV = [14.6e-6, 14.8e-6, 15.2e-6, 15.6e-6, 16.3e-6, 16.9e-6, 17.4e-6, 17.9e-6, 18.3e-6, 
                 18.7e-6, 19.0e-6, 19.3e-6, 19.5e-6 + 0.5e-7, 19.6e-6 + 0.1e-6, 19.8e-6] 
        # Not modified since the mechanical problem doesn't depend on temperature
        ystrT = [100, 300, 816, 1040, 1150]
        ystrV = [225, 168, 115, 31, 15]
        EmodT = [20, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200]
        EmodV = [195, 191, 186, 180, 173, 164, 155, 144, 131, 117, 100, 81, 51]
        hardT, hardV = ystrT, [2091, 1577, 708, 405, 265]
        nuT, nuV = EmodT, [0.35, 0.26, 0.275, 0.315, 0.33, 0.3, 0.32, 0.31, 0.24, 0.24, 0.24, 0.24, 0.24]
            
        defineTemperatures(annealing=1040 * units.C, solid=1375 * units.C, liquid=1400 * units.C)
        material.latentHeatOfFusion = 2.8e5 * units.J / units.kg
    else:
        raise ValueError(f"Unknown material \"{name}\". Available are [IN625, IN718, SS316L].")
    
    applyUnits(rhoV, units.kg / units.m**3)
    applyUnits(sphcV, units.J / (units.kg * units.C))
    applyUnits(condV, units.W / (units.m * units.C))
    applyUnits(rhoD, units.kg / units.m**3)
    applyUnits(sphcD, units.J / (units.kg * units.C))
    applyUnits(condD, units.W / (units.m * units.C))
    applyUnits(texpV, 1 / units.C)
    applyUnits(ystrV, units.MPa)
    applyUnits(EmodV, units.GPa)
    applyUnits(hardV, units.MPa)
    
    #material.density = temperatureFunction(rhoT, rhoV)
    #material.specificHeatCapacity = temperatureFunction(sphcT, sphcV)
    #material.heatConductivity = temperatureFunction(condT, condV)
    material.density = mlhp.hermiteInterpolation(rhoT, rhoV, rhoD, "constant")
    material.specificHeatCapacity = mlhp.hermiteInterpolation(sphcT, sphcV, sphcD, "constant")
    material.heatConductivity = mlhp.hermiteInterpolation(condT, condV, condD, "constant")
    material.thermalExpansionCoefficient = temperatureFunction(texpT, texpV)
    material.yieldStress = temperatureFunction(ystrT, ystrV)
    material.youngsModulus = temperatureFunction(EmodT, EmodV)
    material.poissonRatio = temperatureFunction(nuT, nuV)
    material.hardening = temperatureFunction(hardT, hardV)
    material.plasticModelSelector = 0.5
    
    def liquidMechanicalProperty(function, factor):
        blending = linearMaterialBlending(material.annealingTemperature, material.solidTemperature, flip=True)
        return blendMaterialFunction(function, blending, factor * function(20.0)[0])
    
    material.youngsModulus = liquidMechanicalProperty(material.youngsModulus, 1e-2)
    material.yieldStress = liquidMechanicalProperty(material.yieldStress, 1e-3)
    material.hardening = liquidMechanicalProperty(material.hardening, 1e-3)
    
    return material
    

def makePowder(material, densityScaling=0.5, conductivityScaling=0.08, youngsModulusScaling=1e-3):
    if not isinstance(material, Material):
        raise ValueError(f"Invalid data type for material ({type(material)}).")

    def blend(function, factor, T0, T1, sigmoid):
        blending = sigmoidMaterialBlending if sigmoid else linearMaterialBlending
        return blendMaterialFunction(function, blending(T0, T1), factor * function(20.0)[0])
    
    # Powder conductivity: https://doi.org/10.1016/j.powtec.2022.117323
    Ta, Ts, Tl = material.annealingTemperature, material.solidTemperature, material.liquidTemperature
    Tm, TmLow = (Tl + Ts) / 2, (Tl + Ts) / 2 - 1.5 * material.regularization * (Tl - Ts) / 2
    
    powder = Material()
    powder.initialized = material.initialized
    powder.name = material.name + "Powder"
    powder.density = blend(material.density, densityScaling, 0.4 * TmLow, 0.9 * TmLow, sigmoid=True)
    powder.specificHeatCapacity = material.specificHeatCapacity
    powder.heatConductivity = blend(material.heatConductivity, conductivityScaling, 0.5 * TmLow, 1.0 * TmLow, sigmoid=True)
    powder.annealingTemperature = material.annealingTemperature
    powder.solidTemperature = material.solidTemperature
    powder.liquidTemperature = material.liquidTemperature
    powder.latentHeatOfFusion = material.latentHeatOfFusion
    powder.regularization = material.regularization
    powder.thermalExpansionCoefficient = material.thermalExpansionCoefficient
    powder.youngsModulus = temperatureFunction(youngsModulusScaling * material.youngsModulus( 20 )[0])
    powder.poissonRatio = material.poissonRatio
    powder.yieldStress = temperatureFunction(1e50)
    powder.hardening = temperatureFunction(0.0)
    powder.plasticModelSelector = material.plasticModelSelector
    
    powder.latentHeatOfFusion *= material.density(Tm)[0] / powder.density(Tm)[0]
    
    return powder


def makeAir(material=makeMaterial("IN625"), epsilon=1e-5):
    if not isinstance(epsilon, (int, float, bool)):
        raise ValueError("Invalid data type for epsilon")

    if not isinstance(material, Material):
        raise ValueError(f"Invalid data type for material ({type(material)}).")

    if not material.initialized:
        raise ValueError(f"Material is uninitialzied.")

    def extractAndScale(function, scaling):
        return temperatureFunction(scaling * function(20)[0])

    air = Material()
    air.initialized = True
    air.name = material.name + "Air"
    air.density = extractAndScale(material.density, epsilon)
    air.specificHeatCapacity = material.specificHeatCapacity
    air.heatConductivity = extractAndScale(material.heatConductivity, epsilon)
    air.annealingTemperature = 1e50
    air.solidTemperature = 1e50
    air.liquidTemperature = 1e50
    air.latentHeatOfFusion = 0.0
    air.regularization = 100
    air.thermalExpansionCoefficient = material.thermalExpansionCoefficient
    air.youngsModulus = extractAndScale(material.youngsModulus, epsilon)
    air.poissonRatio = material.poissonRatio
    air.yieldStress = temperatureFunction(1e50)
    air.hardening = temperatureFunction(0.0)
    air.plasticModelSelector = material.plasticModelSelector
    
    return air


def makeLinearElasticMaterial(material, temperature = 22 * units.C):
    if not isinstance(material, Material):
        raise ValueError(f"Invalid data type for material ({type(material)}).")

    linearmaterial = Material()
    linearmaterial.initialized = material.initialized
    linearmaterial.name = "linearElasticMaterial"
    linearmaterial.density = material.density
    linearmaterial.specificHeatCapacity = material.specificHeatCapacity
    linearmaterial.heatConductivity = material.heatConductivity
    linearmaterial.plasticModelSelector = 0.0
    linearmaterial.annealingTemperature = material.annealingTemperature
    linearmaterial.solidTemperature = material.solidTemperature
    linearmaterial.liquidTemperature = material.liquidTemperature
    linearmaterial.latentHeatOfFusion = material.latentHeatOfFusion
    linearmaterial.regularization = material.regularization
    linearmaterial.thermalExpansionCoefficient = temperatureFunction(linearmaterial.thermalExpansionCoefficient(temperature)[0])
    linearmaterial.youngsModulus = temperatureFunction(linearmaterial.youngsModulus(temperature)[0])
    linearmaterial.poissonRatio = temperatureFunction(linearmaterial.poissonRatio(temperature)[0])
    linearmaterial.yieldStress = 1e50
    linearmaterial.hardening = 0.0

    return linearmaterial


def convertBeamDiameter(value, source, target):
    if source.lower() == "d4sigma": D4Sigma = value
    elif source.lower() == "fwhm": D4Sigma = 4 * value / math.sqrt(8 * math.log(2))
    else: raise ValueError("Unknown source beam diameter type")
    if target.lower() == "d4sigma": return D4Sigma
    elif target.lower() == "fwhm": return D4Sigma / 4 * math.sqrt(8 * math.log(2))
    else: raise ValueError("Unknown target beam diameter type")
    

def temperatureBC(faceIndex, temperature):
    def process(thermalProblem, tstate):
        sliced = mlhp.sliceLast(process.function, tstate.time)
        return mlhp.integrateDirichletDofs(sliced, tstate.basis, [process.iface])

    process.function = mlhp.scalarField(4, temperature) if isinstance(temperature, float) else temperature
    process.iface = faceIndex

    return process


def dirichletBC(faceIndex, fieldIndex, value=0.0):
    def process(msetup, mstate):
        sliced = mlhp.sliceLast(process.function, mstate.time)
        return mlhp.integrateDirichletDofs(sliced, mstate.basis, [process.iface], ifield=process.ifield)

    process.function = mlhp.scalarField(4, value) if isinstance(value, float) else value
    process.iface = faceIndex
    process.ifield = fieldIndex

    return process


def _vtuConfig(degree, materialRefinement, writeEdges):
    resolution = [degree + (2 if degree > 1 else 0)] * 3
    topologies = mlhp.PostprocessTopologies.Volumes
    
    if writeEdges or (writeEdges == None and (degree != 1 or materialRefinement)):
        topologies = topologies | mlhp.PostprocessTopologies.Edges
        
    return resolution, topologies


def thermalVtuOutput(filebase, interval=1, *, materialRefinement=True, clipAbove=True, writemode=vtudefault, writeEdges=None, functions=[]):
    def process(thermalProblem, tstate):
        path, vtuInterval, material, clip, mode, edges, scalarFunctions = process.parms
        if tstate.index % vtuInterval == 0:
            processors = [mlhp.functionProcessor(mlhp.sliceLast(create([tstate.time, tstate.time]), tstate.time), 
                "VolumeSource_" + str(i)) for i, create in enumerate(thermalProblem.volumeSources)]
            processors += [mlhp.solutionProcessor(3, tstate.dofs, "Temperature")]
            sliceF = lambda f: mlhp.sliceLast(f, tstate.time) if isinstance(f, mlhp.ScalarFunction4D) else f
            processors += [mlhp.functionProcessor(sliceF(f), name) for f, name in scalarFunctions]
            fileindex = tstate.index // vtuInterval
            vtuparms = _vtuConfig(thermalProblem.degree, material, edges)
            postmesh = clippedPostprocessingMesh(tstate.history.topSurface, 
                *vtuparms) if clip else mlhp.gridCellMesh(*vtuparms)
            writer = mlhp.PVtuOutput(filename=path + "_" + str(fileindex), writemode=mode)
            if material:
                processors.append(mlhp.cellDataProcessor(3, DoubleVector(tstate.basis.nelements(), 0.0), "MaterialState"))
                postmesh = materialRefinedPostprocessingGrid(postmesh, tstate.mesh, tstate.history.grid())
                writer = addThermalHistoryOutput(writer.meshWriter(), tstate.history, "MaterialState")
            mlhp.basisOutput(tstate.basis, postmesh, writer, processors)

    process.parms = (filebase, interval, materialRefinement, clipAbove, writemode, writeEdges, functions)
    return process


def thermomechanicalVtuOutput(filebase, interval=1, *, materialRefinement=True, clipAbove=True, l2project=True,
                              writemode=vtudefault, writeEdges=None, temperature=True, functions=[]):
    def process(problem, state):
        if isinstance(problem, ThermalProblem):
            process.tsetup = problem
            process.tstate = state
            return
        
        tsetup, tstate, msetup, mstate = process.tsetup, process.tstate, problem, state
        path, vtuInterval, material, clip, mode, edges, scalarFunctions = process.parms
        
        if not isinstance(msetup, MechanicalProblem):
            raise ValueError(f"Unknown problem type: {type(msetup)}")
        
        if tsetup is None:
            raise ValueError(f"No thermal time step found. Did you forget to register thermomechanical "
                             f"postprocessor also to the thermal problem?")
        
        if abs(mstate.time - tstate.time) > 1e-6 * units.ms:
            raise ValueError(f"Time stamps of the mechanical and stored thermal states are different.")
        
        if mstate.index % vtuInterval == 0:
            processors = [mlhp.functionProcessor(mlhp.sliceLast(create([mstate.time, mstate.time]), mstate.time), 
                "VolumeSource_" + str(i)) for i, create in enumerate(tsetup.volumeSources)]
            temperature, materialAdapter = thermalEvaluator(tstate), iternalMaterialAdapter(tstate.history, msetup.simulation.materials)
            
            history = mstate.history
            if l2project:
                materialIndicator = materialEvaluator(tstate)
                thresholdTemperature = meltingTemperature(tsetup.simulation.materials, 0.0)
                spatialWeight = historyProjectionWeight(temperature, materialIndicator, thresholdTemperature, 1e-2) 
                thermalEvaluator2 = internalThermalStrainEvaluator(tstate.basis, tstate.basis, tstate.dofs, tstate.dofs,
                                                                   tstate.history, tsetup.simulation.materials,
                                                                   tsetup.simulation.ambientTemperature)
                quadratureOrder = msetup.degree + msetup.offsetQuadrature
                history = l2ProjectHistory(history, mstate.mesh, quadratureOrder, msetup.degree, spatialWeight)
                history = j2HistoryUpdate(history, thermalEvaluator2)
            
            quantities = ["Displacement", "Temperature", "ElasticStrain", "EffectivePlasticStrain", "Stress", "VonMisesStress"]
            processors += [mechanicalPostprocessor(quantities, mstate.dofs, history, temperature, materialAdapter)]
            #processors += [plasticityProcessor(mstate.history)]
            sliceF = lambda f: mlhp.sliceLast(f, mstate.time) if isinstance(f, mlhp.ScalarFunction4D) else f
            processors += [mlhp.functionProcessor(sliceF(f), name) for f, name in scalarFunctions]
            fileindex = mstate.index // vtuInterval
            vtuparms = _vtuConfig(msetup.degree, material, edges)
            postmesh = clippedPostprocessingMesh(tstate.history.topSurface, 
                *vtuparms) if clip else mlhp.gridCellMesh(*vtuparms)
            writer = mlhp.PVtuOutput(filename=path + "_" + str(fileindex), writemode=mode)
            if material:
                processors.append(mlhp.cellDataProcessor(3, DoubleVector(mstate.basis.nelements(), 0.0), "MaterialState"))
                postmesh = materialRefinedPostprocessingGrid(postmesh, mstate.mesh, tstate.history.grid())
                writer = addThermalHistoryOutput(writer.meshWriter(), tstate.history, "MaterialState")
            mlhp.basisOutput(mstate.basis, postmesh, writer, processors)
    
    process.tsetup = None
    process.tstate = None
    process.parms = (filebase, interval, materialRefinement, clipAbove, writemode, writeEdges, functions)
    return process

def materialVtuOutput(filebase, interval=1, *, clipAbove=True, writemode=vtudefault):
    def process(thermalProblem, tstate):
        if tstate.index % process.interval == 0:
            processors = [mlhp.cellDataProcessor(3, tstate.history.data(), "MaterialState")]
            vtuparms = ([1] * 3, mlhp.PostprocessTopologies.Volumes)
            postmesh = clippedPostprocessingMesh(tstate.history.topSurface, 
                *vtuparms) if process.clipAbove else mlhp.gridCellMesh(*vtuparms)
            writer = mlhp.PVtuOutput(filename=process.path + "_material_" + str(tstate.index // process.interval),
                writemode=process.writeMode)
            mlhp.meshOutput(tstate.history.grid(), postmesh, writer, processors)

    process.path = filebase
    process.interval = interval
    process.clipAbove = clipAbove
    process.writeMode = writemode

    return process


def thermalEvaluator(tstate, *, difforder=0, icomponent=0):
    return mlhp.scalarEvaluator(tstate.basis, tstate.dofs, difforder=difforder, icomponent=icomponent)


def materialEvaluator(tstate):
    return internalMaterialEvaluator(tstate.history, tstate.mesh.baseGrid().boundingBox())
    

def meltingTemperature(materials, phi=0.5):
    if "structure" not in materials:
        raise ValueError("Structure material is not present.")
    return (1.0 - phi) * materials["structure"].solidTemperature + phi * materials["structure"].liquidTemperature


def meltPoolContourOutput(output, interval=1, resolution=None, writemode=vtudefault, recoverMeshBoundaries=False):
    def process(thermalProblem, tstate):
        if tstate.index % process.interval == 0:
            threshold = meltingTemperature(thermalProblem.simulation.materials, 0.5)
            function = mlhp.implicitThreshold(thermalEvaluator(tstate), threshold)
            res = mlhp.degreeOffsetResolution(tstate.basis, offset=2) if process.resolution is None else process.resolution
            postmesh = mlhp.boundaryCellMesh(function, recoverMeshBoundaries=process.recoverMeshBoundaries, resolution=res)
            writer = mlhp.DataAccumulator()
            if isinstance(process.output, str):
                writer = mlhp.PVtuOutput(filename=process.output + "_meltpool_" + str(tstate.index // process.interval),
                    writemode=writemode)
            mlhp.meshOutput(tstate.mesh, postmesh, writer, [])
            if not isinstance(process.output, str):
                process.output(writer.mesh())

    process.output = output
    process.interval = interval
    process.resolution = resolution
    process.writemode = writemode
    process.recoverMeshBoundaries = recoverMeshBoundaries

    return process


def meltPoolBoundsPrinter(interval=1, resolution=None):
    def meltPoolBoundsCallback(mesh):
        points = mesh.points()
        bounds = [[1e50, 1e50, 1e50], [-1e50, -1e50, -1e50]]
        for ipoint in range(int(len(points) / 3)):
            for icoord in range(3):
                bounds[0][icoord] = min(bounds[0][icoord], points[3 * ipoint + icoord])
                bounds[1][icoord] = max(bounds[1][icoord], points[3 * ipoint + icoord])
        print(f"    melt pool bounds: {[max(u - l, 0.0) for l, u in zip(*bounds)]}", flush=True)

    return meltPoolContourOutput(meltPoolBoundsCallback, interval, resolution)


def stateInfoOutput(filename, ilayer=0):
    dirname = os.path.dirname(filename)
    if len(dirname) and not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(filename, "w") as file:
        print(f"ilayer; istep; simtime; walltime; nelements; ndof; nmatcells, topsurface", file=file)

    def process(problem, state):
        try:
            with open(process.filename, "a") as file:
                t = time.time() - process.time0
                print(f"{process.ilayer}; {state.index}; {state.time}; {t}; {state.basis.nelements()}; "
                      f"{state.basis.ndof()}; {state.history.grid().ncells()}; {state.history.topSurface}", file=file)
        except IOError:
            print(f"ERROR. Could not open file \"{filename}\".")

    process.filename = filename
    process.ilayer = ilayer
    process.time0 = time.time()

    return process


def createMesh(min, max, elementSize, layerThickness=0.0, zfactor=1.0):
    return mlhp.makeGrid(createMeshTicks(min, max, elementSize, layerThickness, zfactor))


def _filterRefinementPoints(refinementPoints, cutoffDelay):
    if cutoffDelay is not None:
        if cutoffDelay <= refinementPoints[0].delay:
            raise ValueError("Refinement cutoff delay too short.")
            
        for i in range(1, len(refinementPoints)):
            point0, point1 = refinementPoints[i - 1], refinementPoints[i]
            
            if point1.delay > cutoffDelay:
                t = (cutoffDelay - point0.delay) / (point1.delay - point0.delay)
                
                point1.delay = cutoffDelay
                point1.sigma = (1 - t) * point0.sigma + t * point1.sigma
                point1.depth = (1 - t) * point0.depth + t * point1.depth
                point1.zfactor = (1 - t) * point0.zfactor + t * point1.zfactor

                refinementPoints = refinementPoints[:i + 1]
                break
                
    return refinementPoints


def laserRefinement(laserTrack, laserSigma, laserSpeed, depth, *, cutoffDelay=None, nseedpoints=None):
    refinementPoints = [# delay, sigma (refinement width), depth (maximum refinement depth), zfactor
        LaserRefinementPoint(0.00 * units.ms, 4 * laserSigma + 0.01 * units.mm, depth + 0.4, 0.5),
        LaserRefinementPoint(0.60 * units.ms, 4 * laserSigma + 0.07 * units.mm, depth - 0.5, 0.5),
        LaserRefinementPoint(6.00 * units.ms, 4 * laserSigma + 0.40 * units.mm, depth - 1.5, 0.8),
        LaserRefinementPoint(30.0 * units.ms, 4 * laserSigma + 0.90 * units.mm, depth - 2.5, 1.0),
        LaserRefinementPoint(0.10 * units.s, 4 * laserSigma + 1.10 * units.mm, depth - 3.0, 1.0)]
    
    def refinement(problem, state0, state1):
        track = refinement.laserTrack 
        track = track if refinement.cutoffDelay is None else filterTrack(track, (state0.time, state1.time)) 
        nseedpoints = refinement.nseedpoints if refinement.nseedpoints is not None else problem.degree + 2
        return laserTrackPointRefinement(track, refinement.refinementPoints, state1.time, nseedpoints)
    
    refinement.laserTrack = laserTrack
    refinement.cutoffDelay = cutoffDelay
    refinement.nseedpoints = nseedpoints
    refinement.refinementPoints = _filterRefinementPoints(refinementPoints, cutoffDelay)
    
    return refinement


def laserIntensityRefinement(depth, *, sigma=80*units.um, threshold=200*units.W/units.mm**2, nseedpoints=None):
    def refinement(setup, state0, state1):
        source = mlhp.sliceLast(combineSources(setup.volumeSources + setup.surfaceSources, state1.time), state1.time)
        levelFunction = internalSourceIntensityLevelFunction(source, state1.history.topSurface, 
            refinement.threshold, refinement.sigma, refinement.depth)
        nseedpoints_ = setup.degree + 3 if refinement.nseedpoints is None else refinement.nseedpoints 
        return mlhp.refineWithLevelFunction(levelFunction, nseedpoints_)
    refinement.depth = depth
    refinement.sigma = sigma
    refinement.threshold = threshold
    refinement.nseedpoints = nseedpoints
    return refinement


def adaptiveRefinement(depth, *, threshold=20, coarsen=1, refineThreshold=None):
    def refinement(setup, state0, state1):
        if state0.basis.nfields() != 1:
            raise ValueError("Adaptive refinement only implemented for thermal analysis")
        error = integrateError(setup.simulation.materials, state0.basis, state0.dofs, state0.history).tolist()
        levels = state0.mesh.refinementLevels()
        error = [e * refinement.levelFactor**(refinement.depth - l) for l, e in zip(levels, error)]
        diff = [-1 if e < refinement.coarsenThreshold else (1 if e > refinement.refineThreshold else 0) for e in error]
        return mlhp.refineAdaptively(state0.mesh, diff, refinement.depth)
        
    refinement.depth = depth
    refinement.levelFactor = 3 / coarsen
    refinement.coarsenThreshold = threshold
    refinement.refineThreshold = refinement.levelFactor * 5 * threshold if refineThreshold is None else refineThreshold
    
    return refinement


def powderLayerRefinement(depth, sigma=40*units.um, *, nseedpoints=None):
    def refinement(problem, state0, state1):
        nseedpoints_ = refinement.nseedpoints if refinement.nseedpoints is not None else problem.degree + 2
        levelfunction = f"{refinement.depth} * exp(-({state1.history.topSurface} - z)**2 / {2 * refinement.sigma**2})"
        return mlhp.refineWithLevelFunction(mlhp.scalarField(ndim=3, func=levelfunction), nseedpoints_)
        
    refinement.depth = depth
    refinement.sigma = sigma
    refinement.nseedpoints = nseedpoints
    
    return refinement


class ProcessSimulation:
    def __init__(self, grid, material=None, layerThickness=0.0, ambientTemperature=25.0 * units.C):
        self.materials = { }
        if material is not None:
            self.materials["air"] = makeAir(material=material)
            self.materials["powder"] = makePowder(material)
            self.materials["baseplate"] = material
            self.materials["structure"] = material
        self.bounds = grid.boundingBox()
        self.layerThickness = layerThickness
        self.ambientTemperature = ambientTemperature

    def setMaterials(self, **kwargs):
        for key, value in kwargs.items():
            if key != "air" and key != "powder" and key != "baseplate" and key != "structure":
                raise ValueError("Invalid material \"{key}\".")
            self.materials[key] = value


class ThermalProblem:
    def __init__(self, simulation, degree=1, theta=1):
        self.dirichlet = []
        self.postprocess = []
        self.degree = degree
        self.simulation = simulation
        self.theta = theta
        self.volumeSources = []
        self.surfaceSources = []
        self.refinements = []
        self.nfields = 1
        self.convectionRadiationBC = None

    def addPostprocessor(self, postprocessor):
        self.postprocess.append(postprocessor)

    def addDirichletBC(self, condition):
        self.dirichlet.append(condition)

    def setConvectionRadiationBC(self,
                                 emissivity=0.1,
                                 convectionCoefficient=1e-5 * units.W / units.mm ** 2 / units.C):
        self.convectionRadiationBC = emissivity, convectionCoefficient
        
    def addSource(self, source):
        if source[0] == "VolumeSource":
            self.volumeSources.append(source[1])
        elif source[0] == "SurfaceSource":
            self.surfaceSources.append(source[1])
        else:
            raise ValueError("Unknown source type")

    def clearSources(self):
        self.volumeSources.clear()
        self.surfaceSources.clear()

    def addRefinement(self, refinement):
        self.refinements.append(refinement)

    def clearRefinements(self):
        self.refinements = []


@dataclass
class State:
    time: float
    index: int
    mesh: None
    basis: None
    dofs: None
    history: None


def makeThermalState(thermalProblem, mesh, part=None, srefinement=0, powderHeight=0.0, time=0.0, index=0, postprocess=True):
    if part is None:
        domain = mlhp.implicitHalfspace([0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
    elif isinstance(part, (float, int)):
        domain = mlhp.implicitHalfspace([0.0, 0.0, part], [0.0, 0.0, 1.0])
    elif isinstance(part, mlhp.ImplicitFunction3D):
        domain = part
    else:
        raise ValueError("Invalid data type for part.")

    history = initializeThermalHistory(mesh, domain, srefinement, powderHeight, nseedpoints=4)
    refinedMesh = mlhp.makeRefinedGrid(mesh)
    basis = mlhp.makeHpTrunkSpace(refinedMesh, thermalProblem.degree, nfields=thermalProblem.nfields)
    dofs = mlhp.projectOnto(basis, mlhp.scalarField(3, thermalProblem.simulation.ambientTemperature))
    state = State(time, index, refinedMesh, basis, dofs, history)
    dirichletDofs = mlhp.combineDirichletDofs([f(thermalProblem, state) for f in thermalProblem.dirichlet])
    state.dofs = mlhp.inflateDofs(mlhp.split(state.dofs, dirichletDofs[0])[1], dirichletDofs)
    
    if postprocess:
        for pp in thermalProblem.postprocess:
            pp(thermalProblem, state)
    
    return state


def combineSources(sourceCreators, timeBounds):
    bounds = (timeBounds, timeBounds) if isinstance(timeBounds, (float, int)) else timeBounds
    return internalCombineSources([create(bounds) for create in sourceCreators])


def _chunksizeThermal(tstate: State):
    return max(min(int(tstate.basis.nelements() / (4 * mlhp.config.numThreads)), 29), 1)


def _linearFluxIntegrator(thermalProblem: ThermalProblem):
    if len(thermalProblem.surfaceSources):
        def integrate(tstate: State, F: mlhp.DoubleVector, dirichletDofs):
            quadrature = topSurfaceBoundaryQuadrature(tstate.history.topSurface, mlhp.relativeQuadratureOrder(3, 2))
            surfaceSource = mlhp.sliceLast(combineSources(integrate.tsetup.surfaceSources, tstate.time), tstate.time)
            integrand = mlhp.neumannIntegrand(surfaceSource)
            chunks = _chunksizeThermal(tstate)
            mlhp.integrateOnSurface(tstate.basis, integrand, [F], quadrature, dirichletDofs=dirichletDofs, chunksize=chunks)
        
        integrate.tsetup = thermalProblem
    
        return integrate

    else:
        return lambda *args: None


def _nonlinearFluxIntegrator(thermalProblem: ThermalProblem):
    if thermalProblem.convectionRadiationBC:
        def integrate(tstate: State, K: mlhp.AbsSparseMatrix, F: mlhp.DoubleVector, dirichletDofs):
            quadrature = topSurfaceBoundaryQuadrature(tstate.history.topSurface, mlhp.relativeQuadratureOrder(3, 1))
            emissivity, convectionCoefficient = thermalProblem.convectionRadiationBC
            boltzmannConstant = 5.670374419e-8 * units.W / (units.m**2 * units.C**4)
            integrand = makeConvectionRadiationIntegrand(tstate.dofs, emissivity,
                convectionCoefficient, integrate.tsetup.simulation.ambientTemperature, boltzmannConstant)
            chunks = _chunksizeThermal(tstate)
            mlhp.integrateOnSurface(tstate.basis, integrand, [K, F], quadrature, dirichletDofs=dirichletDofs, chunksize=chunks)
        
        integrate.tsetup = thermalProblem
    
        return integrate

    else:
        return lambda *args: None


def _quadratureUnionWithHistory(historyGrid, topSurface, *, quadrature=None, maxdepth=None):
    if quadrature is None:
        topPartitioner = topSurfacePartitioner(topSurface)
    else:
        topPartitioner = topSurfacePartitioner(topSurface, quadrature)
        
    if maxdepth is not None:
        return mlhp.meshProjectionQuadrature(historyGrid, maxdepth=maxdepth, quadrature=topPartitioner)
    else:
        return mlhp.meshProjectionQuadrature(historyGrid, quadrature=topPartitioner)


def thermalTimeStep(thermalProblem, tstate0, deltaT, *, rtol, atol, maxiter, lsolver_rtol, lsolver_atol, qoffset):
    print(f"    Thermal problem: ", end='', flush=True)
    tstate1 = State(time=tstate0.time + deltaT, index=tstate0.index + 1, mesh=mlhp.makeRefinedGrid(
        tstate0.mesh.baseGrid()), basis=None, dofs=None, history=tstate0.history)

    if len(thermalProblem.refinements):
        refinements = [r(thermalProblem, tstate0, tstate1) for r in thermalProblem.refinements]
        refineConstrained(tstate1.mesh, mlhp.refinementOr(refinements), tstate0.history.topSurface)

    print(f"{tstate1.mesh.ncells()} elements", end='', flush=True)
    tstate1.basis = mlhp.makeHpTrunkSpace(tstate1.mesh, thermalProblem.degree)

    print(f", {tstate1.basis.ndof()} dofs, {tstate0.history.grid().ncells()} material cells", flush=True)

    # Gather dirichlet dofs
    dirichletDofs = mlhp.combineDirichletDofs([f(thermalProblem, tstate1) for f in thermalProblem.dirichlet])

    # Project solution from previous state
    K = mlhp.allocateSparseMatrix(tstate1.basis)
    F = mlhp.allocateRhsVector(K)

    l2Integrand = mlhp.l2BasisProjectionIntegrand(3, tstate0.dofs)
    chunksize = _chunksizeThermal(tstate1)
    
    # Should probably weight air (if artificially added) and powder (although not as bad) according to their density
    quadrature = topSurfacePartitioner(tstate0.history.topSurface)
    order = mlhp.relativeQuadratureOrder(3, qoffset)

    mlhp.integrateOnDomain(tstate0.basis, tstate1.basis, l2Integrand, [K, F], quadrature=quadrature, chunksize=chunksize, orderDeterminor=order)

    #projectedDofs0 = mlhp.makeCGSolver(rtol=0.01 * min(rtol, lsolver_rtol), atol=0.01*atol)
    tmpM = mlhp.DoubleVector(1 * tstate1.basis.ndof())
    tmpS = mlhp.DoubleVector(7 * tstate1.basis.ndof())
    M = diagonalPreconditioner(K, target=tmpM)
    
    # Todo: Extract better initial guess from previous solution (than just taking zero)
    projectedDofs0 = mlhp.cg(K, F, rtol=min(1e-8, 0.01 * min(rtol, lsolver_rtol)), M = M, tmp=tmpS)
    tstate1.dofs = projectedDofs0.copy()

    # Prepare nonlinear iterations
    if len(dirichletDofs[0]):
        del K
        K = mlhp.allocateSparseMatrix(tstate1.basis, dirichletDofs[0])
    F.resize(K.shape[0])
    F0 = mlhp.allocateRhsVector(K)
    tmpT = mlhp.DoubleVector(F0.size)

    volumeSource = combineSources(thermalProblem.volumeSources, (tstate0.time, tstate1.time))
    integrateLinearFlux = _linearFluxIntegrator(thermalProblem)
    integrateNonlinearFlux = _nonlinearFluxIntegrator(thermalProblem)

    projectionIntegrand = makeThermalInitializationIntegrand(thermalProblem.simulation.materials, volumeSource,
        tstate0.history, tstate0.dofs, tstate0.time, tstate1.time - tstate0.time, thermalProblem.theta)

    mlhp.integrateOnDomain(
        tstate0.basis, tstate1.basis, projectionIntegrand, [F0], 
        dirichletDofs=dirichletDofs, chunksize=chunksize, orderDeterminor=order)

    integrateLinearFlux(tstate1, F0, dirichletDofs)
        
    norm0, convergence = 0.0, False
    print("    || R || --> ", end="", flush=True)

    # Newton-Raphson iterations
    for i in range(maxiter):
        mlhp.copy(F0, F)
        mlhp.fill(K, 0.0)

        dirichletIncrement = computeDirichletIncrement(dirichletDofs, tstate1.dofs, -1.0)

        domainIntegrand = makeTimeSteppingThermalIntegrand(thermalProblem.simulation.materials, tstate1.history,
            projectedDofs0, tstate1.dofs, tstate1.time - tstate0.time, thermalProblem.theta)

        quadrature = _quadratureUnionWithHistory(tstate1.history.grid(), tstate1.history.topSurface, maxdepth=2)

        mlhp.integrateOnDomain(
            tstate1.basis, domainIntegrand, [K, F], quadrature=quadrature,
            dirichletDofs=dirichletIncrement, orderDeterminor=order, chunksize=chunksize)

        integrateNonlinearFlux(tstate1, K, F, dirichletIncrement)
    
        norm1 = mlhp.norm(F)
        norm0 = norm1 if i == 0 else norm0

        print(f"{norm1:.2e} ", end="", flush=True)
        
        # We should think of weighting the residual with the refinement level
        # since rtol = 1e-6 was high enough to give complete nonsense on fine
        # elements when combined with a high tolerance for the linear solver        
        if norm1 < max(rtol * norm0, atol):
            convergence = True
            break
            
        if norm1 > 1e3 * norm0:
            convergence = False
            break
                
        # Linear solve for internal dofs
        M = diagonalPreconditioner(K, target=tmpM)
        mlhp.fill(tmpT, 0.0)
        internal = mlhp.bicgstab(K, F, x0=tmpT, rtol=lsolver_rtol, atol=lsolver_atol, M=M, tmp=tmpS)
        
        # Expand if we have dirichlet dofs and update solution
        dx = mlhp.inflateDofs(internal, dirichletIncrement) if len(dirichletDofs[0]) else internal

        mlhp.add(tstate1.dofs, dx, factor=-1.0, out=tstate1.dofs)
        
        if (i + 1) % 6 == 0:
            print("\n                ", end="", flush=True)

    if convergence:
        tstate1.history = updateHistory(tstate0.history, tstate1.basis, tstate1.dofs,
            meltingTemperature(thermalProblem.simulation.materials, phi=0.5), thermalProblem.degree)

    print("", flush=True)

    return tstate1, convergence


def addNewPowderLayerThermal(thermalProblem, tstate0, deltaT):
    newPowderHeight=tstate0.history.topSurface + thermalProblem.simulation.layerThickness
    history1 = initializeNewLayerHistory(history=tstate0.history, newTopSurface=newPowderHeight)

    tstate1 = State(time=tstate0.time + deltaT, index=tstate0.index + 1, mesh=mlhp.makeRefinedGrid(
        tstate0.mesh.baseGrid()), basis=None, dofs=None, history=history1)

    if len(thermalProblem.refinements):
        refinements = [r(thermalProblem, tstate0, tstate1) for r in thermalProblem.refinements]
        refineConstrained(tstate1.mesh, mlhp.refinementOr(refinements), tstate0.history.topSurface)

    tstate1.basis = mlhp.makeHpTrunkSpace(tstate1.mesh, thermalProblem.degree)

    print(f"    Thermal problem: {tstate1.basis.nelements()} elements, {tstate1.basis.ndof()} dofs", flush=True)

    # Project solution from previous state
    K = mlhp.allocateSparseMatrix(tstate1.basis)
    F = mlhp.allocateRhsVector(K)

    projectionIntegrand = makeEnergyConsistentProjectionIntegrand(thermalProblem.simulation.materials, tstate0.history,
        tstate1.history, tstate0.dofs, thermalProblem.simulation.ambientTemperature, deltaT)

    mlhp.integrateOnDomain(tstate0.basis, tstate1.basis, projectionIntegrand, [K, F])

    tstate1.dofs = mlhp.makeCGSolver(rtol=1e-10)(K, F)

    for pp in thermalProblem.postprocess:
        pp(thermalProblem, tstate1)
        
    return tstate1


def computeThermalProblem(thermalProblem, tstate0, deltaT, duration, *, ilayer=None, rtol=1e-8, atol=1e-6, maxiter=20, lsolver_rtol=0.05):
    nsteps = int(math.ceil(duration / deltaT))
    realDT = duration / nsteps
    
    for i in range(nsteps):
        if ilayer is not None:
            print(f"Layer {ilayer + 1}, ", end="")
        print(f"Time step {i + 1} / {nsteps} ({tstate0.index + 1} in total)", flush=True)
        print(f"    Time: {tstate0.time:.8g} s, time step size: {realDT:.8g} s", flush=True)

        istepI, nstepsI, dtI, index0, depth = 0, 1, realDT, tstate0.index, 0

        while istepI < nstepsI:
            lrtol, latol, qoffset = (lsolver_rtol, 0.8 * atol, 1) if depth == 0 else (min(lsolver_rtol, 1e-8), 1e-2 * atol, 2)
            tstate1, convergence = thermalTimeStep(
                thermalProblem, tstate0, dtI, rtol=rtol, atol=atol, qoffset=qoffset, 
                maxiter=maxiter, lsolver_rtol=lrtol, lsolver_atol=latol)

            if convergence:
                tstate0, istepI = tstate1, istepI + 1

                if istepI % 2 == 0:
                    istepI, nstepsI, dtI, depth = istepI // 2, nstepsI // 2, dtI * 2, depth - 1
                    print(f"    Thermal Newton iterations converged, increasing time step size to {dtI:.6g}", flush=True)

            else:
                if depth == 20:
                    raise RuntimeError(f"Thermal iterations not converged after {depth} refinements.")
                    
                istepI, nstepsI, dtI, depth = istepI * 2, nstepsI * 2, dtI / 2, depth + 1
                print(f"    Thermal Newton iterations did not converge. Reducing time step to {dtI:.6g}", flush=True)

        tstate1.index = index0 + 1

        for pp in thermalProblem.postprocess:
            pp(thermalProblem, tstate1)

    return tstate1 if nsteps > 0 else tstate0


def computeSteadyStateThermal(thermalProblem, tstate0, laserVelocity, *, rtol=1e-8, atol=1e-8, maxiter=40, treedepth=3, treeseeds=None, qoffset=1):
    print(f"Computing steady-state problem ", flush=True, end='')
    
    tstate1 = State(time=tstate0.time, index=tstate0.index, mesh=mlhp.makeRefinedGrid(
        tstate0.mesh.baseGrid()), basis=None, dofs=None, history=tstate0.history)

    if len(thermalProblem.refinements):
        refinements = [r(thermalProblem, tstate0, tstate1) for r in thermalProblem.refinements]
        refineConstrained(tstate1.mesh, mlhp.refinementOr(refinements), tstate0.history.topSurface)

    tstate1.basis = mlhp.makeHpTrunkSpace(tstate1.mesh, thermalProblem.degree)
    
    print(f"({tstate1.basis.nelements()} elements, {tstate1.basis.ndof()} dofs)", flush=True)
        
    # Gather dirichlet dofs
    dirichletDofs = mlhp.combineDirichletDofs([f(thermalProblem, tstate1) for f in thermalProblem.dirichlet])

    # Prepare for nonlinear iterations
    K = mlhp.allocateSparseMatrix(tstate1.basis, dirichletDofs[0])
    F = mlhp.allocateRhsVector(K)
    tstate1.dofs = mlhp.DoubleVector(tstate1.basis.ndof(), 0.0)

    volumeSource = mlhp.sliceLast(combineSources(thermalProblem.volumeSources, tstate1.time), tstate1.time)
    integrateLinearFlux = _linearFluxIntegrator(thermalProblem)
    integrateNonlinearFlux = _nonlinearFluxIntegrator(thermalProblem)

    if thermalProblem.convectionRadiationBC is not None:
        raise Warning("Convection/radiation boundary condition not available for steady state analysis.")

    norm0, convergence = 1.0, False
    print("    || R || --> ", end="", flush=True)

    for i in range(maxiter):
        mlhp.fill(F, 0.0)
        mlhp.fill(K, 0.0)

        dirichletIncrement = computeDirichletIncrement(dirichletDofs, tstate1.dofs, -1)

        domainIntegrand = makeSteadyStateThermalIntegrand(thermalProblem.simulation.materials, volumeSource,
                                                          tstate1.history, tstate1.dofs, laserVelocity)

        # Create quadrature towards melt pool boundary
        Tm = meltingTemperature(thermalProblem.simulation.materials, phi=0.5)
        MP = mlhp.implicitFunction(3, f"f0(x, y, z) >= {Tm}", fields=[thermalEvaluator(tstate1)])
        nseedpoints = thermalProblem.degree + 3 if treeseeds is None else treeseeds
        quadrature = mlhp.spaceTreeQuadrature(MP, depth=treedepth, nseedpoints=nseedpoints)
        
        # Combine with quadrature on history grid and quadrature split along top surface
        quadrature = _quadratureUnionWithHistory(tstate1.history.grid(), tstate1.history.topSurface, quadrature=quadrature)
        orderDeterminor = mlhp.relativeQuadratureOrder(3, qoffset)

        mlhp.integrateOnDomain(tstate1.basis, domainIntegrand, [K, F], quadrature=quadrature,
            dirichletDofs=dirichletIncrement, orderDeterminor=orderDeterminor)

        integrateLinearFlux(tstate1, F, dirichletIncrement)
        integrateNonlinearFlux(tstate1, K, F, dirichletIncrement)
        
        norm1 = mlhp.norm(F)
        norm0 = norm1 if i == 0 else norm0

        print(f"{norm1:.2e} ", end="", flush=True)

        if norm1 < max(rtol * norm0, atol):
            convergence = True
            break
            
        if norm1 > 1e3 * norm0:
            break
            
        P = mlhp.additiveSchwarzPreconditioner(K, tstate1.basis, dirichletIncrement[0])
        dx = mlhp.bicgstab(K, F, M=P, maxiter=10000, rtol=1e-8)
        dx = mlhp.inflateDofs(dx, dirichletIncrement)

        tstate1.dofs = mlhp.add(tstate1.dofs, dx, -1.0)

        if (i + 1) % 6 == 0:
            print("\n                ", end="", flush=True)
    
    print("", flush=True)

    del K, F, dirichletDofs

    if not convergence:
        print(f"Steady-state thermal Newton iterations did not converge.")
        
    for pp in thermalProblem.postprocess:
        pp(thermalProblem, tstate1)
    
    return tstate1

class MechanicalProblem:
    def __init__(self, simulation, degree=1, quadratureOrderOffset=1):
        self.dirichlet = []
        self.degree = degree
        self.simulation = simulation
        self.postprocess = []
        self.refinements = []
        self.nfields = 3
        self.offsetQuadrature = quadratureOrderOffset
        self.materials = simulation.materials

    def addPostprocessor(self, postprocessor):
        self.postprocess.append(postprocessor)

    def addDirichletBC(self, condition):
        self.dirichlet.append(condition)

    def clearRefinements(self):
            self.refinements.clear()

    def addRefinement(self, refinement):
        self.refinements.append(refinement)

def makeMechanicalState(msetup, mesh, *, part=None, time=0.0, index=0, powderHeight=0.0, postprocess=True):
    domain = part if part is not None else mlhp.implicitHalfspace([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
    refinedInitialMesh = mlhp.makeRefinedGrid(mesh)
    basis = mlhp.makeHpTrunkSpace(refinedInitialMesh, msetup.degree, nfields=msetup.nfields)
    history = piecewiseConstantHistory(refinedInitialMesh, msetup.degree + msetup.offsetQuadrature, powderHeight)
    dofs = mlhp.projectOnto(basis, mlhp.vectorField(3, [0.0] * 3))
    state = State(index=index, time=time, basis=basis, mesh=refinedInitialMesh, dofs=dofs, history=history)
    refinedMesh = mlhp.makeRefinedGrid(mesh)
    if len(msetup.refinements):
        refinements = [r(msetup, state, state) for r in msetup.refinements]
        refineConstrained(refinedMesh, mlhp.refinementOr(refinements), powderHeight)
    basis = mlhp.makeHpTrunkSpace(refinedMesh, msetup.degree, nfields=msetup.nfields)
    history = piecewiseConstantHistory(refinedMesh, msetup.degree + msetup.offsetQuadrature, powderHeight)
    dofs = mlhp.projectOnto(basis, mlhp.vectorField(3, [0.0] * 3))
    state = State(index=index, time=time, basis=basis, mesh=refinedMesh, dofs=dofs, history=history)
    dirichletDofs = mlhp.combineDirichletDofs([f(msetup, state) for f in msetup.dirichlet])
    state.dofs = mlhp.inflateDofs(mlhp.split(state.dofs, dirichletDofs[0])[1], dirichletDofs)
     
    if postprocess:
        for pp in msetup.postprocess:
            pp(msetup, state)
        
    return state

def CGSolver():
    def solve(K, F, i, atol, rtol, norm0, norm1):
        lsolver_rtol=min(1e-2, max(10**(-2**i), 1e-14))     # Start with 0.01, but then reduce exponentially until 1e-14
        lsolver_atol=0.8*max(min(rtol, 1e-0) * norm0, atol) # Stop at atol or rtol * norm0, but for large rtol use 1e-5
        return mlhp.makeCGSolver(rtol=lsolver_rtol, atol=lsolver_atol)(K, F)
    # -1 -> cannot do symetric, 0 -> prefers unsymmetric, 1 -> prefers symmetric, 2 -> can only do symmetric
    solve.symmetric = 0
    return solve

def mechanicalTimeStep(msetup, mstate0, tstate1, thermalStrainEvaluator, *, maxiter, rtol, atol, solver, useL2):
    if mstate0.time > tstate1.time:
        raise ValueError("Previous mechanical time before next thermal time")

    mstate1 = State(time=tstate1.time, index=mstate0.index + 1, mesh=mlhp.makeRefinedGrid(mstate0.mesh.baseGrid()),
        basis=None, dofs=None, history=mstate0.history)

    if len(msetup.refinements):
        refinements = [r(msetup, mstate0, mstate1) for r in msetup.refinements]
        refineConstrained(mstate1.mesh, mlhp.refinementOr(refinements), tstate1.history.topSurface)
    
    newHistoryGrid = mlhp.makeRefinedGrid(mstate0.mesh.baseGrid())
    refine1 = mlhp.refineAdaptively(mstate0.history.grid(), [0] * mstate0.history.grid().ncells())
    refine2 = mlhp.refineAdaptively(mstate1.mesh, [0] * mstate1.mesh.ncells())
    newHistoryGrid.refine(mlhp.refinementOr([refine1, refine2]))
    
    mstate1.basis = mlhp.makeHpTrunkSpace(mstate1.mesh, msetup.degree, nfields=msetup.nfields)

    print(f"    Mechanical problem: {mstate1.basis.nelements()} elements, {mstate1.basis.ndof()} dofs", flush=True)

    # Gather dirichlet dofs
    dirichletDofs = mlhp.combineDirichletDofs([f(msetup, mstate1) for f in msetup.dirichlet])

    # Project solution from previous state
    K = mlhp.allocateSparseMatrix(mstate1.basis)
    F = mlhp.allocateRhsVector(K)

    l2Integrand = mlhp.l2BasisProjectionIntegrand(3, mstate0.dofs)
    
    # Todo: not only top surface, but properly remove air, powder, and liquid
    quadrature = topSurfacePartitioner(mstate0.history.topSurface) 

    mlhp.integrateOnDomain(mstate0.basis, mstate1.basis, l2Integrand, [K, F], quadrature=quadrature)

    #projectedDofs0 = mlhp.makeCGSolver(rtol=min(0.01 * rtol, 1e-6), atol=0.01*atol)(K, F)
    projectedDofs0 = mlhp.makeCGSolver(rtol=min(1e-10, 0.01 * rtol))(K, F)
    mstate1.dofs = projectedDofs0

    del K, F

    # Prepare nonlinear iterations
    K = mlhp.allocateSparseMatrix(mstate1.basis, dirichletDofs[0], symmetric=solver.symmetric > 0)
    F = mlhp.allocateRhsVector(K)

    norm0 = 0.0
    convergence = False
    print("    || R || --> ", end="", flush=True)

    # Newton-Raphson iterations
    for i in range(maxiter):
        mlhp.fill(K, 0.0)
        mlhp.fill(F, 0.0)

        dirichletIncrement = computeDirichletIncrement(dirichletDofs, mstate1.dofs, 1.0)

        dofIncrement = mlhp.add(mstate1.dofs, projectedDofs0, -1.0)

        kinematics = mlhp.smallStrainKinematics(3)
        material = makeJ2Plasticity(mstate1.mesh, mstate0.history, thermalStrainEvaluator)

        domainIntegrand = staticDomainIntegrand(kinematics, material, dofIncrement,
            mlhp.vectorField(3, [0.0] * 3))

        quadrature = _quadratureUnionWithHistory(newHistoryGrid, tstate1.history.topSurface)
        orderDeterminor = mlhp.relativeQuadratureOrder(3, msetup.offsetQuadrature)

        mlhp.integrateOnDomain(
            mstate1.basis, domainIntegrand, [K, F], quadrature=quadrature,
            dirichletDofs=dirichletIncrement, orderDeterminor=orderDeterminor)

        norm1 = mlhp.norm(F)
        norm0 = norm1 if i == 0 else norm0

        print(f"{norm1:.2e} ", end="", flush=True)

        if norm1 < max(rtol * norm0, atol):
            convergence = True
            break

        if norm1 > 1e3 * norm0:
            convergence = false
            break

        dx = mlhp.inflateDofs(solver(K, F, i, atol, rtol, norm0, norm1), dirichletIncrement)

        mstate1.dofs = mlhp.add(mstate1.dofs, dx)

        if (i + 1) % 6 == 0:
            print("\n                ", end="", flush=True)

    print("", flush=True)
    
    #j2update = j2HistoryUpdate(mstate0.history, mstate0.basis, mstate1.basis, mstate0.dofs, mstate1.dofs, thermalStrainEvaluator)
    j2update = j2HistoryUpdate(mstate0.history, mstate1.basis, mstate1.basis, projectedDofs0, mstate1.dofs, thermalStrainEvaluator)
    quadratureOrder = msetup.degree + msetup.offsetQuadrature
    
    if not useL2:
        mstate1.history = piecewiseConstantHistory(j2update, newHistoryGrid, quadratureOrder)
    else:
        materialIndicator = materialEvaluator(tstate1)
        thresholdTemperature = meltingTemperature(msetup.simulation.materials, 0.0)
        spatialWeight = historyProjectionWeight(thermalEvaluator(tstate1), materialIndicator, thresholdTemperature, 1e-2) 
        mstate1.history = l2ProjectHistory(j2update, newHistoryGrid, quadratureOrder, msetup.degree, spatialWeight)
        noThermalStrain = internalThermalStrainEvaluator(tstate1.basis, tstate1.dofs, 
            tstate1.history, msetup.simulation.materials)
        mstate1.history = j2HistoryUpdate(mstate1.history, noThermalStrain)

    return mstate1, convergence


def addNewPowderLayerMechanical(msetup, mstate0, deltaT):
    mstate1 = State(time=mstate0.time + deltaT, index=mstate0.index + 1, mesh=mstate0.mesh, 
                    basis=mstate0.basis, dofs=mstate0.dofs, history=mstate0.history.clone())
    mstate1.history.topSurface = mstate0.history.topSurface + msetup.simulation.layerThickness
    
    for pp in msetup.postprocess:
        pp(msetup, mstate1)
        
    return mstate1
    

def computeThermomechanicalProblem(tsetup, msetup, tstate0, mstate0, deltaT, duration, *, ilayer=None,
                                   maxiter=20, rtol=1e-8, atol=1e-9, msolver=CGSolver(), useL2=False):

    nsteps = int(math.ceil(duration / deltaT))
    realDT = duration / nsteps

    print(f"Integrating thermomechanical problem:", flush=True)
    print(f"    duration        = {duration}", flush=True)
    print(f"    number of steps = {nsteps}", flush=True)

    for i in range(nsteps):
        if ilayer is not None:
            print(f"Layer {ilayer + 1}, ", end="")
        print(f"Time step {i + 1} / {nsteps} ({tstate0.index + 1} in total)", flush=True)
        print(f"    Time: {tstate0.time:.8g} s, time step size: {realDT:.8g} s", flush=True)

        istepI, nstepsI, dtI, tindex0, mindex0, depth = 0, 1, realDT, tstate0.index, mstate0.index, 0

        # Thermomechanical time step
        while istepI < nstepsI:
            if depth + 1 == 20:
                raise RuntimeError(f"Thermomechanical iterations not converged after {depth + 1} refinements.")
                    
            lrtol, latol, qoffset = (1e-4, 0.8 * atol, 2) if depth == 0 else (1e-10, 1e-2 * atol, 4)
            tstate1, tconvergence = thermalTimeStep(
                tsetup, tstate0, dtI, maxiter=maxiter, rtol=rtol, qoffset=qoffset, 
                atol=atol, lsolver_rtol=lrtol, lsolver_atol=latol)
            
            if tconvergence:
                thermalEvaluator = internalThermalStrainEvaluator(
                    tstate0.basis, tstate1.basis, tstate0.dofs, tstate1.dofs, tstate1.history, 
                    tsetup.simulation.materials, tsetup.simulation.ambientTemperature)
                
                mstate1, mconvergence = mechanicalTimeStep(
                    msetup, mstate0, tstate1, thermalEvaluator, maxiter=maxiter, 
                    rtol=rtol, atol=atol, solver=msolver, useL2=useL2)
                
                if mconvergence:
                    tstate0, mstate0, istepI = tstate1, mstate1, istepI + 1

                    if istepI % 2 == 0:
                        istepI, nstepsI, dtI, depth = istepI // 2, nstepsI // 2, dtI * 2, depth - 1
                        print(f"    Thermomechanical Newton iterations converged, increasing time step size to"
                              f" {dtI:.6g}")
                else:
                    istepI, nstepsI, dtI, depth = istepI * 2, nstepsI * 2, dtI / 2, depth + 1
                    print(f"    Mechanical Newton iterations did not converge. Reducing time step to {dtI:.6g}")
                
            else:
                istepI, nstepsI, dtI, depth = istepI * 2, nstepsI * 2, dtI / 2, depth + 1
                print(f"    Thermal Newton iterations did not converge. Reducing time step to {dtI:.6g}")
        
        tstate1.index = tindex0 + 1
        mstate1.index = mindex0 + 1
        
        for pp in tsetup.postprocess:
            pp(tsetup, tstate1)
        
        for pp in msetup.postprocess:
                pp(msetup, mstate1)
    
    return tstate1, mstate1

#del os, sys, path
from mlhp import *
