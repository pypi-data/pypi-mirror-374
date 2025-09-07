// This file is part of the mlhpbf project. License: See LICENSE

#ifndef MLHPBF_MECHANICAL_HPP
#define MLHPBF_MECHANICAL_HPP

#include "meltstate.hpp"

namespace mlhp
{

template<size_t D>
using ThermalEvaluator = std::function<std::tuple<double, const Material*, double>( std::array<double, D> )>;

template<size_t D> inline
ThermalEvaluator<D> makeThermalEvaluator( const BasisConstSharedPtr<D>& tbasis0,
                                          const BasisConstSharedPtr<D>& tbasis1,
                                          memory::vptr<const std::vector<double>> tdofs0,
                                          memory::vptr<const std::vector<double>> tdofs1,
                                          const ThermalHistory<D>& thermalHistory1,
                                          const MaterialPtrs& materials,
                                          double ambientTemperature )
{
    auto evaluate0 = basis::scalarEvaluator<3>( tbasis0, tdofs0 );
    auto evaluate1 = basis::scalarEvaluator<3>( tbasis1, tdofs1 );

    return [evaluate0 = std::move( evaluate0 ), 
            evaluate1 = std::move( evaluate1 ), 
            &thermalHistory1, materials, ambientTemperature]( std::array<double, D> xyz )
    { 
        auto T1 = evaluate1( xyz );
        auto T0 = evaluate0( xyz );

        auto material = materialFor( materials, thermalHistory1( xyz ) );

        auto exp0 = material->thermalExpansionCoefficient( T0 )[0];
        auto exp1 = material->thermalExpansionCoefficient( T1 )[0];

        if( T0 > T1 && material->thermalExpansionCoefficientCooling != nullptr )
        {
            exp0 = material->thermalExpansionCoefficientCooling( T0 )[0];
            exp1 = material->thermalExpansionCoefficientCooling( T1 )[0];
        }

        auto e0 = ( T0 - ambientTemperature ) * exp0;
        auto e1 = ( T1 - ambientTemperature ) * exp1;

        return std::tuple { T1, material, e0 - e1 };
    };
}

template<size_t D> inline
ThermalEvaluator<D> makeThermalEvaluator( const BasisConstSharedPtr<D>& tbasis,
                                          memory::vptr<const std::vector<double>> tdofs,
                                          const ThermalHistory<D>& thermalHistory,
                                          const MaterialPtrs& materials )
{
    auto evaluate = basis::scalarEvaluator<3>( tbasis, tdofs );

    return [evaluate = std::move( evaluate ), &thermalHistory, materials]( std::array<double, D> xyz )
    { 
        auto T = evaluate( xyz );

        auto material = materialFor( materials, thermalHistory( xyz ) );

        return std::tuple { T, material, 0.0 };
    };
}

inline auto evaluateLinearElasticity( const Material* material, double T, const std::array<double, 6> strain )
{
    auto nu = material->poissonRatio( T )[0];
    auto tmp1 = ( 1.0 - 2.0 * nu );
    auto tmp2 = material->youngsModulus( T )[0] / ( ( 1.0 + nu ) * tmp1 );

    auto lambda = nu * tmp2;
    auto mu = 0.5 * tmp1 * tmp2;

    // Elastic tangent stiffness
    auto tangent = std::array<double, 6 * 6> { };
    auto D = linalg::adapter( tangent, 6 );
    auto diagonal = lambda + 2.0 * mu;

    D( 0, 0 ) = diagonal; D( 0, 1 ) = lambda;   D( 0, 2 ) = lambda;
    D( 1, 0 ) = lambda;   D( 1, 1 ) = diagonal; D( 1, 2 ) = lambda;
    D( 2, 0 ) = lambda;   D( 2, 1 ) = lambda;   D( 2, 2 ) = diagonal;
    D( 3, 3 ) = mu; D( 4, 4 ) = mu; D( 5, 5 ) = mu;

    // Trial stress
    auto stress = std::array<double, 6> { };

    linalg::mmproduct( tangent.data( ), strain.data( ), stress.data( ), 6, 6, 1 );
    
    return std::tuple { stress, tangent, mu };
}

struct PlasticityData
{
    std::array<double, 6> elasticStrain = { };
    std::array<double, 6> backstress = { };
    double effectivePlasticStrain;
    size_t nvariables = 13;
};

class J2Plasticity
{
private:
    std::array<double, 6> elasticStrainTrial, sigma, backstress0;
    std::array<double, 6 * 6> elasticTangent;
    double temperature, sigmaY, H, beta, mu, ep0, etaTrialNorm;
    const Material* material;

    struct Plasticity
    {
        double deltaLambda;
        std::array<double, 6> N;
    };

    std::optional<Plasticity> plasticity;

public:
    J2Plasticity( const ThermalEvaluator<3>& evaluator,
                  const PlasticityData& history0,
                  std::array<double, 6> totalStrainIncrement,
                  std::array<double, 3> xyz )
    {
        auto [T1, material_, thermalStrainIncrement] = evaluator( xyz );
        temperature = T1;
        material = material_;

        // Thermal strain
        totalStrainIncrement[0] += thermalStrainIncrement;
        totalStrainIncrement[1] += thermalStrainIncrement;
        totalStrainIncrement[2] += thermalStrainIncrement;

        // Trial stress
        backstress0 = history0.backstress;
        elasticStrainTrial = totalStrainIncrement + history0.elasticStrain;

        auto sigmaTrial = std::array<double, 6> { };
        auto unitTensor = std::array<double, 6> { 1.0, 1.0, 1.0, 0.0, 0.0, 0.0 };

        std::tie( sigmaTrial, elasticTangent, mu ) = evaluateLinearElasticity( material, temperature, elasticStrainTrial );

        auto sigmaTrialTrace = sigmaTrial[0] + sigmaTrial[1] + sigmaTrial[2];

        // Shifted stress
        auto etaTrial = sigmaTrial - history0.backstress - 1.0 / 3.0 * sigmaTrialTrace * unitTensor;

        etaTrialNorm = std::sqrt( etaTrial[0] * etaTrial[0] +
                                  etaTrial[1] * etaTrial[1] + 
                                  etaTrial[2] * etaTrial[2] +
                          2.0 * ( etaTrial[3] * etaTrial[3] + 
                                  etaTrial[4] * etaTrial[4] + 
                                  etaTrial[5] * etaTrial[5] ) );

        // Yield function
        sigmaY = material->yieldStress( temperature )[0];
        H = material->hardeningParameter( temperature )[0];
        beta = material->plasticModelSelector;
        
        auto Hn = H;
        ep0 = history0.effectivePlasticStrain;

        auto f =  etaTrialNorm - std::sqrt( 2.0 / 3.0 ) * ( sigmaY + ( 1.0 - beta ) * Hn * ep0 );
        
        // If elastic or liquid
        if( f < 0.0 || temperature >= material->annealingTemperature )
        {
            sigma = sigmaTrial;
        }
        else
        {
            plasticity = Plasticity { };

            // Consistency parameter: flow amount
            plasticity->deltaLambda = f / ( 2.0 * mu + 2.0 / 3.0 * H );

            // Unit deviatoric vector: flow direction
            plasticity->N = etaTrial / etaTrialNorm;

            // Update stress
            sigma = sigmaTrial - 2.0 * mu * plasticity->deltaLambda * plasticity->N;
        }
    }

    auto evaluateTangent( std::span<double, 6 * 6> tangentStiffness )
    {
        if( !plasticity )
        {
            std::copy( elasticTangent.begin( ), elasticTangent.end( ), tangentStiffness.begin( ) );
        }
        else
        {
            // Tangent stiffness
            auto c1 = 4.0 * mu * mu / ( 2.0 * mu + 2.0 / 3.0 * H );

            // Algorithmic contribution 
            auto c2 = 4.0 * mu * mu * plasticity->deltaLambda / etaTrialNorm;

            auto D = linalg::adapter( elasticTangent, 6 );
            auto Dalg = linalg::adapter( tangentStiffness, 6 );

            // Elastic with plastic correction
            for( size_t i = 0; i < 6; i++ )
            {
                for( size_t j = 0; j < 6; j++ )
                {
                    Dalg( i, j ) = D( i, j ) - ( c1 - c2 ) * plasticity->N[i] * plasticity->N[j];
                }
            }
            
            // Deviatoric projection
            for( size_t i = 0; i < 3; ++i )
            {
                for( size_t j = 0; j < 3; ++j )
                {
                    Dalg( i, j ) -= -1.0 / 3.0 * c2;
                }
                
                Dalg( i + 0, i + 0 ) -= c2;
                Dalg( i + 3, i + 3 ) -= c2 / 2.0;
            }
        }
    }

    auto evaluateStress( )
    {
        return sigma;
    }

    PlasticityData createNewHistory( )
    {
        auto history1 = PlasticityData { };

        if( !plasticity )
        {
            if( temperature < material->annealingTemperature )
            {
                history1.elasticStrain = elasticStrainTrial;
                history1.backstress = backstress0;
                history1.effectivePlasticStrain = ep0;
            }
            else
            {
                history1.elasticStrain = std::array<double, 6> { };
                history1.backstress = std::array<double, 6> { };
                history1.effectivePlasticStrain = 0.0;
            }
        }
        else
        {
            auto flowDirection = array::multiply( plasticity->N, std::array { 1.0, 1.0, 1.0, 2.0, 2.0, 2.0 } );

            history1.elasticStrain = elasticStrainTrial - plasticity->deltaLambda * flowDirection;
            history1.backstress = backstress0 + ( 2.0 / 3.0 ) * beta * H * plasticity->deltaLambda * plasticity->N;
            history1.effectivePlasticStrain = ep0 + std::sqrt( 2.0 / 3.0 ) * plasticity->deltaLambda;
        }

        history1.effectivePlasticStrain = std::max( 0.0, history1.effectivePlasticStrain );

        return history1;
    }
};

template<size_t D>
class AbsHistoryRepresentation : public utilities::DefaultVirtualDestructor
{
    HierarchicalGridSharedPtr<D> grid_; 
public:
    double topSurface;

    AbsHistoryRepresentation( const HierarchicalGridSharedPtr<D>& grid, double topSurface_ ) :
        grid_ { grid }, topSurface { topSurface_ }
    { }

    const AbsHierarchicalGrid<D>& grid( ) const { return *grid_; };
    const HierarchicalGridSharedPtr<D> gridPtr( ) const { return grid_; }

    PlasticityData evaluate( const AbsHierarchicalGrid<D>& otherGrid, 
                             CellIndex otherCell, 
                             std::array<double, D> otherRst,
                             std::array<double, D> xyz ) const
    {
        auto [historyCell, historyRst] = mesh::mapToOtherGrid( otherGrid, this->grid( ), otherCell, otherRst );

        return this->evaluate( historyCell, historyRst, xyz );
    }

    PlasticityData evaluate( CellIndex historyCell,
                             std::array<double, D> rst,
                             std::array<double, D> xyz ) const
    {
        if( xyz.back( ) > topSurface )
        {
            return PlasticityData { };
        }

        return evaluateInternal( historyCell, rst, xyz );
    }

    virtual std::shared_ptr<AbsHistoryRepresentation<D>> clone( ) const = 0;

private:
    virtual PlasticityData evaluateInternal( CellIndex historyCell, 
                                             std::array<double, D> rst, 
                                             std::array<double, D> xyz ) const = 0;

};

template<size_t D> inline
auto makeQuadraturePointIndexFinder( size_t quadratureOrder )
{
    auto points = gaussLegendrePoints( quadratureOrder )[0];
    auto strides = nd::stridesFor( array::make<D>( quadratureOrder ) );

    auto find1D = [=]( double r )
    {
        auto index = utilities::findInterval( points, r );
        auto local = utilities::mapToLocal0( points[index], points[index + 1], r );

        return local < 0.5 ? index : index + 1;
    };

    return [=]( std::array<double, D> rst )
    {
        auto index = size_t { 0 };

        for( size_t axis = 0; axis < D; ++axis )
        {
            index += strides[axis] * find1D( rst[axis] );
        }

        return index;
    };
}

template<size_t D>
class PiecewiseConstantHistoryGrid : public AbsHistoryRepresentation<D>
{
public:
    PiecewiseConstantHistoryGrid( const HierarchicalGridSharedPtr<D>& grid, size_t quadratureOrder, double topSurface_ ) :
        AbsHistoryRepresentation<D>( grid, topSurface_ ), quadratureOrder_ { quadratureOrder }
    { 
        indexFinder = makeQuadraturePointIndexFinder<D>( quadratureOrder_ );

        auto generator = [this, n = size_t { 0 }]( ) mutable
        {
            auto n0 = n;

            n += utilities::integerPow( quadratureOrder_, 3 );

            return n0;
        };

        std::get<0>( data ).resize( grid->ncells( ) + 1 );
        std::generate( std::get<0>( data ).begin( ), std::get<0>( data ).end( ), generator );
        std::get<1>( data ).resize( std::get<0>( data ).back( ) );
    }

    PiecewiseConstantHistoryGrid( const AbsHistoryRepresentation<D>& oldHistory,
                                  const HierarchicalGridSharedPtr<D>& newGrid,
                                  size_t quadratureOrder ) :
        PiecewiseConstantHistoryGrid( newGrid, quadratureOrder, oldHistory.topSurface )
    {
        auto orders = array::makeSizes<D>( quadratureOrder );
        auto points = gaussLegendrePoints( quadratureOrder )[0];

        #pragma omp parallel
        {
            auto ncells = static_cast<std::int64_t>( newGrid->ncells( ) );
            auto mapping = newGrid->createMapping( );

            #pragma omp for
            for( std::int64_t ii = 0; ii < ncells; ++ii )
            {
                auto icell = static_cast<CellIndex>( ii );

                newGrid->prepareMapping( icell, mapping );

                nd::executeWithIndex( orders, [&]( std::array<size_t, D> ijk, size_t gaussPointIndex )
                {
                    auto newRst = std::array<double, D> { };

                    for( size_t axis = 0; axis < D; ++axis )
                    {
                        newRst[axis] = points[ijk[axis]];
                    }
                                      
                    auto [oldIndex, oldRst] = mesh::mapToOtherGrid( *newGrid, oldHistory.grid( ), icell, newRst );

                    std::get<1>( data )[std::get<0>( data )[icell] + gaussPointIndex] = 
                        oldHistory.evaluate( oldIndex, oldRst, mapping( newRst ) );
                } );
            }
        }
    }

    PlasticityData evaluateInternal( CellIndex historyCell,
                                     std::array<double, D> historyRst,
                                     std::array<double, D> /* xyz */ ) const override
    {
        return std::get<1>( data )[std::get<0>( data )[historyCell] + indexFinder( historyRst )];
    }

    std::shared_ptr<AbsHistoryRepresentation<D>> clone( ) const override
    {
        return std::make_shared<PiecewiseConstantHistoryGrid<D>>( *this );
    }

private:
    size_t quadratureOrder_;
    LinearizedVectors<PlasticityData> data;
    std::function<size_t( std::array<double, D> rst )> indexFinder;
};

inline auto l2projectMechanicalHistory( const MultilevelHpBasis<3>& newBasis,
                                        const AbsHistoryRepresentation<3>& oldHistory,
                                        const AbsQuadrature<3>& quadrature,
                                        const QuadratureOrderDeterminor<3>& determiner,
                                        const linalg::SparseSolver& solver,
                                        const spatial::ScalarFunction<3>& spatialWeight )
{
    auto nHistoryVariables = size_t { 13 };
    auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( newBasis );
    auto vectors = std::vector<std::vector<double>>( nHistoryVariables );

    auto assemblyTypes = AssemblyTypeVector { };
    auto assemblyTargets = AssemblyTargetVector { };

    for( size_t ivar = 0; ivar < nHistoryVariables; ++ivar )
    {
        vectors[ivar] = std::vector<double>( newBasis.ndof( ), 0.0 );

        assemblyTypes.push_back( AssemblyType::Vector );
        assemblyTargets.push_back( vectors[ivar] );
    }

    assemblyTypes.push_back( AssemblyType::SymmetricMatrix );
    assemblyTargets.push_back( matrix );

    auto evaluate = [&]( const BasisFunctionEvaluation<3>& shapes, 
                         const LocationMap&,
                         AlignedDoubleVectors& targets, 
                         AlignedDoubleVector&, double weightDetJ )
    {
        auto ndofelement = shapes.ndof( );
        auto nblocks = shapes.nblocks( );
        auto N = shapes.noalias( 0, 0 );

        auto history = oldHistory.evaluate( newBasis.hierarchicalGrid( ), 
            shapes.elementIndex( ), shapes.rst( ), shapes.xyz( ) );

        weightDetJ *= spatialWeight( shapes.xyz( ) );

        for( size_t iElasticStrain = 0; iElasticStrain < 6; iElasticStrain++ )
        {
            linalg::elementRhs( targets[iElasticStrain].data( ), ndofelement, nblocks, [&]( size_t i )
            {
                return N[i] * history.elasticStrain[iElasticStrain] * weightDetJ;
            } );
        }
        
        for( size_t iBackstress = 0; iBackstress < 6; iBackstress++ )
        {
            linalg::elementRhs( targets[iBackstress + 6].data( ), ndofelement, nblocks, [&]( size_t i )
            {
                return N[i] * history.backstress[iBackstress] * weightDetJ;
            } );
        }
        
        linalg::elementRhs( targets[12].data( ), ndofelement, nblocks, [&]( size_t i )
        {
            return N[i] * history.effectivePlasticStrain * weightDetJ;
        } );


        linalg::symmetricElementLhs( targets.back( ).data( ), ndofelement, nblocks, [=]( size_t i, size_t j )
        {
            return N[i] * N[j] * weightDetJ;
        } );
    };

    auto integrand = DomainIntegrand<3>( assemblyTypes, DiffOrders::Shapes, evaluate );

    integrateOnDomain( newBasis, integrand, assemblyTargets, quadrature, determiner );

    auto result = std::vector<std::vector<double>>( nHistoryVariables );

    for( size_t ivar = 0; ivar < nHistoryVariables; ++ivar )
    {
        result[ivar] = solver( matrix, vectors[ivar] );
    }

    return result;
}

inline spatial::ScalarFunction<3> makeHistoryProjectionWeight( const spatial::ScalarFunction<3>& temperature,
                                                               const spatial::ScalarFunction<3>& materialType,
                                                               double temperatureThreshold,
                                                               double outsideWeight )
{
    return [=]( std::array<double, 3> xyz )
    {
        return temperature( xyz ) <= temperatureThreshold && materialType( xyz ) <= 1.0 ? 1.0 : outsideWeight;
    };
}

template<size_t D>
class L2ProjectedHistory : public AbsHistoryRepresentation<D>
{
public:
    L2ProjectedHistory( const AbsHistoryRepresentation<D>& oldHistory,
                        const HierarchicalGridSharedPtr<D>& newGrid,
                        size_t quadratureOrder, 
                        size_t polynomialDegree,
                        const spatial::ScalarFunction<D>& spatialWeight ) :
        AbsHistoryRepresentation<D>( newGrid, oldHistory.topSurface )
    {
        basis = makeHpBasis<TrunkSpace>( newGrid, polynomialDegree );

        auto quadrature = StandardQuadrature<D>( );
        auto determiner = absoluteQuadratureOrder<D>( array::make<D>( quadratureOrder ) );
        auto dofs = l2projectMechanicalHistory( *basis, oldHistory, quadrature, determiner, linalg::makeCGSolver( ), spatialWeight );

        projectedDofs = std::make_shared<std::vector<std::vector<double>>>( std::move( dofs ) );
    }

    PlasticityData evaluateInternal( CellIndex historyCell,
                                     std::array<double, D> historyRst,
                                     std::array<double, D> /* xyz */ ) const override
    {
        auto& cache = container.get( );

        if( !cache )
        {
            cache = std::make_shared<Cache>( );
            cache->basisCache = basis->createEvaluationCache( );
        }

        basis->prepareEvaluation( historyCell, 1, cache->shapes, cache->basisCache );
        basis->locationMap( historyCell, utilities::resize0( cache->locationMap ) );
        basis->evaluateSinglePoint( historyRst, cache->shapes, cache->basisCache );

        auto result = PlasticityData { };

        for( size_t icomponent = 0; icomponent < 6; ++icomponent )
        {
            result.elasticStrain[icomponent] = evaluateSolution( cache->shapes, 
                cache->locationMap, projectedDofs->at( icomponent ) );
        }
        
        for( size_t icomponent = 0; icomponent < 6; ++icomponent )
        {
            result.backstress[icomponent] = evaluateSolution( cache->shapes, 
                cache->locationMap, projectedDofs->at( icomponent + 6 ) );
        }
        
        result.effectivePlasticStrain = evaluateSolution( cache->shapes, 
            cache->locationMap, projectedDofs->at( 12 ) );

        return result;
    }

    std::shared_ptr<AbsHistoryRepresentation<D>> clone( ) const override
    {
        auto history = std::make_shared<L2ProjectedHistory>( *this );

        for( auto& value : history->container.data )
        {
            value = nullptr;
        }

        return history;
    }

private:
    struct Cache
    {
        BasisFunctionEvaluation<D> shapes;
        BasisEvaluationCache<D> basisCache;
        std::vector<DofIndex> locationMap;
    };

    mutable utilities::ThreadLocalContainer<std::shared_ptr<Cache>> container;

    std::shared_ptr<std::vector<std::vector<double>>> projectedDofs;
    std::shared_ptr<MultilevelHpBasis<D>> basis;
};


template<size_t D>
class J2HistoryUpdate : public AbsHistoryRepresentation<D>
{
public:
    J2HistoryUpdate( std::shared_ptr<const AbsHistoryRepresentation<D>> oldHistory,
                     std::shared_ptr<const MultilevelHpBasis<D>> mbasis0,
                     std::shared_ptr<const MultilevelHpBasis<D>> mbasis1,
                     std::shared_ptr<const std::vector<double>> dofs0,
                     std::shared_ptr<const std::vector<double>> dofs1,
                     const ThermalEvaluator<3>& evaluator ) :
        AbsHistoryRepresentation<D>( oldHistory->gridPtr( ), oldHistory->topSurface ), oldHistory_ { std::move( oldHistory ) }, 
        mbasis0_ { std::move( mbasis0 ) }, mbasis1_ { std::move( mbasis1 ) }, dofs0_ { std::move( dofs0 ) }, 
        dofs1_ { std::move( dofs1 ) }, evaluator_ { evaluator }, 
        kinematics_ { std::make_shared<KinematicEquation<D>>( makeSmallStrainKinematics<D>( ) ) }
    {
        for( size_t i = 0; i < container_.data.size( ); ++i )
        {
            std::get<0>( container_.data[i] ).basisCache = mbasis0_->createEvaluationCache( );
            std::get<0>( container_.data[i] ).kinematicsCache = kinematics_->create( *mbasis0_ );
            std::get<1>( container_.data[i] ).basisCache = mbasis1_->createEvaluationCache( );
            std::get<1>( container_.data[i] ).kinematicsCache = kinematics_->create( *mbasis1_ );
        }
    }

    J2HistoryUpdate( std::shared_ptr<const AbsHistoryRepresentation<D>> oldHistory,
                     const ThermalEvaluator<3>& evaluator ) :
        AbsHistoryRepresentation<D>( oldHistory->gridPtr( ), oldHistory->topSurface ), 
        oldHistory_ { std::move( oldHistory ) }, mbasis0_{ nullptr }, evaluator_ { evaluator }
    { }

    PlasticityData evaluateInternal( CellIndex historyCell,
                                     std::array<double, D> historyRst,
                                     std::array<double, D> xyz ) const override
    {
        auto& caches = container_.get( );
        auto history0 = oldHistory_->evaluate( historyCell, historyRst, xyz );

        if( mbasis0_ == nullptr )
        {
            auto zeroStrainIncrement = std::array<double, 6> { };

            return J2Plasticity( evaluator_, history0, zeroStrainIncrement, xyz ).createNewHistory( );
        }

        auto evaluateStrain = [&]( auto& basis, auto& dofs, auto& cache )
        {
            auto backward = mesh::mapToOtherGrid( oldHistory_->grid( ), basis.hierarchicalGrid(), historyCell, historyRst);
            
            basis.prepareEvaluation( backward.first, 1, cache.shapes, cache.basisCache );
            basis.locationMap( backward.first, utilities::resize0( cache.locationMap ) );
            basis.evaluateSinglePoint( backward.second, cache.shapes, cache.basisCache );

            auto gradient = std::array<double, 9> { };
            auto strain = std::array<double, 6> { };

            evaluateSolutions( cache.shapes, cache.locationMap, dofs, gradient, 1 );
                
            kinematics_->prepare( cache.kinematicsCache, basis.mapping( cache.basisCache ), cache.locationMap );
            kinematics_->evaluate( cache.kinematicsCache, cache.shapes, gradient, std::span { strain }, std::span<double> { } );

            return strain;
        };

        auto strain0 = evaluateStrain( *mbasis0_, *dofs0_, std::get<0>( caches ) );
        auto strain1 = evaluateStrain( *mbasis1_, *dofs1_, std::get<1>( caches ) );

        return J2Plasticity( evaluator_, history0, strain1 - strain0, std::get<1>( caches ).shapes.xyz( ) ).createNewHistory( );
    }

    std::shared_ptr<AbsHistoryRepresentation<D>> clone( ) const override
    {
        if( mbasis0_ )
        {
            return std::make_shared<J2HistoryUpdate<D>>( oldHistory_, mbasis0_, mbasis1_, dofs0_, dofs1_, evaluator_ );
        }
        else
        {
            return std::make_shared<J2HistoryUpdate<D>>( oldHistory_, evaluator_ );
        }
    }

private:
    struct Cache
    {
        BasisFunctionEvaluation<D> shapes;
        BasisEvaluationCache<D> basisCache;
        std::vector<DofIndex> locationMap;

        typename KinematicEquation<D>::AnyCache kinematicsCache;
    };

    mutable utilities::ThreadLocalContainer<std::tuple<Cache, Cache>> container_;

    std::shared_ptr<const AbsHistoryRepresentation<D>> oldHistory_;
    std::shared_ptr<const MultilevelHpBasis<D>> mbasis0_;
    std::shared_ptr<const MultilevelHpBasis<D>> mbasis1_;
    std::shared_ptr<const std::vector<double>> dofs0_;
    std::shared_ptr<const std::vector<double>> dofs1_;
    ThermalEvaluator<D> evaluator_;
    memory::vptr<const KinematicEquation<D>> kinematics_;
};

inline auto makeJ2Plasticity( const AbsHierarchicalGrid<3>& mgrid1, 
                              const AbsHistoryRepresentation<3>& mhistory0,
                              const ThermalEvaluator<3>& evaluator )
{
    auto evaluate = [=, &mgrid1, &mhistory0] ( typename ConstitutiveEquation<3>::AnyCache&,
                                               const BasisFunctionEvaluation<3>& shapes,
                                               std::span<const double> strain,
                                               std::span<double> stress,
                                               std::span<double> tangentStiffness )
    {
        auto history0 = mhistory0.evaluate( mgrid1, shapes.elementIndex( ), shapes.rst( ), shapes.xyz( ) );
        
        auto totalStrainIncrement = std::array<double, 6> { };
        
        std::copy( strain.begin( ), strain.end( ), totalStrainIncrement.begin( ) );

        auto j2 = J2Plasticity( evaluator, history0, totalStrainIncrement, shapes.xyz( ) );

        if( !tangentStiffness.empty( ) )
        {
            j2.evaluateTangent( tangentStiffness.last<36>( ) );
        }
        if( !stress.empty( ) )
        {
            auto S = j2.evaluateStress( );

            std::copy( S.begin( ), S.end( ), stress.begin( ) );
        }
    };

    auto material = ConstitutiveEquation<3> { };

    material.evaluate = evaluate;
    material.incremental = true;
    material.name = "J2Plasticity";
    material.ncomponents = 6;
    material.symmetric = true;

    return material;
}

inline auto mechanicalPostprocessor( const std::vector<std::string>& quantities, 
                                     memory::vptr<const std::vector<double>> displacement,
                                     memory::vptr<const AbsHistoryRepresentation<3>> historyRepresentation,
                                     const spatial::ScalarFunction<3>& temperature,
                                     const MaterialAdapter<3>& material )
{
    static constexpr size_t D = 3;

    auto ncomponentMap = std::map<std::string, size_t>
    {
        { "Displacement", size_t { 3 } },
        { "Temperature", size_t { 1 } },
        { "ElasticStrain", size_t { 6 } },
        { "Stress", size_t { 6 } },
        { "VonMisesStress", size_t { 1 } },
        { "EffectivePlasticStrain", size_t { 1 } }
    };

    struct Cache
    {
        const std::vector<DofIndex>* locationMap;
        const AbsHierarchicalGrid<3>* grid;
        const AbsMapping<D>* mapping;
    };

    auto evaluateCell = []( auto& anyCache, auto, 
                            auto& locationMap, auto& mapping  )  
    {
        utilities::cast<Cache>( anyCache ).locationMap = &locationMap;
        utilities::cast<Cache>( anyCache ).mapping = &mapping;
    };

    auto initialize = []( auto& basis ) -> typename ElementProcessor<D>::Cache
    {
        auto* mlhpBasis = dynamic_cast<const MultilevelHpBasis<3>*>( &basis );

        MLHP_CHECK( mlhpBasis, "Mechanical postprocessing needs MultilevelHpBasis." );

        return Cache { nullptr, &mlhpBasis->hierarchicalGrid( ), nullptr };
    };

    auto evaluatePoint = [=]( auto& anyCache, auto targets, const auto& shapes )
    {
        auto& cache = utilities::cast<Cache>( anyCache );
        
        auto xyzShifted = cache.mapping->map( 0.9999 * shapes.rst( ) );

        // Create optionals with corresponding evaluation function to prevent evaluating expensive quantities more than once
        auto T_ = std::optional<double> { };
        auto H_ = std::optional<PlasticityData> { };
        auto S_ = std::optional<std::array<double, 6>> { };

        auto evaluateTemperature = [&]( ) 
        { 
            return T_ ? *T_ : *( T_ = temperature( shapes.xyz( ) ) ); 
        };

        auto evaluateHistory = [&]( )
        { 
            return H_ ? *H_ : *( H_ = historyRepresentation->evaluate( *cache.grid, 
                shapes.elementIndex( ), shapes.rst( ), shapes.xyz( ) ) );
        };

        auto evaluateElasticStress = [&]( )
        {
            return S_ ? *S_ : *( S_ = std::get<0>( evaluateLinearElasticity( material( xyzShifted ), 
                evaluateTemperature( ), evaluateHistory( ).elasticStrain ) ) );  
        };

        for( size_t iquantity = 0; iquantity < quantities.size( ); ++iquantity )
        {
            auto copyComponents = [&]( const std::array<double, 6>& result )
            {
                auto T = targets[iquantity];

                // We order [xx, yy, zz, yz, xz, xy], Paraview instead [xx, yy, zz, xy, yz, xz]
                T[0] = result[0]; T[1] = result[1]; T[2] = result[2];
                T[3] = result[5]; T[4] = result[3]; T[5] = result[4];
            };

            if( quantities[iquantity] == "Displacement" )
            {
                evaluateSolutions( shapes, *cache.locationMap, *displacement, targets[iquantity] );
            }
            else if( quantities[iquantity] == "Temperature" )
            {
                targets[iquantity][0] = evaluateTemperature( );
            }
            else if( quantities[iquantity] == "ElasticStrain" )
            {
                copyComponents( evaluateHistory( ).elasticStrain );
            }
            else if( quantities[iquantity] == "Stress" )
            {
                copyComponents(evaluateElasticStress( ) );
            }
            else if( quantities[iquantity] == "VonMisesStress" )
            {
                auto [S11, S22, S33, S23, S13, S12] = evaluateElasticStress( );

                auto D1 = ( S11 - S22 ) * ( S11 - S22 );
                auto D2 = ( S22 - S33 ) * ( S22 - S33 );
                auto D3 = ( S33 - S11 ) * ( S33 - S11 );
                auto S = S12 * S12 + S23 * S23 + S13 * S13;

                targets[iquantity][0] = std::sqrt(0.5 * (D1 + D2 + D3) + 3.0 * S);
            }
            else if( quantities[iquantity] ==  "EffectivePlasticStrain" )
            {
                targets[iquantity][0] = evaluateHistory( ).effectivePlasticStrain;
            }
        }
    };

    auto outputData = [=]( auto& /* basis */ )
    {
        auto outputs = OutputVector { };
        
        for( auto& quantity : quantities )
        {
            MLHP_CHECK( ncomponentMap.contains( quantity ), "Invalid mechanical postprocessing quantity: " + quantity );

            outputs.push_back( mlhp::Output { .name = quantity,
                                              .type = Output::Type::PointData, 
                                              .ncomponents = ncomponentMap.at( quantity ) } );
        }

        return outputs;
    };

    return ElementProcessor<D>
    { 
        .outputData = std::move( outputData ), 
        .initialize = std::move( initialize ),
        .evaluateCell = std::move( evaluateCell ),
        .evaluatePoint = std::move( evaluatePoint ),
        .diffOrder = DiffOrders::Shapes
    };
}

} // namespace mlhp

#endif // MLHPBF_MECHANICAL_HPP
