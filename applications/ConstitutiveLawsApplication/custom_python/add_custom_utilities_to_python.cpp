// KRATOS   ___                _   _ _         _   _             __
//        / __\___  _ __  ___| |_(_) |_ _   _| |_(_)_   _____  / /  __ ___      _____
//       / /  / _ \| '_ \/ __| __| | __| | | | __| \ \ / / _ \/ /  / _` \ \ /\ / / __|
//      / /__| (_) | | | \__ \ |_| | |_| |_| | |_| |\ V /  __/ /__| (_| |\ V  V /\__ \
//      \____/\___/|_| |_|___/\__|_|\__|\__,_|\__|_| \_/ \___\____/\__,_| \_/\_/ |___/  Application
//
//  License:         BSD License
//                     license: structural_mechanics_application/license.txt
//
//  Main authors:   Alejandro Cornejo
//
//

// System includes

// External includes

// Project includes
#include "custom_python/add_custom_utilities_to_python.h"

//Utilities
#include "custom_utilities/calculate_crack_length_utility.h"

namespace Kratos {
namespace Python {

void  AddCustomUtilitiesToPython(pybind11::module& m)
{
    namespace py = pybind11;

    py::class_<CalculateCrackLengthUtility>(m, "CalculateCrackLengthUtility")
        .def(py::init<ModelPart&, const array_1d<double, 3>&, const std::size_t>())
        // .def(py::init<ModelPart&, const array_1d<double, 3>&>())
        ;

}

}  // namespace Python.
} // Namespace Kratos

