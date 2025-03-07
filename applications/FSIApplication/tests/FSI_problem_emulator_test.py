from KratosMultiphysics import *
from KratosMultiphysics.FSIApplication import *
import KratosMultiphysics.StructuralMechanicsApplication as KratosStructural

import KratosMultiphysics.KratosUnittest as UnitTest
import KratosMultiphysics.kratos_utilities as KratosUtils

if KratosUtils.CheckIfApplicationsAvailable("StructuralMechanicsApplication"):
    from KratosMultiphysics.StructuralMechanicsApplication import python_solvers_wrapper_structural

from os import remove

class WorkFolderScope:
    # TODO use KratosUnittest.WorkFolderScope
    def __init__(self, work_folder):
        self.currentPath = os.getcwd()
        self.scope = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),work_folder))

    def __enter__(self):
        os.chdir(self.scope)

    def __exit__(self, type, value, traceback):
        os.chdir(self.currentPath)

@UnitTest.skipIfApplicationsNotAvailable("StructuralMechanicsApplication", "LinearSolversApplication")
class FSIProblemEmulatorTest(UnitTest.TestCase):

    def setUp(self):
        self.work_folder = "FSIProblemEmulatorTest"
        self.input_file = "test_FSI_emulator_Structural"

        self.Dt = 0.1
        self.end_time = 1.0

        self.point_load_updater = 1.5
        self.initial_point_load = 10000

        self.max_nl_it = 250
        self.nl_tol = 1.0e-10
        self.initial_relaxation = 0.825

    def tearDown(self):
        self.deleteOutFile(self.input_file+'.time')

    def deleteOutFile(self,filename):
        with WorkFolderScope(self.work_folder):
            try:
                remove(filename)
            except FileNotFoundError as e:
                pass

    def test_FSI_problem_emulator_with_aitken(self):
        self.coupling_utility = AitkenConvergenceAccelerator(self.initial_relaxation)
        self.RunTestCase()

    def test_FSI_problem_emulator_with_MVQN(self):
        abs_cut_off = 1.0e-2
        used_in_block_newton = False
        self.coupling_utility = MVQNFullJacobianConvergenceAccelerator(self.initial_relaxation, abs_cut_off, used_in_block_newton)
        self.RunTestCase()

    def test_FSI_problem_emulator_with_IBQN_MVQN(self):
        abs_cut_off = 1.0e-2
        self.fluid_emulator_stiffness = 1000.0
        ibqn_mvqn_settings = Parameters(r'''{
            "w_0" : 0.825,
            "abs_cut_off_tol" : 1e-2
        }''')
        self.coupling_utility = IBQNMVQNConvergenceAccelerator(ibqn_mvqn_settings)
        self.RunTestCaseIBN()

    def test_FSI_problem_emulator_with_MVQN_recursive(self):
        buffer_size = 7
        abs_cut_off = 1.0e-2
        self.coupling_utility = MVQNRecursiveJacobianConvergenceAccelerator(self.initial_relaxation, buffer_size, abs_cut_off)
        self.RunTestCase()

    def RunTestCase(self):
        StructureSolverSettings = Parameters("""
        {
            "problem_data": {
                "parallel_type" : "OpenMP"
            },
            "solver_settings" : {
                "model_part_name"         : "Structure",
                "domain_size"             : 2,
                "solver_type"             : "Dynamic",
                "echo_level"              : 0,
                "analysis_type"           : "linear",
                "time_integration_method" : "implicit",
                "scheme_type"             : "bossak",
                "model_import_settings"              : {
                    "input_type"       : "mdpa",
                    "input_filename"   : "test_FSI_emulator_Structural",
                    "input_file_label" : 0
                },
                "material_import_settings" :{
                    "materials_filename": "materials_2D.json"
                },
                "line_search"                        : false,
                "convergence_criterion"              : "Residual_criterion",
                "displacement_relative_tolerance"    : 1e-8,
                "displacement_absolute_tolerance"    : 1e-10,
                "residual_relative_tolerance"        : 1e-8,
                "residual_absolute_tolerance"        : 1e-10,
                "max_iteration"                      : 20,
                "rotation_dofs"                      : false,
                "linear_solver_settings"             : {
                    "solver_type" : "LinearSolversApplication.sparse_lu",
                    "scaling"     : true
                }
            }
        }
        """)

        with WorkFolderScope(self.work_folder):

            self.model = Model()

            # Construct the structure solver
            self.structure_solver = python_solvers_wrapper_structural.CreateSolver(self.model, StructureSolverSettings)

            self.structure_solver.AddVariables()

            self.structure_solver.ImportModelPart()

            self.structure_solver.PrepareModelPart()

            self.structure_main_model_part = self.model["Structure"]

            self.structure_solver.AddDofs()

            self.SetStructureBoundaryConditions()

            self.structure_solver.Initialize()

            self.coupling_utility.Initialize()

            residual_size = self.GetInterfaceProblemSize()*2                   # Interface DOFs number times PROBLEM_SIZE
            self.iteration_value = Vector(residual_size)     # Interface solution guess (it might be velocity or fluxes depending on the type of coupling)
            for i in range(0,residual_size):
                self.iteration_value[i] = 0.0

            step = 0
            time = 0.0


            while(time <= self.end_time):

                time = time + self.Dt
                step = step + 1

                print("##################################")
                print("########## step = ", step, "#############")
                print("##################################")

                self.structure_solver.main_model_part.ProcessInfo.SetValue(TIME_STEPS, step)

                self.structure_main_model_part.CloneTimeStep(time)

                self.PointLoadUpdate()

                self.structure_solver.InitializeSolutionStep()
                self.structure_solver.Predict()

                self.coupling_utility.InitializeSolutionStep()

                for nl_it in range(1,self.max_nl_it+1):

                    self.coupling_utility.InitializeNonLinearIteration()

                    # Residual computation
                    disp_residual = self.ComputeDirichletNeumannResidual()
                    nl_res_norm = UblasSparseSpace().TwoNorm(disp_residual)

                    print("nl_it: ",nl_it," nl_res_norm: ",nl_res_norm)

                    # Check convergence
                    if nl_res_norm < self.nl_tol:
                        break

                    else:
                        # If convergence is not achieved, perform the correction of the prediction
                        self.coupling_utility.UpdateSolution(disp_residual, self.iteration_value)
                        self.coupling_utility.FinalizeNonLinearIteration()

                self.structure_solver.FinalizeSolutionStep()
                self.coupling_utility.FinalizeSolutionStep()

                # Unitcest convergence criterion check
                self.assertLess(nl_res_norm, self.nl_tol)

    def RunTestCaseIBN(self):
        StructureSolverSettings = Parameters("""
        {
            "problem_data": {
                "parallel_type" : "OpenMP"
            },
            "solver_settings" : {
                "model_part_name"         : "Structure",
                "domain_size"             : 2,
                "solver_type"             : "Dynamic",
                "echo_level"              : 0,
                "analysis_type"           : "linear",
                "time_integration_method" : "implicit",
                "scheme_type"             : "bossak",
                "model_import_settings"              : {
                    "input_type"       : "mdpa",
                    "input_filename"   : "test_FSI_emulator_Structural",
                    "input_file_label" : 0
                },
                "material_import_settings" :{
                    "materials_filename": "materials_2D.json"
                },
                "line_search"                        : false,
                "convergence_criterion"              : "Residual_criterion",
                "displacement_relative_tolerance"    : 1e-8,
                "displacement_absolute_tolerance"    : 1e-10,
                "residual_relative_tolerance"        : 1e-8,
                "residual_absolute_tolerance"        : 1e-10,
                "max_iteration"                      : 20,
                "rotation_dofs"                      : false,
                "linear_solver_settings"             : {
                    "solver_type" : "LinearSolversApplication.sparse_lu",
                    "scaling"     : true
                }
            }
        }
        """)

        with WorkFolderScope(self.work_folder):

            self.model = Model()

            # Construct the structure solver
            self.structure_solver = python_solvers_wrapper_structural.CreateSolver(self.model, StructureSolverSettings)

            self.structure_solver.AddVariables()

            self.structure_solver.ImportModelPart()

            self.structure_solver.PrepareModelPart()

            self.structure_main_model_part = self.model["Structure"]

            self.structure_solver.AddDofs()

            self.SetStructureBoundaryConditions()

            self.structure_solver.Initialize()

            self.coupling_utility.Initialize()

            residual_size = self.GetInterfaceProblemSize()*2 # Interface DOFs number times PROBLEM_SIZE
            self.iteration_value_u = Vector(residual_size) # Interface displacement iteration guess
            self.iteration_value_f = Vector(residual_size) # Interface fluxes iteration guess
            self.corrected_iteration_value_u = Vector(residual_size) # Interface displacement iteration guess
            self.corrected_iteration_value_f = Vector(residual_size) # Interface fluxes iteration guess
            for i in range(0,residual_size):
                self.iteration_value_u[i] = 0.0
                self.iteration_value_f[i] = 0.0
                self.corrected_iteration_value_u[i] = 0.0
                self.corrected_iteration_value_f[i] = 0.0

            step = 0
            time = 0.0

            while(time <= self.end_time):

                time = time + self.Dt
                step = step + 1

                print("##################################")
                print("########## step = ", step, "#############")
                print("##################################")

                self.structure_solver.main_model_part.ProcessInfo.SetValue(TIME_STEPS, step)

                self.structure_main_model_part.CloneTimeStep(time)

                self.PointLoadUpdate()

                self.structure_solver.InitializeSolutionStep()
                self.structure_solver.Predict()

                self.coupling_utility.InitializeSolutionStep()

                # Compute and check first residual
                disp_residual = self.__ComputeInitialResidual()
                nl_res_norm = UblasSparseSpace().TwoNorm(disp_residual)
                if nl_res_norm > self.nl_tol:
                    for nl_it in range(self.max_nl_it):

                        self.coupling_utility.InitializeNonLinearIteration()

                        # Update the structure displacement values
                        self.coupling_utility.UpdateSolutionRight(self.corrected_iteration_value_f, self.iteration_value_u, self.corrected_iteration_value_u)

                        # Solve fluid emulator with the obtained displacements
                        self.__SolveFluidEmulator()

                        # Update the fluid emulator force values
                        self.coupling_utility.UpdateSolutionLeft(self.corrected_iteration_value_u, self.iteration_value_f, self.corrected_iteration_value_f)

                        # Finalize the current non-linear iteration
                        self.coupling_utility.FinalizeNonLinearIteration()

                        # Transfer fluid emulator load to structure
                        self.__TransferFluidEmulatorLoad()

                        # Solve the structure problem
                        self.structure_solver.SolveSolutionStep()

                        # Compute displalcement residual
                        disp_residual = self.__ComputeStructureResidual()

                        # Residual computation
                        nl_res_norm = UblasSparseSpace().TwoNorm(disp_residual)
                        print("nl_it: ",nl_it," nl_res_norm: ",nl_res_norm)

                        # Check convergence
                        if nl_res_norm < self.nl_tol:
                            break

                self.structure_solver.FinalizeSolutionStep()
                self.coupling_utility.FinalizeSolutionStep()

                # Unitcest convergence criterion check
                self.assertLess(nl_res_norm, self.nl_tol)

    def SetStructureBoundaryConditions(self):
        zero_vect = Vector(3)
        zero_vect[0] = 0.0
        zero_vect[1] = 0.0
        zero_vect[2] = 0.0

        # Constraint boundary condition
        for node in self.structure_main_model_part.GetSubModelPart("DISPLACEMENT_Displacement_BC").Nodes:
            node.SetSolutionStepValue(DISPLACEMENT, 0, zero_vect)
            node.Fix(DISPLACEMENT_X)
            node.Fix(DISPLACEMENT_Y)
            node.Fix(DISPLACEMENT_Z)

        # Set initial point load value
        for node in self.structure_main_model_part.GetSubModelPart("PointLoad2D_Point_load").Nodes:
            node.SetSolutionStepValue(KratosStructural.POINT_LOAD_X, 0, self.initial_point_load)

        # Set the structure interface
        for node in self.structure_main_model_part.GetSubModelPart("StructureInterface2D_Solid_interface").Nodes:
            node.Set(INTERFACE)

        # Set structure Neumann condition (create the point load condition in the structure interface submodelpart)
        structure_computational_submodelpart = self.structure_solver.GetComputingModelPart()

        aux_count = 0
        for cond in self.structure_solver.main_model_part.Conditions:
            if(cond.Id > aux_count):
                aux_count = cond.Id

        for node in self.structure_main_model_part.GetSubModelPart("StructureInterface2D_Solid_interface").Nodes:
            aux_count+=1
            structure_computational_submodelpart.CreateNewCondition("PointLoadCondition2D1N",
                                                                    aux_count,[node.Id],
                                                                    self.structure_solver.main_model_part.Properties[0])

    def PointLoadUpdate(self):
        for node in self.structure_main_model_part.GetSubModelPart("PointLoad2D_Point_load").Nodes:
            point_load = node.GetSolutionStepValue(KratosStructural.POINT_LOAD_X)
            node.SetSolutionStepValue(KratosStructural.POINT_LOAD_X, 0, self.point_load_updater*point_load)

    def GetInterfaceProblemSize(self):
        return len(self.structure_solver.main_model_part.GetSubModelPart("StructureInterface2D_Solid_interface").Nodes)

    def ComputeDirichletNeumannResidual(self):

        interface_submodelpart = self.structure_solver.main_model_part.GetSubModelPart("StructureInterface2D_Solid_interface")

        K = 1000.0 # Spring stiffness

        # Impose the spring reactions that emulate the fluid load over the structure interface
        i = 0
        for node in interface_submodelpart.Nodes:
            point_load = Vector(3)
            point_load[0] = - K*self.iteration_value[i]
            point_load[1] = - K*self.iteration_value[i+1]
            point_load[2] = 0.0

            node.SetSolutionStepValue(KratosStructural.POINT_LOAD, 0, point_load)

            i += 2

        # Solve structure problem
        self.structure_solver.SolveSolutionStep()

        # Compute the displacement residual
        disp_residual = Vector(self.GetInterfaceProblemSize()*2)

        i = 0
        for node in interface_submodelpart.Nodes:
            vector_projected = node.GetSolutionStepValue(DISPLACEMENT,0)

            disp_residual[i] = vector_projected[0] - self.iteration_value[i]
            disp_residual[i+1] = vector_projected[1] - self.iteration_value[i+1]
            i+=2

        return disp_residual

    def __ComputeInitialResidual(self):
        # Solve the fluid emulator problem with the initial displacement guess
        self.__SolveFluidEmulator()

        # Transfer fluid load
        for i in range(len(self.corrected_iteration_value_f)):
            self.corrected_iteration_value_f[i] = self.iteration_value_f[i]
        self.__TransferFluidEmulatorLoad()

        # Solve structure problem
        self.structure_solver.SolveSolutionStep()

        # Compute the displacement residual
        disp_residual = self.__ComputeStructureResidual()

        return disp_residual

    def __SolveFluidEmulator(self):
        # Calculate the spring reactions that emulate the fluid load over the structure interface
        for i in range(self.GetInterfaceProblemSize()):
            self.iteration_value_f[2*i] = self.fluid_emulator_stiffness * self.corrected_iteration_value_u[2*i]
            self.iteration_value_f[2*i+1] = self.fluid_emulator_stiffness * self.corrected_iteration_value_u[2*i+1]

    def __TransferFluidEmulatorLoad(self):
        interface_submodelpart = self.structure_solver.main_model_part.GetSubModelPart("StructureInterface2D_Solid_interface")

        i = 0
        for node in interface_submodelpart.Nodes:
            point_load = Vector(3)
            point_load[0] = - self.corrected_iteration_value_f[i]
            point_load[1] = - self.corrected_iteration_value_f[i+1]
            point_load[2] = 0.0
            node.SetSolutionStepValue(KratosStructural.POINT_LOAD, 0, point_load)
            i += 2

    def __ComputeStructureResidual(self):
        interface_submodelpart = self.structure_solver.main_model_part.GetSubModelPart("StructureInterface2D_Solid_interface")

        # Calculate the structure displacement error
        disp_residual = Vector(2 * self.GetInterfaceProblemSize())

        i = 0
        for node in interface_submodelpart.Nodes:
            disp = node.GetSolutionStepValue(DISPLACEMENT,0)
            self.iteration_value_u[i] = disp[0]
            self.iteration_value_u[i+1] = disp[1]
            disp_residual[i] = disp[0] - self.corrected_iteration_value_u[i]
            disp_residual[i+1] = disp[1] - self.corrected_iteration_value_u[i+1]
            i+=2

        return disp_residual

if __name__ == '__main__':
    test = FSIProblemEmulatorTest()
    test.setUp()
    # test.test_FSI_problem_emulator_with_aitken()
    # test.test_FSI_problem_emulator_with_MVQN()
    test.test_FSI_problem_emulator_with_IBQN_MVQN()
    # test.test_FSI_problem_emulator_with_MVQN_recursive()
    test.tearDown()
