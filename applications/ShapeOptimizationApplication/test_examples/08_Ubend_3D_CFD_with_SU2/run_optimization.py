# Making KratosMultiphysics backward compatible with python 2.6 and 2.7
from __future__ import print_function, absolute_import, division

# Import Kratos core and apps
from KratosMultiphysics import *
from KratosMultiphysics.ShapeOptimizationApplication import *

# Additional imports
from interface_su2 import InterfaceSU2
from analyzer_base import AnalyzerBaseClass

# =======================================================================================================
# Define external analyzer
# =======================================================================================================

with open("parameters.json",'r') as parameter_file:
    parameters = Parameters(parameter_file.read())

interface_su2 = InterfaceSU2(parameters["su2_interface_settings"])
#interface_su2.WriteSU2MeshAsMDPA()

# Definition of external analyzer
class CustomSU2Analyzer(AnalyzerBaseClass):

    # --------------------------------------------------------------------------
    def __init__( self ):
        interface_su2.InitializeNewSU2Project()

    # --------------------------------------------------------------------------------------------------
    def AnalyzeDesignAndReportToCommunicator(self, current_design, optimization_iteration, communicator):

        if optimization_iteration == 1:
            interface_su2.WriteNodesAsSU2MeshMotionFile(current_design.GetNodes())
        else:
            previos_iteration = optimization_iteration-1
            interface_su2.WriteNodesAsSU2MeshMotionFile(current_design.GetNodes(),"DESIGNS/DSN_"+str(previos_iteration).zfill(3))

        if communicator.isRequestingValueOf("pressure_loss"):
            update_mesh = True
            [pressure_loss] = interface_su2.ComputeValues(["SURFACE_TOTAL_PRESSURE"], update_mesh, optimization_iteration)

            if communicator.isRequestingValueOf("pressure_loss"):
                communicator.reportValue("pressure_loss", pressure_loss)

            #if communicator.isRequestingValueOf("lift"):
            #    communicator.reportValue("lift", lift)

        if communicator.isRequestingGradientOf("pressure_loss"):
            update_mesh = False
            [pressure_gradient] = interface_su2.ComputeGradient(["SURFACE_TOTAL_PRESSURE"], update_mesh, optimization_iteration)
            communicator.reportGradient("pressure_loss", pressure_gradient)

#        if communicator.isRequestingGradientOf("lift"):
#            update_mesh = False
#            [lift_gradient] = interface_su2.ComputeGradient(["LIFT"], update_mesh, optimization_iteration)
#            communicator.reportGradient("lift", lift_gradient)

# =======================================================================================================
# Perform optimization
# =======================================================================================================
model = Model()

# Create optimizer and perform optimization
import optimizer_factory
optimizer = optimizer_factory.CreateOptimizer(parameters["optimization_settings"], model, CustomSU2Analyzer())
optimizer.Optimize()
