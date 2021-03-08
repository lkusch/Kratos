// KRATOS   ___                _   _ _         _   _             __
//        / __\___  _ __  ___| |_(_) |_ _   _| |_(_)_   _____  / /  __ ___      _____
//       / /  / _ \| '_ \/ __| __| | __| | | | __| \ \ / / _ \/ /  / _` \ \ /\ / / __|
//      / /__| (_) | | | \__ \ |_| | |_| |_| | |_| |\ V /  __/ /__| (_| |\ V  V /\__ \
//      \____/\___/|_| |_|___/\__|_|\__|\__,_|\__|_| \_/ \___\____/\__,_| \_/\_/ |___/  Application
//
//  License:         BSD License
//                   license: constitutive_laws_application/license.txt
//
//  Main authors:    Alejandro Cornejo Velazquez
//                   Riccardo Rossi
//


// System includes

#if defined(KRATOS_PYTHON)
// External includes
#include <pybind11/pybind11.h>


// Project includes
#include "includes/define_python.h"
#include "constitutive_laws_application.h"
#include "constitutive_laws_application_variables.h"

#include "custom_python/add_custom_constitutive_laws_to_python.h"
#include "custom_python/add_custom_utilities_to_python.h"


namespace Kratos {
namespace Python {

PYBIND11_MODULE(KratosConstitutiveLawsApplication,m)
{
    namespace py = pybind11;

    py::class_<KratosConstitutiveLawsApplication,
        KratosConstitutiveLawsApplication::Pointer,
        KratosApplication>(m, "KratosConstitutiveLawsApplication")
        .def(py::init<>())
        ;

    AddCustomConstitutiveLawsToPython(m);
    AddCustomUtilitiesToPython(m);

    KRATOS_REGISTER_IN_PYTHON_VARIABLE(m, CRACK_LENGTH)
}

} // namespace Python.
} // namespace Kratos.

#endif // KRATOS_PYTHON defined
