// This file is part of the mlhpbf project. License: See LICENSE

#ifndef MLHPBF_LASER_HPP
#define MLHPBF_LASER_HPP

#include "mlhp/core.hpp"
#include <iomanip>

namespace mlhp::laser
{

// Discrete point in laser path
template<size_t D>
struct Point
{
    std::array<double, D> xyz;
    double time;
    double power;
};

template<size_t D>
using LaserTrack = std::vector<Point<D>>;

// Discrete refinement point seen backwards from current time
struct Refinement
{
    double timeDelay;
    double sigma;
    double refinementLevel;
    double zfactor = 1.0;
};

template<size_t D> inline
auto interpolateTrack( const LaserTrack<D>& track, double time )
{
    if( time == track.back( ).time )
    {
        return std::make_tuple( track.back( ).xyz, track.back( ).power );
    }

    auto predicate = [&]( auto& point0, auto& point1 )
    {
        return point0.time < point1.time;
    };

    auto value = Point<D> { .xyz = { }, .time = time, .power = 0.0 };
    auto point1 = std::upper_bound( track.begin( ), track.end( ), value, predicate );
    auto point0 = point1 - 1;

    MLHP_CHECK( point1 != track.begin( ) && point1 != track.end( ), "LaserPoint not found ??" );

    double tau = ( time - point0->time ) / ( point1->time - point0->time );

    auto power = point1->power; // tau * ( point1->power - point0->power ) + point0->power;

    auto xyz = tau * ( point1->xyz - point0->xyz ) + point0->xyz;

    return std::make_tuple( xyz, power );
}

template<size_t D> inline
auto volumeSource( const LaserTrack<D>& track, 
                   const spatial::ScalarFunction<D - 1>& beamShape, 
                   double depthSigma )
{
    if( track.size( ) < 2 )
    {
        return spatial::constantFunction<D + 1>( 0.0 );
    }

    std::function shapeZ = spatial::integralNormalizedGaussBell<1>( { }, depthSigma, 2.0 );

    std::function source = [=]( std::array<double, D + 1> xyzt )
    {
        auto [xyz, time] = array::peel( xyzt );

        if( time < track.front( ).time || time > track.back( ).time )
        {
            return 0.0;
        }

        auto [Pxyz, power] = interpolateTrack( track, time );
 
        auto [Pxy, Pz] = array::peel( Pxyz );
        auto [xy, z] = array::peel( xyz );
        auto depth = shapeZ( std::array { z - Pz } );

        return z <= Pz + 1e-10 ? power * beamShape( xy - Pxy ) * depth : 0.0;
    };

    return source;
}

template<size_t D> inline
auto surfaceSource( const LaserTrack<D>& track, 
                    const spatial::ScalarFunction<D - 1>& beamShape )
{
    std::function source = [=]( std::array<double, D + 1> xyzt )
    {
        auto [xyz, time] = array::peel( xyzt );

        if( time < track.front( ).time || time > track.back( ).time )
        {
            return 0.0;
        }

        auto [Pxyz, power] = interpolateTrack( track, time );

        return -power * beamShape( std::get<0>( array::peel( xyz ) ) - 
                                   std::get<0>( array::peel( Pxyz ) ));
    };

    return source;
}

template<size_t D> inline
auto evaluateRefinements( const std::vector<Refinement>& refinements,
                          double delay, std::array<double, D> difference )
{
    double eps = 1e-8 * ( refinements.back( ).timeDelay - refinements.front( ).timeDelay );

    for( size_t irefinement = 0; irefinement + 1 < refinements.size( ); ++irefinement )
    {
        auto& refinement0 = refinements[irefinement];
        auto& refinement1 = refinements[irefinement + 1];

        if( delay < refinement1.timeDelay - eps )
        {
            // Map into current refinement segment
            auto tau = utilities::mapToLocal0( refinement0.timeDelay, refinement1.timeDelay, delay );

            // Interpolate sigma and level in current refinement segment
            auto sigma = ( 1.0 - tau ) * refinement0.sigma + tau * refinement1.sigma;
            auto zfactor = ( 1.0 - tau ) * refinement0.zfactor + tau * refinement1.zfactor;
            auto maxlevel = ( 1.0 - tau ) * refinement0.refinementLevel + tau * refinement1.refinementLevel;

            auto difference2 = difference;
   
            difference2.back( ) /= zfactor; 

            auto distanceSquared = spatial::normSquared( difference2 );

            // Evaluate exponential
            auto level = maxlevel * std::exp( -distanceSquared / ( 2.0 * sigma * sigma ) );

            return static_cast<RefinementLevel>( std::round( std::max( level, 0.0 ) ) );
        }
    }

    return RefinementLevel { 0 };
}

template<size_t D> inline
auto refinementLevelBasedOnLaserHistory( const LaserTrack<D>& track,
                                         const std::vector<Refinement>& refinements )
{
    auto delay0 = refinements.front( ).timeDelay;
    auto delay1 = refinements.back( ).timeDelay;

    return [=]( std::array<double, D + 1> xyzt )
    {
        auto [xyz, time] = array::peel( xyzt );

        RefinementLevel level = 0;

        // Loop over laser path segments
        for( size_t iSegment = 0; iSegment + 1 < track.size( ); ++iSegment )
        {
            auto& point0 = track[iSegment];
            auto& point1 = track[iSegment + 1];

            // Continue if segment is not yet active, or finished longer ago than delay
            if( point1.power > 0.0 && point0.time <= time + delay0 && point1.time >= time - delay1 )
            {
                // If second point of segment is in future, then interpolate with current time
                auto alpha = ( time + delay0 - point0.time ) / ( point1.time - point0.time );

                alpha = std::clamp( alpha, 0.0, 1.0 );

                auto xyz1 = ( 1.0 - alpha ) * point0.xyz + alpha * point1.xyz;

                auto [p, t] = spatial::closestPointOnSegment( point0.xyz, xyz1, xyz );

                t *= alpha;

                // Local coordinate of projection p along axis point0 - point1
                double tau = time - ( 1.0 - t ) * point0.time - t * point1.time;

                level = std::max( level, evaluateRefinements( refinements, tau, p - xyz ) );
            }
        }

        return level;
    };
}

template<size_t D>
LaserTrack<D> filterTrack( const LaserTrack<D>& track,
                           std::array<double, 2> timeBounds )
{
    auto predicate0 = [&]( auto& p0, auto& p1 ) { return p0.time > p1.time; };
    auto predicate1 = [&]( auto& p0, auto& p1 ) { return p0.time < p1.time; };
    auto value = []( double time ) { return Point<D> { .xyz = { }, .time = time, .power = 0.0 }; };

    auto it0 = std::upper_bound( track.rbegin( ), track.rend( ), value( timeBounds[0] ), predicate0 ) + 1;
    auto it1 = std::upper_bound( track.begin( ), track.end( ), value( timeBounds[1] ), predicate1 ) + 1;

    auto begin = std::max( it0.base( ), track.begin( ) );
    auto end = std::min( it1, track.end( ) );

    return begin < end ? LaserTrack<D>( begin, end ) : LaserTrack<D> { };
}

template<size_t D>
LaserTrack<D> filterTrack( const LaserTrack<D>& track,
                           spatial::BoundingBox<D> spaceBounds )
{
    auto newTrack = LaserTrack<D> { };

    if( track.size( ) < 2 )
    {
        return { };
    }

    MLHP_THROW( "TODO: Intersection line with box rather than checking only the end points." );

    auto previous = spatial::insideBoundingBox( spaceBounds, track.front( ).xyz );
    auto lastAdded = NoValue<size_t>;

    for( size_t i = 1; i < track.size( ); ++i )
    {
        auto current = spatial::insideBoundingBox( spaceBounds, track[i].xyz );

        if( previous or current )
        {
            if( lastAdded != i - 1 )
            {
                newTrack.push_back( track[i - 1] );
            }

            newTrack.push_back( track[i] );
        }

        previous = current;
    }

    return newTrack;
}

// Refinement based on laser history sliced for given time (for time-stepping)
template<size_t D> inline
auto makeRefinement( const LaserTrack<D>& track,
                     const std::vector<Refinement>& refinements,
                     double time,
                     size_t nseedpoints = 7 )
{
    auto levelFunction = refinementLevelBasedOnLaserHistory( track, refinements );

    auto slicedLevelFunction = [=]( std::array<double, D> xyz )
    {
        return levelFunction( array::insert( xyz, D, time ) );
    };

    return refineWithLevelFunction<D>( slicedLevelFunction, nseedpoints );
}

template<size_t D> inline
spatial::ScalarFunction<D> sourceIntensityLevelFunction( const spatial::ScalarFunction<D>& source,
                                                         double topSurface, double threshold, 
                                                         double sigma, size_t depth )
{
    if( depth == 0 )
    {
        return spatial::constantFunction<D>( 0.0 );
    }

    auto dzMax = std::sqrt( -2 * std::log( 1.0 / ( depth + 0.49 ) ) * sigma * sigma );
    auto factor = -1.0 / ( 2.0 * sigma * sigma );

    return [=]( std::array<double, D> xyz )
    { 
        if( auto dz = topSurface - xyz.back( ); dz < dzMax || dz > 0.0 )
        {
            if( auto f = source( array::setEntry( xyz, D - 1, topSurface ) ); f >= threshold )
            {
                return ( depth + 0.49 ) * std::exp( dz * dz * factor );
            }
        }

        return 0.0;
    };
}

} // namespace mlhp::laser

namespace mlhp
{

template<size_t D> inline
auto createBaseMeshTicks( spatial::BoundingBox<D> buildChamber,
                          double rootElementSize,
                          double layerHeight,
                          double zfactor = 1.0 )
{
    auto basePlate = 0.0;
    auto ticks = CoordinateGrid<D> { }; 

    auto appendLinspace = [&]( double min, double max, size_t axis )
    {
        auto diff = buildChamber[1][axis] - buildChamber[0][axis];
        auto before = ticks[axis].size( );

        MLHP_CHECK( diff > 1e-20, "Invalid domain bounds: "
            "min[" + std::to_string( axis ) + "] = " + std::to_string( buildChamber[0][axis] ) + ", "
            "max[" + std::to_string( axis ) + "] = " + std::to_string( buildChamber[1][axis] ) + "." );

        // This check is only for the z-direction where we want to interpolate the base plate level
        if( max - min > std::numeric_limits<double>::epsilon( ) * diff )
        {
            auto nelements = static_cast<size_t>( std::max( ( max - min ) / rootElementSize + 0.9, 1.0 ) );
            auto axisTicks = utilities::linspace( min, max, nelements + 1 );

            ticks[axis].insert( ticks[axis].end( ), axisTicks.begin( ), axisTicks.end( ) );
        }
        else
        {
            ticks[axis].push_back( max );
        }

        return ticks[axis].size( ) - before;
    };

    // Mesh ticks in x, y
    for( size_t axis = 0; axis + 1 < D; ++axis )
    {
        appendLinspace( buildChamber[0][axis], buildChamber[1][axis], axis );
    }

    // Mesh ticks in z - below base plate
    rootElementSize *= zfactor;

    appendLinspace( buildChamber[0].back( ), basePlate, D - 1 );
    
    auto zeps = 20.0 * std::numeric_limits<double>::epsilon( ) * ( buildChamber[1].back( ) - buildChamber[0].back( ) );

    // Discard layer height info if zero
    if( layerHeight < zeps )
    {
        auto before = ticks.back( ).size( );
        auto nnew = appendLinspace( basePlate, buildChamber[1].back( ), D - 1 );

        // To avoid adding basePlate twice
        if( before != 0 && nnew != 0 )
        {
            ticks.back( ).erase( utilities::begin( ticks.back( ), before ) );
        }
    }
    // Try to align or "snap" the mesh to the layer height as coarse as possible
    else
    {
        for( size_t power = 0; ; ++power )
        {
            auto testsize = rootElementSize / utilities::binaryPow<size_t>( power );
            auto ninlayer = std::llround( layerHeight / testsize );
        
            if( ninlayer && std::abs( testsize - layerHeight / ninlayer ) < 0.125 * testsize )
            {
                rootElementSize = layerHeight / ninlayer * utilities::binaryPow<size_t>( power );

                break;
            }
        }

        // Append base elements until above buildChamber
        for( auto z = basePlate; z < buildChamber[1].back( ) - zeps; z += rootElementSize )
        {
            ticks.back( ).push_back( z + rootElementSize );
        }
    }

    return ticks;
}

} // namespace mlhp

#endif // MLHPBF_LASER_HPP
