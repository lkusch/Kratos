//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:         BSD License
//                   Kratos default license: kratos/license.txt
//
//  Main authors:    Tobias Teschemacher
//                   Andreas Apostolatos
//                   Pooyan Dadvand
//                   Philipp Bucher
//

#if !defined(KRATOS_BREP_CURVE_ON_SURFACE_3D_H_INCLUDED )
#define  KRATOS_BREP_CURVE_ON_SURFACE_3D_H_INCLUDED

// System includes

// External includes

// Project includes
#include "geometries/geometry.h"
#include "geometries/nurbs_shape_function_utilities/nurbs_interval.h"

#include "geometries/nurbs_curve_on_surface_geometry.h"

#include "utilities/nurbs_utilities/projection_nurbs_geometry_utilities.h"

namespace Kratos
{
///@name Kratos Classes
///@{

/**
 * @class BrepCurveOnSurface
 * @ingroup KratosCore
 * @brief The BrepCurveOnSurface acts as topology for curves on surfaces.
 */
template<class TContainerPointType, class TContainerPointEmbeddedType = TContainerPointType>
class BrepCurveOnSurface
    : public Geometry<typename TContainerPointType::value_type>
{
public:
    ///@}
    ///@name Type Definitions
    ///@{

    /** Pointer definition of BrepCurveOnSurface */
    KRATOS_CLASS_POINTER_DEFINITION( BrepCurveOnSurface );

    typedef typename TContainerPointType::value_type PointType;

    typedef Geometry<typename TContainerPointType::value_type> BaseType;
    typedef Geometry<typename TContainerPointType::value_type> GeometryType;
    typedef typename GeometryType::Pointer GeometryPointer;

    typedef GeometryData::IntegrationMethod IntegrationMethod;

    typedef NurbsSurfaceGeometry<3, TContainerPointType> NurbsSurfaceType;
    typedef NurbsCurveGeometry<2, TContainerPointEmbeddedType> NurbsCurveType;

    typedef NurbsCurveOnSurfaceGeometry<3, TContainerPointEmbeddedType, TContainerPointType> NurbsCurveOnSurfaceType;

    typedef typename NurbsCurveOnSurfaceType::Pointer NurbsCurveOnSurfacePointerType;

    typedef typename BaseType::GeometriesArrayType GeometriesArrayType;

    typedef typename BaseType::IndexType IndexType;
    typedef typename BaseType::SizeType SizeType;

    typedef typename BaseType::PointsArrayType PointsArrayType;
    typedef typename BaseType::CoordinatesArrayType CoordinatesArrayType;
    typedef typename BaseType::IntegrationPointsArrayType IntegrationPointsArrayType;

    static constexpr IndexType CURVE_ON_SURFACE_INDEX = std::numeric_limits<IndexType>::max() - 2;

    ///@}
    ///@name Life Cycle
    ///@{

    /// constructor for untrimmed surface
    BrepCurveOnSurface(
        typename NurbsSurfaceType::Pointer pSurface,
        typename NurbsCurveType::Pointer pCurve,
        bool SameCurveDirection = true)
        : BaseType(PointsArrayType(), &msGeometryData)
        , mpCurveOnSurface(
            Kratos::make_shared<NurbsCurveOnSurfaceType>(
                pSurface, pCurve))
        , mCurveNurbsInterval(pCurve->DomainInterval())
        , mSameCurveDirection(SameCurveDirection)
    {
    }

    /// constructor for trimmed surface
    BrepCurveOnSurface(
        typename NurbsSurfaceType::Pointer pSurface,
        typename NurbsCurveType::Pointer pCurve,
        NurbsInterval CurveNurbsInterval,
        bool SameCurveDirection = true)
        : BaseType(PointsArrayType(), &msGeometryData)
        , mpCurveOnSurface(
            Kratos::make_shared<NurbsCurveOnSurfaceType>(
                pSurface, pCurve))
        , mCurveNurbsInterval(CurveNurbsInterval)
        , mSameCurveDirection(SameCurveDirection)
    {
    }

    /// constructor for untrimmed surface with curve on surface
    BrepCurveOnSurface(
        NurbsCurveOnSurfacePointerType pNurbsCurveOnSurface,
        bool SameCurveDirection = true)
        : BaseType(PointsArrayType(), &msGeometryData)
        , mpCurveOnSurface(pNurbsCurveOnSurface)
        , mCurveNurbsInterval(pNurbsCurveOnSurface->DomainInterval())
        , mSameCurveDirection(SameCurveDirection)
    {
    }

    /// constructor for trimmed surface with curve on surface
    BrepCurveOnSurface(
        NurbsCurveOnSurfacePointerType pNurbsCurveOnSurface,
        NurbsInterval CurveNurbsInterval,
        bool SameCurveDirection = true)
        : BaseType(PointsArrayType(), &msGeometryData)
        , mpCurveOnSurface(pNurbsCurveOnSurface)
        , mCurveNurbsInterval(CurveNurbsInterval)
        , mSameCurveDirection(SameCurveDirection)
    {
    }

    BrepCurveOnSurface()
        : BaseType(PointsArrayType(), &msGeometryData)
    {}

    explicit BrepCurveOnSurface(const PointsArrayType& ThisPoints)
        : BaseType(ThisPoints, &msGeometryData)
    {
    }

    /// Copy constructor.
    BrepCurveOnSurface( BrepCurveOnSurface const& rOther )
        : BaseType( rOther )
        , mpCurveOnSurface(rOther.mpCurveOnSurface)
        , mCurveNurbsInterval(rOther.mCurveNurbsInterval)
        , mSameCurveDirection(rOther.mSameCurveDirection)
    {
    }

    /// Copy constructor from a geometry with different point type.
    template<class TOtherContainerPointType, class TOtherContainerPointEmbeddedType>
    explicit BrepCurveOnSurface(
        BrepCurveOnSurface<TOtherContainerPointType, TOtherContainerPointEmbeddedType> const& rOther )
        : BaseType( rOther )
        , mpCurveOnSurface(rOther.mpCurveOnSurface)
        , mCurveNurbsInterval(rOther.mCurveNurbsInterval)
        , mSameCurveDirection(rOther.mSameCurveDirection)
    {
    }

    /// Destructor
    ~BrepCurveOnSurface() override = default;

    ///@}
    ///@name Operators
    ///@{

    /// Assignment operator.
    BrepCurveOnSurface& operator=( const BrepCurveOnSurface& rOther )
    {
        BaseType::operator=( rOther );
        mpCurveOnSurface = rOther.mpCurveOnSurface;
        mCurveNurbsInterval = rOther.mCurveNurbsInterval;
        mSameCurveDirection = rOther.mSameCurveDirection;
        return *this;
    }

    /// Assignment operator for geometries with different point type.
    template<class TOtherContainerPointType, class TOtherContainerPointEmbeddedType>
    BrepCurveOnSurface& operator=( BrepCurveOnSurface<TOtherContainerPointType, TOtherContainerPointEmbeddedType> const & rOther )
    {
        BaseType::operator=( rOther );
        mpCurveOnSurface = rOther.mpCurveOnSurface;
        mCurveNurbsInterval = rOther.mCurveNurbsInterval;
        mSameCurveDirection = rOther.mSameCurveDirection;
        return *this;
    }

    ///@}
    ///@name Operations
    ///@{

    typename BaseType::Pointer Create( PointsArrayType const& ThisPoints ) const override
    {
        return typename BaseType::Pointer( new BrepCurveOnSurface( ThisPoints ) );
    }

    ///@}
    ///@name Access to Geometry Parts
    ///@{

    /**
    * @brief This function returns the pointer of the geometry
    *        which is corresponding to the index.
    *        Possible indices are:
    *        SURFACE_INDEX, EMBEDDED_CURVE_INDEX or CURVE_ON_SURFACE_INDEX.
    * @param Index: SURFACE_INDEX, EMBEDDED_CURVE_INDEX or CURVE_ON_SURFACE_INDEX.
    * @return pointer of geometry, corresponding to the index.
    */
    GeometryPointer pGetGeometryPart(const IndexType Index) override
    {
        const auto& const_this = *this;
        return std::const_pointer_cast<GeometryType>(
            const_this.pGetGeometryPart(Index));
    }

    /**
    * @brief This function returns the pointer of the geometry
    *        which is corresponding to the index.
    *        Possible indices are:
    *        GeometryType::BACKGROUND_GEOMETRY_INDEX, EMBEDDED_CURVE_INDEX or CURVE_ON_SURFACE_INDEX.
    * @param Index: SURFACE_INDEX, EMBEDDED_CURVE_INDEX or CURVE_ON_SURFACE_INDEX.
    * @return pointer of geometry, corresponding to the index.
    */
    const GeometryPointer pGetGeometryPart(const IndexType Index) const override
    {
        if (Index == GeometryType::BACKGROUND_GEOMETRY_INDEX)
            return mpCurveOnSurface->pGetGeometryPart(GeometryType::BACKGROUND_GEOMETRY_INDEX);

        if (Index == CURVE_ON_SURFACE_INDEX)
            return mpCurveOnSurface;

        KRATOS_ERROR << "Index " << Index << " not existing in BrepCurveOnSurface: "
            << this->Id() << std::endl;
    }

    /**
    * @brief This function is used to check if the index is either
    *        GeometryType::BACKGROUND_GEOMETRY_INDEX or CURVE_ON_SURFACE_INDEX.
    * @param Index of the geometry part.
    * @return true if GeometryType::BACKGROUND_GEOMETRY_INDEX or CURVE_ON_SURFACE_INDEX.
    */
    bool HasGeometryPart(const IndexType Index) const override
    {
        return (Index == GeometryType::BACKGROUND_GEOMETRY_INDEX || Index == CURVE_ON_SURFACE_INDEX);
    }

    ///@}
    ///@name Set / Calculate access
    ///@{

    void Calculate(
        const Variable<array_1d<double, 3>>& rVariable,
        array_1d<double, 3>& rOutput
        ) const override
    {
        if (rVariable == PARAMETER_2D_COORDINATES) {
            mpCurveOnSurface->Calculate(rVariable, rOutput);
        }
    }

    ///@}
    ///@name Mathematical Informations
    ///@{

    /// Return polynomial degree of the nurbs curve on surface
    SizeType PolynomialDegree(IndexType LocalDirectionIndex) const override
    {
        return mpCurveOnSurface->PolynomialDegree(LocalDirectionIndex);
    }

    ///@}
    ///@name Set/ Get functions
    ///@{

    /* @brief Provides the natural boundaries of the NURBS/B-Spline curve.
     * @return domain interval.
     */
    NurbsInterval DomainInterval() const
    {
        return mCurveNurbsInterval;
    }

    /*
    * @brief Indicates if the NURBS-curve is pointing in the same direction
    *        as the B-Rep curve.
    * @return true -> brep curve and nurbs curve point in same direction.
    *        false -> brep curve and nurbs curve point in opposite directions.
    */
    bool HasSameCurveDirection()
    {
        return mSameCurveDirection;
    }

    /// Returns the NurbsCurveOnSurface::Pointer of this brep.
    NurbsCurveOnSurfacePointerType pGetCurveOnSurface()
    {
        return mpCurveOnSurface;
    }

    /// Returns the const NurbsCurveOnSurface::Pointer of this brep.
    const NurbsCurveOnSurfacePointerType pGetCurveOnSurface() const
    {
        return mpCurveOnSurface;
    }

    /// Returns number of points of NurbsCurveOnSurface.
    SizeType PointsNumberInDirection(IndexType DirectionIndex) const override
    {
        return mpCurveOnSurface->PointsNumberInDirection(DirectionIndex);
    }

    ///@}
    ///@name Curve Properties
    ///@{

    /* @brief Provides intersections of the nurbs curve with the knots of the surface,
     *         using the interval of this curve.
     * @param vector of span intervals.
     * @param index of chosen direction, for curves always 0.
     */
    void Spans(std::vector<double>& rSpans, IndexType DirectionIndex = 0) const
    {
        mpCurveOnSurface->Spans(rSpans,
            mCurveNurbsInterval.GetT0(), mCurveNurbsInterval.GetT1());
    }

    ///@}
    ///@name Projection
    ///@{

    /* Makes projection of rPointGlobalCoordinates to
     * the closest point rProjectedPointGlobalCoordinates on the curve,
     * with local coordinates rProjectedPointLocalCoordinates.
     *
     * Condiders limits of this BrepCurveOnSurface as borders.
     *
     * @param Tolerance is the breaking criteria.
     * @return 1 -> projection succeeded
     *         0 -> projection failed
     */
    int ProjectionPoint(
        const CoordinatesArrayType& rPointGlobalCoordinates,
        CoordinatesArrayType& rProjectedPointGlobalCoordinates,
        CoordinatesArrayType& rProjectedPointLocalCoordinates,
        const double Tolerance = std::numeric_limits<double>::epsilon()
    ) const override
    {
        return ProjectionNurbsGeometryUtilities::NewtonRaphsonCurve(
            rProjectedPointLocalCoordinates,
            rPointGlobalCoordinates,
            rProjectedPointGlobalCoordinates,
            *this,
            20, Tolerance);
    }

    ///@}
    ///@name Geometrical Operations
    ///@{

    /// Provides the center of the underlying curve on surface
    Point Center() const override
    {
        return mpCurveOnSurface->Center();
    }

    /*
    * @brief This method maps from dimension space to working space.
    * @param rResult array_1d<double, 3> with the coordinates in working space
    * @param LocalCoordinates The local coordinates in dimension space
    * @return array_1d<double, 3> with the coordinates in working space
    * @see PointLocalCoordinates
    */
    CoordinatesArrayType& GlobalCoordinates(
        CoordinatesArrayType& rResult,
        const CoordinatesArrayType& rLocalCoordinates
    ) const override
     {
        return mpCurveOnSurface->GlobalCoordinates(rResult, rLocalCoordinates);
    }
    
    /**
    * @brief This method maps from local space to global/working space and computes the
    *        number of derivatives at the underlying nurbs curve on surface
    *        at the parameter rLocalCoordinates[0].
    *
    * @param LocalCoordinates The local coordinates in paramater space
    * @param Derivative Number of computed derivatives
    *        0 -> Location = PointLocalCoordinates
    *        1 -> Tangent
    *        2 -> Curvature
    *        ...
    * @return std::vector<array_1d<double, 3>> with the global space derivatives
    */
    void GlobalSpaceDerivatives(
        std::vector<CoordinatesArrayType>& rGlobalSpaceDerivatives,
        const CoordinatesArrayType& rLocalCoordinates,
        const SizeType DerivativeOrder) const override
    {
        return mpCurveOnSurface->GlobalSpaceDerivatives(rGlobalSpaceDerivatives, rLocalCoordinates, DerivativeOrder);
    }

    /**
    * Returns whether given arbitrary point is inside the Geometry and the respective
    * local point for the given global point
    * @param rPoint The point to be checked if is inside o note in global coordinates
    * @param rResult The local coordinates of the point
    * @param Tolerance The  tolerance that will be considered to check if the point is inside or not
    * @return True if the point is inside, false otherwise
    */
    bool IsInside(
        const CoordinatesArrayType& rPoint,
        CoordinatesArrayType& rResult,
        const double Tolerance = std::numeric_limits<double>::epsilon()
    ) const override
    {
        KRATOS_ERROR << "IsInside is not yet implemented within the BrepCurveOnSurface";
    }

    ///@}
    ///@name Geometrical Informations
    ///@{

    /// Computes the length of a nurbs curve
    double Length() const override
    {
        IntegrationPointsArrayType integration_points;
        CreateIntegrationPoints(integration_points);

        double length = 0.0;
        for (IndexType i = 0; i < integration_points.size(); ++i) {
            const double determinant_jacobian = mpCurveOnSurface->DeterminantOfJacobian(integration_points[i]);
            length += integration_points[i].Weight() * determinant_jacobian;
        }
        return length;
    }

    ///@}
    ///@name Integration Points
    ///@{

    /* Creates integration points on the nurbs surface of this geometry.
     * @param return integration points.
     */
    void CreateIntegrationPoints(
        IntegrationPointsArrayType& rIntegrationPoints) const override
    {
        const SizeType points_per_span = mpCurveOnSurface->PolynomialDegree(0) + 1;

        std::vector<double> spans;
        Spans(spans);

        IntegrationPointUtilities::CreateIntegrationPoints1D(
            rIntegrationPoints, spans, points_per_span);
    }

    ///@}
    ///@name Quadrature Point Geometries
    ///@{

    /* @brief creates a list of quadrature point geometries
     *        from a list of integration points on the
     *        curve on surface of this geometry.
     *
     * @param rResultGeometries list of quadrature point geometries.
     * @param rIntegrationPoints list of provided integration points.
     * @param NumberOfShapeFunctionDerivatives the number of evaluated
     *        derivatives of shape functions at the quadrature point geometries.
     *
     * @see quadrature_point_geometry.h
     */
    void CreateQuadraturePointGeometries(
        GeometriesArrayType& rResultGeometries,
        IndexType NumberOfShapeFunctionDerivatives) override
    {
        mpCurveOnSurface->CreateQuadraturePointGeometries(
            rResultGeometries, NumberOfShapeFunctionDerivatives);

        for (IndexType i = 0; i < rResultGeometries.size(); ++i) {
            rResultGeometries(i)->SetGeometryParent(this);
        }
    }

    ///@}
    ///@name Shape Function
    ///@{

    Vector& ShapeFunctionsValues(
        Vector &rResult,
        const CoordinatesArrayType& rCoordinates) const override
    {
        return mpCurveOnSurface->ShapeFunctionsValues(rResult, rCoordinates);
    }

    Matrix& ShapeFunctionsLocalGradients(
        Matrix& rResult,
        const CoordinatesArrayType& rCoordinates) const override
    {
        return mpCurveOnSurface->ShapeFunctionsLocalGradients(rResult, rCoordinates);
    }

    GeometryData::KratosGeometryFamily GetGeometryFamily() const override
    {
        return GeometryData::Kratos_Brep;
    }

    GeometryData::KratosGeometryType GetGeometryType() const override
    {
        return GeometryData::Kratos_Brep_Curve;
    }
    ///@}
    ///@name Input and output
    ///@{


    ///@}
    ///@name Information
    ///@{

    /// Turn back information as a string.
    std::string Info() const override
    {
        return "Brep face curve";
    }

    /// Print information about this object.
    void PrintInfo( std::ostream& rOStream ) const override
    {
        rOStream << "Brep face curve";
    }

    /// Print object's data.
    void PrintData( std::ostream& rOStream ) const override
    {
        BaseType::PrintData( rOStream );
        std::cout << std::endl;
        rOStream << "    Brep face curve : " << std::endl;
    }

    ///@}

private:
    ///@name Static Member Variables
    ///@{

    static const GeometryData msGeometryData;

    static const GeometryDimension msGeometryDimension;

    ///@}
    ///@name Member Variables
    ///@{

    NurbsCurveOnSurfacePointerType mpCurveOnSurface;

    NurbsInterval mCurveNurbsInterval;

    /** true-> brep curve and nurbs curve point in same direction.
    *  false-> brep curve and nurbs curve point in opposite directions. */
    bool mSameCurveDirection;

    ///@}
    ///@name Serialization
    ///@{

    friend class Serializer;

    void save( Serializer& rSerializer ) const override
    {
        KRATOS_SERIALIZE_SAVE_BASE_CLASS( rSerializer, BaseType );
        rSerializer.save("CurveOnSurface", mpCurveOnSurface);
        rSerializer.save("NurbsInterval", mCurveNurbsInterval);
        rSerializer.save("SameCurveDirection", mSameCurveDirection);
    }

    void load( Serializer& rSerializer ) override
    {
        KRATOS_SERIALIZE_LOAD_BASE_CLASS( rSerializer, BaseType );
        rSerializer.load("CurveOnSurface", mpCurveOnSurface);
        rSerializer.load("NurbsInterval", mCurveNurbsInterval);
        rSerializer.load("SameCurveDirection", mSameCurveDirection);
    }

    ///@}
}; // Class BrepCurveOnSurface

///@name Input and output
///@{

/// input stream functions
template<class TContainerPointType, class TContainerPointEmbeddedType = TContainerPointType> inline std::istream& operator >> (
    std::istream& rIStream,
    BrepCurveOnSurface<TContainerPointType, TContainerPointEmbeddedType>& rThis );

/// output stream functions
template<class TContainerPointType, class TContainerPointEmbeddedType = TContainerPointType> inline std::ostream& operator << (
    std::ostream& rOStream,
    const BrepCurveOnSurface<TContainerPointType, TContainerPointEmbeddedType>& rThis )
{
    rThis.PrintInfo( rOStream );
    rOStream << std::endl;
    rThis.PrintData( rOStream );
    return rOStream;
}

///@}
///@name Static Type Declarations
///@{

template<class TContainerPointType, class TContainerPointEmbeddedType> const
GeometryData BrepCurveOnSurface<TContainerPointType, TContainerPointEmbeddedType>::msGeometryData(
    &msGeometryDimension,
    GeometryData::GI_GAUSS_1,
    {}, {}, {});

template<class TContainerPointType, class TContainerPointEmbeddedType>
const GeometryDimension BrepCurveOnSurface<TContainerPointType, TContainerPointEmbeddedType>::msGeometryDimension(
    1, 3, 2);

///@}
}// namespace Kratos.

#endif // KRATOS_BREP_CURVE_ON_SURFACE_3D_H_INCLUDED  defined
