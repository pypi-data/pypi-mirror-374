// This file is part of the mlhpbf project. License: See LICENSE

#ifndef MLHPBF_THERMAL_HPP
#define MLHPBF_THERMAL_HPP

#include "laser.hpp"
#include "meltstate.hpp"

namespace mlhp
{

template<size_t D> inline
auto makeThermalInitializationIntegrand( const MaterialPtrs& materials,
                                         const spatial::ScalarFunction<D + 1>& source,
                                         const ThermalHistory<D>& history0,
                                         memory::vptr<const std::vector<double>> dofs0,
                                         double time0,
                                         double deltaT,
                                         double theta )
{
    auto evaluate = [=, &history0]( const LocationMap& locationMap0,
                                    const LocationMap&,
                                    const BasisFunctionEvaluation<D>& shapes0,
                                    const BasisFunctionEvaluation<D>& shapes1,
                                    AlignedDoubleVectors& targets,
                                    double weightDetJ )
    {
        auto N0 = shapes0.noalias( 0, 0 );
        auto dN0 = shapes0.noalias( 0, 1 );
        auto ndof0 = shapes0.ndof( );
        auto ndofpadded0 = shapes0.ndofpadded( );
        auto u0 = 0.0;
        auto du0 = std::array<double, D> { };
        auto dofs0Ptr = memory::assumeNoalias( dofs0->data( ) );

        for( size_t i = 0; i < ndof0; ++i )
        {
            auto dof = dofs0Ptr[locationMap0[i]];

            u0 += dof * N0[i];

            for( size_t axis = 0; axis < D; ++axis )
            {
                du0[axis] += dN0[axis * ndofpadded0 + i] * dof;
            }
        }

        auto ndof = shapes1.ndof( );
        auto nblocks = shapes1.nblocks( );
        auto ndofpadded = shapes1.ndofpadded( );

        auto N = shapes1.noalias( 0, 0 );
        auto dN = shapes1.noalias( 0, 1 );

        auto material = materialFor( materials, history0( shapes0.xyz( ) ) );

        auto [k0, dk0] = material->heatConductivity( u0 );

        auto kscaling0 = array::make<D>( 1.0 );
        auto sourceTheta = 0.0;

        if( theta != 1.0  )
        {
            sourceTheta += ( 1.0 - theta ) * source( array::insert( shapes1.xyz( ), D, time0 ) );
        }

        if( theta != 0.0  )
        {
            sourceTheta += theta * source( array::insert( shapes1.xyz( ), D, time0 + deltaT ) );
        }

        auto conductivities0 = array::multiply( kscaling0, k0 * ( 1.0 - theta ) );        
        auto flux = array::multiply( conductivities0, du0 );

        linalg::elementRhs( targets[0].data( ), ndof, nblocks, [&]( size_t i )
        {
            double value = -N[i] * sourceTheta;

            for( size_t axis = 0; axis < D; ++axis )
            {
                value += dN[axis * ndofpadded + i] * flux[axis];
            }

            return value * weightDetJ;
        } );
    };

    auto types = std::vector { AssemblyType::Vector };

    return BasisProjectionIntegrand<D>( types, DiffOrders::FirstDerivatives, evaluate );
}

template<size_t D> inline
auto makeTimeSteppingThermalIntegrand( const MaterialPtrs& materials,
                                       const ThermalHistory<D>& historyContainer,
                                       memory::vptr<const std::vector<double>> projectedDofs0,
                                       memory::vptr<const std::vector<double>> dofs1,
                                       double dt,
                                       double theta )
{
    using AnyCache = typename DomainIntegrand<D>::Cache;
    using ThisCache = AlignedDoubleVector;

    auto create = []( const AbsBasis<D>& ) -> AnyCache
    {
        return ThisCache { };
    };

    auto prepare = [=]( AnyCache& anyCache,
                        const MeshMapping<D>&,
                        const LocationMap& locationMap )
    { 
        auto& elementDofs = utilities::cast<ThisCache>( anyCache );

        // Cache element dofs
        auto ndof = locationMap.size( );
        auto npadded = memory::paddedLength<double>( ndof );

        elementDofs.resize( 2 * npadded );

        for( size_t i = 0; i < ndof; ++i )
        {
            elementDofs[i] = ( *dofs1 )[locationMap[i]];
        }

        for( size_t i = 0; i < ndof; ++i )
        {
            elementDofs[i + npadded] = ( *projectedDofs0 )[locationMap[i]];
        }
    };

    auto evaluate = [=, &historyContainer]( AnyCache& anyCache,
                                            const BasisFunctionEvaluation<D>& shapes,
                                            AlignedDoubleVectors& targets,
                                            double weightDetJ )
    {
        auto ndof = shapes.ndof( );
        auto nblocks = shapes.nblocks( );
        auto ndofpadded = shapes.ndofpadded( );

        auto N = shapes.noalias( 0, 0 );
        auto dN = shapes.noalias( 0, 1 );

        // Evaluate solution using cached element dofs
        auto u0 = 0.0, u1 = 0.0;
        auto du1 = std::array<double, D> { };
        auto elementDofs = memory::assumeAlignedNoalias( utilities::cast<ThisCache>( anyCache ).data( ) );

        for( size_t i = 0; i < ndof; ++i )
        {
            u0 += elementDofs[ndofpadded + i] * N[i];
            u1 += elementDofs[i] * N[i];

            for( size_t axis = 0; axis < D; ++axis )
            {
                du1[axis] += dN[axis * ndofpadded + i] * elementDofs[i];
            }
        }

        // Evaluate materials
        auto material = materialFor( materials, historyContainer( shapes.xyz( ) ) );

        auto [rho0, drho0] = theta != 1.0 ? material->density( u0 ) : std::array<double, 2> { };
        auto [c0, dc0] = theta != 1.0 ? material->specificHeatCapacity( u0 ) : std::array<double, 2> { };

        auto [rho1, drho1] = material->density( u1 );
        auto [c1, dc1] = material->specificHeatCapacity( u1 );
        auto [k1, dk1] = material->heatConductivity( u1 );
        auto [L0, dL0, ddL0] = evaluatePhaseTransition( *material, u0 );
        auto [L1, dL1, ddL1] = evaluatePhaseTransition( *material, u1 );

        auto cTheta = ( 1.0 - theta ) * c0 * rho0 + theta * c1 * rho1;
        auto mass = ( cTheta + theta * ( dc1 * rho1 + c1 * drho1 ) * ( u1 - u0 ) + dL1 ) / dt;
        auto kappa1 = k1 * theta;
        auto dkappa1 = dk1 * theta;

        // Element tangent matrix
        linalg::unsymmetricElementLhs( targets[0].data( ), ndof, nblocks, [&]( size_t i, size_t j )
        {
            auto value = N[i] * N[j] * mass;

            for( size_t axis = 0; axis < D; ++axis )
            {
                value += dN[axis * ndofpadded + i] * ( dN[axis * ndofpadded + j] * kappa1 + du1[axis] * dkappa1 * N[j] );

            } // component

            return value * weightDetJ;
        } );

        // Element residual vector
        auto dc = cTheta * ( u1 - u0 ) / dt;
        auto dL = ( L1 - L0 ) / dt;

        linalg::elementRhs( targets[1].data( ), ndof, nblocks, [&]( size_t i )
        {
            double value = N[i] * ( dc + dL );

            for( size_t axis = 0; axis < D; ++axis )
            {
                value += dN[axis * ndofpadded + i] * kappa1 * du1[axis];
            }

            return value * weightDetJ;
        } );
    };

    auto types = std::vector { AssemblyType::UnsymmetricMatrix, AssemblyType::Vector };

    return DomainIntegrand<D>( types, DiffOrders::FirstDerivatives, 
        std::move( create ), std::move( prepare ), std::move( evaluate ) );
}

template<size_t D> inline
BasisProjectionIntegrand<D> makeEnergyConsistentProjectionIntegrand( const MaterialPtrs& materials,
                                                                     const ThermalHistory<D>& historyContainer0,
                                                                     const ThermalHistory<D>& historyContainer1,
                                                                     const std::vector<double>& dofs,
                                                                     double ambientTemperature,
                                                                     double dt )
{
    auto evaluate = [=, &historyContainer0, &historyContainer1, &dofs]( const LocationMap& locationMap0,
                                                                        const LocationMap&,
                                                                        const BasisFunctionEvaluation<D>& shapes0,
                                                                        const BasisFunctionEvaluation<D>& shapes1,
                                                                        AlignedDoubleVectors& targets,
                                                                        double weightDetJ )
    {
        auto tmp1 = shapes1.sizes( );

        auto ndof = std::get<0>( tmp1 );
        auto nblocks = std::get<1>( tmp1 );
        auto ndofpadded = std::get<2>( tmp1 );

        auto N = shapes1.noalias( 0, 0 );
        auto dN = shapes1.noalias( 0, 1 );

        auto u = evaluateSolution( shapes0, locationMap0, dofs );

        auto history0 = historyContainer0( shapes0.xyz( ) );
        auto material1 = materialFor( materials, historyContainer1( shapes1.xyz( ) ) );

        auto ambientTemperatureFunction = spatial::constantFunction<D>( ambientTemperature );

        auto [rho, drho] = material1->density( u );
        auto [c, dc] = material1->specificHeatCapacity( u );
        auto [k, dk] = material1->heatConductivity( u );

        auto kscaling1 = array::make<D>( 1.0 );
        auto mass = ( c * rho ) / dt;

        auto conductivities = array::multiply( kscaling1, k );

        linalg::symmetricElementLhs( targets[0].data( ), ndof, nblocks, [&]( size_t i, size_t j )
        {
            auto value = N[i] * N[j] * mass;

            for( size_t axis = 0; axis < D; ++axis )
            {
                value += dN[axis * ndofpadded + i] * dN[axis * ndofpadded + j] * conductivities[axis];

            } // component

            return value * weightDetJ;
        } );

        auto dcold = ( c * rho * u ) / dt;
        auto dcnew = ( c * rho * ambientTemperatureFunction( shapes1.xyz( ) ) ) / dt;

        linalg::elementRhs( targets[1].data( ), ndof, nblocks, [&]( size_t i )
        {
            auto value = ( history0 == MaterialType::Air ) ? N[i] * dcnew : N[i] * dcold;

            return value * weightDetJ;
        } );
    };

    auto types = std::vector { AssemblyType::SymmetricMatrix, AssemblyType::Vector };

    return BasisProjectionIntegrand<D>( types, DiffOrders::FirstDerivatives, evaluate );
}

using NonlinearFlux = std::function<std::array<double, 2>( double T )>;

template<size_t D> inline
auto makeNonlinearFluxIntegrand( const NonlinearFlux& flux,
                                 memory::vptr<const std::vector<double>>&& dofs )
{
    auto evaluate = [=, dofs = std::move( dofs )]( typename SurfaceIntegrand<D>::Cache&,
                                                   const BasisFunctionEvaluation<D>& shapes,
                                                   const LocationMap& locationMap,
                                                   std::array<double, D> /* normal */,
                                                   AlignedDoubleVectors& targets,
                                                   double weightDetJ )
    {
        auto u = evaluateSolution( shapes, locationMap, *dofs );

        auto [f, df] = flux( u );

        auto N = shapes.noalias( 0, 0 );
        auto ndof = shapes.ndof( );
        auto nblocks = shapes.nblocks( );

        auto left = df * weightDetJ;
        auto right = f * weightDetJ;

        linalg::symmetricElementLhs( targets[0].data( ), ndof, nblocks, 
                                     [&]( size_t idof, size_t jdof )
        { 
            return N[idof] * N[jdof] * left;
        } );

        linalg::elementRhs( targets[1].data( ), ndof, nblocks, [&]( size_t idof )
        { 
            return N[idof] * right;
        } );
    };

    auto types = std::vector { AssemblyType::SymmetricMatrix, AssemblyType::Vector };

    return makeSurfaceIntegrand<D>( std::move( types ), DiffOrders::Shapes, std::move( evaluate ) );
}

template<size_t D> inline
auto makeConvectionRadiationIntegrand( memory::vptr<const std::vector<double>> dofs,
                                       double emissivity,
                                       double conductivity,
                                       double ambientTemperature,
                                       double boltzmannConstant,
                                       double theta )
{
    MLHP_CHECK( theta == 1.0, "Convection radiation only implemented for backward euler." );

    auto flux = [=]( double T ) noexcept -> std::array<double, 2>
    {
        auto dT = T - ambientTemperature;
        auto pT = T + ambientTemperature;

        auto f = conductivity * dT + boltzmannConstant * emissivity * dT * dT * pT * pT;
        auto df = conductivity + boltzmannConstant * emissivity * 2.0 * dT * pT * ( pT + dT );
        
        return { f, df };
    };

    return makeNonlinearFluxIntegrand<D>( std::move( flux ), std::move( dofs ) );
}

template<size_t D> inline
auto makeSteadyStateThermalIntegrand( const MaterialPtrs& materials,
                                      const spatial::ScalarFunction<D>& sourceFunction,
                                      const ThermalHistory<D>& historyContainer,
                                      const std::vector<double>& dofs,
                                      std::array<double, D> laserVelocity )
{
    auto evaluate = [=, &historyContainer, &dofs]( const BasisFunctionEvaluation<D>& shapes,
                                const LocationMap& locationMap,
                                AlignedDoubleVectors& targets, 
                                AlignedDoubleVector&, 
                                double weightDetJ )
    {
        auto ndof = shapes.ndof( );
        auto nblocks = shapes.nblocks( );
        auto ndofpadded = shapes.ndofpadded( );

        auto N = shapes.noalias( 0, 0 );
        auto dN = shapes.noalias( 0, 1 );

        auto u = 0.0;
        auto du = std::array<double, D> { };

        for( size_t i = 0; i < ndof; ++i )
        {
            auto dof = dofs[locationMap[i]];

            u += dof * N[i];

            for( size_t axis = 0; axis < D; ++axis )
            {
                du[axis] += dN[axis * ndofpadded + i] * dof;
            }
        }

        auto material = materialFor( materials, historyContainer( shapes.xyz( ) ) );

        auto [rho, drho] = material->density( u );
        auto [c, dc] = material->specificHeatCapacity( u );
        auto [k, dk] = material->heatConductivity( u );
        auto [L, dL, ddL] = evaluatePhaseTransition( *material, u );

        auto m = rho * c + dL;
        auto dm = rho * dc + drho * c + ddL;
        auto source = sourceFunction( shapes.xyz( ) );

        auto karray = array::make<D>( k );
        auto dkarray = array::make<D>( dk );

        linalg::unsymmetricElementLhs( targets[0].data( ), ndof, nblocks, [&]( size_t i, size_t j )
        {
            auto advection = 0.0;
            auto diffusion = 0.0;
                        
            for( size_t axis = 0; axis < D; ++axis )
            {
                auto dNj = dN[axis * ndofpadded + j];

                advection += N[i] * laserVelocity[axis] * ( m * dNj + dm * du[axis] * N[j] );
            }

            for( size_t axis = 0; axis < D; ++axis )
            {
                auto dNi = dN[axis * ndofpadded + i];
                auto dNj = dN[axis * ndofpadded + j];

                diffusion += dNi * ( karray[axis] * dNj + dkarray[axis] * du[axis] * N[j] );
            }

            return ( diffusion - advection ) * weightDetJ;
        } );

        linalg::elementRhs( targets[1].data( ), ndof, nblocks, [&]( size_t i )
        {
            auto advection = 0.0;
            auto diffusion = 0.0;
            
            for( size_t axis = 0; axis < D; ++axis )
            {
                advection += N[i] * ( laserVelocity[axis] * m * du[axis] );
            }

            for( size_t axis = 0; axis < D; ++axis )
            {
                diffusion += dN[axis * ndofpadded + i] * karray[axis] * du[axis];
            }

            return ( diffusion - advection - N[i] * source ) * weightDetJ;
        } );
    };

    auto types = std::vector { AssemblyType::UnsymmetricMatrix, AssemblyType::Vector };

    return DomainIntegrand<D>( types, DiffOrders::FirstDerivatives, evaluate );
}

namespace
{

template<size_t D> inline
auto crossVector( const JacobianMatrix<D, D - 1>& jacobian )
{
    MLHP_CHECK( D == 3, "Dimension not implemented" );

    //auto J = linalg::adapter( jacobian, D );
    //
    //auto v1 = std::array { J( 0, 0 ), J( 1, 0 ), J( 2, 0 ) };
    //auto v2 = std::array { J( 0, 1 ), J( 1, 1 ), J( 2, 1 ) };
    auto& J = jacobian;
    auto v1 = std::array { J[0], J[2], J[4] };
    auto v2 = std::array { J[1], J[3], J[5] };
    return spatial::cross( v1, v2 );
}

template<size_t D> inline
auto faceDiameter( const JacobianMatrix<D, D - 1>& J )
{
    MLHP_CHECK( D == 3, "Dimension not implemented" );

    auto d1 = spatial::normSquared( std::array { J[0], J[2], J[4] } );
    auto d2 = spatial::normSquared( std::array { J[1], J[3], J[5] } );

    return std::sqrt( std::max( d1, d2 ) );
}

template<size_t D> inline
auto materialAtSubcell( const AbsHierarchicalGrid<D>& temperatureGrid,
                        const ThermalHistory<D>& thermalHistory,
                        CellIndex temperatureFullIndex, 
                        std::array<double, D> rst,
                        std::array<double, D> xyz )
{
    auto historyCell0 = mesh::findInOtherGrid( temperatureGrid, *thermalHistory.grid, temperatureFullIndex );

    return thermalHistory( historyCell0.otherCell, rst, xyz );
}

// https://link.springer.com/article/10.1007/s10092-003-0073-2
template<size_t D> inline
auto makeFluxJumpIntegrand( [[maybe_unused]] const MaterialPtrs& materials,
                            [[maybe_unused]] const AbsHierarchicalGrid<D>& temperatureGrid,
                            [[maybe_unused]] const std::vector<double>& dofs,
                            [[maybe_unused]] const ThermalHistory<D>& historyContainer )
{
    auto integrateFluxJumps = [=, &dofs]( const BasisFunctionEvaluation<D>& shapes0,
                                          const BasisFunctionEvaluation<D>& shapes1,
                                          const LocationMap& locationMap0,
                                          const LocationMap& locationMap1,
                                          std::array<double, D> normal,
                                          double diameter0,
                                          double diameter1,
                                          AlignedDoubleVector& targets,
                                          double weightDetJ )
    {
        //auto u0 = evaluateSolution( shapes0, locationMap0, dofs );
        //auto u1 = evaluateSolution( shapes1, locationMap1, dofs );
        //
        //auto fullIndex0 = temperatureGrid.fullIndex( shapes0.elementIndex( ) );
        //auto fullIndex1 = temperatureGrid.fullIndex( shapes1.elementIndex( ) );
        //
        //auto material0 = materialAtSubcell( temperatureGrid, historyContainer, fullIndex0, shapes0.rst( ), shapes0.xyz( ) );
        //auto material1 = materialAtSubcell( temperatureGrid, historyContainer, fullIndex1, shapes1.rst( ), shapes1.xyz( ) );
        //
        //auto k0 = materialFor( materials, material0 )->heatConductivity( u0 )[0];
        //auto k1 = materialFor( materials, material1 )->heatConductivity( u1 )[0];
        //
        //auto flux0 = spatial::dot( array::multiply( du0, k0 ), normal );
        //auto flux1 = spatial::dot( array::multiply( du1, k1 ), normal );

        auto du0 = evaluateGradient( shapes0, locationMap0, dofs );
        auto du1 = evaluateGradient( shapes1, locationMap1, dofs );

        auto flux0 = spatial::dot( du0, normal );
        auto flux1 = spatial::dot( du1, normal );

        //auto h0 = utilities::integerPow( 0.5, temperatureGrid.refinementLevel( fullIndex0 ) );
        //auto h1 = utilities::integerPow( 0.5, temperatureGrid.refinementLevel( fullIndex1 ) );

        auto jumpSquared = utilities::integerPow( flux1 - flux0, 2 );

        targets[0] += jumpSquared * diameter0 * weightDetJ;
        targets[1] += jumpSquared * diameter1 * weightDetJ;
    };

    return integrateFluxJumps;
}

} // namespace

template<size_t D> inline
auto integrateError( const MaterialPtrs& materials,
                     const MultilevelHpBasis<D>& basis,
                     const std::vector<double>& dofs,
                     const ThermalHistory<D>& history )
{
    auto nelements = static_cast<std::int64_t>( basis.nelements( ) );
    auto errors = std::vector<double>( basis.nelements( ), 0.0 );
    auto& mesh = basis.hierarchicalGrid( );
    auto maxdiff = size_t { 1 };
    auto integrand = makeFluxJumpIntegrand( materials, mesh, dofs, history );

    [[maybe_unused]] auto chunksize = parallel::clampChunksize( basis.nelements( ), 13, 2 );

    #pragma omp parallel
    {
        auto neighbours = std::vector<MeshCellFace> { };
        auto interfaceMapping0 = mesh.createInterfaceMapping( );
        auto interfaceMapping1 = mesh.createInterfaceMapping( );
        auto locationMap0 = LocationMap { };
        auto locationMap1 = LocationMap { };
        auto shapes0 = BasisFunctionEvaluation<D> { };
        auto shapes1 = BasisFunctionEvaluation<D> { };
        auto basisCache0 = basis.createEvaluationCache( );
        auto basisCache1 = basis.createEvaluationCache( );
        auto rs = CoordinateGrid<D - 1> { };
        auto weights = std::vector<double> { };
        auto quadratureCache = QuadraturePointCache { };
        auto targets = AlignedDoubleVector( 2 );

        #pragma omp for schedule(dynamic, chunksize)
        for( std::int64_t ii = 0; ii < nelements; ++ii )
        {
            auto ielement0 = static_cast<CellIndex>( ii );
            auto nfaces = mesh.nfaces( ielement0 );
            targets[0] = 0.0;

            basis.locationMap( ielement0, utilities::resize0( locationMap0 ) );

            auto maxdegrees0 = basis.prepareEvaluation( ielement0, maxdiff, shapes0, basisCache0 );
            auto& elementMapping0 = basis.mapping( basisCache0 );
            
            for( size_t iface0 = 0; iface0 < nfaces; ++iface0 )
            {
                mesh.neighbours( ielement0, iface0, utilities::resize0( neighbours ) );

                for( auto [ielement1, iface1] : neighbours )
                {
                    if( ielement1 < ielement0 )
                    {
                        utilities::resize0( rs, weights, locationMap1 );

                        basis.locationMap( ielement1, locationMap1 );

                        auto maxdegrees1 = basis.prepareEvaluation( ielement1, maxdiff, shapes1, basisCache1 );
                        auto maxdegree = std::max( array::maxElement( maxdegrees0 ), array::maxElement( maxdegrees1 ) );
                        auto orders = array::makeSizes<D - 1>( maxdegree + 1 );

                        mesh.prepareInterfaceMappings( { ielement0, iface0 }, { ielement1, iface1 },
                            *interfaceMapping0, *interfaceMapping1 );

                        tensorProductQuadrature( orders, rs, weights, quadratureCache );

                        targets[1] = 0.0;

                        nd::executeWithIndex( orders, [&]( std::array<size_t, D - 1> ij, size_t ipoint )
                        {
                            auto [rst0, JInterface0] = map::withJ( *interfaceMapping0, array::extract( rs, ij ) );
                            auto [rst1, JInterface1] = map::withJ( *interfaceMapping1, array::extract( rs, ij ) );
                            
                            auto Jelement0 = elementMapping0.J( rst0 );
                            auto Jelement1 = elementMapping0.J( rst1 );

                            auto J0 = spatial::concatenateJacobians<D, D, D - 1>( JInterface0, Jelement0 );
                            auto J1 = spatial::concatenateJacobians<D, D, D - 1>( JInterface1, Jelement1 );

                            auto detJ0 = spatial::computeDeterminant<D, D - 1>( J0 );
                            auto normal0 = spatial::normalize( crossVector<D>( J0 ) );

                            auto d0 = faceDiameter<D>( J0 );
                            auto d1 = faceDiameter<D>( J1 );

                            basis.evaluateSinglePoint( rst0, shapes0, basisCache0 );
                            basis.evaluateSinglePoint( rst1, shapes1, basisCache1 );

                            integrand( shapes0, shapes1, locationMap0, locationMap1, normal0, d0, d1, targets, weights[ipoint] * detJ0 );
                        } );

                        #pragma omp atomic
                        errors[ielement1] += targets[1];
                    }
                } // for neighbors
            } // for iface0

            #pragma omp atomic
            errors[ielement0] += targets[0];

        } // for elements
    
        #pragma omp barrier
        { }

        #pragma omp for schedule(static)
        for( std::int64_t ii = 0; ii < nelements; ++ii )
        {
            auto ielement = static_cast<size_t>( ii );

            errors[ielement] = std::sqrt( errors[ielement] );
        }
    } // omp parallel


    return errors;
}

template<size_t D> inline
CellMeshCreator<D> clippedPostprocessingMesh( double topSurface,
                                              std::array<size_t, D> resolution,
                                              PostprocessTopologies topologies )
{
    auto resolutionDeterminor = [=]( const MeshMapping<D>& mapping ) -> std::array<size_t, D>
    {
        auto newresolution = resolution;
        auto zmin = mapping.map( array::make<D>( -1.0 ) ).back( );
        auto zmax = mapping.map( array::make<D>( 1.0 ) ).back( );

        auto eps = 1e-5 * ( zmax - zmin );

        MLHP_CHECK( zmin < zmax, "Collappsed finite element." );

        if( zmin >= topSurface - eps || resolution.back( ) == 0 )
        {
            return { };
        }

        if( zmax > topSurface )
        {
            auto dz = ( zmax - zmin ) / resolution.back( );

            newresolution.back( ) = static_cast<size_t>( std::max( ( topSurface - zmin ) / dz, 1.0 ) );
        }

        return newresolution;
    };

    auto createGrid = cellmesh::grid<D>( resolutionDeterminor, topologies );

    return [=, createGrid = std::move( createGrid )]( const MeshMapping<D>& mapping,
                                                      std::array<std::vector<double>, D>& pointData,
                                                      std::vector<std::int64_t>& connectivity,
                                                      std::vector<std::int64_t>& offsets,
                                                      std::vector<std::int8_t>& vtkTypes,
                                                      std::any& anyCache ) -> bool
    {
        auto isgrid = createGrid( mapping, pointData, connectivity, offsets, vtkTypes, anyCache );

        auto zmin = mapping.map( array::make<D>( -1.0 ) ).back( );
        auto zmax = mapping.map( array::make<D>( 1.0 ) ).back( );

        if( zmax > topSurface )
        {
            auto factor = ( topSurface - zmin ) / ( zmax - zmin );

            for( auto& z : pointData.back( ) )
            {
                z = ( ( z + 1.0 ) * factor ) - 1.0;
            }
        }

        return isgrid;
    };
}

template<size_t D> inline
auto filterInternalBoundaryTopologies( std::array<std::vector<double>, D>& pointData,
                                       std::vector<std::int64_t>& connectivity,
                                       std::vector<std::int64_t>& offsets,
                                       std::vector<std::int8_t>& vtkTypes, 
                                       size_t cellBegin )
{
    MLHP_CHECK( D == 3, "Not implemented for D != 3." );

    if( pointData.front( ).empty( ) || cellBegin == offsets.size( ) )
    {
        return;
    }

    auto bounds = spatial::BoundingBox<D> { };

    for( size_t axis = 0; axis < D; ++axis )
    {
        bounds[0][axis] = *std::min_element( pointData[axis].begin( ), pointData[axis].end( ) );
        bounds[1][axis] = *std::max_element( pointData[axis].begin( ), pointData[axis].end( ) );
    }

    auto cellCount = cellBegin;
    auto connCount = cellBegin == 0 ? size_t { 0 } : static_cast<size_t>( offsets[cellBegin - 1] );

    for( size_t icell = cellBegin; icell < offsets.size( ); ++icell )
    {
        auto keepCell = true;
        auto pointBegin = icell == 0 ? size_t { 0 } : static_cast<size_t>( offsets[icell - 1] );

        if( vtkTypes[icell] != 11 && vtkTypes[icell] != 12 )
        {
            auto nvertices = offsets[icell] - static_cast<std::int64_t>( pointBegin );

            MLHP_CHECK( vtkTypes[icell] == 3 && nvertices == 2, "Invalid cell." );

            auto isOnEdge = [&bounds]( std::array<double, D> rst )
            { 
                auto boundaryCount = size_t { 0 };

                for( size_t axis = 0; axis < D; ++axis )
                {
                    boundaryCount += std::abs( rst[axis] - bounds[0][axis] ) < 1e-8;
                    boundaryCount += std::abs( rst[axis] - bounds[1][axis] ) < 1e-8;
                }

                return boundaryCount >= 2;
            };

            auto rst0 = array::extract( pointData, array::makeSizes<D>( static_cast<size_t>( connectivity[pointBegin] ) ) );
            auto rst1 = array::extract( pointData, array::makeSizes<D>( static_cast<size_t>( connectivity[pointBegin + 1] ) ) );
            auto rst2 = spatial::interpolate( rst0, rst1, 0.5 );

            keepCell = isOnEdge( rst0 ) && isOnEdge( rst1 ) && isOnEdge( rst2 );
        }

        if( keepCell )
        {
            for( auto ilocal = pointBegin; ilocal < static_cast<size_t>( offsets[icell] ); ++ilocal )
            {
                connectivity[connCount++] = connectivity[ilocal];
            }

            offsets[cellCount] = static_cast<std::int64_t>( connCount );
            vtkTypes[cellCount] = vtkTypes[icell];

            cellCount += 1;
        }
    }

    offsets.resize( cellCount );
    vtkTypes.resize( cellCount );
    connectivity.resize( connCount );
}

template<size_t D> inline
CellMeshCreator<D> materialRefinedPostprocessingGrid( const CellMeshCreator<D>& meshCreator,
                                                      const HierarchicalGridSharedPtr<D>& temperatureGrid,
                                                      const HierarchicalGridSharedPtr<D>& materialGrid )
{
    return [=]( const MeshMapping<D>& mapping,
                std::array<std::vector<double>, D>& pointData,
                std::vector<std::int64_t>& connectivity,
                std::vector<std::int64_t>& offsets,
                std::vector<std::int8_t>& vtkTypes,
                std::any& anyCache ) -> bool
    {
        struct Cache
        {
            std::vector<mesh::SharedSupport<D>> supports;
            std::array<std::vector<double>, D> rst;
            std::any subCache;
        };

        if( !anyCache.has_value( ) )
        {
            anyCache = Cache { };
        }

        auto& [sharedSupports, rst_, subCache] = std::any_cast<Cache&>( anyCache );

        mesh::findInOtherGrid( *temperatureGrid, *materialGrid, utilities::resize0( 
            sharedSupports ), temperatureGrid->fullIndex( mapping.icell ) );

        auto fullMapping = MeshMapping<D> { };
        auto offsetsSize0 = offsets.size( );

        MLHP_CHECK( array::elementSizes( pointData ) == array::makeSizes<D>( 0 ), "Invalid postprocessing grid." );

        for( auto& support : sharedSupports )
        {
            auto& submapping = support.thisCell;
            auto& rst = rst_;

            auto fullMapping2 = ConcatenatedMapping<D> { &mapping, &submapping };
            fullMapping.reset( fullMapping2, mapping.icell );

            auto npoints0 = pointData.front( ).size( );
            auto connectivitySize = connectivity.size( );

            auto isgrid = meshCreator( fullMapping, utilities::resize0( rst ), connectivity, offsets, vtkTypes, subCache );

            MLHP_CHECK( isgrid, "Invalid mesh creator (no grid)." );

            submapping.mapGrid( rst );

            nd::execute( array::elementSizes( rst ), [&]( std::array<size_t, D> ijk )
            { 
                for( size_t axis = 0; axis < D; ++axis )
                {
                    pointData[axis].push_back( rst[axis][ijk[axis]] );
                }
            } );

            for( size_t i = connectivitySize; i < connectivity.size( ); ++i )
            {
                connectivity[i] += static_cast<std::int64_t>( npoints0 );
            }
        }

        filterInternalBoundaryTopologies( pointData, connectivity, offsets, vtkTypes, offsetsSize0 );
        
        return false;
    };
}

inline 
MeshWriter addThermalHistoryOutput( const MeshWriter& meshWriter,
                                    const ThermalHistory<3>& history,
                                    std::string dataSetName )
{
    auto writer = std::make_shared<MeshWriter>( MeshWriter { meshWriter } );
    auto stateContainer = std::make_shared<utilities::ThreadLocalContainer<std::vector<double>>>( );

    struct Cache
    {
        MeshWriter::Cache cache;
        size_t stateIndex;
    };

    auto initialize = [=]( size_t npartitions, const std::vector<Output>& outputs )
    { 
        auto cache = writer->initialize( npartitions, outputs );
        auto predicate = [=]( auto& v ) { return v.name == dataSetName; };
        auto it = std::find_if( outputs.begin( ), outputs.end( ), predicate );
        auto index = static_cast<size_t>( std::distance( outputs.begin( ), it ) );

        MLHP_CHECK( it != outputs.end( ), "Did not find data set name in outputs." );

        return MeshWriter::Cache { Cache { .cache = std::move( cache ), .stateIndex = index } };
    };

    auto writePartition = [=]( MeshWriter::Cache& anyCache,
                               const OutputMeshPartition& partition,
                               const std::vector<std::vector<double>>& data )
    {
        auto& cache = utilities::cast<Cache>( anyCache );
        auto& state = stateContainer->get( );

        state.resize( partition.points.size( ) / 3 );

        auto foreachCell = [&]( auto&& callback )
        { 
            for( size_t icell = 0; icell < partition.offsets.size( ); ++icell )
            {
                auto offset0 = icell == 0 ? std::int64_t { 0 } : partition.offsets[icell - 1];

                callback( icell, static_cast<size_t>( offset0 ), static_cast<size_t>( partition.offsets[icell] ) );
            }
        };

        foreachCell( [&]( auto icell, auto offset0, auto offset1 )
        { 
            if( partition.types[icell] == 11 || partition.types[icell] == 12 )
            {
                auto sum = std::array<double, 3> { };
                auto minz = std::numeric_limits<double>::max( );

                for( auto ipoint = offset0; ipoint < offset1; ++ipoint )
                {
                    auto pointIndex = static_cast<size_t>( partition.connectivity[ipoint] );

                    for( size_t axis = 0; axis < 3; ++axis )
                    {
                        sum[axis] += partition.points[3 * pointIndex + axis];
                    }

                    minz = std::min( minz, partition.points[3 * pointIndex + 2] );
                }

                auto midpoint = sum / static_cast<double>( offset1 - offset0 );
                
                //// If top surface is below, move evaluation point lower until the smallest z-value of the cell 
                //auto newz = std::max( std::min( midpoint.back( ), history.topSurface ), minz );
                //
                //midpoint.back( ) = 0.9999 * newz + 0.0001 * midpoint.back( );

                auto material = static_cast<double>( history( midpoint ) );

                for( auto ipoint = offset0; ipoint < offset1; ++ipoint )
                {
                    state[static_cast<size_t>( partition.connectivity[ipoint] )] = material;
                }
            }       
        } );

        foreachCell( [&]( auto icell, auto offset0, auto )
        { 
            auto& casted = const_cast<std::vector<double>&>( data[cache.stateIndex] );

            casted[icell] = state[static_cast<size_t>( partition.connectivity[offset0] )];
        } );

        writer->writePartition( cache.cache, partition, data );
    };

    auto finalize = [=]( MeshWriter::Cache& anyCache )
    {
        auto& cache = utilities::cast<Cache>( anyCache );

        writer->finalize( cache.cache );
    };

    return
    {
        .initialize = std::move( initialize ),
        .writePartition = std::move( writePartition ),
        .finalize = std::move( finalize ),
        .maxpartitions = writer->maxpartitions
    };
}

template<size_t D>
auto refineConstrained( AbsHierarchicalGrid<D>& refinedGrid,
                        const RefinementFunction<D>& refinementStrategy,
                        double topSurface )
{
    MLHP_CHECK( refinedGrid.ncells( ) == refinedGrid.baseGrid( ).ncells( ), "Grid was already refined." );

    auto begin = CellIndex { 0 };
    auto end = refinedGrid.nfull( );
    auto refinementLevel = RefinementLevel { 0 };

    while( begin != end )
    {
        auto refinementMask = std::vector<std::uint8_t>( end - begin, 0 );

        [[maybe_unused]] auto chunksize = parallel::clampChunksize( refinementMask.size( ), 6, 2 );

        #pragma omp parallel 
        {
            auto mapping = refinedGrid.createMapping( );

            #pragma omp for schedule(dynamic, chunksize)
            for( std::int64_t index = 0; index < static_cast<std::int64_t>( end - begin ); ++index )
            {
                if( auto icell = static_cast<CellIndex>( index ); refinedGrid.isLeaf( begin + icell ) )
                {
                    refinedGrid.prepareMapping( refinedGrid.leafIndex( begin + icell ), mapping );

                    auto zmin = mapping( array::make<D>( -1.0 ) )[D - 1];
                    auto zmax = mapping( array::make<D>( 1.0 ) )[D - 1];
                    auto eps = 1e-10 * ( zmax - zmin );

                    // If parts of the element are below the top surface
                    if( zmin < topSurface - eps )
                    {
                        refinementMask[icell] = refinementStrategy( mapping, refinementLevel );

                        // If we refine this and the element touches or crosses the top surface
                        if( refinementMask[icell] && zmax >= topSurface - eps )
                        {
                            auto neighborAbove = refinedGrid.neighbour(icell + begin, D - 1, 1);

                            if( neighborAbove != NoCell )
                            {
                                refinementMask[neighborAbove - begin] = true;
                            }
                        }
                    }
                }
            }
        }

        auto indices = algorithm::forwardIndexMap<CellIndex>( refinementMask );

        for( auto& index : indices )
        {
            index = refinedGrid.leafIndex( index + begin );
        }

        refinedGrid.refine( indices );

        begin = end;
        end = refinedGrid.nfull( );
        refinementLevel += 1;
    }
}

template<size_t D>
std::optional<double> mapTopSurfaceToLocal( const AbsMapping<D>& mapping, 
                                            double topSurface, 
                                            double eps0, 
                                            double eps1 )
{
    auto z0 = mapping( array::setEntry<double, D>( { }, D - 1, -1.0 ) )[D - 1];
    auto z1 = mapping( array::setEntry<double, D>( { }, D - 1, +1.0 ) )[D - 1];

    if( z0 + eps0 * ( z1 - z0 ) < topSurface && topSurface < z1 + eps1 * ( z1 - z0) )
    {
        return utilities::mapToLocal1( z0, z1, topSurface );
    }

    return std::nullopt;
}

template<size_t D>
class TopSurfacePartitioner : public AbsQuadrature<D>
{
    double topSurface_;
    memory::vptr<const AbsQuadrature<D>> quadrature_;

public:
    TopSurfacePartitioner( double topSurface,
                           memory::vptr<const AbsQuadrature<D>> quadrature ) noexcept :
        topSurface_ { topSurface }, quadrature_ { quadrature }
    { }

    struct Cache
    {
        std::array<CartesianMapping<D>, 2> submappings = { CartesianMapping<D> { }, CartesianMapping<D> { } };
        std::array<const AbsMapping<D>*, 2> submappingPtrs = { nullptr, nullptr };

        std::vector<SubcellCache<D>> subcellCache;
        std::vector<size_t> mapToSubcell;
    };

    QuadratureCache<D> initialize( ) const override
    {
        return Cache{ };
    }
    
    size_t partition( const MeshMapping<D>& mapping,
                      QuadratureCache<D>& anyCache ) const override
    {
        auto& cache = utilities::cast<Cache>( anyCache );

        cache.submappingPtrs[0] = &cache.submappings[0];
        cache.submappingPtrs[1] = &cache.submappings[1];

        auto t = mapTopSurfaceToLocal( mapping, topSurface_, 1e-10, -1e-10 );

        auto bounds0 = array::make<D>( -1.0 );
        auto bounds1 = array::make<D>( 1.0 );

        // top surface is within z-interval
        if( t )
        {
            cache.submappings[0] = CartesianMapping<D>( { bounds0, array::setEntry( bounds1, D - 1, *t ) } );
            cache.submappings[1] = CartesianMapping<D>( { array::setEntry( bounds0, D - 1, *t ), bounds1 } );
        }
        else
        {
            cache.submappings[0] = CartesianMapping<D>( { bounds0, bounds1 } );
        }

        auto subcells = std::span( cache.submappingPtrs.begin( ), 1 + ( t != std::nullopt ) );

        return cacheQuadratureCells<D>( *quadrature_, mapping, subcells, cache.subcellCache, cache.mapToSubcell );
    }

    bool distribute( size_t ipartition,
                     std::array<size_t, D> orders,
                     CoordinateGrid<D>& rstGrid,
                     CoordinateList<D>& xyzList,
                     std::vector<double>& weights,
                     QuadratureCache<D>& anyCache ) const override
    {
        auto& cache = utilities::cast<Cache>( anyCache );
        auto& isubcell = cache.mapToSubcell[ipartition];
        auto& [meshMapping, quadratureCache, offset] = cache.subcellCache[isubcell];

        auto isgrid = quadrature_->distribute( ipartition - offset, orders, 
            rstGrid, xyzList, weights, quadratureCache );

        MLHP_CHECK( isgrid, "Quadrature points must be a grid." );

        cache.submappings[isubcell].mapGrid( rstGrid );

        return true;
    }
};

template<size_t D>
class TopSurfaceBoundaryQuadrature : public AbsQuadratureOnMesh<D>
{
    struct Cache
    {
        QuadraturePointCache quadrature;
        CoordinateList<D - 1> rs = { };
    };

    double topSurface_;
    QuadratureOrderDeterminor<D> order_;

public:
    TopSurfaceBoundaryQuadrature( double topSurface,
                                  QuadratureOrderDeterminor<D> order ) noexcept :
        topSurface_ { topSurface }, order_ { std::move( order ) }
    { }

    typename AbsQuadratureOnMesh<D>::AnyCache initialize( ) const override
    {
        return Cache { };
    }

    void distribute( const MeshMapping<D>& mapping,
                     std::array<size_t, D> orders,
                     CoordinateList<D>& rst,
                     CoordinateList<D>& normals,
                     std::vector<double>& weights,
                     typename AbsQuadratureOnMesh<D>::AnyCache& anyCache ) const override
    {
        MLHP_CHECK( mapping.type == CellType::NCube, "Invalid cell type." );

        // Prevent duplicates on element interfaces. This will exclude the bottom
        // boundary faces, but those should never be the top surface. Right?
        if( auto t = mapTopSurfaceToLocal( mapping, topSurface_, 1e-10, 1e-10 ) )
        {
            auto& cache = utilities::cast<Cache>( anyCache );
            auto order = array::maxElement( order_( mapping.icell, orders ) );
            auto wsize = weights.size( );

            utilities::resize0( cache.rs );
            
            tensorProductQuadrature( array::make<D - 1>( order ), 
                cache.rs, weights, cache.quadrature );
            
            auto npoints = cache.rs.size( );
            auto [rsize, nsize] = utilities::increaseSizes( npoints, rst, normals );

            for( size_t ipoint = 0; ipoint < npoints; ++ipoint )
            {
                auto coords = array::insert( cache.rs[ipoint], D - 1, *t );
                auto [xyz, J] = map::withJ( mapping, coords );
                
                MLHP_CHECK( spatial::isDiagonal<D>( J, 1e-12 ), "Jacobian is not diagonal." );

                for( size_t axis = 0; axis + 1 < D; ++axis )
                {
                    weights[wsize + ipoint] *= J[axis * D + axis];
                }

                rst[rsize + ipoint] = coords;
                normals[nsize + ipoint] = spatial::standardBasisVector<D>( D - 1 );
            }
        }
    }
};

} // namespace mlhp

#endif // MLHPBF_THERMAL_HPP
