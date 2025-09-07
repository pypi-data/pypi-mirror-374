// This file is part of the mlhpbf project. License: See LICENSE

#include "mlhp/pbf.hpp"
#include "main_test.hpp"

namespace mlhp
{

TEST_CASE( "createBaseMeshTicks_test" )
{
    auto ticks0 = createBaseMeshTicks<2>( { std::array { 0.3, -0.1 }, std::array { 0.4, 0.2 } }, 0.1, 0.8, 1.0 );

    REQUIRE( ticks0[0].size( ) == 2 );
    REQUIRE( ticks0[1].size( ) == 4 );

    CHECK( ticks0[0][0] == Approx( 0.3 ).epsilon( 1e-10 ) );
    CHECK( ticks0[0][1] == Approx( 0.4 ).epsilon( 1e-10 ) );

    CHECK( ticks0[1][0] == Approx( -0.1 ).epsilon( 1e-10 ) );
    CHECK( ticks0[1][1] == Approx( 0.0 ).margin( 1e-10 ) );
    CHECK( ticks0[1][2] == Approx( 0.1 ).epsilon( 1e-10 ) );
    CHECK( ticks0[1][3] == Approx( 0.2 ).epsilon( 1e-10 ) );

    auto ticks1 = createBaseMeshTicks<3>( { std::array { 0.3, 0.0, 0.0 }, std::array { 0.42, 0.109, 0.3 } }, 0.1, 1.03 * 0.1 / 8, 1.0 );

    REQUIRE( ticks1[0].size( ) == 3 );
    REQUIRE( ticks1[1].size( ) == 2 );
    REQUIRE( ticks1[2].size( ) == 4 );

    CHECK( ticks1[0][0] == Approx( 0.3 ).epsilon( 1e-10 ) );
    CHECK( ticks1[0][1] == Approx( 0.36 ).epsilon( 1e-10 ) );
    CHECK( ticks1[0][2] == Approx( 0.42 ).epsilon( 1e-10 ) );

    CHECK( ticks1[1][0] == Approx( 0.0 ).margin( 1e-10 ) );
    CHECK( ticks1[1][1] == Approx( 0.109 ).epsilon( 1e-10 ) );

    CHECK( ticks1[2][0] == Approx( 1.03 * 0.0 ).margin( 1e-10 ) );
    CHECK( ticks1[2][1] == Approx( 1.03 * 0.1 ).epsilon( 1e-10 ) );
    CHECK( ticks1[2][2] == Approx( 1.03 * 0.2 ).epsilon( 1e-10 ) );
    CHECK( ticks1[2][3] == Approx( 1.03 * 0.3 ).epsilon( 1e-10 ) );

    // Collapsed level thickness only base plate
    auto ticks2 = createBaseMeshTicks<1>( { std::array { -1.0 }, std::array { 0.0 } }, 0.49, 0.0, 1.0 );

    REQUIRE( ticks2[0].size( ) == 3 );

    CHECK( ticks2[0][0] == Approx( -1.0 ).epsilon( 1e-10 ) );
    CHECK( ticks2[0][1] == Approx( -0.5 ).epsilon( 1e-10 ) );
    CHECK( ticks2[0][2] == Approx( 0.0 ).margin( 1e-10 ) );

    // Collapsed level thickness no base plate
    auto ticks3 = createBaseMeshTicks<1>( { std::array { 0.0 }, std::array { 1.0 } }, 0.4, 0.0, 1.0 );

    REQUIRE( ticks3[0].size( ) == 4 );

    CHECK( ticks3[0][0] == Approx( 0.0 ).epsilon( 1e-10 ) );
    CHECK( ticks3[0][1] == Approx( 1.0 / 3.0 ).epsilon( 1e-10 ) );
    CHECK( ticks3[0][2] == Approx( 2.0 / 3.0 ).epsilon( 1e-10 ) );
    CHECK( ticks3[0][3] == Approx( 1.0 ).epsilon( 1e-10 ) );

    // Only base plate
    auto ticks4 = createBaseMeshTicks<1>( { std::array { -1.0 }, std::array { 0.0 } }, 3.0, 1.0, 1.0 );

    REQUIRE( ticks4[0].size( ) == 2 );

    CHECK( ticks4[0][0] == Approx( -1.0 ).epsilon( 1e-10 ) );
    CHECK( ticks4[0][1] == Approx( 0.0 ).margin( 1e-10 ) );

    // No base plate, element size 0.36 (zfactor 0.8 and size 0.4), but a but less (0.98) 
    // than one sixth of one element size as layer height. 
    auto ticks5 = createBaseMeshTicks<1>( { std::array { 0.0 }, std::array { 1.0 } }, 0.4, 0.98 * 0.36 / 6, 0.8 );

    //for( auto t : ticks5 )
    //{
    //    for( auto v : t )
    //        std::cout << v << ", ";
    //    std::cout << std::endl;
    //}

    //REQUIRE( ticks5[0].size( ) == 4 );
}

TEST_CASE( "projectHistoryVariables_test" )
{
    static constexpr size_t D = 3;

    struct TestHistory : public AbsHistoryRepresentation<D>
    {
        PlasticityData history_;

        TestHistory( const HierarchicalGridSharedPtr<D>& grid, PlasticityData history ) :
            AbsHistoryRepresentation( grid, 1.0 ), history_ { history }
        { }

        std::shared_ptr<AbsHistoryRepresentation<D>> clone( ) const override
        {
            return std::make_shared<TestHistory>( *this );
        }

        PlasticityData evaluateInternal( CellIndex historyCell,
                                         std::array<double, D> rst,
                                         std::array<double, D> xyz ) const override
        {
            return history_;
        }
    };

    auto history = PlasticityData
    {
        .elasticStrain = { 4.6, 3.1, 6.7, 4.2, 9.3, 3.0 },
        .backstress = { 0.6, 2.9, 8.6, 0.0, 7.2, 1.7 },
        .effectivePlasticStrain = 5.2
    };

    auto grid = makeRefinedGrid<D>( makeCartesianGrid<D>( { 1, 1, 1 }, { 1.0, 1.0, 1.0 } ) );
    auto basis = makeHpBasis<TrunkSpace>( grid, 1, 1 );
    auto spatialWeight = spatial::constantFunction<D>( 1.0 );
    auto solver = linalg::makeCGSolver( 1e-12 );
    auto historyInterpolation = TestHistory { grid, history };

    auto historyAtNodes = l2projectMechanicalHistory( *basis, historyInterpolation,
        StandardQuadrature<3> { }, relativeQuadratureOrder<D>( ), solver, spatialWeight );

    REQUIRE( historyAtNodes.size( ) == 13 );

    for( auto& component : historyAtNodes )
    {
        REQUIRE( component.size( ) == basis->ndof( ) );
    }

    for( size_t inode = 0; inode < basis->ndof( ); ++inode )
    {
        for( size_t icomponent = 0; icomponent < 6; ++icomponent)
        {
            CHECK( historyAtNodes[icomponent][inode] == Approx( history.elasticStrain[icomponent] ).epsilon( 1e-10 ) );
            CHECK( historyAtNodes[icomponent + 6][inode] == Approx( history.backstress[icomponent] ).epsilon( 1e-10 ) );
        }

        CHECK( historyAtNodes[12][inode] == Approx( history.effectivePlasticStrain ).epsilon( 1e-10 ) );
    }
}

} // namespace mlhp
