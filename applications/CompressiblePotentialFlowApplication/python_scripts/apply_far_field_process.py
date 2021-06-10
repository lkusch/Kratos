import KratosMultiphysics
import KratosMultiphysics.FluidDynamicsApplication as KratosCFD
import KratosMultiphysics.CompressiblePotentialFlowApplication as CPFApp
import math

def DotProduct(A,B):
    result = 0
    for i,j in zip(A,B):
        result += i*j
    return result

def Factory(settings, Model):
    if( not isinstance(settings,KratosMultiphysics.Parameters) ):
        raise Exception("expected input shall be a Parameters object, encapsulating a json string")
    return ApplyFarFieldProcess(Model, settings["Parameters"])

## All the processes python should be derived from "Process"
class ApplyFarFieldProcess(KratosMultiphysics.Process):
    def __init__(self, Model, settings ):
        KratosMultiphysics.Process.__init__(self)

        default_parameters = KratosMultiphysics.Parameters( """
            {
                "model_part_name":"",
                "angle_of_attack": 0.0,
                "mach_infinity": 0.02941176471,
                "free_stream_density"  : 1.0,
                "speed_of_sound": 340,
                "heat_capacity_ratio": 1.4,
                "inlet_potential": 1.0,
                "mach_number_limit": 0.94,
                "mach_number_squared_limit": 3.0,
                "critical_mach": 0.99,
                "upwind_factor_constant": 1.0,
                "initialize_flow_field": true,
                "perturbation_field": false
            }  """ )
        settings.ValidateAndAssignDefaults(default_parameters)


        self.far_field_model_part = Model[settings["model_part_name"].GetString()]
        self.fluid_model_part = self.far_field_model_part.GetRootModelPart()

        self.angle_of_attack = settings["angle_of_attack"].GetDouble()
        self.free_stream_mach = settings["mach_infinity"].GetDouble()
        self.density_inf = settings["free_stream_density"].GetDouble()
        self.free_stream_speed_of_sound = settings["speed_of_sound"].GetDouble()
        self.heat_capacity_ratio = settings["heat_capacity_ratio"].GetDouble()
        self.inlet_potential_0 = settings["inlet_potential"].GetDouble()
        self.mach_number_limit = settings["mach_number_limit"].GetDouble()
        self.mach_number_squared_limit = settings["mach_number_squared_limit"].GetDouble()
        self.critical_mach = settings["critical_mach"].GetDouble()
        self.upwind_factor_constant = settings["upwind_factor_constant"].GetDouble()
        self.initialize_flow_field = settings["initialize_flow_field"].GetBool()
        self.perturbation_field = settings["perturbation_field"].GetBool()
        if(self.perturbation_field):
            self.initialize_flow_field = False

        # TODO: create tables
        self.u_inf_table = KratosMultiphysics.PiecewiseLinearTable()
        self.u_inf_table.AddRow(0.0000,0.9583)
        self.u_inf_table.AddRow(1800.0000,0.9583)
        self.u_inf_table.AddRow(5400.0000,0.7500)
        self.u_inf_table.AddRow(9000.0000,0.7083)
        self.u_inf_table.AddRow(12600.0000,0.6528)
        self.u_inf_table.AddRow(16200.0000,0.9583)
        self.u_inf_table.AddRow(19800.0000,1.1528)
        self.u_inf_table.AddRow(23400.0000,1.0000)
        self.u_inf_table.AddRow(27000.0000,1.9444)
        self.u_inf_table.AddRow(30600.0000,2.4028)
        self.u_inf_table.AddRow(34200.0000,3.2500)
        self.u_inf_table.AddRow(37800.0000,3.6528)
        self.u_inf_table.AddRow(41400.0000,4.5972)
        self.u_inf_table.AddRow(45000.0000,4.7500)
        self.u_inf_table.AddRow(48600.0000,4.9583)
        self.u_inf_table.AddRow(52200.0000,5.5972)
        self.u_inf_table.AddRow(55800.0000,5.7500)
        self.u_inf_table.AddRow(59400.0000,5.4444)
        self.u_inf_table.AddRow(63000.0000,4.2083)
        self.u_inf_table.AddRow(66600.0000,3.7500)
        self.u_inf_table.AddRow(70200.0000,2.0556)
        self.u_inf_table.AddRow(73800.0000,0.8472)
        self.u_inf_table.AddRow(77400.0000,2.8056)
        self.u_inf_table.AddRow(81000.0000,2.7083)
        self.u_inf_table.AddRow(84600.0000,3.2500)
        self.u_inf_table.AddRow(86400.0000,3.2500)
        self.fluid_model_part.AddTable(1, self.u_inf_table)

        self.angle_of_attack_table = KratosMultiphysics.PiecewiseLinearTable()
        self.angle_of_attack_table.AddRow(0.0000,2.5133)
        self.angle_of_attack_table.AddRow(1800.0000,2.5133)
        self.angle_of_attack_table.AddRow(5400.0000,3.3598)
        self.angle_of_attack_table.AddRow(9000.0000,3.4121)
        self.angle_of_attack_table.AddRow(12600.0000,2.8100)
        self.angle_of_attack_table.AddRow(16200.0000,3.3947)
        self.angle_of_attack_table.AddRow(19800.0000,3.2289)
        self.angle_of_attack_table.AddRow(23400.0000,2.7314)
        self.angle_of_attack_table.AddRow(27000.0000,2.1118)
        self.angle_of_attack_table.AddRow(30600.0000,0.9163)
        self.angle_of_attack_table.AddRow(34200.0000,0.6109)
        self.angle_of_attack_table.AddRow(37800.0000,0.5411)
        self.angle_of_attack_table.AddRow(41400.0000,0.5061)
        self.angle_of_attack_table.AddRow(45000.0000,0.4538)
        self.angle_of_attack_table.AddRow(48600.0000,0.5672)
        self.angle_of_attack_table.AddRow(52200.0000,0.4102)
        self.angle_of_attack_table.AddRow(55800.0000,0.5323)
        self.angle_of_attack_table.AddRow(59400.0000,0.5585)
        self.angle_of_attack_table.AddRow(63000.0000,0.4800)
        self.angle_of_attack_table.AddRow(66600.0000,0.4363)
        self.angle_of_attack_table.AddRow(70200.0000,0.5585)
        self.angle_of_attack_table.AddRow(73800.0000,2.6354)
        self.angle_of_attack_table.AddRow(77400.0000,3.7612)
        self.angle_of_attack_table.AddRow(81000.0000,3.6303)
        self.angle_of_attack_table.AddRow(84600.0000,3.2987)
        self.angle_of_attack_table.AddRow(86400.0000,3.2987)
        self.fluid_model_part.AddTable(2, self.angle_of_attack_table)

        # Computing free stream velocity
        self.u_inf = self.free_stream_mach * self.free_stream_speed_of_sound
        self.free_stream_velocity = KratosMultiphysics.Vector(3)
        self.free_stream_velocity[0] = round(self.u_inf*math.cos(self.angle_of_attack),8)
        self.free_stream_velocity[1] = round(self.u_inf*math.sin(self.angle_of_attack),8)
        self.free_stream_velocity[2] = 0.0

        self.fluid_model_part.ProcessInfo.SetValue(CPFApp.FREE_STREAM_MACH,self.free_stream_mach)
        self.fluid_model_part.ProcessInfo.SetValue(CPFApp.FREE_STREAM_VELOCITY,self.free_stream_velocity)
        self.fluid_model_part.ProcessInfo.SetValue(CPFApp.FREE_STREAM_DENSITY,self.density_inf)
        self.fluid_model_part.ProcessInfo.SetValue(KratosMultiphysics.SOUND_VELOCITY,self.free_stream_speed_of_sound)
        self.fluid_model_part.ProcessInfo.SetValue(KratosCFD.HEAT_CAPACITY_RATIO,self.heat_capacity_ratio)
        self.fluid_model_part.ProcessInfo.SetValue(CPFApp.MACH_LIMIT,self.mach_number_limit)
        self.fluid_model_part.ProcessInfo.SetValue(CPFApp.MACH_SQUARED_LIMIT,self.mach_number_squared_limit)
        self.fluid_model_part.ProcessInfo.SetValue(CPFApp.CRITICAL_MACH,self.critical_mach)
        self.fluid_model_part.ProcessInfo.SetValue(CPFApp.UPWIND_FACTOR_CONSTANT,self.upwind_factor_constant)

    def ExecuteInitializeSolutionStep(self):
        # TODO: read angle_of_attack and free_stream_mach from a table
        step = self.fluid_model_part.ProcessInfo[KratosMultiphysics.STEP]
        if step%250 == 1:
            time = self.fluid_model_part.ProcessInfo[KratosMultiphysics.TIME]
            self.u_inf = self.u_inf_table.GetValue(time)
            self.angle_of_attack = self.angle_of_attack_table.GetValue(time)
            # self.u_inf = self.u_inf * 1.0e-3

            self.free_stream_velocity = KratosMultiphysics.Vector(3)
            self.free_stream_velocity[0] = round(self.u_inf*math.cos(self.angle_of_attack),8)
            self.free_stream_velocity[1] = round(self.u_inf*math.sin(self.angle_of_attack),8)
            self.free_stream_velocity[2] = 0.0
            self.fluid_model_part.ProcessInfo.SetValue(CPFApp.FREE_STREAM_VELOCITY,self.free_stream_velocity)

            far_field_process=CPFApp.ApplyFarFieldProcess(self.far_field_model_part, self.inlet_potential_0, self.initialize_flow_field, self.perturbation_field)
            far_field_process.Execute()

        # self.Execute()

    def Execute(self):
        reference_inlet_node = self._FindFarthestUpstreamBoundaryNode()
        self._AssignFarFieldBoundaryConditions(reference_inlet_node)

        if(self.initialize_flow_field):
            for node in self.fluid_model_part.Nodes:
                initial_potential = DotProduct( node - reference_inlet_node, self.free_stream_velocity)
                node.SetSolutionStepValue(CPFApp.VELOCITY_POTENTIAL,0,initial_potential + self.inlet_potential_0)
                node.SetSolutionStepValue(CPFApp.AUXILIARY_VELOCITY_POTENTIAL,0,initial_potential + self.inlet_potential_0)

    def _FindFarthestUpstreamBoundaryNode(self):
        # The farthest upstream boundary node is the node with smallest
        # projection of its position vector onto the free stream velocity.

        # Find the farthest upstream boundary node
        temporal_smallest_projection = 1e30
        for node in self.far_field_model_part.Nodes:
            # Projecting the node position vector onto the free stream velocity
            distance_projection = DotProduct(node, self.free_stream_velocity)

            if(distance_projection < temporal_smallest_projection):
                temporal_smallest_projection = distance_projection
                reference_inlet_node = node

        return reference_inlet_node

    def _AssignFarFieldBoundaryConditions(self, reference_inlet_node):
        # A Dirichlet condition is applied at the inlet nodes and
        # a Neumann condition is applied at the outlet nodes
        for cond in self.far_field_model_part.Conditions:
            normal = cond.GetGeometry().Normal()

            # Computing the projection of the free stream velocity onto the normal
            velocity_projection = DotProduct(normal, self.free_stream_velocity)

            if( velocity_projection < 0):
                # A negative projection means inflow (i.e. inlet condition)
                self._AssignDirichletFarFieldBoundaryCondition(reference_inlet_node, cond)
            else:
                # A positive projection means outlow (i.e. outlet condition)
                self._AssignNeumannFarFieldBoundaryCondition(cond)

    def _AssignDirichletFarFieldBoundaryCondition(self, reference_inlet_node, cond):
        for node in cond.GetNodes():
            # Computing the value of the potential at the inlet
            if(self.perturbation_field):
                inlet_potential = 0.0
            else:
                inlet_potential = DotProduct( node - reference_inlet_node, self.free_stream_velocity)

            # Fixing the potential at the inlet nodes
            node.Fix(CPFApp.VELOCITY_POTENTIAL)
            node.SetSolutionStepValue(CPFApp.VELOCITY_POTENTIAL,0,inlet_potential + self.inlet_potential_0)

            # Applying Dirichlet condition in the adjoint problem
            if self.far_field_model_part.HasNodalSolutionStepVariable(CPFApp.ADJOINT_VELOCITY_POTENTIAL):
                node.Fix(CPFApp.ADJOINT_VELOCITY_POTENTIAL)
                node.SetSolutionStepValue(CPFApp.ADJOINT_VELOCITY_POTENTIAL,0,inlet_potential)

    def _AssignNeumannFarFieldBoundaryCondition(self, cond):
        cond.SetValue(CPFApp.FREE_STREAM_VELOCITY, self.free_stream_velocity)


