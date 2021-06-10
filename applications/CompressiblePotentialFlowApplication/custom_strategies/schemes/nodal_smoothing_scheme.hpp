
//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:         BSD License
//                   Kratos default license: kratos/license.txt
//
//  Main authors:    Ignasi de Pouplana


#if !defined(KRATOS_NODAL_SMOOTHING_SCHEME )
#define  KRATOS_NODAL_SMOOTHING_SCHEME

// Project includes
#include "includes/define.h"
#include "includes/model_part.h"
#include "solving_strategies/schemes/residualbased_incrementalupdate_static_scheme.h"

// Application includes
#include "compressible_potential_flow_application_variables.h"

namespace Kratos
{

template<class TSparseSpace, class TDenseSpace>

class NodalSmoothingScheme : public ResidualBasedIncrementalUpdateStaticScheme<TSparseSpace,TDenseSpace>
{

public:

    KRATOS_CLASS_POINTER_DEFINITION( NodalSmoothingScheme );

    typedef Scheme<TSparseSpace,TDenseSpace>                      BaseType;
    typedef typename BaseType::TSystemMatrixType         TSystemMatrixType;
    typedef typename BaseType::TSystemVectorType         TSystemVectorType;

//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    ///Constructor
    NodalSmoothingScheme() : ResidualBasedIncrementalUpdateStaticScheme<TSparseSpace,TDenseSpace>()
    {
    }

    //------------------------------------------------------------------------------------

    ///Destructor
    ~NodalSmoothingScheme() override {}

//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    /**
     * @brief Function called once at the end of a solution step, after convergence is reached if an iterative process is needed
     * @param rModelPart The model part of the problem to solve
     * @param A LHS matrix
     * @param Dx Incremental update of primary variables
     * @param b RHS Vector
     */
    void FinalizeSolutionStep(
        ModelPart& rModelPart,
        TSystemMatrixType& A,
        TSystemVectorType& Dx,
        TSystemVectorType& b) override
    {
        KRATOS_TRY

        const int NNodes = static_cast<int>(rModelPart.Nodes().size());
        ModelPart::NodesContainerType::iterator node_begin = rModelPart.NodesBegin();

        // Clear nodal variables
        #pragma omp parallel for
        for(int i = 0; i < NNodes; i++)
        {
            ModelPart::NodesContainerType::iterator itNode = node_begin + i;

            itNode->FastGetSolutionStepValue(NODAL_AREA) = 0.0;
            array_1d<double,3>& rTransportVelocity = itNode->FastGetSolutionStepValue(VELOCITY);
            noalias(rTransportVelocity) = ZeroVector(3);
        }

        BaseType::FinalizeSolutionStep(rModelPart,A,Dx,b);

        const double& velocity_height_factor = rModelPart.GetProcessInfo()[VELOCITY_HEIGHT_FACTOR];

        // Compute smoothed nodal variables
        #pragma omp parallel for
        for(int n = 0; n < NNodes; n++)
        {
            ModelPart::NodesContainerType::iterator itNode = node_begin + n;

            const double& NodalArea = itNode->FastGetSolutionStepValue(NODAL_AREA);
            if (NodalArea>1.0e-20)
            {
                const double InvNodalArea = 1.0/NodalArea;
                array_1d<double,3>& rTransportVelocity = itNode->FastGetSolutionStepValue(VELOCITY);
                array_1d<double,3>& rNodalVelocity = itNode->FastGetSolutionStepValue(NODAL_VELOCITY);
                noalias(rNodalVelocity) = rTransportVelocity;
                for(unsigned int i = 0; i<3; i++)
                {
                    rNodalVelocity[i] *= InvNodalArea;
                    rTransportVelocity[i] *= InvNodalArea * velocity_height_factor;
                }
            }
        }

        KRATOS_CATCH("")
    }

//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

protected:

    /// Member Variables

//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


}; // Class NodalSmoothingScheme
}  // namespace Kratos

#endif // KRATOS_NODAL_SMOOTHING_SCHEME defined
