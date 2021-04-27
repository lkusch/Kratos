from __future__ import print_function, absolute_import, division

import os
import math

# Importing the Kratos Library
import KratosMultiphysics

import KratosMultiphysics.KratosUnittest as KratosUnittest
import KratosMultiphysics.kratos_utilities as kratos_utils
import KratosMultiphysics.avro_output_process as avro_output

from KratosMultiphysics import process_factory
from KratosMultiphysics.testing.utilities import ReadModelPart

def GetFilePath(fileName):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)

class TestProcesses(KratosUnittest.TestCase):

    def test_point_output_process_node(self):
        current_model = KratosMultiphysics.Model()
        model_part = current_model.CreateModelPart("Main")

        model_part.AddNodalSolutionStepVariable(KratosMultiphysics.PRESSURE)
        model_part.AddNodalSolutionStepVariable(KratosMultiphysics.VISCOSITY)

        model_part.CreateNewNode(1, 0.0, 0.0, 0.0)
        model_part.CreateNewNode(2, 1.0, 0.0, 0.0)
        model_part.CreateNewNode(3, 1.0, 1.0, 0.0)

        for node in model_part.Nodes:
            node.SetSolutionStepValue(KratosMultiphysics.PRESSURE, node.Id)
            node.SetSolutionStepValue(KratosMultiphysics.VISCOSITY, -node.Id)

        settings = KratosMultiphysics.Parameters("""{
            "model_part_name": "Main",
            "output_name": "test_avro_output.avro",
            "postprocess_parameters": {
                "result_file_configuration": {
                    "gidpost_flags": {
                        "GiDPostMode": "GiD_PostBinary",
                        "WriteDeformedMeshFlag": "WriteDeformed",
                        "WriteConditionsFlag": "WriteConditions",
                        "MultiFileFlag": "SingleFile"
                    },
                    "file_label": "time",
                    "output_control_type": "step",
                    "output_frequency": 1.0,
                    "body_output": true,
                    "node_output": false,
                    "skin_output": false,
                    "plane_output": [],
                    "nodal_results": ["PRESSURE","VISCOSITY"],
                    "gauss_point_results": []
                },
                "point_data_configuration": []
            }
        }""")

        output = avro_output.AvroOutputProcess(current_model, settings)

        output.PrintOutput()

        model_part.CloneTimeStep(1.0)

        model_part.ProcessInfo[KratosMultiphysics.STEP] += 1

        for node in model_part.Nodes:
            node.SetSolutionStepValue(KratosMultiphysics.PRESSURE, node.Id * 10)
            node.SetSolutionStepValue(KratosMultiphysics.VISCOSITY, -node.Id * 10)

        output.PrintOutput()
        output.ReadPrint()

if __name__ == '__main__':
    KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING)
    KratosUnittest.main()
