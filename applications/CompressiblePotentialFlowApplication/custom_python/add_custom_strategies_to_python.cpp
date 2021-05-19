//
//   Project Name:        KratosPoromechanicsApplication $
//   Last Modified by:    $Author:    Ignasi de Pouplana $
//   Date:                $Date:            January 2016 $
//   Revision:            $Revision:                 1.0 $
//

// External includes
#include "spaces/ublas_space.h"

// Project includes
#include "custom_python/add_custom_strategies_to_python.h"
#include "includes/kratos_parameters.h"

//strategies

//builders and solvers

//schemes
#include "custom_strategies/schemes/nodal_smoothing_scheme.hpp"

//linear solvers
// #include "linear_solvers/linear_solver.h"


namespace Kratos
{

namespace Python
{

namespace py = pybind11;

void  AddCustomStrategiesToPython(pybind11::module& m)
{
    typedef UblasSpace<double, CompressedMatrix, Vector> SparseSpaceType;
    typedef UblasSpace<double, Matrix, Vector> LocalSpaceType;

    typedef Scheme< SparseSpaceType, LocalSpaceType > BaseSchemeType;

    typedef NodalSmoothingScheme< SparseSpaceType, LocalSpaceType >  NodalSmoothingSchemeType;

//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    py::class_< NodalSmoothingSchemeType, typename NodalSmoothingSchemeType::Pointer, BaseSchemeType >
    (m, "NodalSmoothingScheme")
    .def( py::init< >());

}

}  // namespace Python.
} // Namespace Kratos
