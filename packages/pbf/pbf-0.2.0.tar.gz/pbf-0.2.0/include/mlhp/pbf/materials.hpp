// This file is part of the mlhpbf project. License: See LICENSE

#ifndef MLHPBF_MATERIALS_HPP
#define MLHPBF_MATERIALS_HPP

#include "json/json.hpp"
#include "mlhp/core.hpp"

namespace mlhp
{

struct Units
{
    static constexpr double m = 1000.0;
    static constexpr double cm = 1e-2 * m;
    static constexpr double mm = 1e-3 * m; // <---
    static constexpr double um = 1e-6 * m;
    static constexpr double s = 1.0;       // <---
    static constexpr double ms = 1e-3 * s;
    static constexpr double kg = 1000.0;
    static constexpr double g = 1e-3 * kg; // <---
    static constexpr double N = 1.0;       // <---
    static constexpr double J = N * m;
    static constexpr double kJ = 1e3 * J;
    static constexpr double W = J / s;
    static constexpr double kW = 1e3 * W;
    static constexpr double C = 1.0;       // <---
    static constexpr double Pa = N / ( m * m );
    static constexpr double MPa = 1e6 * Pa;
    static constexpr double GPa = 1e9 * Pa;
};

using TemperatureFunction = RealFunctionWithDerivative;

struct Material
{
    bool initialized = false;
    std::string name = "UninitializedMaterial";

    TemperatureFunction density = { };

    // Thermal parameters
    TemperatureFunction specificHeatCapacity = { };
    TemperatureFunction heatConductivity = { };

    double annealingTemperature = std::numeric_limits<double>::max( );
    double solidTemperature = std::numeric_limits<double>::max( );
    double liquidTemperature = std::numeric_limits<double>::max( );
    double latentHeatOfFusion = 0.0;
    double regularization = 1.0; // The higher the smoother

    //double emissivity;
    //double conductivity; // convectivity?

    TemperatureFunction thermalExpansionCoefficient = { };
    TemperatureFunction thermalExpansionCoefficientCooling = { };

    // Linear elastic parameters
    TemperatureFunction youngsModulus = { };
    TemperatureFunction poissonRatio = { };

    // Plastic parameters
    TemperatureFunction yieldStress = { };
    TemperatureFunction hardeningParameter = { };

    // beta = 0.0 -> isotropic hardening
    // beta = 1.0 -> kinematic hardening
    double plasticModelSelector = 0.0; // should be model parameter
};

enum class MaterialType : size_t 
{ 
    BasePlate  = 0, 
    Structure  = 1, 
    Powder     = 2, 
    Air        = 3,
    Undefined  = 4,
};

struct MaterialPtrs
{
    const Material* baseplate;
    const Material* structure;
    const Material* powder;
    const Material* air;
};

static constexpr const char* MaterialString[] = { "Base plate", "Structure", "Powder", "Air", "Undefined" };

inline auto materialFor( const MaterialPtrs& materials, MaterialType type )
{
    const Material* material = nullptr;

    if( type == MaterialType::Air       ) material = materials.air;
    if( type == MaterialType::BasePlate ) material = materials.baseplate;
    if( type == MaterialType::Powder    ) material = materials.powder;
    if( type == MaterialType::Structure ) material = materials.structure;

    MLHP_CHECK( type != MaterialType::Undefined, "Undefined material type encountered." );
    MLHP_CHECK( material, std::string { MaterialString[static_cast<int>( type )] } + " material is uninitialized." );

    return material;
}

inline auto parseCSV( std::filesystem::path file, 
                      std::string separator = "," )
{
    auto fstream = std::ifstream { file };
    auto data = std::vector<std::vector<std::string>> { };
    auto irow = size_t { 0 };

    MLHP_CHECK( fstream.is_open( ), "Unable to open file " + file.string( ) + "." );

    auto appendLine = [&]( auto&& line )
    {
        auto entries = std::vector<std::string> { };
        auto icolumn = size_t { 0 };

        auto appendColumn = [&]( auto begin, auto end )
        {
            auto sub = line.substr( begin, end - begin );

            if( !sub.empty( ) )
            {
                if( irow == 0 ) 
                {
                    data.push_back( { std::move( sub ) } );
                }
                else
                {
                    MLHP_CHECK( icolumn < data.size( ), "Too many columns in row " +
                        std::to_string( irow ) + " of data file " + file.string( ) + "." );

                    data[icolumn].push_back( std::move( sub ) );
                }

                icolumn += 1;
            }
        };
        
        auto index0 = size_t { 0 };
        auto index1 = line.find( separator, index0 );
        
        while( index1 != std::string::npos )
        {
            appendColumn( index0, index1 );

            index0 = index1 + 1;
            index1 = line.find( separator, index0 );
        }

        appendColumn( index0, line.size( ) );

        if( icolumn > 0 )
        {
            MLHP_CHECK( icolumn == data.size( ), "Too few columns in row " +
                std::to_string( irow ) + " of data file " + file.string( ) + "." );

            irow += 1;
        }
    };
    
    auto line = std::string { };

    while( std::getline( fstream, line ) )
    {
        appendLine( line );
    }

    fstream.close( );

    return data;
}

namespace detail 
{

inline auto parseTemperatureData( std::filesystem::path file, 
                                  std::string separator = "," )
{
    auto columns = parseCSV( file, separator );

    MLHP_CHECK( columns.size( ) == 2, "Too many columns in input file " + file.string( ) + ".");

    auto convertColumn = []( auto&& column )
    {
        auto converted = std::vector<double> { };

        for( size_t i = 1; i < column.size( ); ++i )
        {
            converted.push_back( std::stod( column[i] ) );
        }

        return converted;
    };

    return std::array { convertColumn( std::move( columns[0] ) ), 
                        convertColumn( std::move( columns[1] ) ) };
}

inline auto createTemperatureFunction( const std::string& name,
                                       std::vector<double>&& T, 
                                       std::vector<double>&& V,
                                       bool constantExtrapolation,
                                       double scaling )
{
    MLHP_CHECK( !T.empty( ), "No data point given for material " + name + "." );

    MLHP_CHECK( T.size( ) == V.size( ), "Inconsistent number of data "
        "points for parameter " + name + "." );

    for( auto& value : V )
    {
        value *= scaling;
    }

    auto extrapolate = constantExtrapolation ? 
        interpolation::Extrapolate::Constant : 
        interpolation::Extrapolate::Linear;

    return interpolation::makeLinearInterpolation( T, V, extrapolate );
}

struct ReadMaterial : Units
{
    static auto read( std::istream& istream, std::filesystem::path parentpath )
    {
        auto json = nlohmann::json::parse( istream );
        auto material = Material { .initialized = true, .name = "JsonMaterial" };
        auto input = json;//[key];

        if( input.contains( "name" ) )
        {
            material.name = input["name"];
        }

        auto readParameterFunction = [&]( std::string name, double unit ) -> TemperatureFunction
        {
            if( !input.contains( name ) )
            {
                return { };
            }

            if( auto field = input[name]; field.is_number( ) )
            {
                auto number = field.get<double>( );

                return [number]( auto ) noexcept { return std::array { number, 0.0 }; };
            }
            else if( field.is_string( ) )
            {
                auto datafile = field.get<std::filesystem::path>( );

                if( !std::filesystem::exists( datafile ) )
                {
                    datafile = parentpath / field.get<std::filesystem::path>( );
                }

                if( !std::filesystem::exists( datafile ) )
                {
                    datafile = parentpath / material.name / field.get<std::filesystem::path>( );
                }

                MLHP_CHECK( std::filesystem::exists( datafile ), "Unable to read data file " + 
                    field.get<std::string>( ) + " for parameter " + name + ".");

                auto [T, V] = detail::parseTemperatureData( datafile );

                return detail::createTemperatureFunction( name, std::move( T ), std::move( V ), true, unit );
            }
            else if( field.contains( "temperatures" ) )
            {
                MLHP_CHECK( field.contains( "values" ), "Parameter " + name + " has temperatures but no values." );
                
                auto constantExtrapolation = true;

                if( field.contains( "extrapolation" ) )
                {
                    auto extrapolation = field["extrapolation"];

                    constantExtrapolation = extrapolation == "constant";

                    MLHP_CHECK( extrapolation == "constant" || extrapolation == "linear",
                        "Invalid extrapolation \"" + std::string { extrapolation } + "\" "
                        "for parameter " + name + ". Must be \"constant\" or \"linear\"." );
                }

                return detail::createTemperatureFunction( name, 
                    field["temperatures"].get<std::vector<double>>( ), 
                    field["values"].get<std::vector<double>>( ),
                    constantExtrapolation, unit );
            }

            MLHP_THROW( "Could not read " + name + " data." );
        };

        auto readParameterConstant = [&]( std::string name, double unit ) -> double
        {
            MLHP_CHECK( input.contains( name ), "Could not find " + name + " parameter." );
            MLHP_CHECK( input[name].is_number( ), "Invalid format for parameter constant " + name + "." );

            return input[name].get<double>( ) * unit;
        };

        material.density              = readParameterFunction( "density", kg / ( m * m * m ) );
        material.specificHeatCapacity = readParameterFunction( "specificHeatCapacity", J / ( kg * C ) );
        material.heatConductivity     = readParameterFunction( "heatConductivity", W / ( m * C ) );
        material.annealingTemperature = readParameterConstant( "annealingTemperature", C );
        material.solidTemperature     = readParameterConstant( "solidTemperature", C );
        material.liquidTemperature    = readParameterConstant( "liquidTemperature", C );
        material.latentHeatOfFusion   = readParameterConstant( "latentHeatOfFusion", J / kg );
        material.thermalExpansionCoefficient = readParameterFunction( "thermalExpansionCoefficient", 1.0 );
        material.thermalExpansionCoefficientCooling = readParameterFunction( "thermalExpansionCoefficientCooling", 1.0 );
        material.youngsModulus        = readParameterFunction( "youngsModulus", Units::GPa );
        material.poissonRatio         = readParameterFunction( "poissonRatio", 1.0 );
        material.yieldStress          = readParameterFunction( "yieldStress", Units::MPa );
        material.hardeningParameter   = readParameterFunction( "hardening", Units::MPa );
        material.plasticModelSelector = 0.0;

        return material;
    }
};

} // detail

inline auto readMaterialString( std::string json )
{
    auto sstream = std::stringstream { std::move( json ) };

    return detail::ReadMaterial::read( sstream, std::filesystem::path { "." } );
}

inline auto readMaterialFile( std::filesystem::path file )
{    
    auto fstream = std::ifstream { file };
    
    MLHP_CHECK( fstream.is_open( ), "Unable to open file " + file.string( ) + "." );

    auto material = detail::ReadMaterial::read( fstream, file.parent_path( ) );

    fstream.close( );

    return material;
}

// Returns [fpc, dfpc/dT, ddfpc/ddT]
inline auto regularizedStepFunction( double Ts, double Tl, double T, double S )
{
    double Tmid = ( Tl + Ts ) / 2.0;
    double Tstd = ( Tl - Ts ) / 2.0 * S;
    double xi = ( T - Tmid ) / Tstd;

    if( std::abs( xi ) < 5.0 )
    {
        auto tanhXi = std::tanh( xi );

        double fpc_d0 = 0.5 * ( tanhXi + 1.0 );
        double fpc_d1 = ( 1.0 - tanhXi * tanhXi ) / ( 2.0 * Tstd );
        double fpc_d2 = ( tanhXi * tanhXi - 1.0 ) * tanhXi / ( Tstd * Tstd );

        return std::array { fpc_d0, fpc_d1, fpc_d2 };
    }
    else
    {
        return std::array { xi > 0.0 ? 1.0 : 0.0, 0.0, 0.0 };
    }
}

inline auto evaluatePhaseTransition( const Material& material, double T )
{
    auto [f, df, ddf] = regularizedStepFunction( material.solidTemperature, 
        material.liquidTemperature, T, material.regularization );

    auto L = material.latentHeatOfFusion;
    auto rho = material.density( std::midpoint( material.liquidTemperature, material.solidTemperature ) )[0];
    
    return std::array { f * L * rho, df * L * rho, ddf * L * rho };
}

} // namespace mlhp

#endif // MLHPBF_MATERIALS_HPP
