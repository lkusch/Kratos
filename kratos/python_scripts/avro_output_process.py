import os
import json

try:
    import fastavro
except:
    print("Unable to import AVRO. Please install fastavro drivers for python.")

import KratosMultiphysics
import KratosMultiphysics.kratos_utilities as kratos_utils

from  KratosMultiphysics.deprecation_management import DeprecationManager

def Factory(settings, model):
    if not isinstance(settings, KratosMultiphysics.Parameters):
        raise Exception("expected input shall be a Parameters object, encapsulating a json string")
    return AvroOutputProcess(model, settings["Parameters"])


class AvroOutputProcess(KratosMultiphysics.Process):
    def __init__(self, model, settings):
        KratosMultiphysics.Process.__init__(self)

        model_part_name = settings["model_part_name"].GetString()
        
        self.model_part = model[model_part_name]
        self.schema = None
        self.codec = 'null'
        self.settings = settings

        force_generate_schema = False

        named_schemas = {}
        sub_schemas = {
            "kratos.result.type.scalar":{
                "namespace": "kratos.result.type",
                "type": "record",
                "name": "scalar",
                "fields" : [
                    {"name":"Value", "type":"double"}
                ]
            },
            "kratos.result.type.array":{
                "namespace": "kratos.result.type",
                "type": "record",
                "name": "array",
                "fields" : [
                    {"name":"array", "type": {
                            "type":"array", "items": "double"
                        }
                    }
                ]
            },
            "kratos.result.nodal":{
                "namespace": "kratos.result",
                "type": "record",
                "name": "nodal",
                "fields": [
                    {"name":"variable_name", "type":"string"},
                    {"name":"variable_type", "type":"string"},
                    {"name":"variable_data", "type": {
                            "type": "array", "items" : [ 
                                "double",
                                "kratos.result.type.array"
                            ]
                        }
                    }
                ]
            },
            "kratos.result.elemental":{
                "namespace": "kratos.result",
                "type": "record",
                "name": "elemental",
                "fields": [
                    {"name":"variable_name", "type":"string"},
                    {"name":"variable_type", "type":"string"},
                    {"name":"variable_data", "type":
                        {
                            "type": "array", "items" : [ 
                                "double",
                                "kratos.result.type.array"
                            ]
                        }
                    }
                ]
            }
        }

        results_schema = {
            "namespace": "kratos",
            "type": "record",
            "name": "result",
            "fields": [
                {"name":"time_step", "type":"double"},
                {"name":"mesh", "type":["null", "double"]},
                {"name":"nodal_results", "type":[
                    "null", 
                    {"type": "array", "items": "kratos.result.nodal"},
                    {"type": "array", "items": "kratos.result.elemental"}
                ]}
            ]
        }

        for schema in sub_schemas:
            print("Loading:",schema)
            fastavro.schema.parse_schema(sub_schemas[schema], named_schemas)

        self.schema = fastavro.schema.parse_schema(results_schema, named_schemas)
        
        print(self.schema)

        # Replace deprecations
        self.TranslateLegacyVariablesAccordingToCurrentStandard(settings, {})

        self.folder_name = None
        if "save_output_files_in_folder" in settings and settings["save_output_files_in_folder"].GetBool():
            if self.model_part.GetCommunicator().MyPID() == 0:
                self.folder_name = settings["folder_name"].GetString()
                if not self.model_part.ProcessInfo[KratosMultiphysics.IS_RESTARTED]:
                    kratos_utils.DeleteDirectoryIfExisting(self.folder_name)
                if not os.path.isdir(folder_name):
                    os.mkdir(self.folder_name)
            self.model_part.GetCommunicator().GetDataCommunicator().Barrier()

            # self.output_interval = settings["output_interval"].GetDouble()
            # self.output_control = settings["output_control_type"].GetString()
            # self.next_output = 0.0

            # Charlie: ???
            # self.__ScheduleNextOutput() # required here esp for restart

    def TranslateLegacyVariablesAccordingToCurrentStandard(self, settings, deprecations):
        # Defining a string to help the user understand where the warnings come from (in case any is thrown)
        context_string = type(self).__name__

        for dep in deprecations:
            if DeprecationManager.HasDeprecatedVariable(context_string, settings, dep['old_name'], dep['new_name']):
                DeprecationManager.ReplaceDeprecatedVariableName(settings, dep['old_name'], dep['new_name'])

    def PrintOutput(self):
        output_file = self.settings["output_name"].GetString()
        
        if self.folder_name:
            output_file = os.path.join(self.folder_name, output_file)
        
        with open(output_file, "a+b") as out:
            nodal_results = []
            
            for nodal_solution_step_variable in self.settings['postprocess_parameters']['result_file_configuration']['nodal_results']:
                variable_name = nodal_solution_step_variable.GetString()
                variable_type = KratosMultiphysics.KratosGlobals.GetVariableType(variable_name)

                nodal_results.append({
                    "variable_name": variable_name,
                    "variable_type": variable_type,
                    "variable_data": [node.GetSolutionStepValue(KratosMultiphysics.KratosGlobals.GetVariable(nodal_solution_step_variable.GetString())) for node in self.model_part.Nodes]
                })

            records = [{
                "time_step": float(self.model_part.ProcessInfo[KratosMultiphysics.STEP]),
                "nodal_results": ("kratos.result.nodal",nodal_results)
            }]

            print(records)

            fastavro.writer(out, self.schema, records)
    
    def ReadPrint(self):
        with DataFileReader(open(self.settings["output_name"].GetString(), "rb"), DatumReader()) as reader:
            for result in reader:
                print(result)


    def IsOutputStep(self):
        if self.output_control == "time":
            return self.__GetTime() >= self.next_output
        else:
            return self.model_part.ProcessInfo[KratosMultiphysics.STEP] >= self.next_output

    def __ScheduleNextOutput(self):
        if self.output_interval > 0.0: # Note: if == 0, we'll just always print
            if self.output_control == "time":
                while self.next_output <= self.__GetTime():
                    self.next_output += self.output_interval
            else:
                while self.next_output <= self.model_part.ProcessInfo[KratosMultiphysics.STEP]:
                    self.next_output += self.output_interval

    def __GetTime(self):
        # remove rounding errors that mess with the comparison
        # e.g. 1.99999999999999999 => 2.0
        return float("{0:.12g}".format(self.model_part.ProcessInfo[KratosMultiphysics.TIME]))
