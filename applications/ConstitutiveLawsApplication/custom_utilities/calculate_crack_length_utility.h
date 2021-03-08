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
#include "processes/process.h"
#include "includes/model_part.h"
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
template <class TDimension>
class KRATOS_API(CONSTITUTIVE_LAWS_APPLICATION) CalculateCrackLengthUtility
    : public Process
{
public:
    ///@name Type Definitions
    ///@{

    /// Pointer definition of CalculateCrackLengthUtility
    KRATOS_CLASS_POINTER_DEFINITION(CalculateCrackLengthUtility);

    /// Definition of size type
    typedef std::size_t SizeType;

    static constexpr SizeType Dimension = TDimension;

    static constexpr SizeType VoigtSize = (Dimension == 3) ? 6 : 3;

    /// The definition of the Voigt array type
    typedef array_1d<double, VoigtSize> BoundedVectorVoigtType;
    typedef array_1d<double, Dimension> BoundedVectorDimensionType;

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

    int mCrackTipElementId = 0;
    double mCrackLength    = 0;
    BoundedVectorVoigtType mAdvancingDirection = ZeroVector(VoigtSize);
    std::vector<int> mArrayElementIds;

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

    /// Assignment operator.
    CalculateCrackLengthUtility &operator=(CalculateCrackLengthUtility const &rOther);
};
} // namespace Kratos.
#endif // KRATOS_CALCULATE_CRACK_LENGTH_UTILITY_H_INCLUDED  defined
