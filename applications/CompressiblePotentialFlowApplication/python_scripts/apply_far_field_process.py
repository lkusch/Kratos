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
        self.u_inf_table.AddRow(0.0,0.806)
        self.u_inf_table.AddRow(900.0,0.806)
        self.u_inf_table.AddRow(2700.0,1.111)
        self.u_inf_table.AddRow(4500.0,0.694)
        self.u_inf_table.AddRow(6300.0,0.806)
        self.u_inf_table.AddRow(8100.0,0.806)
        self.u_inf_table.AddRow(9900.0,0.611)
        self.u_inf_table.AddRow(11700.0,0.694)
        self.u_inf_table.AddRow(13500.0,0.611)
        self.u_inf_table.AddRow(15300.0,0.806)
        self.u_inf_table.AddRow(17100.0,1.111)
        self.u_inf_table.AddRow(18900.0,1.194)
        self.u_inf_table.AddRow(20700.0,1.111)
        self.u_inf_table.AddRow(22500.0,1.111)
        self.u_inf_table.AddRow(24300.0,0.889)
        self.u_inf_table.AddRow(26100.0,1.889)
        self.u_inf_table.AddRow(27900.0,2.000)
        self.u_inf_table.AddRow(29700.0,2.000)
        self.u_inf_table.AddRow(31500.0,2.806)
        self.u_inf_table.AddRow(33300.0,3.111)
        self.u_inf_table.AddRow(35100.0,3.389)
        self.u_inf_table.AddRow(36900.0,3.306)
        self.u_inf_table.AddRow(38700.0,4.000)
        self.u_inf_table.AddRow(40500.0,4.694)
        self.u_inf_table.AddRow(42300.0,4.500)
        self.u_inf_table.AddRow(44100.0,4.389)
        self.u_inf_table.AddRow(45900.0,5.111)
        self.u_inf_table.AddRow(47700.0,4.806)
        self.u_inf_table.AddRow(49500.0,5.111)
        self.u_inf_table.AddRow(51300.0,5.806)
        self.u_inf_table.AddRow(53100.0,5.389)
        self.u_inf_table.AddRow(54900.0,5.889)
        self.u_inf_table.AddRow(56700.0,5.611)
        self.u_inf_table.AddRow(58500.0,5.389)
        self.u_inf_table.AddRow(60300.0,5.500)
        self.u_inf_table.AddRow(62100.0,4.306)
        self.u_inf_table.AddRow(63900.0,4.111)
        self.u_inf_table.AddRow(65700.0,3.889)
        self.u_inf_table.AddRow(67500.0,3.611)
        self.u_inf_table.AddRow(69300.0,2.611)
        self.u_inf_table.AddRow(71100.0,1.500)
        self.u_inf_table.AddRow(72900.0,0.500)
        self.u_inf_table.AddRow(74700.0,1.194)
        self.u_inf_table.AddRow(76500.0,2.500)
        self.u_inf_table.AddRow(78300.0,3.111)
        self.u_inf_table.AddRow(80100.0,2.806)
        self.u_inf_table.AddRow(81900.0,2.611)
        self.u_inf_table.AddRow(83700.0,3.611)
        self.u_inf_table.AddRow(85500.0,2.889)
        self.u_inf_table.AddRow(87300.0,0.806)
        self.u_inf_table.AddRow(89100.0,1.111)
        self.u_inf_table.AddRow(90900.0,0.694)
        self.u_inf_table.AddRow(92700.0,0.806)
        self.u_inf_table.AddRow(94500.0,0.806)
        self.u_inf_table.AddRow(96300.0,0.611)
        self.u_inf_table.AddRow(98100.0,0.694)
        self.u_inf_table.AddRow(99900.0,0.611)
        self.u_inf_table.AddRow(101700.0,0.806)
        self.u_inf_table.AddRow(103500.0,1.111)
        self.u_inf_table.AddRow(105300.0,1.194)
        self.u_inf_table.AddRow(107100.0,1.111)
        self.u_inf_table.AddRow(108900.0,1.111)
        self.u_inf_table.AddRow(110700.0,0.889)
        self.u_inf_table.AddRow(112500.0,1.889)
        self.u_inf_table.AddRow(114300.0,2.000)
        self.u_inf_table.AddRow(116100.0,2.000)
        self.u_inf_table.AddRow(117900.0,2.806)
        self.u_inf_table.AddRow(119700.0,3.111)
        self.u_inf_table.AddRow(121500.0,3.389)
        self.u_inf_table.AddRow(123300.0,3.306)
        self.u_inf_table.AddRow(125100.0,4.000)
        self.u_inf_table.AddRow(126900.0,4.694)
        self.u_inf_table.AddRow(128700.0,4.500)
        self.u_inf_table.AddRow(130500.0,4.389)
        self.u_inf_table.AddRow(132300.0,5.111)
        self.u_inf_table.AddRow(134100.0,4.806)
        self.u_inf_table.AddRow(135900.0,5.111)
        self.u_inf_table.AddRow(137700.0,5.806)
        self.u_inf_table.AddRow(139500.0,5.389)
        self.u_inf_table.AddRow(141300.0,5.889)
        self.u_inf_table.AddRow(143100.0,5.611)
        self.u_inf_table.AddRow(144900.0,5.389)
        self.u_inf_table.AddRow(146700.0,5.500)
        self.u_inf_table.AddRow(148500.0,4.306)
        self.u_inf_table.AddRow(150300.0,4.111)
        self.u_inf_table.AddRow(152100.0,3.889)
        self.u_inf_table.AddRow(153900.0,3.611)
        self.u_inf_table.AddRow(155700.0,2.611)
        self.u_inf_table.AddRow(157500.0,1.500)
        self.u_inf_table.AddRow(159300.0,0.500)
        self.u_inf_table.AddRow(161100.0,1.194)
        self.u_inf_table.AddRow(162900.0,2.500)
        self.u_inf_table.AddRow(164700.0,3.111)
        self.u_inf_table.AddRow(166500.0,2.806)
        self.u_inf_table.AddRow(168300.0,2.611)
        self.u_inf_table.AddRow(170100.0,3.611)
        self.u_inf_table.AddRow(171900.0,2.889)
        self.u_inf_table.AddRow(173700.0,0.806)
        self.fluid_model_part.AddTable(1, self.u_inf_table)

        self.angle_of_attack_table = KratosMultiphysics.PiecewiseLinearTable()
        self.angle_of_attack_table.AddRow(0.0,2.548)
        self.angle_of_attack_table.AddRow(900.0,2.548)
        self.angle_of_attack_table.AddRow(2700.0,2.478)
        self.angle_of_attack_table.AddRow(4500.0,3.281)
        self.angle_of_attack_table.AddRow(6300.0,3.438)
        self.angle_of_attack_table.AddRow(8100.0,3.316)
        self.angle_of_attack_table.AddRow(9900.0,3.508)
        self.angle_of_attack_table.AddRow(11700.0,2.985)
        self.angle_of_attack_table.AddRow(13500.0,2.635)
        self.angle_of_attack_table.AddRow(15300.0,3.543)
        self.angle_of_attack_table.AddRow(17100.0,3.246)
        self.angle_of_attack_table.AddRow(18900.0,3.107)
        self.angle_of_attack_table.AddRow(20700.0,3.351)
        self.angle_of_attack_table.AddRow(22500.0,3.334)
        self.angle_of_attack_table.AddRow(24300.0,2.129)
        self.angle_of_attack_table.AddRow(26100.0,2.129)
        self.angle_of_attack_table.AddRow(27900.0,2.094)
        self.angle_of_attack_table.AddRow(29700.0,1.222)
        self.angle_of_attack_table.AddRow(31500.0,0.611)
        self.angle_of_attack_table.AddRow(33300.0,0.593)
        self.angle_of_attack_table.AddRow(35100.0,0.628)
        self.angle_of_attack_table.AddRow(36900.0,0.559)
        self.angle_of_attack_table.AddRow(38700.0,0.524)
        self.angle_of_attack_table.AddRow(40500.0,0.489)
        self.angle_of_attack_table.AddRow(42300.0,0.524)
        self.angle_of_attack_table.AddRow(44100.0,0.471)
        self.angle_of_attack_table.AddRow(45900.0,0.436)
        self.angle_of_attack_table.AddRow(47700.0,0.593)
        self.angle_of_attack_table.AddRow(49500.0,0.541)
        self.angle_of_attack_table.AddRow(51300.0,0.401)
        self.angle_of_attack_table.AddRow(53100.0,0.419)
        self.angle_of_attack_table.AddRow(54900.0,0.524)
        self.angle_of_attack_table.AddRow(56700.0,0.541)
        self.angle_of_attack_table.AddRow(58500.0,0.541)
        self.angle_of_attack_table.AddRow(60300.0,0.576)
        self.angle_of_attack_table.AddRow(62100.0,0.436)
        self.angle_of_attack_table.AddRow(63900.0,0.524)
        self.angle_of_attack_table.AddRow(65700.0,0.471)
        self.angle_of_attack_table.AddRow(67500.0,0.401)
        self.angle_of_attack_table.AddRow(69300.0,0.349)
        self.angle_of_attack_table.AddRow(71100.0,0.768)
        self.angle_of_attack_table.AddRow(72900.0,0.663)
        self.angle_of_attack_table.AddRow(74700.0,4.608)
        self.angle_of_attack_table.AddRow(76500.0,3.805)
        self.angle_of_attack_table.AddRow(78300.0,3.718)
        self.angle_of_attack_table.AddRow(80100.0,3.683)
        self.angle_of_attack_table.AddRow(81900.0,3.578)
        self.angle_of_attack_table.AddRow(83700.0,3.281)
        self.angle_of_attack_table.AddRow(85500.0,3.316)
        self.angle_of_attack_table.AddRow(87300.0,2.548)
        self.angle_of_attack_table.AddRow(89100.0,2.478)
        self.angle_of_attack_table.AddRow(90900.0,3.281)
        self.angle_of_attack_table.AddRow(92700.0,3.438)
        self.angle_of_attack_table.AddRow(94500.0,3.316)
        self.angle_of_attack_table.AddRow(96300.0,3.508)
        self.angle_of_attack_table.AddRow(98100.0,2.985)
        self.angle_of_attack_table.AddRow(99900.0,2.635)
        self.angle_of_attack_table.AddRow(101700.0,3.543)
        self.angle_of_attack_table.AddRow(103500.0,3.246)
        self.angle_of_attack_table.AddRow(105300.0,3.107)
        self.angle_of_attack_table.AddRow(107100.0,3.351)
        self.angle_of_attack_table.AddRow(108900.0,3.334)
        self.angle_of_attack_table.AddRow(110700.0,2.129)
        self.angle_of_attack_table.AddRow(112500.0,2.129)
        self.angle_of_attack_table.AddRow(114300.0,2.094)
        self.angle_of_attack_table.AddRow(116100.0,1.222)
        self.angle_of_attack_table.AddRow(117900.0,0.611)
        self.angle_of_attack_table.AddRow(119700.0,0.593)
        self.angle_of_attack_table.AddRow(121500.0,0.628)
        self.angle_of_attack_table.AddRow(123300.0,0.559)
        self.angle_of_attack_table.AddRow(125100.0,0.524)
        self.angle_of_attack_table.AddRow(126900.0,0.489)
        self.angle_of_attack_table.AddRow(128700.0,0.524)
        self.angle_of_attack_table.AddRow(130500.0,0.471)
        self.angle_of_attack_table.AddRow(132300.0,0.436)
        self.angle_of_attack_table.AddRow(134100.0,0.593)
        self.angle_of_attack_table.AddRow(135900.0,0.541)
        self.angle_of_attack_table.AddRow(137700.0,0.401)
        self.angle_of_attack_table.AddRow(139500.0,0.419)
        self.angle_of_attack_table.AddRow(141300.0,0.524)
        self.angle_of_attack_table.AddRow(143100.0,0.541)
        self.angle_of_attack_table.AddRow(144900.0,0.541)
        self.angle_of_attack_table.AddRow(146700.0,0.576)
        self.angle_of_attack_table.AddRow(148500.0,0.436)
        self.angle_of_attack_table.AddRow(150300.0,0.524)
        self.angle_of_attack_table.AddRow(152100.0,0.471)
        self.angle_of_attack_table.AddRow(153900.0,0.401)
        self.angle_of_attack_table.AddRow(155700.0,0.349)
        self.angle_of_attack_table.AddRow(157500.0,0.768)
        self.angle_of_attack_table.AddRow(159300.0,0.663)
        self.angle_of_attack_table.AddRow(161100.0,4.608)
        self.angle_of_attack_table.AddRow(162900.0,3.805)
        self.angle_of_attack_table.AddRow(164700.0,3.718)
        self.angle_of_attack_table.AddRow(166500.0,3.683)
        self.angle_of_attack_table.AddRow(168300.0,3.578)
        self.angle_of_attack_table.AddRow(170100.0,3.281)
        self.angle_of_attack_table.AddRow(171900.0,3.316)
        self.angle_of_attack_table.AddRow(173700.0,2.548)
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


