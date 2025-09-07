// This file is part of the mlhpbf project. License: See LICENSE

#include "mlhp/pbf.hpp"
#include "main_test.hpp"

namespace mlhp
{
namespace
{

template<size_t D>
ThermalRefinement<D> makePhaseChangeRefinement( );

struct Compute : Units
{
    static void compute( )
    {
        static constexpr size_t D = 3;

        auto buildChamber = std::array { std::array { 0.0 * mm, 0.0 * mm, 0.0 * mm },
                                         std::array { 100.0 * mm, 10.0 * mm, 10.0 * mm } };
    
        auto density = []( double T ) -> std::array<double, 2>
        {
            return { 4510 * Units::kg / Units::m / Units::m / Units::m, 0.0 };
        };

        auto cp = []( double T ) -> std::array<double, 2>
        {
            return { 520 * Units::J / Units::kg , 0.0 };
        };

        auto kappa = []( double T ) -> std::array<double, 2>
        {
            return { 16.0 * Units::W / Units::m, 0.0 };
        };

        auto expCoeff = []( double T ) -> std::array<double, 2>
        {
            return { 1.0, 0.0 };
        };

        auto youngsModulus = []( double T ) -> std::array<double, 2>
        {
            return { 206.9 * Units::GPa, 0.0 };
        };

        auto poissonsRatio = []( double T ) -> std::array<double, 2>
        {
            return { 0.29, 0.0 };
        };

        auto yieldStress = []( double T ) -> std::array<double, 2>
        {
            return { 0.45 * Units::GPa, 0.0 };
        };

        auto hardening = []( double T ) -> std::array<double, 2>
        {
            return { 0.2, 0.0 };
        };

        Material barMaterial =
        {
            .initialized = true,
            .name = "Titanium",
            .density = density,
            .specificHeatCapacity = cp,
            .heatConductivity = kappa,
            .solidTemperature = 1670.0 * Units::C - 1.0 * Units::C,
            .liquidTemperature = 1670.0 * Units::C + 1.0 * Units::C,
            .latentHeatOfFusion = 325e3 * Units::J / Units::kg,
            .regularization = 1.0,
            .thermalExpansionCoefficient = expCoeff,
            .youngsModulus = youngsModulus,
            .poissonRatio = poissonsRatio,
            .yieldStress = yieldStress,
            .hardeningParameter = hardening,
            .plasticModelSelector = 0.0,
        };

        // Discretization
        auto trefinement = size_t { 0 };
        auto hrefinement = size_t { 0 };
    
        auto telementsize = 1 * mm;
        auto timestep = 1 * s;
        
        // Create base mesh ticks and reduce top layer element height
        auto baseGrid = std::make_shared<CartesianGrid<D>>( std::array<size_t, D> 
            { 160, 1, 1 }, buildChamber[1] - buildChamber[0], buildChamber[0] );

        auto general = ProblemSetup<D>
        {
            .buildChamber = buildChamber,
            .duration = 100.0 * s,
            .baseplate = barMaterial,
            .air = barMaterial,
            .baseGrid = baseGrid,
        };
    
        std::function analyticalSolution = [&](const std::array<double, D + 1> xyzt) -> double
        {
            double Ts = 1500.0;
            double Tl = 2000.0;
            double Tm = 1670.0;
            double lambda = 0.388150542167233;
            double alpha = 6.8224e-06 * Units::m * Units::m / Units::s;
            double solidificationFront = 2 * lambda * std::sqrt(alpha * xyzt[3]);
            double tanal = 0.0;
            if (xyzt[0] < solidificationFront)
            {
                tanal = Tl - (Tl - Tm) * std::erf(xyzt[0] / std::sqrt(4.0 * alpha * xyzt[3])) / std::erf(lambda);
                return tanal;
            }
            else
            {
                tanal = Ts + (Tm - Ts) * std::erfc(xyzt[0] / std::sqrt(4.0 * alpha * xyzt[3])) / std::erfc(lambda);
                return tanal;
            }
        };

        size_t nseedpoints = 2;

        auto analyticalBoundaryFunction = [=](size_t iface, spatial::ScalarFunction<D + 1> function)
        {
            return [=](const ThermalState<D>& tstate)
            {
                auto sliced = spatial::sliceLast<D + 1>(function, tstate.time);

                return boundary::boundaryDofs(sliced, *tstate.basis, { iface });
            };
        };

        auto dirichletLeft = makeTemperatureBC<D>( boundary::left, 2000.0 * C );
        auto dirichletRight = analyticalBoundaryFunction(boundary::right, analyticalSolution);
        auto sharedSetup = std::make_shared<ProblemSetup<D>>( std::move( general ) );

        auto thermal = ThermalProblem<D>
        {
            .general = sharedSetup,
            .ambientTemperature = 1500 * C,
            //.refinement = makePhaseChangeRefinement<D>( ),
            .refinement = makeUniformRefinement<D>( static_cast<RefinementLevel>( trefinement ) ),
            .degree = 3,
            .timeStep = timestep,
            .source = spatial::constantFunction<D + 1>( 0.0 ),
            .dirichlet = { dirichletLeft, dirichletRight },
            .imposeDirichletInInitialCondition = false,
            .postprocess = makeThermalPostprocessing<D>( "outputs/mlhpbf_tests/meltingbar_", 8 )
        };

        //auto ux = DirichletBC<D> { .face = boundary::left, .field = 0 };
        //auto uy = DirichletBC<D> { .face = boundary::right, .field = 1 };
        //auto uz = DirichletBC<D> { .face = boundary::right, .field = 2 };

        //auto mechanical = MechanicalProblem<D>
        //{
        //    .general = sharedSetup,
        //    .dirichlet = { ux, uy, uz },
        //    .postprocess = makeMechanicalPostprocessing<D>( "outputs/bar_", 8 )
        //};

        auto history0 = initializeHistory<D>( sharedSetup->baseGrid, 0.0, hrefinement );

        auto tstate = computeThermalProblem( thermal, std::move( history0 ) );
        //computeThermomechanicalProblem( thermal, mechanical, std::move( history0 ) );

        for (int i = 0; i < 100; i++)
        {
            double x = static_cast<double>(i);
            double y = 5.0;
            double z = 5.0; 
            double tanal = analyticalSolution({ x, y, z, general.duration });
            auto evalTempNum = makeEvaluationFunction<D>(tstate.basis, tstate.dofs);
            double tnum = evalTempNum({x, y, z});
            double tempDiff = std::abs(tanal - tnum);
            double tol = 1.0490990024;
            CHECK(tempDiff <= tol);
        }
        
    }
};

template<size_t D>
ThermalRefinement<D> makePhaseChangeRefinement( )
{
    return [=]( const ThermalProblem<D>& problem,
                const ThermalState<D>& state0, 
                const ThermalState<D>& state1 )
    {
        // Coarsen indefinitely
        auto levelDiff = std::vector<int>( state0.basis->nelements( ), std::numeric_limits<int>::min( ) );

        #pragma omp parallel
        {
            auto nelements = state0.basis->nelements( );
            auto cache = state0.basis->createEvaluationCache( );
            auto shapes = BasisFunctionEvaluation<D> { };
            auto locationMap = LocationMap { };
            auto nseedpoints = array::make<D>( problem.degree + 1 );

            auto rst = spatial::cartesianTickVectors( array::subtract( nseedpoints, size_t { 1 } ),
                array::make<D>( 2.0 ), array::make<D>( -1.0 ) );

            #pragma omp for
            for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( nelements ); ++ii )
            {
                auto ielement = static_cast<CellIndex>( ii );

                utilities::resize0( locationMap );

                state0.basis->prepareEvaluation( ielement, 0, shapes, cache );
                state0.basis->prepareGridEvaluation( rst, cache );
                state0.basis->locationMap( ielement, locationMap );

                auto fullIndex = state0.basis->hierarchicalGrid( ).fullIndex( ielement );
                auto level = state0.basis->hierarchicalGrid( ).refinementLevel( fullIndex );

                auto Ts = 1670.0;
                auto Tl = 2000.0;

                auto refine = false;
                auto state = int { 0 };

                // Refine if element contains phase transition
                nd::execute( nseedpoints, [&]( auto ijk )
                {
                    state0.basis->evaluateGridPoint( ijk, shapes, cache );

                    auto T = evaluateSolution( shapes, locationMap, state0.dofs );
                    auto stateI = T < Ts ? -1 : ( T > Tl ? 1 : 0 );

                    if( ijk != array::make<D>( size_t { 0 } ) )
                    {
                        refine = refine || stateI == 0 || state != stateI;
                    }
                    else
                    {
                        state = stateI;
                        refine = stateI == 0;
                    }
                } );

                if( refine )
                {
                    levelDiff[ielement] = 2 - static_cast<int>( level );
                }
            }
        }

        return mesh::refineAdaptively( state0.basis->hierarchicalGrid( ), levelDiff );
    };
}

} // namespace


TEST_CASE( "solidificationbar_test" )
{
    mlhp::Compute::compute( );
}

} // namespace mlhp
