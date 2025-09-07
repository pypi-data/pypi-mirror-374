// This file is part of the mlhpbf project. License: See LICENSE

#include "pybind11/pybind11.h"
#include "pybind11/functional.h"
#include "pybind11/stl.h"

#include "mlhp/pbf.hpp"
#include "external/mlhp/src/python/pymlhpcore.hpp"

namespace mlhp::bindings
{

PYBIND11_MODULE( pymlhpbf, m )
{
    m.doc( ) = "Work-in-progress part-scale powder bed fusion simulation.";

    // Base grid
    auto createBaseMeshTicksF = []( std::array<double, 3> min, std::array<double, 3> max, 
                                    double elementSize, double layerHeight, double zfactor )
    {
        return createBaseMeshTicks<3>( { min, max }, elementSize, layerHeight, zfactor );
    };
     
    m.def( "createMeshTicks", createBaseMeshTicksF, 
        pybind11::arg( "min" ), 
        pybind11::arg( "max" ),
        pybind11::arg( "elementSize" ), 
        pybind11::arg( "layerHeight" ) = 0.0, 
        pybind11::arg( "zfactor" ) = 1.0 );

    // Materials
    auto material = pybind11::class_<Material, std::shared_ptr<Material>>( m, "Material" );

    auto bindTemperatureFunction = [&]<typename C, typename D>( const char *name, D C::*pm )
    {
        auto get = [=]( const Material& mat ) {
            return RealFunctionWithDerivativeWrapper { mat.*pm }; };
        
        auto set = [=]( Material& mat, const RealFunctionWithDerivativeWrapper& f ) 
            { mat.*pm = f.get( ); };

        material.def_property( name, get, set );
    };

    material.def( pybind11::init<>( ) );
    material.def( "__str__", []( const Material& self ){ return "Material (name: " + self.name + ")"; } );
    material.def_readwrite( "initialized", &Material::initialized );
    material.def_readwrite( "name", &Material::name );
    bindTemperatureFunction( "density", &Material::density );
    bindTemperatureFunction( "specificHeatCapacity", &Material::specificHeatCapacity );
    bindTemperatureFunction( "heatConductivity", &Material::heatConductivity );
    material.def_readwrite( "annealingTemperature", &Material::annealingTemperature );
    material.def_readwrite( "solidTemperature", &Material::solidTemperature );
    material.def_readwrite( "liquidTemperature", &Material::liquidTemperature );
    material.def_readwrite( "latentHeatOfFusion", &Material::latentHeatOfFusion );
    material.def_readwrite( "regularization", &Material::regularization );
    bindTemperatureFunction( "thermalExpansionCoefficient", &Material::thermalExpansionCoefficient );
    bindTemperatureFunction( "youngsModulus", &Material::youngsModulus );
    bindTemperatureFunction( "poissonRatio", &Material::poissonRatio );
    bindTemperatureFunction( "yieldStress", &Material::yieldStress );
    bindTemperatureFunction( "hardening", &Material::hardeningParameter );
    material.def_readwrite( "plasticModelSelector", &Material::plasticModelSelector );
    material.def( "copy", []( const Material& self ) { return Material { self }; } );

    m.def( "readMaterialFile", []( std::string path ) { return readMaterialFile( path ); }, 
        pybind11::arg( "Path to material json file." ) );

    m.def( "readMaterialString", readMaterialString, 
        pybind11::arg( "Json string with material data." ) );

    auto blendMaterialFunctionsF = []( const FunctionWrapper<RealFunctionWithDerivative, RealFunctionTag>& function, 
                                       const FunctionWrapper<RealFunctionWithDerivative, RealFunctionTag>& blending,
                                       double value )
    { 
        auto result = [=, function = function.get( ), blending = blending.get( )]( double T )
        {
            auto [f, df] = function( T );
            auto [b, db] = blending( T );
        
            return std::array { b * f + ( 1 - b ) * value, b * df + db * f - db * value };
       };

        return FunctionWrapper<RealFunctionWithDerivative, RealFunctionTag> { std::move( result ) };
    };

    m.def( "blendMaterialFunction", blendMaterialFunctionsF, pybind11::arg( "function" ), pybind11::arg( "blending" ),
        pybind11::arg( "value" ) );

    auto sigmoidMaterialBlendingF = []( double T0, double T1, bool flip )
    {
        auto sign = ( flip ? -1.0 : 1.0 );
        auto invDiff = -sign * 4.0 / ( T1 - T0 );
        auto offset = -T0 * invDiff + 2.0 * sign;
    
        auto function = [=]( double T ) noexcept
        {
            if( auto arg = T * invDiff + offset; std::abs( arg ) < 20 )
            {
                auto tmp = std::exp( arg );
                auto f = 1.0 / ( 1.0 + tmp );

                return std::array { f, -invDiff * tmp * f * f };
            }
            else
            {
                return std::array { static_cast<double>( arg < 0 ), 0.0 };
            }
        };
    
        return FunctionWrapper<RealFunctionWithDerivative, RealFunctionTag> { std::move( function ) };
    };

    auto linearMaterialBlendingF = []( double T0, double T1, bool flip )
    {
        auto invDiff = ( flip ? -1.0 : 1.0 ) / ( T1 - T0 );
        auto offset = ( flip ? -T1 : -T0 ) * invDiff;
    
        auto function = [=]( double T ) noexcept
        {
            if( T <= T0 || T >= T1)
            {
                return std::array { static_cast<double>( ( T >= T1 ) != flip ), 0.0 };
            }
            else
            {
                return std::array { T * invDiff + offset, invDiff };
            }
        };
    
        return FunctionWrapper<RealFunctionWithDerivative, RealFunctionTag> { std::move( function ) };
    };

    m.def( "sigmoidMaterialBlending", sigmoidMaterialBlendingF, pybind11::arg( "T0" ),  
        pybind11::arg( "T1" ), pybind11::arg( "flip" ) = false );

    m.def( "linearMaterialBlending", linearMaterialBlendingF, pybind11::arg( "T0" ), 
        pybind11::arg( "T1" ), pybind11::arg( "flip" ) = false );

    // Laser
    auto laserPosition = pybind11::class_<laser::Point<3>>( m, "LaserPosition" );

    auto laserPositionStr = []( const laser::Point<3>& position )
    {
        auto sstream = std::ostringstream { };

        sstream << "LaserPosition: xyz = " << position.xyz << 
            ", time = " << position.time << ", power = " << position.power << "";

        return sstream.str( );
    };

    laserPosition.def( pybind11::init<std::array<double, 3>, double, double>( ),
                       pybind11::arg( "xyz" ), pybind11::arg( "time" ), pybind11::arg( "power" ) );
    laserPosition.def( "__str__", laserPositionStr );
    laserPosition.def_readwrite( "xyz", &laser::Point<3>::xyz );
    laserPosition.def_readwrite( "time", &laser::Point<3>::time );
    laserPosition.def_readwrite( "power", &laser::Point<3>::power );

    auto filterTrackF = []( laser::LaserTrack<3>&& track, 
                            std::optional<std::array<double, 2>> timeBounds,
                            std::optional<spatial::BoundingBox<3>> spaceBounds ) -> laser::LaserTrack<3>
    {
        if( timeBounds )
        {
            track = filterTrack( std::move( track ), *timeBounds );
        }

        if( spaceBounds )
        {
            track = filterTrack( std::move( track ), *spaceBounds );
        }

        return laser::LaserTrack<3> { std::move( track ) };
    };

    m.def( "filterTrack", filterTrackF,  pybind11::arg( "track" ), 
           pybind11::arg( "timeBounds" ) = std::nullopt,
           pybind11::arg( "spaceBounds" ) = std::nullopt );

    auto gaussianBeamF = []( double sigma, double absorptivity ) -> ScalarFunctionWrapper<2>
    {
        return std::function { spatial::integralNormalizedGaussBell<2>( { }, sigma, absorptivity ) };
    };
    
    m.def( "gaussianBeam", gaussianBeamF, pybind11::arg( "sigma" ), pybind11::arg( "absorptivity" ) = 1.0 );

    auto volumeSourceF = []( const laser::LaserTrack<3>& track,
                             const ScalarFunctionWrapper<2>& beamShape,
                             double depthSigma )
    {
        return ScalarFunctionWrapper<4> { laser::volumeSource<3>( track, beamShape, depthSigma ) };
    };

    auto surfaceSourceF = []( const laser::LaserTrack<3>& track,
                              const ScalarFunctionWrapper<2>& beamShape )
    {
        return ScalarFunctionWrapper<4>{ laser::surfaceSource<3>( track, beamShape ) };
    };
    
    m.def( "internalVolumeSource", volumeSourceF, pybind11::arg( "laserTrack" ), 
        pybind11::arg( "beamShape" ), pybind11::arg( "depthSigma" ) = 1.0 );

    m.def( "internalSurfaceSource", surfaceSourceF, pybind11::arg( "laserTrack" ), pybind11::arg( "beamShape" ) );

    auto refinement = pybind11::class_<laser::Refinement>( m, "LaserRefinementPoint" );

    auto refinementInit = []( double t, double s, double r, double z ) 
    { 
        return laser::Refinement { t, s, r, z }; 
    };

    auto refinementStr = []( laser::Refinement ref )
    {
        auto sstream = std::ostringstream { };

        sstream << "LaserRefinementPoint (" <<
            "delay = " << ref.timeDelay << "," <<
            "sigma = " << ref.sigma << ", " <<
            "depth = " << ref.refinementLevel << ", " <<
            "zfactor = " << ref.zfactor << ")";

        return sstream.str( );
    };

    refinement.def( pybind11::init( refinementInit ),
        pybind11::arg( "delay" ) = 0.0, pybind11::arg( "sigma" ) = 0.0, 
        pybind11::arg( "depth" ) = 0.0, pybind11::arg( "zfactor" ) = 1.0 );

    refinement.def( "__str__", refinementStr );
    refinement.def_readwrite( "delay", &laser::Refinement::timeDelay );
    refinement.def_readwrite( "sigma", &laser::Refinement::sigma );
    refinement.def_readwrite( "depth", &laser::Refinement::refinementLevel );
    refinement.def_readwrite( "zfactor", &laser::Refinement::zfactor );

    auto refineUniformlyF = []( size_t refinementLevel )
    {
        MLHP_CHECK( refinementLevel < NoValue<RefinementLevel> -1, "Invalid refinement level." );

        return RefinementFunctionWrapper<3>{ refineUniformly<3>( static_cast<RefinementLevel>( refinementLevel ) ) };
    };

    m.def( "refineUniformly", refineUniformlyF, pybind11::arg( "maxDepth" ) );

    auto makeLaserTrackRefinementF = []( const laser::LaserTrack<3>& track,
                               const std::vector<laser::Refinement>& refinements,
                               double time, size_t nseedpoints)
    {
        return RefinementFunctionWrapper<3> { laser::makeRefinement<3>( 
            track, refinements, time, nseedpoints ) };
    };

    m.def( "laserTrackPointRefinement", makeLaserTrackRefinementF, pybind11::arg( "laserTrack" ),
        pybind11::arg( "refinements" ), pybind11::arg( "time" ), pybind11::arg( "nseedpoints" ) );

    auto makeLaserTrackRefinementFunctionF = []( const laser::LaserTrack<3>& track,
                                                 const std::vector<laser::Refinement>& refinements )
    {
        return ScalarFunctionWrapper<4> { std::function { refinementLevelBasedOnLaserHistory( track, refinements ) } };
    };

    m.def( "laserTrackPointRefinementFunction", makeLaserTrackRefinementFunctionF,
        pybind11::arg( "laserTrack" ), pybind11::arg( "refinements" ) );

    auto sourceIntensityLevelFunctionF = []( const ScalarFunctionWrapper<3>& source,
                                             double topSurface, double threshold,
                                             double sigma, size_t depth )
    { 
        return ScalarFunctionWrapper<3> { laser::sourceIntensityLevelFunction<3>( 
            source.get( ), topSurface, threshold, sigma, depth ) };
    };

    m.def( "internalSourceIntensityLevelFunction", sourceIntensityLevelFunctionF, 
        pybind11::arg( "source" ), pybind11::arg( "topSurface" ), pybind11::arg( "threshold" ),
        pybind11::arg( "sigma" ), pybind11::arg( "depth" ) );

    auto refineConstrainedF = []( AbsHierarchicalGrid<3>& refinedGrid,
                                  const RefinementFunctionWrapper<3>& refinementFunction,
                                  double topSurface )
    { 
        return refineConstrained( refinedGrid, refinementFunction.get( ), topSurface );
    };

    m.def( "refineConstrained", refineConstrainedF, pybind11::arg( "baseGrid" ), 
        pybind11::arg( "refinement" ), pybind11::arg( "topSurface" ) );

    // Thermal history
    auto thermalHistory = pybind11::class_<ThermalHistory<3>, 
        std::shared_ptr<ThermalHistory<3>>>( m, "ThermalHistory" );

    auto thermalHistoryString = []( const ThermalHistory<3>& self )
    {
        auto sstream = std::stringstream { };
        auto memory = self.grid->memoryUsage( ) + utilities::vectorInternalMemory( self.data );

        sstream << "ThermalHistory (address: " << &self << ")\n";
        sstream << "    nleaves / ncells         : " << self.grid->nleaves( ) << " / " << self.grid->ncells( ) << "\n";
        sstream << "    maximum refinement level : " << static_cast<int>( self.maxdepth ) << "\n";
        sstream << "    top surface z-coordinate : " << self.topSurface << "\n";
        sstream << "    heap memory usage        : " << utilities::memoryUsageString( memory ) << "\n";

        return sstream.str( );
    };

    auto dataF = []( const ThermalHistory<3>& self )
    {
        return DoubleVector { utilities::convertVector<double>( self.data ) };
    };

    thermalHistory.def( pybind11::init<>( ) );
    thermalHistory.def( "__str__", thermalHistoryString );
    thermalHistory.def( "grid", []( const ThermalHistory<3>& history ){ return history.grid; } );
    thermalHistory.def( "data", dataF );
    thermalHistory.def_readwrite( "topSurface", &ThermalHistory<3>::topSurface );

    auto initializeThermalHistoryF = []( const GridSharedPtr<3>& baseGrid,
                                         const ImplicitFunctionWrapper<3>& part,
                                         size_t maxdepth, 
                                         double topSurface,
                                         size_t nseedpoints )
    {
        auto history = initializeHistory<3>( baseGrid, part.get( ), topSurface, nseedpoints, maxdepth );

        return std::make_shared<ThermalHistory<3>>( std::move( history ) );
    };

    m.def( "initializeThermalHistory", initializeThermalHistoryF,
        pybind11::arg( "baseGrid" ), pybind11::arg( "part" ), pybind11::arg( "maxdepth" ), 
        pybind11::arg( "topSurface" ) = 0.0, pybind11::arg( "nseedpoints" ) = 4 );

    auto updateHistoryF = []( const ThermalHistory<3>& history,
                              const MultilevelHpBasis<3>& tbasis, 
                              const DoubleVector& tdofs,
                              double meltingTemperature,
                              size_t degree )
    {
        return updateHistory( history, tbasis, tdofs.get( ), meltingTemperature, degree );
    };

    m.def( "updateHistory", updateHistoryF, pybind11::arg( "history" ), pybind11::arg("basis"),
        pybind11::arg( "tdofs" ), pybind11::arg( "meltingTemperature" ), pybind11::arg( "degree" ) );

    auto initializeNewLayerHistoryF = []( const ThermalHistory<3>& history,
                                          double newTopSurface )
    {
        return addPowderLayer( history, newTopSurface );
    };

    m.def( "initializeNewLayerHistory", initializeNewLayerHistoryF, pybind11::arg( "history" ), 
           pybind11::arg( "newTopSurface" ) );

    // Thermal physics
    using MaterialMap = std::map<std::string, std::shared_ptr<Material>>;

    auto convertMaterials = []( MaterialMap&& map )
    {
        auto find = [&]( const char* name ) -> const Material*
        { 
            auto result = map.find( name );

            return result != map.end( ) ? result->second.get( ) : nullptr;
        };

        return MaterialPtrs
        {
            .baseplate = find( "baseplate" ),
            .structure = find( "structure" ),
            .powder = find( "powder" ),
            .air = find( "air" )
        };
    };

    auto combineSourcesF = []( std::vector<ScalarFunctionWrapper<4>>&& sources )
    {
        auto function = [sources = std::move( sources )]( std::array<double, 4> xyzt ) -> double
        {
            auto intensity = 0.0;

            for( auto& source : sources )
            {
                intensity += source.get( )( xyzt );
            }
        
            return intensity;
        };

        return ScalarFunctionWrapper<4> { spatial::ScalarFunction<4> { std::move( function ) } };
    };

    m.def( "internalCombineSources", combineSourcesF, pybind11::arg( "sources" ) );

    auto internalMaterialEvaluatorF = []( std::shared_ptr<ThermalHistory<3>> history,
                                          spatial::BoundingBox<3> bounds )
    { 
        return ScalarFunctionWrapper<3> { [=]( std::array<double, 3> xyz )
        { 
            if( !spatial::insideBoundingBox( bounds, xyz ) )
            {
                return -1.0;
            }

            return static_cast<double>( history->operator()( xyz ) );
        } };
    };

    m.def( "internalMaterialEvaluator", internalMaterialEvaluatorF, pybind11::arg( "history" ), pybind11::arg( "bounds" ) );

    auto makeConvectionRadiationIntegrandF = [=]( const DoubleVector& dofs,
                                                  double emissivity,
                                                  double conductivity,
                                                  double ambientTemperature,
                                                  double boltzmannConstant,
                                                  double theta )
    { 
        return makeConvectionRadiationIntegrand<3>( dofs.getShared( ), emissivity, 
            conductivity, ambientTemperature, boltzmannConstant, theta );
    };

    m.def( "makeConvectionRadiationIntegrand", makeConvectionRadiationIntegrandF,
           pybind11::arg( "dof" ), pybind11::arg( "emissivity" ), pybind11::arg( "conductivity" ),
           pybind11::arg( "ambientTemperature" ), pybind11::arg( "boltzmannConstant" ), pybind11::arg( "theta" ) = 1.0 );

    auto makeThermalInitializationIntegrandF = [=]( MaterialMap map,
                                                    const ScalarFunctionWrapper<4>& source,
                                                    std::shared_ptr<ThermalHistory<3>> history0,
                                                    const DoubleVector& dofs0,
                                                    double time0, double dt, double theta )
    {
        auto materials = convertMaterials( std::move( map ) );
 
        return makeThermalInitializationIntegrand<3>( materials, source.get( ),
            *history0, dofs0.getShared( ), time0, dt, theta );
    };

    m.def( "makeThermalInitializationIntegrand", makeThermalInitializationIntegrandF,
        pybind11::arg( "materials" ), pybind11::arg( "sources" ), pybind11::arg( "history" ), 
        pybind11::arg( "dofs0" ), pybind11::arg( "time0" ), pybind11::arg( "deltaT" ), 
        pybind11::arg( "theta" ) );

    auto makeTimeSteppingThermalIntegrandF = [=]( MaterialMap map,
                                                  std::shared_ptr<ThermalHistory<3>> history,
                                                  const DoubleVector& projectedDofs0,
                                                  const DoubleVector& dofs1,
                                                  double dt, double theta )
    {
        auto materials = convertMaterials( std::move( map ) );
        
        return makeTimeSteppingThermalIntegrand<3>( materials, *history, 
            projectedDofs0.getShared( ), dofs1.getShared( ), dt, theta );
    };

    m.def( "makeTimeSteppingThermalIntegrand", makeTimeSteppingThermalIntegrandF,
        pybind11::arg( "materials" ), pybind11::arg( "history" ), 
        pybind11::arg( "projectedDofs0" ), pybind11::arg( "dofs1" ), 
        pybind11::arg( "deltaT" ), pybind11::arg( "theta" ) );

    auto makeEnergyConsistentProjectionIntegrandF = [=]( MaterialMap map,
                                                         std::shared_ptr<ThermalHistory<3>> history0,
                                                         std::shared_ptr<ThermalHistory<3>> history1,
                                                         const DoubleVector& projectedDofs0,
                                                         double ambientTemperature,
                                                         double dt )
    {
        auto materials = convertMaterials( std::move( map ) );

        return makeEnergyConsistentProjectionIntegrand<3>( materials, *history0, *history1,
            projectedDofs0.get( ), ambientTemperature, dt );
    };

    m.def( "makeEnergyConsistentProjectionIntegrand", makeEnergyConsistentProjectionIntegrandF,
           pybind11::arg( "materials" ), pybind11::arg( "history0" ), pybind11::arg( "history1" ),
           pybind11::arg( "projectedDofs0" ),pybind11::arg( "ambientTemperature" ), pybind11::arg( "deltaT" ));

    auto makeSteadyStateThermalIntegrandF = [=]( MaterialMap map,
                                                 const ScalarFunctionWrapper<3>& source,
                                                 std::shared_ptr<ThermalHistory<3>> history,
                                                 const DoubleVector& dofs,
                                                 std::array<double, 3> laserVelocity )
    {
        auto materials = convertMaterials( std::move( map ) );

        return makeSteadyStateThermalIntegrand<3>( materials, 
            source.get( ), *history, dofs.get(), laserVelocity);
    };
    
    m.def( "makeSteadyStateThermalIntegrand", makeSteadyStateThermalIntegrandF,
        pybind11::arg( "materials" ), pybind11::arg( "sources" ), pybind11::arg( "history" ),
        pybind11::arg( "dofs" ), pybind11::arg( "laserVelocity" ) = std::array { 1.0, 0.0, 0.0 } );

    // Mechanical problem    
    using ThermalStrainEvaluatorWrapper = FunctionWrapper<ThermalEvaluator<3>>;

    pybind11::class_<ThermalStrainEvaluatorWrapper>( m, "ThermalStrainEvaluator" );

    pybind11::class_<AbsHistoryRepresentation<3>, std::shared_ptr<AbsHistoryRepresentation<3>>>
        absHistoryRepresentation( m, "HistoryRepresentation" );

    absHistoryRepresentation.def( "grid", []( const AbsHistoryRepresentation<3>& history ) { return history.gridPtr( ); } );
    absHistoryRepresentation.def_readwrite( "topSurface", &AbsHistoryRepresentation<3>::topSurface );
    absHistoryRepresentation.def( "clone", &AbsHistoryRepresentation<3>::clone );

    pybind11::class_<PiecewiseConstantHistoryGrid<3>, std::shared_ptr<PiecewiseConstantHistoryGrid<3>>,
        AbsHistoryRepresentation<3>>( m, "PiecewiseConstantHistoryGrid" );
    
    auto piecewiseConstantHistoryF1 = []( HierarchicalGridSharedPtr<3> grid, size_t quadratureOrder, double topSurface )
    {
        return std::make_shared<PiecewiseConstantHistoryGrid<3>>( grid, quadratureOrder, topSurface );
    };

    auto piecewiseConstantHistoryF2 = []( const AbsHistoryRepresentation<3>& history,
                                          const HierarchicalGridSharedPtr<3>& grid,
                                          size_t quadratureOrder )
    { 
        return std::make_shared<PiecewiseConstantHistoryGrid<3>>( history, grid, quadratureOrder );
    };

    m.def( "piecewiseConstantHistory", piecewiseConstantHistoryF1, pybind11::arg( "grid" ), 
           pybind11::arg( "quadratureOrder" ), pybind11::arg( "topSurface" ) );
    m.def( "piecewiseConstantHistory", piecewiseConstantHistoryF2, pybind11::arg( "history" ),
              pybind11::arg( "grid" ), pybind11::arg( "quadratureOrder" ) );

    pybind11::class_<L2ProjectedHistory<3>, std::shared_ptr<L2ProjectedHistory<3>>, AbsHistoryRepresentation<3>>(m, "L2ProjectedHistory");

    auto initL2ProjectedHistoryF = []( const AbsHistoryRepresentation<3>& oldHistory,
                                       const HierarchicalGridSharedPtr<3>& newGrid,
                                       size_t quadratureOrder,
                                       size_t polynomialDegree,
                                       const ScalarFunctionWrapper<3>& spatialWeight )
    {
        return std::make_shared<L2ProjectedHistory<3>>( oldHistory, newGrid, quadratureOrder, polynomialDegree, spatialWeight.get( ) );
    };

    m.def( "l2ProjectHistory", initL2ProjectedHistoryF, pybind11::arg( "history" ), pybind11::arg( "grid" ),
        pybind11::arg( "quadratureOrder" ), pybind11::arg( "polynomialDegree" ), pybind11::arg( "spatialWeight" ) );
    
    pybind11::class_<J2HistoryUpdate<3>, std::shared_ptr<J2HistoryUpdate<3>>, AbsHistoryRepresentation<3>>( m, "J2HistoryUpdate" );
    
    auto j2HistoryUpdateF1 = [](  std::shared_ptr<const AbsHistoryRepresentation<3>> oldHistory,
                                  const ThermalStrainEvaluatorWrapper& evaluator  )
    {
        return std::make_shared<J2HistoryUpdate<3>>( std::move( oldHistory ), evaluator.get( ) );
    };

    auto j2HistoryUpdateF2 = []( std::shared_ptr<const AbsHistoryRepresentation<3>> oldHistory,
                                 std::shared_ptr<const MultilevelHpBasis<3>> mbasis0,
                                 std::shared_ptr<const MultilevelHpBasis<3>> mbasis1,
                                 const DoubleVector& dofs0,
                                 const DoubleVector& dofs1,
                                 const ThermalStrainEvaluatorWrapper& evaluator  )
    {
        return std::make_shared<J2HistoryUpdate<3>>( std::move( oldHistory ), std::move( mbasis0 ), 
            std::move( mbasis1 ), dofs0.getShared( ), dofs1.getShared( ), evaluator.get( ) );
    };

    m.def( "j2HistoryUpdate", j2HistoryUpdateF1, pybind11::arg( "oldHistory" ), pybind11::arg( "thermalEvaluator" ) );
    
    m.def( "j2HistoryUpdate", j2HistoryUpdateF2, pybind11::arg( "oldHistory" ), pybind11::arg( "basis0" ), pybind11::arg( "basis1" ), 
        pybind11::arg( "dofs0" ), pybind11::arg( "dofs1" ), pybind11::arg( "thermalEvaluator" ) );
    
    auto makeThermalStainEvaluatorF1 = [=]( const BasisConstSharedPtr<3>& tbasis0,
                                       const BasisConstSharedPtr<3>& tbasis1,
                                       const DoubleVector& tdofs0,
                                       const DoubleVector& tdofs1,
                                       const ThermalHistory<3>& thermalHistory1,
                                       MaterialMap materialMap,
                                       double ambientTemperature ) -> ThermalStrainEvaluatorWrapper
    {
        return makeThermalEvaluator<3>( tbasis0, tbasis1, tdofs0.getShared( ), tdofs1.getShared( ),
            thermalHistory1, convertMaterials( std::move( materialMap ) ), ambientTemperature );
    };

    m.def( "internalThermalStrainEvaluator", makeThermalStainEvaluatorF1,
           pybind11::arg( "tbasis0" ), pybind11::arg( "tbasis1" ),
           pybind11::arg( "tdofs0" ), pybind11::arg( "tdofs1" ),
           pybind11::arg( "thermalHistory1" ), pybind11::arg( "materials" ),
           pybind11::arg( "ambientTemperature") );

    auto makeThermalStainEvaluatorF2 = [=]( const BasisConstSharedPtr<3>& tbasis,
                                            const DoubleVector& tdofs,
                                            const ThermalHistory<3>& thermalHistory_,
                                            MaterialMap materialMap ) -> ThermalStrainEvaluatorWrapper
    {
        return makeThermalEvaluator<3>( tbasis, tdofs.getShared( ), thermalHistory_,
            convertMaterials( std::move( materialMap ) ) );
    };

    m.def( "internalThermalStrainEvaluator", makeThermalStainEvaluatorF2,
           pybind11::arg( "tbasis" ), pybind11::arg( "tdofs" ),
           pybind11::arg( "thermalHistory" ), pybind11::arg( "materials" ) );
           
    auto integrateErrorF = [=]( MaterialMap materialMap, 
                                const MultilevelHpBasis<3>& basis,
                                const DoubleVector& vector,
                                const ThermalHistory<3>& history )
    {
        auto materials = convertMaterials( std::move( materialMap ) );

        return DoubleVector { integrateError( materials, basis, vector.get( ), history ) };
    };

    m.def( "integrateError", integrateErrorF );

    auto clippedPostprocessingMeshF = []( double topSurface,
                                          std::array<size_t, 3> resolution,
                                          PostprocessTopologies topologies )
    {
        return CellMeshCreatorWrapper<3> { clippedPostprocessingMesh<3>( topSurface, resolution, topologies ) };
    };

    m.def( "clippedPostprocessingMesh", clippedPostprocessingMeshF, pybind11::arg( "topSurface" ),
           pybind11::arg( "resolution" ), pybind11::arg( "topologies" ) );

    auto materialRefinedPostprocessingGridF = []( const CellMeshCreatorWrapper<3>& meshCreator,
                                                  const HierarchicalGridSharedPtr<3>& temperatureGrid,
                                                  const HierarchicalGridSharedPtr<3>& materialGrid )
    { 
        return CellMeshCreatorWrapper<3> { materialRefinedPostprocessingGrid( meshCreator.get( ), temperatureGrid, materialGrid ) };
    };

    m.def( "materialRefinedPostprocessingGrid", materialRefinedPostprocessingGridF, pybind11::arg(
        "meshCreator" ), pybind11::arg( "temperatureGrid" ), pybind11::arg( "materialGrid" ) );
    
    m.def( "addThermalHistoryOutput", addThermalHistoryOutput, pybind11::arg( "meshWriter" ),
        pybind11::arg( "history" ), pybind11::arg( "dataSetName" ) );
    
    auto makeJ2PlasticityF = []( const AbsHierarchicalGrid<3>& mgrid1,
                                 const AbsHistoryRepresentation<3>& mhistory0,
                                 const ThermalStrainEvaluatorWrapper& evaluator )
    { 
        return makeJ2Plasticity( mgrid1, mhistory0, evaluator.get( ) );
    };

    m.def( "makeJ2Plasticity", makeJ2PlasticityF, pybind11::arg( "mgrid1" ), pybind11::arg( "mhistory0" ), pybind11::arg( "thermalEvaluator" ) );

    auto historyProjectionWeightF = [=]( const ScalarFunctionWrapper<3>& temperature,
                                         const ScalarFunctionWrapper<3>& materialType,
                                         double temperatureThreshold, double outsideWeight )
    {
        return ScalarFunctionWrapper<3> { makeHistoryProjectionWeight( temperature.get( ), 
            materialType.get( ), temperatureThreshold, outsideWeight ) };
    };

    m.def( "historyProjectionWeight", historyProjectionWeightF, pybind11::arg( "temperature" ), pybind11::arg( "materialType" ), 
        pybind11::arg( "temperatureThreshold" ), pybind11::arg( "outsideWeight" ) );

    defineFunctionWrapper<MaterialAdapter<3>>( m, "MaterialAdapter" );

    auto materialAdapterF = [=]( std::shared_ptr<ThermalHistory<3>> thistory, MaterialMap materialMap )
    {
        return FunctionWrapper<MaterialAdapter<3>> { makeMaterialAdapter<3>( 
            thistory, convertMaterials( std::move( materialMap ) ) ) };
    };

    m.def( "iternalMaterialAdapter", materialAdapterF, pybind11::arg( "thermalHistory" ), pybind11::arg( "materials" ) );

    auto mechanicalPostprocessorF = []( std::vector<std::string> quantities, 
                                        const DoubleVector& displacement,
                                        std::shared_ptr<const AbsHistoryRepresentation<3>> history,
                                        const ScalarFunctionWrapper<3>& temperature,
                                        const FunctionWrapper<MaterialAdapter<3>>& materialAdapter )
    {
        return mechanicalPostprocessor( quantities, displacement.getShared( ), history, temperature.get( ), materialAdapter.get( ) );
    };

    m.def( "mechanicalPostprocessor", mechanicalPostprocessorF, pybind11::arg( "quantities" ), pybind11::arg( "displacement" ), 
        pybind11::arg( "history" ), pybind11::arg( "temperatureFunction" ), pybind11::arg( "materialAdapter" ) );

    // Other stuff
    auto computeDirichletIncrementF = []( const DofIndicesValuesPair& dirichlet,
                                          const DoubleVector& dofs,
                                          double factor )
    { 
        auto dirichletIncrement = dirichlet;

        MLHP_CHECK( dirichlet.first.size( ) == dirichlet.second.size( ),
                    "Dirichlet dof vectors have different size." );

        for( size_t idof = 0; idof < dirichlet.first.size( ); ++idof )
        {
            MLHP_CHECK( dirichlet.first[idof] < dofs.get( ).size( ), "Dirichlet dof index out of bounds." );

            dirichletIncrement.second[idof] = factor * ( dirichlet.second[idof] - 
                dofs.get( )[dirichlet.first[idof]] );
        }    

        return dirichletIncrement;
    };

    m.def( "computeDirichletIncrement", computeDirichletIncrementF, pybind11::arg( "dirichletDofs" ), 
           pybind11::arg( "dofs" ), pybind11::arg( "factor" ) = 1.0 );

    [[maybe_unused]] auto topSurfacePartitioner = pybind11::class_<TopSurfacePartitioner<3>, 
        std::shared_ptr<TopSurfacePartitioner<3>>, AbsQuadrature<3>>( m, "TopSurfacePartitioner3D" );

    auto topSurfacePartitionerF = []( double topSurface, std::shared_ptr<AbsQuadrature<3>> quadrature )
    {
        return std::make_shared<TopSurfacePartitioner<3>>( topSurface, std::move( quadrature ) );
    };

    m.def( "topSurfacePartitioner", topSurfacePartitionerF, pybind11::arg( "topSurface" ), 
        pybind11::arg( "quadrature" ) = std::make_shared<StandardQuadrature<3>>( ) );
    
    [[maybe_unused]] auto topSurfaceBoundaryQuadrature = pybind11::class_<TopSurfaceBoundaryQuadrature<3>,
        std::shared_ptr<TopSurfaceBoundaryQuadrature<3>>, AbsQuadratureOnMesh<3>>( m, "TopSurfaceBoundaryQuadrature3D" );

    auto topSurfaceBoundaryQuadratureF = []( double topSurface,
                                             const QuadratureOrderDeterminorWrapper<3>& order )
    {
        return std::make_shared<TopSurfaceBoundaryQuadrature<3>>( topSurface, order.get( ) );
    };
    
    m.def( "topSurfaceBoundaryQuadrature", topSurfaceBoundaryQuadratureF, pybind11::arg( "topSurface" ),
        pybind11::arg( "order" ) = QuadratureOrderDeterminorWrapper<3> { relativeQuadratureOrder<3>( 1 ) } );
}

} // mlhp::bindings

