// KRATOS   ___                _   _ _         _   _             __
//        / __\___  _ __  ___| |_(_) |_ _   _| |_(_)_   _____  / /  __ ___      _____
//       / /  / _ \| '_ \/ __| __| | __| | | | __| \ \ / / _ \/ /  / _` \ \ /\ / / __|
//      / /__| (_) | | | \__ \ |_| | |_| |_| | |_| |\ V /  __/ /__| (_| |\ V  V /\__ \
//      \____/\___/|_| |_|___/\__|_|\__|\__,_|\__|_| \_/ \___\____/\__,_| \_/\_/ |___/  Application
//
//  License:         BSD License
//                   license: constitutive_laws_application/license.txt
//
//  Main authors:   Alejandro Cornejo
//  Collaborator:
//

#if !defined(KRATOS_CALCULATE_CRACK_LENGTH_UTILITY_H_INCLUDED)
#define KRATOS_CALCULATE_CRACK_LENGTH_UTILITY_H_INCLUDED

// System includes

// External includes

// Project includes

#include "structural_mechanics_application_variables.h"

namespace Kratos
{

///@name Kratos Globals
///@{

///@}
///@name Type Definitions
///@{

///@}
///@name  Enum's
///@{

///@}
///@name  Functions
///@{

///@}
///@name Kratos Classes
///@{

/**
 * @class CalculateCrackLengthUtility
 * @ingroup ConstitutiveLawsApplication
 * @brief This utility computed the crack length in damage mechanics
 * @authors Alejandro Cornejo
 */
class CalculateCrackLengthUtility
{
public:
    ///@name Type Definitions
    ///@{

    /// Pointer definition of CalculateCrackLengthUtility
    KRATOS_CLASS_POINTER_DEFINITION(CalculateCrackLengthUtility);

    /// Definition of size type
    typedef std::size_t SizeType;

    /// Definition of index type
    typedef std::size_t IndexType;

    /// Definition of the zero tolerance
    static constexpr double tolerance = std::numeric_limits<double>::epsilon();

    ///@}
    ///@name Life Cycle
    ///@{

    /// Constructor
    CalculateCrackLengthUtility()
    {
    }

    /// Destructor.
    virtual ~CalculateCrackLengthUtility() {}

    ///@}
    ///@name Operators
    ///@{

    ///@}
    ///@name Operations
    ///@{

protected:
    ///@name Protected static Member Variables
    ///@{

    ///@}
    ///@name Protected member Variables
    ///@{

    ///@}
    ///@name Protected Operators
    ///@{

    ///@}
    ///@name Protected Operations
    ///@{

    ///@}
    ///@name Protected  Access
    ///@{

    ///@}
    ///@name Protected Inquiry
    ///@{

    ///@}
    ///@name Protected LifeCycle
    ///@{

    ///@}
private:
    ///@name Static Member Variables
    ///@{

    ///@}
    ///@name Member Variables
    ///@{

    ///@}
    ///@name Private Operators
    ///@{

    ///@}
    ///@name Private Operations
    ///@{

protected:
    ///@name Protected static Member Variables
    ///@{

    ///@}
    ///@name Protected member Variables
    ///@{

    ///@}
    ///@name Protected Operators
    ///@{

    ///@}
    ///@name Protected Operations
    ///@{

    ///@}
    ///@name Protected  Access
    ///@{

    ///@}
    ///@name Protected Inquiry
    ///@{

    ///@}
    ///@name Protected LifeCycle
    ///@{

    ///@}
private:
    ///@name Static Member Variables
    ///@{

    ///@}
    ///@name Member Variables
    ///@{

    ///@}
    ///@name Private Operators
    ///@{

    ///@}
    ///@name Private Operations
    ///@{

    ///@}
    ///@name Private  Access
    ///@{

    ///@}
    ///@name Private Inquiry
    ///@{

    ///@}
    ///@name Un accessible methods
    ///@{

    /// Assignment operator.
    CalculateCrackLengthUtility &operator=(CalculateCrackLengthUtility const &rOther);
};
} // namespace Kratos.
#endif // KRATOS_CALCULATE_CRACK_LENGTH_UTILITY_H_INCLUDED  defined
