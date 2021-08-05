# Making KratosMultiphysics backward compatible with python 2.6 and 2.7
from __future__ import print_function, absolute_import, division

# Import Kratos core and apps
from KratosMultiphysics import *
from KratosMultiphysics.ShapeOptimizationApplication import *

# Additional imports
from interface_su2 import InterfaceSU2
from analyzer_base import AnalyzerBaseClass

import os, sys, shutil, copy, string
import optimizer_factory

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

        if communicator.isRequestingValueOf("drag") or communicator.isRequestingValueOf("lift"):
            update_mesh = True
            [drag,lift] = interface_su2.ComputeValues(["DRAG","LIFT"], update_mesh, optimization_iteration)

            if communicator.isRequestingValueOf("drag"):
                communicator.reportValue("drag", drag)

            if communicator.isRequestingValueOf("lift"):
                communicator.reportValue("lift", lift)

        if communicator.isRequestingGradientOf("drag"):
            update_mesh = False
            [drag_gradient] = interface_su2.ComputeGradient(["DRAG"], update_mesh, optimization_iteration)
            communicator.reportGradient("drag", drag_gradient)

        if communicator.isRequestingGradientOf("lift"):
            update_mesh = False
            [lift_gradient] = interface_su2.ComputeGradient(["LIFT"], update_mesh, optimization_iteration)
            communicator.reportGradient("lift", lift_gradient)


def optimize():
    # =======================================================================================================
    # Perform optimization
    # =======================================================================================================
    model = Model()

    # Create optimizer and perform optimization
    optimizer = optimizer_factory.CreateOptimizer(parameters["optimization_settings"], model, CustomSU2Analyzer())
    optimizer.Optimize()

def calculate_pareto_point(outer, inner, obj):
    #outer defines the current objective function
    #inner defines the current step (0 stands for no additional constraint)

    #define objective and constraints for optimization problem
    parameters["optimization_settings"]["objectives"][0]["identifier"].SetString(moo_parameters["moo_settings"]["objectives"][outer]["identifier"].GetString())
    parameters["optimization_settings"]["objectives"][0]["type"].SetString(moo_parameters["moo_settings"]["objectives"][outer]["type"].GetString())
    parameters["optimization_settings"]["objectives"][0]["use_kratos"].SetBool(moo_parameters["moo_settings"]["objectives"][outer]["use_kratos"].GetBool())
    parameters["optimization_settings"]["objectives"][0]["project_gradient_on_surface_normals"].SetBool(moo_parameters["moo_settings"]["objectives"][outer]["project_gradient_on_surface_normals"].GetBool())

    #if (inner!=0):
    if (0==0):
        countNum=0
        for ihelp in range(0,numObj):
            if (ihelp != outer):
                print(countNum)
                print(ihelp)
                print(str(parameters["optimization_settings"]["constraints"][countNum]["identifier"].GetString()))
                parameters["optimization_settings"]["constraints"][countNum]["identifier"].SetString(moo_parameters["moo_settings"]["objectives"][ihelp]["identifier"].GetString())
                parameters["optimization_settings"]["constraints"][countNum]["reference_value"].SetDouble(obj[ihelp])
                parameters["optimization_settings"]["constraints"][countNum]["use_kratos"].SetBool(moo_parameters["moo_settings"]["objectives"][ihelp]["use_kratos"].GetBool())
                parameters["optimization_settings"]["constraints"][countNum]["project_gradient_on_surface_normals"].SetBool(moo_parameters["moo_settings"]["objectives"][ihelp]["project_gradient_on_surface_normals"].GetBool())
                #different treatment for maximization/minimization
                if (moo_parameters["moo_settings"]["objectives"][ihelp]["type"]=="minimization"):
                    parameters["optimization_settings"]["constraints"][countNum]["type"].SetString("<")
                    if(inner==0):
                        parameters["optimization_settings"]["constraints"][countNum]["reference_value"].SetDouble(9999.0)
                else:
                    parameters["optimization_settings"]["constraints"][countNum]["type"].SetString(">")
                    if(inner==0):
                        parameters["optimization_settings"]["constraints"][countNum]["reference_value"].SetDouble(-9999.0)
                countNum=countNum+1
        
    #run optimization problem
    optimize()

    counterLog=0
    totalcons=[]
    storeoptimum=1
    if(parameters["optimization_settings"]["objectives"][0]["type"].GetString()=="minimization"):
        optimum=999999
    else:
        optimum=-999999
    with open("Optimization_Results/response_log.csv","r") as optlog:
        for line in optlog:
            cons=[]
            if(counterLog>=1):
                values=string.split(line,",")
                objVal=string.atof(values[1])
                for iCons in range(0,parameters["optimization_settings"]["constraints"].size()):
                    cons.append(string.atof(values[4+2*iCons]))
                totalcons.append(cons)           
                betterResult = 0
                #check for better objective function
                if(parameters["optimization_settings"]["objectives"][0]["type"].GetString()=="minimization"):
                    betterResult = (objVal<optimum)
                else:
                    betterResult = (objVal>optimum)
                #check for constraint (objective functions)
                for iCons in range(0,parameters["optimization_settings"]["constraints"].size()):
                    if(parameters["optimization_settings"]["constraints"][iCons]["type"].GetString()=="<"):
                        betterResult=betterResult*(cons[iCons]<parameters["optimization_settings"]["constraints"][iCons]["reference_value"].GetDouble()) 
                    else: 
                        betterResult=betterResult*(cons[iCons]>parameters["optimization_settings"]["constraints"][iCons]["reference_value"].GetDouble()) 
                #store result    
                if(betterResult == 1):
                    optimum = objVal
                    storeoptimum = counterLog-1
            counterLog=counterLog+1
    print("Best solution is design number: ",storeoptimum+1, ", Value: ",optimum)

    objective=[]
    counterLog=0
    for ihelp in range(0,numObj):
        if(ihelp==outer):
            objective.append(optimum)
        else:
            print(counterLog)
            print(totalcons)
            objective.append(totalcons[storeoptimum][counterLog])
            counterLog=counterLog+1
            
    print("Pareto point: ", objective+[outer,inner])

    if(os.path.exists('Pareto'+str(outer)+'_'+str(inner))==0):
        os.system("mkdir Pareto"+str(outer)+"_"+str(inner))
#    os.system("cp DESIGNS/ Pareto"+str(outer)+"_"+str(inner)+" -rf")
    if(os.path.exists('history_project.dat')):
        os.system("cp history_project.dat Pareto"+str(outer)+"_"+str(inner)+" -rf")
    if(os.path.exists('history_project.csv')):
        os.system("cp history_project.csv Pareto"+str(outer)+"_"+str(inner)+" -rf")
    os.system("cp Optimization_Results/ Pareto"+str(outer)+"_"+str(inner)+" -rf")
# use if only optimum design shall be stored
    if (storeoptimum+1<10):
        os.system("mkdir Pareto"+str(outer)+"_"+str(inner)+"/DESIGN_00"+str(storeoptimum+1))
        os.system("cp DESIGNS/DSN_00"+str(storeoptimum+1)+" Pareto"+str(outer)+"_"+str(inner)+"/DESIGN_00"+str(storeoptimum+1)+" -rf")
    elif (storeoptimum+1<100):
        os.system("mkdir Pareto"+str(outer)+"_"+str(inner)+"/DESIGN_0"+str(storeoptimum+1))
        os.system("cp DESIGNS/DSN_0"+str(storeoptimum+1)+" Pareto"+str(outer)+"_"+str(inner)+"/DESIGN_0"+str(storeoptimum+1)+" -rf")
    else:
        os.system("mkdir Pareto"+str(outer)+"_"+str(inner)+"/DESIGN_"+str(storeoptimum+1))
        os.system("cp DESIGNS/DSN_"+str(storeoptimum+1)+" Pareto"+str(outer)+"_"+str(inner)+"/DESIGN_"+str(storeoptimum+1)+" -rf")

    return objective
#: calculate_pareto_point()

def loop(s, itbegin, itend, border, obj, deltaObj):
    global firstiteration, itCounter
    #iterate only constraints and skip current objective function (s)
    if(itend-itbegin == numObj-1): 
        if(s==itend): 
	    itend=itend-1
    if(itbegin==s): 
        itbegin=itbegin+1

    #reset border for new loop
    obj[itbegin]=border[s][itbegin] 

    #find constraints for each step
    for k in range(0,stepNumber):
        #recursively find all possible combinations
	if(itbegin!=itend):
            loop(s, itbegin+1, itend, border, obj, deltaObj)
        #solve optimization problem for current combination
	else:
            if(firstiteration):
                #the first combination is already the Pareto point at the border and does not need to be calculated
                firstiteration = 0
            else:
            	store=calculate_pareto_point((s),(itCounter), obj);
		pareto.append(store+[(s),(itCounter)])
                output = ""
                for l in range(0,numObj):
                    output = output+str(store[l])+" "
                paretofile.write(output+"\n")
                itCounter=itCounter+1;
        #update constraint
        obj[itbegin]=obj[itbegin]-deltaObj[itbegin]
    return 0
#: loop()

# =======================================================================================================
# Define external analyzer
# =======================================================================================================

with open("moo_parameters.json",'r') as moo_parameter_file:
    moo_parameters = Parameters(moo_parameter_file.read())

with open("parameters.json",'r') as parameter_file:
    parameters = Parameters(parameter_file.read())

interface_su2 = InterfaceSU2(parameters["su2_interface_settings"])
#interface_su2.WriteSU2MeshAsMDPA()

#additional variables
obj=[] 	#store current objective function values (for constraints)	
deltaObj=[] #store stepsize for scanning
border=[] 	#store borders of Pareto front
pareto=[]   #store all Pareto optimal points 
objec=[]	#store solution of single-objective optimization
calcBorder = 1

#default values multi-objective optimization
default_moo_parameters = Parameters("""
{
    "moo_settings": {
        "objectives" : [{
            "identifier" : "drag", 
            "type"       : "minimization",
            "use_kratos" : false,
            "project_gradient_on_surface_normals" : false,
            "marker" : "airfoil"
        },{
            "identifier" : "lift",
            "type"       : "maximization",
            "use_kratos" : false,
            "project_gradient_on_surface_normals" : false,
            "marker" : "airfoil"
        }],
        "constraints" : [],
        "numsteps" : 5,
        "numobj" : 2 
    }
}""")
moo_parameters.RecursivelyValidateAndAssignDefaults(default_moo_parameters)

numObj=moo_parameters["moo_settings"]["numobj"].GetInt()
stepNumber = moo_parameters["moo_settings"]["numsteps"].GetInt()

for i in range(0,numObj):
    obj.append(0.0)		
    deltaObj.append(0.0)
    
#output
paretofile=open("ParetoPoints",'w')
paretofile.close()
paretofile=open("ParetoPoints",'a')
    
if calcBorder:
    #calculate SOO problems to find border of Pareto front
    for i in range(0,numObj):
        objec=calculate_pareto_point(i,0, obj)
        border.append(objec)

for i in range(0,numObj):
    pareto.append(border[i]+[i,0])
    output = ""
    for j in range(0,numObj):
        output = output+str(border[i][j])+" "
    paretofile.write(output+"\n")

#perform scanning of front
#with open("parameters_with_constraints.json",'r') as parameter_file:
#    parameters = Parameters(parameter_file.read())
global firstiteration, itCounter
for i in range(0,numObj):
    firstiteration=1
    itCounter=1
    for j in range(0,numObj):
	deltaObj[j]=float(border[i][j]-border[j][j])/float(stepNumber)
        obj[j]=border[i][j]
    loop(i,0,(numObj-1), border, obj, deltaObj)

paretofile.close()
