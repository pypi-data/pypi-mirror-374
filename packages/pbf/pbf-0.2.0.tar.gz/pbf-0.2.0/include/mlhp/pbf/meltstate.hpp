// This file is part of the mlhpbf project. License: See LICENSE

#ifndef MLHPBF_HISTORY_HPP
#define MLHPBF_HISTORY_HPP

#include "mlhp/core.hpp"
#include "materials.hpp"

namespace mlhp
{

template<size_t D>
struct ThermalHistory
{
    using Initialize = std::function<MaterialType( std::array<double, D> xyz )>;

    ThermalHistory( ) :
        grid { makeRefinedGrid<D>( array::makeSizes<D>( 1 ), array::make<D>( 1.0 ) ) },
        data ( 1, MaterialType { } ), maxdepth { 0 }, topSurface { 1e50 },
        backwardMappings { mesh::threadLocalBackwardMappings( *grid ) }
    { }

    ThermalHistory( const HierarchicalGridSharedPtr<D>& grid_,
                    const Initialize& initialize,
                    RefinementLevel maxdepth_,
                    double topSurface_ ) :
        grid { grid_ }, data( grid_->ncells( ) ), maxdepth { maxdepth_ }, topSurface { topSurface_ },
        backwardMappings { mesh::threadLocalBackwardMappings( *grid ) }
    { 
        auto ncells = static_cast<std::int64_t>( grid->ncells( ) );

        #pragma omp parallel
        {
            auto mapping = grid->createMapping( );

            #pragma omp for
            for( std::int64_t ii = 0; ii < ncells; ++ii )
            {
                auto icell = static_cast<CellIndex>( ii );

                grid->prepareMapping( icell, mapping );

                auto xyz0 = mapping( array::setEntry<double, D>( { }, D - 1, -1.0 ) );
                auto xyz1 = mapping( array::setEntry<double, D>( { }, D - 1, +1.0 ) );

                auto dz = xyz1[D - 1] - xyz0[D - 1];

                if( xyz0[D - 1] > topSurface - 1e-10 * dz )
                {
                    data[icell] = MaterialType::Air;
                }
                else
                {
                    xyz0[D - 1] = std::min( xyz0[D - 1] + dz / 2, topSurface );

                    data[icell] = initialize( xyz0 );
                }
            }
        }
    }

    ThermalHistory( const HierarchicalGridSharedPtr<D>& grid_, 
                    RefinementLevel maxdepth_,
                    double topSurface_,
                    std::vector<MaterialType>&& data_ ) :
        grid { grid_ }, data( std::move( data_ ) ), maxdepth { maxdepth_ }, topSurface { topSurface_ },
        backwardMappings { mesh::threadLocalBackwardMappings( *grid ) }
    { 
        MLHP_CHECK( grid->ncells( ) == data.size( ), "Inconsistent history array size." );
    }

    MaterialType operator() ( std::array<double, D> xyz ) const
    {
        if( xyz.back( ) > topSurface )
        {
            return MaterialType::Air;
        }

        auto result = backwardMappings.get( )->map( xyz );

        if( !result )
        {
            return MaterialType::Undefined;
        }

        return data[result->first];
    }

    MaterialType operator()( CellIndex fullIndex, std::array<double, D> rst, std::array<double, D> xyz ) const
    {
        if( xyz.back( ) > topSurface )
        {
            return MaterialType::Air;
        }
        else
        {
            return data[grid->mapToLeaf( fullIndex, rst ).first];
        }
    }

    HierarchicalGridSharedPtr<D> grid;
    std::vector<MaterialType> data;
    RefinementLevel maxdepth;
    double topSurface;
    ThreadLocalBackwardMappings<D> backwardMappings;
};

template<size_t D>
using MaterialAdapter = std::function<const Material* (std::array<double, D> xyz)>;

template<size_t D>
MaterialAdapter<D> makeMaterialAdapter( memory::vptr<ThermalHistory<D>> history, MaterialPtrs materials )
{
    return [=]( std::array<double, D> xyz )
    {
        return materialFor( materials, history->operator()(xyz) );
    };
}

template<size_t D>
spatial::ScalarFunction<D> makeMaterialAdapter( const ThermalHistory<D>& history, MaterialPtrs materials )
{
    return makeMaterialAdapter<D>( &history, materials );
}

template<size_t D> inline
ThermalHistory<D> createNewHistory( auto&& materialInitializer,
                                    const GridConstSharedPtr<D>& baseGrid,
                                    size_t nseedpoints,
                                    size_t maxdepth,
                                    double powderHeight )
{
    auto refinement = [&]( const MeshMapping<D>& mapping, 
                           RefinementLevel level )
    {
        auto refine = false;

        if( level < maxdepth )
        {
            auto pointsPerDirection = array::make<D>( nseedpoints );
            auto rstGenerator = spatial::makeRstGenerator( pointsPerDirection, 1.0 - 1e-5 );
            auto ijk0 = array::makeSizes<D>( 0 );
            auto xyz0 = mapping.map( rstGenerator( ijk0 ) );

            if( xyz0.back( ) < powderHeight )
            {
                auto initialType = materialInitializer( xyz0 );

                nd::execute( pointsPerDirection, [&]( std::array<size_t, D> ijk )
                {
                    if( refine == false && ijk != ijk0 )
                    {
                        auto xyz = mapping.map( rstGenerator( ijk ) );

                        refine = xyz.back( ) < powderHeight && materialInitializer( xyz ) != initialType;
                    }
                } );
            }
        }

        return refine;
    };

    auto grid = makeRefinedGrid<D>( baseGrid->cloneGrid( ) );

    grid->refine( refinement );

    return ThermalHistory<D>( grid, materialInitializer, static_cast<RefinementLevel>( maxdepth ), powderHeight );
}

template<size_t D> inline
ThermalHistory<D> initializeHistory( const GridSharedPtr<D>& baseGrid,
                                     const ImplicitFunction<D>& part,
                                     double powderHeight,
                                     size_t nseedpoints, 
                                     size_t maxdepth ) 
{
    auto materialInitializer = [=]( std::array<double, D> xyz )
    {
        if( xyz[2] <= 0.0 )
        {
            return MaterialType::BasePlate;
        }
        else if( xyz[2] > powderHeight )
        {
            return MaterialType::Air;
        }
        else
        {
            return part( xyz ) ? MaterialType::Structure : MaterialType::Powder;
        }
    };

    return createNewHistory<D>( materialInitializer, baseGrid, nseedpoints, maxdepth, powderHeight );
}

template<size_t D> inline
ThermalHistory<D> initializeHistory( const GridSharedPtr<D>& baseGrid,
                                     double powderHeight,
                                     size_t maxdepth ) 
{
    return initializeHistory<D>( baseGrid, utilities::returnValue( false ), powderHeight, 4, maxdepth );
}

namespace
{

template<size_t D> inline
auto updateMeltState( const MultilevelHpBasis<D>& tbasis, 
                      const std::vector<double>& tdofs, 
                      const AbsHierarchicalGrid<D>& grid,
                      std::vector<int>& meltstate,
                      double meltingTemperature,
                      double topSurface,
                      size_t maxdepth,
                      size_t degree )
{
    auto abovecount = std::vector<size_t>( grid.ncells( ), 0 );
    auto belowcount = std::vector<size_t>( grid.ncells( ), 0 );
    auto ntelements = tbasis.nelements( );

    [[maybe_unused]] auto chunksize = parallel::clampChunksize( ntelements, 13, 2 );

    // Determine cells inside melt pool
    #pragma omp parallel
    {
        auto subcells = std::vector<mesh::SharedSupport<D>> { };
        auto shapes = BasisFunctionEvaluation<D> { };
        auto cache = tbasis.createEvaluationCache( );
        auto locationMap = LocationMap { };
        auto elementDofs = std::vector<double> { };
        auto seedgrid = CoordinateGrid<D> { };
        auto seedbounds = std::array { array::make<D>( 2.0 ), array::make<D>( -1.0 ) };

        #pragma omp for schedule(dynamic, chunksize)
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( ntelements ); ++ii )
        {
            auto icell = static_cast<CellIndex>( ii );

            utilities::resize0( subcells, locationMap, elementDofs );

            mesh::findInOtherGrid( tbasis.hierarchicalGrid( ), grid,
                subcells, tbasis.hierarchicalGrid( ).fullIndex( icell ) );

            // If none of the history grid cells are to be checked
            bool skip = true;

            for( auto& subcell : subcells )
            {
                if( meltstate[grid.leafIndex( subcell.otherIndex )] == -1 )
                {
                    skip = false;
                    break;
                }
            }

            if( skip ) continue;

            // Otherwise prepare to evaluate this element
            tbasis.prepareEvaluation( icell, 0, shapes, cache );
            tbasis.locationMap( icell, locationMap );

            auto& mapping = tbasis.mapping( cache );
            auto ndofelement = locationMap.size( );

            for( CellIndex isubcell = 0; isubcell < subcells.size( ); ++isubcell )
            {
                auto hindex = grid.leafIndex( subcells[isubcell].otherIndex );

                if( meltstate[hindex] != -1 ) continue;

                if( elementDofs.empty( ) )
                {
                    elementDofs.resize( ndofelement );

                    for( size_t idof = 0; idof < ndofelement; ++idof )
                    {
                        elementDofs[idof] = tdofs[locationMap[idof]];
                    }
                }

                auto evaluateBounds = [&]( size_t npoints )
                {
                    // Instead of this we may be able to just skip this element (maybe dont even check when coarsening)
                    auto z0 = mapping( subcells[isubcell].thisCell.map( array::makeAndSet<double, D>( 0.0, D - 1, -1.0 ) ) )[D - 1];
                    auto z1 = mapping( subcells[isubcell].thisCell.map( array::makeAndSet<double, D>( 0.0, D - 1, 1.0 ) ) )[D - 1];

                    if( z0 >= topSurface - 1e-10 * ( z1 - z0 ) )
                    {
                        return std::tuple { 0.0, 0.0 };
                    }

                    spatial::cartesianTickVectors( array::makeSizes<D>( npoints - 1 ), 
                        seedbounds[0], seedbounds[1], seedgrid );

                    subcells[isubcell].thisCell.mapGrid( seedgrid );

                    tbasis.prepareGridEvaluation( seedgrid, cache );

                    auto Tmin = std::numeric_limits<double>::max( );
                    auto Tmax = std::numeric_limits<double>::lowest( );
                    auto limits = array::makeSizes<D>( npoints );

                    nd::execute( limits, [&]( std::array<size_t, D> ijk )
                    {
                        tbasis.evaluateGridPoint( ijk, shapes, cache );
                                    
                        auto N = shapes.noalias( 0, 0 );
                        auto T = 0.0;

                        for( size_t idof = 0; idof < ndofelement; ++idof )
                        {
                            T += N[idof] * elementDofs[idof];
                        }
                                
                        Tmin = std::min( Tmin, T );
                        Tmax = std::max( Tmax, T );
                    } );

                    return std::tuple { Tmin, Tmax };
                };

                auto [Tmin, Tmax] = evaluateBounds( degree + 1 );

                // Evaluate again if bound is close to melting
                if( degree > 1 )
                {
                    if( ( Tmin < 1.5 * meltingTemperature && Tmin > meltingTemperature ) ||
                        ( Tmax > 0.5 * meltingTemperature && Tmax < meltingTemperature ) )
                    {
                        std::tie( Tmin, Tmax ) = evaluateBounds( degree + 4 );
                    }
                }

                if( Tmin < meltingTemperature )
                {
                    #pragma omp atomic
                    belowcount[hindex] += 1;
                }

                if( Tmax >= meltingTemperature )
                {
                    #pragma omp atomic
                    abovecount[hindex] += 1;
                }
            }
        }
    } // omp parallel

    for( CellIndex i = 0; i < abovecount.size( ); ++i )
    {
        if( meltstate[i] == -1 )
        {
            auto meltint = static_cast<int>( abovecount[i] > 0 ) - static_cast<int>( belowcount[i] > 0 );

            if( meltint == 0 && grid.refinementLevel( grid.fullIndex( i ) ) < maxdepth )
            {
                meltstate[i] = -1;
            }
            else
            {
                meltstate[i] = meltint >= 0 ? static_cast<int>( MaterialType::Structure ) : static_cast<int>( MaterialType::Powder );
            }
        }
    }

    return meltstate;
}


template<size_t D> inline
auto interpolateNewMaterialState( const AbsHierarchicalGrid<D>& previousHistoryGrid,
                                  const AbsHierarchicalGrid<D>& newGrid,
                                  const std::vector<int>& materialstate )
{
    auto ncells = static_cast<size_t>( newGrid.ncells( ) );
    auto newstate = std::vector<int>( ncells, 0 );

    [[maybe_unused]] auto chunksize = parallel::clampChunksize( ncells, 13, 2 );

    #pragma omp parallel
    {
        auto subcells = std::vector<mesh::SharedSupport<D>> { };

        #pragma omp for schedule(dynamic, chunksize)
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( ncells ); ++ii )
        {
            auto icell = static_cast<CellIndex>( ii );

            mesh::findInOtherGrid( newGrid, previousHistoryGrid,
                utilities::resize0( subcells ), newGrid.fullIndex( icell ) );

            newstate[icell] = materialstate[previousHistoryGrid.leafIndex( subcells[0].otherIndex )];
        }
    } // pragma omp parallel

    return newstate;
}

template<size_t D>
auto isEntirelyAboveTop( const MeshMapping<D>& mapping, double topSurface )
{
    auto z0 = mapping( array::makeAndSet<double, D>( 0.0, D - 1, -1.0 ) )[D - 1];
    auto z1 = mapping( array::makeAndSet<double, D>( 0.0, D - 1, 1.0 ) )[D - 1];

    return z0 > topSurface - 1e-10 * ( z1 - z0 );
}
    
template<size_t D> inline
auto adaptGridAndMeltstate( const AbsHierarchicalGrid<D>& previousHistoryGrid,
                            const std::vector<int>& meltstate,
                            double topSurface )
{
    auto adapt = std::vector<int>( previousHistoryGrid.ncells( ), 0 );
    auto nroots = previousHistoryGrid.baseGrid( ).ncells();

    auto recursive = [&]( auto&& self, CellIndex ifull, MeshMapping<D>& mapping ) -> std::tuple<int, bool, bool>
    {
        if( auto child = previousHistoryGrid.child( ifull, { } ); child != NoCell )
        {
            auto value = 0;
            auto valueInitialized = false;
            auto coarsen = true;
            auto entirelyAbove = true;
               
            // Determine material values of children are equal
            nd::execute( array::make<D>( LocalPosition { 2 } ), [&]( auto ijk )
            {
                auto [valueI, coarsenI, entirelyAboveI] = self( self, previousHistoryGrid.child( ifull, ijk ), mapping );
                
                entirelyAbove = entirelyAbove && entirelyAboveI;

                if( !entirelyAboveI )
                {
                    if( !valueInitialized )
                    {
                        value = valueI;
                        valueInitialized = true;
                    }
                    else
                    {
                        coarsen = coarsen && coarsenI && ( valueI == value );
                    }
                }
            } );

            if( coarsen || entirelyAbove )
            {
                nd::execute( array::make<D>( LocalPosition { 2 } ), [&]( auto ijk )
                {
                    if( auto child2 = previousHistoryGrid.child( ifull, ijk ); previousHistoryGrid.isLeaf( child2 ) )
                    {
                        adapt[previousHistoryGrid.leafIndex( child2 )] = std::numeric_limits<int>::min( );
                    }
                } );
            }

            return { value, coarsen, entirelyAbove };
        }
        else
        {
            auto ileaf = previousHistoryGrid.leafIndex( ifull );
            
            previousHistoryGrid.prepareMapping( ileaf, mapping );

            auto entirelyAbove = isEntirelyAboveTop( mapping, topSurface );

            adapt[ileaf] = static_cast<int>( !entirelyAbove && meltstate[ileaf] == -1 );

            return { meltstate[ileaf], meltstate[ileaf] != -1, entirelyAbove };
        }
    };

    [[maybe_unused]] auto chunksize = parallel::clampChunksize( nroots, 7, 2 );

    #pragma omp parallel 
    {
        auto mapping = previousHistoryGrid.createMapping( );

        #pragma omp for schedule(dynamic, chunksize)
        for( std::int64_t iroot = 0; iroot < static_cast<std::int64_t>( nroots ); ++iroot )
        {
            recursive( recursive, static_cast<CellIndex>( iroot ), mapping );
        }
    }

    auto newGrid = makeRefinedGrid( previousHistoryGrid, adapt );
    auto newmeltstate = interpolateNewMaterialState( previousHistoryGrid, *newGrid, meltstate );

    return std::pair { std::move( newGrid ), std::move( newmeltstate ) };
}

// For Debugging
template<typename T, size_t D>
void postprocessHistory( const AbsHierarchicalGrid<D>& grid,
                         const std::vector<T>& data,
                         std::string name )
{ 
    auto writer = VtuOutput { name };
    auto meshcreator = cellmesh::grid<D>( array::makeSizes<D>( 1 ), PostprocessTopologies::Volumes );
    auto converted = utilities::convertVector<double>( data );
    auto processor = makeCellDataProcessor<D>( converted );
    
    writeOutput( grid, meshcreator, processor, writer );
}

} // namespace

template<size_t D> inline
auto updateHistory( const ThermalHistory<D>& history_,
                    const MultilevelHpBasis<D>& tbasis, 
                    const std::vector<double>& tdofs,
                    double meltingTemperature,
                    size_t degree )
{
    auto newGrid = history_.grid;
    auto meltstate = std::vector<int>( newGrid->ncells( ) );
    auto nint = static_cast<std::int64_t>( newGrid->ncells( ) );

    #pragma omp parallel for schedule(static) 
    for( std::int64_t ii = 0; ii < nint; ++ii )
    {
        auto i = static_cast<CellIndex>( ii );

        meltstate[i] = history_.data[i] == MaterialType::Powder ? -1 : static_cast<int>( history_.data[i] );
    }

    while( std::find( meltstate.begin( ), meltstate.end( ), -1 ) != meltstate.end( ) )
    {
        updateMeltState( tbasis, tdofs, *newGrid, meltstate, meltingTemperature, history_.topSurface, history_.maxdepth, degree );

        std::tie( newGrid, meltstate ) = adaptGridAndMeltstate( *newGrid, meltstate, history_.topSurface );
    }

    return ThermalHistory<D>( newGrid, history_.maxdepth, history_.topSurface, utilities::convertVector<MaterialType>( meltstate ) );
}

template<size_t D>
ThermalHistory<D> addPowderLayer( const ThermalHistory<D>& history, double newTopSurface )
{
    if( history.topSurface == newTopSurface )
    {
        return history;
    }

    MLHP_CHECK( newTopSurface > history.topSurface, "New powder layer level must be above old layer." );

    auto newGrid = history.grid;
    auto meltstate = std::vector<int>( newGrid->ncells( ), -1 );

    while( std::find( meltstate.begin( ), meltstate.end( ), -1 ) != meltstate.end( ) )
    {
        [[maybe_unused]] 
        auto chunksize = parallel::clampChunksize( newGrid->ncells( ), 100 );
        auto nint = static_cast<std::int64_t>( newGrid->ncells( ) );

        #pragma omp parallel
        {
            auto mapping = newGrid->createMapping( );

            // For all history cells
            #pragma omp for schedule(dynamic, chunksize) 
            for( std::int64_t ii = 0; ii < nint; ++ii )
            {
                auto icell = static_cast<CellIndex>( ii );

                if( meltstate[icell] != -1 )
                {
                    continue;
                }

                newGrid->prepareMapping( icell, mapping );

                auto z0 = mapping( array::setEntry<double, D>( { }, D - 1, -1.0 ) )[D - 1];
                auto z1 = mapping( array::setEntry<double, D>( { }, D - 1, +1.0 ) )[D - 1];

                auto eps = 1e-10 * ( z1 - z0 );

                // History cell is fully below old top surface
                if( z1 <= history.topSurface + eps )
                {
                    auto jcell = mesh::mapToOtherGrid<D>( *newGrid, *history.grid, icell, { } ).first;

                    meltstate[icell] = static_cast<int>( history.data[jcell] );
                }
                // Above new top surface (completely outside)
                else if( z0 >= newTopSurface - eps )
                {
                    meltstate[icell] = static_cast<int>( MaterialType::Air );
                }
                // Above old top surface
                else if( z0 >= history.topSurface - eps )
                {
                    meltstate[icell] = static_cast<int>( MaterialType::Powder );
                }
                // Intersects old top surface
                else
                {
                    auto jcell = mesh::mapToOtherGrid<D>( *newGrid, *history.grid, icell, { } ).first;

                    if( history.data[jcell] == MaterialType::Powder )
                    {
                        meltstate[icell] = static_cast<int>( MaterialType::Powder );

                        continue;
                    }

                    auto level = newGrid->refinementLevel( newGrid->fullIndex( icell ) );

                    // If we are still allowed to refine
                    if( level < history.maxdepth )
                    {
                        meltstate[icell] = -1;
                    }
                    // Already at maximum depth but still cut: we need to make a choice
                    else
                    {
                        // If cell is primarily above: entire cell is powder
                        if( z1 - history.topSurface > history.topSurface - z0 )
                        {
                            meltstate[icell] = static_cast<int>( MaterialType::Powder );
                        }
                        // Primarily below: entire cell is whatever it was before
                        else
                        {
                            meltstate[icell] = static_cast<int>( history.data[jcell] );
                        }
                    }
                }
            } // for each cell
        } // omp parallel

        std::tie( newGrid, meltstate ) = adaptGridAndMeltstate( *newGrid, meltstate, newTopSurface );
    }

    return ThermalHistory<D>( newGrid, history.maxdepth, newTopSurface, utilities::convertVector<MaterialType>( meltstate ) );
}

} // namespace mlhp

#endif // MLHPBF_HISTORY_HPP
