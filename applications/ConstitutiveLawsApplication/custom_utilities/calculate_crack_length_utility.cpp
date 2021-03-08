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

// System includes

// External includes

// Project includes
#include "custom_utilities/calculate_crack_length_utility.h"

namespace Kratos
{
/***********************************************************************************/
/***********************************************************************************/

    CalculateCrackLengthUtility::CalculateCrackLengthUtility(
        ModelPart& rModelPart,
        const BoundedVectorDimensionType& rAdvancingDirection,
        const SizeType InitialElementId
        ) : mrModelPart(rModelPart),
            mAdvancingDirection(rAdvancingDirection),
            mCrackTipElementId(InitialElementId)
    {
        if (mCrackTipElementId > 0)
            mArrayElementIds.push_back(mCrackTipElementId);
    }

/***********************************************************************************/
/***********************************************************************************/

    CalculateCrackLengthUtility::CalculateCrackLengthUtility(
        ModelPart& rModelPart,
        const BoundedVectorDimensionType& rAdvancingDirection
        ) : mrModelPart(rModelPart),
            mAdvancingDirection(rAdvancingDirection)
    {
    }

/***********************************************************************************/
/***********************************************************************************/

    double CalculateCrackLengthUtility::RetrieveCrackLength()
    {
        // for (auto& r_elem : mrModelPart.Elements()) {

        // }
        return 0.0;
    }

/***********************************************************************************/
/***********************************************************************************/

/***********************************************************************************/
/***********************************************************************************/

/***********************************************************************************/
/***********************************************************************************/

/***********************************************************************************/
/***********************************************************************************/

} // namespace Kratos.

