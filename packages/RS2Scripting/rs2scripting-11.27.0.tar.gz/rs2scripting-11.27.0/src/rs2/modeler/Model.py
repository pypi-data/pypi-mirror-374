from rs2.modeler.properties.bolt.Bolt import BoltProperty
from rs2.modeler.properties.liner.Liner import LinerProperty
from rs2.modeler.properties.joint.Joint import JointProperty
from rs2.modeler.properties.field_stress.FieldStress import FieldStress
from rs2.modeler.properties.material.hydraulic.HydroDistribution import HydroDistribution
from rs2.modeler.properties.pile.Pile import PileProperty
from rs2.modeler.properties.StructuralInterface import StructuralInterfaceProperty
from rs2.modeler.properties.CompositeProperty import CompositeProperty

from rs2.modeler.properties.material.MaterialProperty import MaterialProperty
from rs2.modeler.properties.ShearNormalFunction import ShearNormalFunction
from rs2.modeler.properties.UserDefinedWaterMode import UserDefinedWaterMode
from rs2.modeler.properties.DiscreteFunction import DiscreteFunction
from rs2.modeler.properties.HydroDistributionFunction import HydroDistributionFunction
from rs2.modeler.properties.PropertyEnums import HydraulicVariableTypes, HydraulicDistributionTypes
from rs2.modeler.managed_properties.GanFunctions import Gan3DFunction, Gan2DFunction, GanAngleRangeFunction


from rs2.modeler import properties

from rs2.BaseModel import BaseModel

class Model(BaseModel):
	"""
	:ref:`Model Example`
	"""
	def getBoltPropertyByName(self, boltName : str) -> BoltProperty:
		'''
		|  Returns a Bolt Property object based on its name.
		'''

		boltObjectID = self._callFunction('getBoltPropertyByName', [boltName], keepReturnValueReference=True)
		return BoltProperty(self._client, boltObjectID, self._documentProxy._ID)
    
	def getLinerPropertyByName(self, linerName : str) -> LinerProperty:
		'''
		|  Returns a Liner Property object based on its name.
		'''
		linerObjectID = self._callFunction('getLinerPropertyByName', [linerName], keepReturnValueReference=True)
		return LinerProperty(self._client, linerObjectID, self._documentProxy._ID)
	
	def getJointPropertyByName(self, jointName : str) -> JointProperty:
		'''
		|  Returns a Joint Property object based on its name.
		'''
		jointObjectID = self._callFunction('getJointPropertyByName', [jointName], keepReturnValueReference=True)
		return JointProperty(self._client, jointObjectID, self._documentProxy._ID)
	
	def getPilePropertyByName(self, pileName : str) -> PileProperty:
		'''
		|  Returns a Pile Property object based on its name.
		'''
		pileObjectID = self._callFunction('getPilePropertyByName', [pileName], keepReturnValueReference=True)
		return PileProperty(self._client, pileObjectID, self._documentProxy._ID)

	def getStructuralInterfacePropertyByName(self, structuralName : str) -> StructuralInterfaceProperty:
		'''
		|  Returns a Structural Interface Property object based on its name.
		'''
		structuralInterfaceObjectID = self._callFunction('getStructuralPropertyByName', [structuralName], keepReturnValueReference=True)
		return StructuralInterfaceProperty(self._client, structuralInterfaceObjectID, self._documentProxy._ID)
	
	def getCompositeLinerPropertyByName(self, compositeName : str) -> CompositeProperty:
		'''
		|  Returns a Composite Liner Property object based on its name.
		'''
		compositeLinerObjectID = self._callFunction('getCompositePropertyByName', [compositeName], keepReturnValueReference=True)
		return CompositeProperty(self._client, compositeLinerObjectID, self._documentProxy._ID)

	def getMaterialPropertyByName(self, materialName : str) -> MaterialProperty:
		'''
		|  Returns a Material Property object based on its name.
		'''
		materialObjectID = self._callFunction('getMaterialPropertyByName', [materialName], keepReturnValueReference=True)
		return MaterialProperty(self._client, materialObjectID, self._documentProxy._ID)
	
	def getFieldStressProperty(self) -> FieldStress:
		'''
		   Returns a Field Stress Property object
		'''
		fieldStressObjectID = self._callFunction('getFieldStressProperty', [], keepReturnValueReference=True)
		return FieldStress(self._client, fieldStressObjectID, self._documentProxy._ID)

	def getAllBoltProperties(self) -> list[BoltProperty]:

		'''
		|  Returns a list of all Bolt Property objects
		'''
		activeBoltProperties = []
		boltObjectIDList = self._callFunction('getAllBoltProperties', [], keepReturnValueReference=True)
		for boltObjectID in boltObjectIDList:
			activeBoltProperties.append(BoltProperty(self._client, boltObjectID, self._documentProxy._ID))
		return activeBoltProperties

	def getAllLinerProperties(self) -> list[LinerProperty]:
		'''
		|  Returns a list of all Liner Property objects
		'''
		activeLinerProperties = []
		linerObjectIDList = self._callFunction('getAllLinerProperties', [], keepReturnValueReference=True)
		for linerObjectID in linerObjectIDList:
			activeLinerProperties.append(LinerProperty(self._client, linerObjectID, self._documentProxy._ID))
		return activeLinerProperties
	
	def getAllJointProperties(self) -> list[JointProperty]:
		'''
		|  Returns a list of all Joint Property objects
		'''
		activeJointProperties = []
		jointObjectIDList = self._callFunction('getAllJointProperties', [], keepReturnValueReference=True)
		for jointObjectID in jointObjectIDList:
			activeJointProperties.append(JointProperty(self._client, jointObjectID, self._documentProxy._ID))
		return activeJointProperties
	
	def getAllPileProperties(self) -> list[PileProperty]:
		'''
		|  Returns a list of all Pile Property objects
		'''
		activePileProperties = []
		pileObjectIDList = self._callFunction('getAllPileProperties', [], keepReturnValueReference=True)
		for pileObjectID in pileObjectIDList:
			activePileProperties.append(PileProperty(self._client, pileObjectID, self._documentProxy._ID))
		return activePileProperties
	
	def getAllStructuralInterfaceProperties(self) -> list[StructuralInterfaceProperty]:
		'''
		|  Returns a list of all Structural Interface Property objects
		'''
		activeStructuralProperties = []
		structuralObjectIDList = self._callFunction('getAllStructuralProperties', [], keepReturnValueReference=True)
		for structuralObjectID in structuralObjectIDList:
			activeStructuralProperties.append(StructuralInterfaceProperty(self._client, structuralObjectID, self._documentProxy._ID))
		return activeStructuralProperties
	
	def getAllCompositeLinerProperties(self) -> list[CompositeProperty]:
		'''
		|  Returns a list of all Composite Liner Property objects
		'''
		activeCompositeProperties = []
		compositeObjectIDList = self._callFunction('getAllCompositeProperties', [], keepReturnValueReference=True)
		for compositeObjectID in compositeObjectIDList:
			activeCompositeProperties.append(CompositeProperty(self._client, compositeObjectID, self._documentProxy._ID))
		return activeCompositeProperties
	
	def getAllMaterialProperties(self) -> list[MaterialProperty]:
		'''
		|  Returns a list of all Material Property objects
		'''
		activeMaterialProperties = []
		materialObjectIDList = self._callFunction('getAllMaterialProperties', [], keepReturnValueReference=True)
		for materialObjectID in materialObjectIDList:
			activeMaterialProperties.append(MaterialProperty(self._client, materialObjectID, self._documentProxy._ID))
		return activeMaterialProperties
	
	def getShearNormalFunctions(self) -> list[ShearNormalFunction]:
		'''
		|  Returns a list of all shear normal functions
		'''
		activeShearNormalFunctionProperties = []
		shearNormalFunctionIDList = self._callFunction('getShearNormalFunctions', [], keepReturnValueReference=True)
		for shearNormalFunctionObjectID in shearNormalFunctionIDList:
			activeShearNormalFunctionProperties.append(ShearNormalFunction(self._client, shearNormalFunctionObjectID))
		return activeShearNormalFunctionProperties
	
	def getShearNormalFunctionByName(self, shearNormalFunctionName : str) -> ShearNormalFunction:
		'''
		|  Returns a shear normal function object based on its name.
		'''
		shearNormalFunctionObjectID = self._callFunction('getShearNormalFunctionByName', [shearNormalFunctionName], keepReturnValueReference=True)
		return ShearNormalFunction(self._client, shearNormalFunctionObjectID)
	
	def createNewShearNormalFunction(self, functionName):
		'''
		|  Creates a new shear normal function with the given name
		'''
		return self._callFunction('createNewShearNormalFunction', [functionName])
	
	def deleteShearNormalFunction(self, functionName):
		'''
		|  Deletes a shear normal function with the given name
		'''
		return self._callFunction('deleteShearNormalFunction', [functionName])
	
	def renameShearNormalFunction(self, oldName, newName):
		'''
		|  Renames a shear normal function with the given name
		'''
		return self._callFunction('renameShearNormalFunction', [oldName, newName])
	
	def getUserDefinedPermeabilityAndWaterContentMode(self, name : str) -> UserDefinedWaterMode:
		'''
		|  Returns a User Defined Water Mode object based on its name.
		'''
		userDefinedWaterModeObjectID = self._callFunction('getUserDefinedWaterMode', [name], keepReturnValueReference=True)
		return UserDefinedWaterMode(self._client, userDefinedWaterModeObjectID)
	
	def createUserDefinedPermeabilityAndWaterContentMode(self, name : str) -> UserDefinedWaterMode:
		'''
		|  Creates a User Defined Water Mode object with the given name.
		'''
		userDefinedWaterModeObjectID = self._callFunction('createUserDefinedWaterMode', [name], keepReturnValueReference=True)
		return UserDefinedWaterMode(self._client, userDefinedWaterModeObjectID)

	def deleteUserDefinedPermeabilityAndWaterContentMode(self, name : str):
		'''
		|  Deletes a User Defined Water Mode object with the given name.
		'''
		return self._callFunction('deleteUserDefinedWaterMode', [name])
	
	def renameUserDefinedPermeabilityAndWaterContentMode(self, oldName : str, newName : str):
		'''
		|  Renames a User Defined Water Mode object with the given name.
		'''
		return self._callFunction('renameUserDefinedWaterMode', [oldName, newName])
	
	def AddHistoryQueryPoint(self, x: float, y: float, history_query_name: str):
		'''
		:ref:`History Query Example`

		|  Add a new History Query point to your model with the specified coordinates and label name

		'''
		return self._callFunction('AddHistoryQueryPoint', [x, y, history_query_name])

	def RemoveHistoryQueryPoint(self, history_query_name: str):
		'''
		:ref:`History Query Example`

		|  Remove a History Query point from your model by label name.

		'''
		return self._callFunction('RemoveHistoryQueryPoint', [history_query_name])

	def AddTimeQueryLine(self, points: list[list[float]], points_on_line: int) -> str:
		'''
		:ref:`Time Query Example`

		|  Add a new Time Query Line to your model with the specified coordinates
		
		Warning:
			points_on_line must be between 1 and 10 inclusive.

		'''
		return self._callFunction('AddTimeQueryLine', [points, points_on_line])
	
	def RemoveTimeQueryLine(self, IDs_toRemove: list[str]):
		'''
		:ref:`Time Query Example`

		|  Removes Time Query Line(s) from your model using provided list of IDs.

		'''
		return self._callFunction('RemoveTimeQueryLine', [IDs_toRemove])
	
	def AddTimeQueryPoint(self, x: float, y: float) -> str:
		'''
		:ref:`Time Query Example`

		|  Add a new Time Query Point to your model with the specified x and y coordinates

		'''
		return self._callFunction('AddTimeQueryPoint', [x, y])
	
	def RemoveTimeQueryPoint(self, IDs_toRemove: list[str]):
		'''
		:ref:`Time Query Example`
		
		|  Removes Time Query Point(s) from your model using provided list of IDs.

		'''
		return self._callFunction('RemoveTimeQueryPoint', [IDs_toRemove])
	
	def compute(self):
		'''
		|  Saves the file if modified and then runs compute. Replaces any existing results.

		Warning:
			All objects retrieved from the interpreter for this file will be invalidated after this call.
			If you have an interpreter model open, you should close, compute, and then re-open the model.

			.. code-block:: python

				interpreterModel.close()
				model.compute()
				interpreterModel = modeler.openFile('C:/previouslyOpened.fez')
				
		'''
		return self._callFunction('compute', [False])

	def computeGroundWater(self):
		'''
		|  Saves the file if modified and then runs groundwater compute. Replaces any existing results.

		Warning:
			All objects retrieved from the interpreter for this file will be invalidated after this call.
			If you have an interpreter model open, you should close, compute, and then re-open the model.

			.. code-block:: python

				interpreterModel.close()
				model.compute()
				interpreterModel = modeler.openFile('C:/previouslyOpened.fez')
		'''
		return self._callFunction('compute', [True])

	def saveAs(self, fileName : str):
		'''
		|  Saves the model using the given file name.

		Example:

		.. code-block:: python

			model.saveAs('C:/simple_3_stage.fez')
		'''
		formattedFileName = fileName.replace('/', '\\')
		self._enforceFeaFezEnding(formattedFileName)
		return self._callFunction('saveAs', [formattedFileName])

	def getDiscreteFunctions(self) -> list[DiscreteFunction]:
		'''
		|  Returns a list of all discrete functions
		'''
		activeDiscreteFunctionProperties = []
		discreteFunctionIDList = self._callFunction('getDiscreteFunctions', [], keepReturnValueReference=True)
		for discreteFunctionObjectID in discreteFunctionIDList:
			activeDiscreteFunctionProperties.append(DiscreteFunction(self._client, discreteFunctionObjectID))
		return activeDiscreteFunctionProperties
	
	def getDiscreteFunctionByName(self, discreteFunctionName : str) -> DiscreteFunction:
		'''
		|  Returns a discrete function object based on its name.
		'''
		discreteFunctionObjectID = self._callFunction('getDiscreteFunctionByName', [discreteFunctionName], keepReturnValueReference=True)
		return DiscreteFunction(self._client, discreteFunctionObjectID)
	
	def createNewDiscreteFunction(self, functionName):
		'''
		|  Creates a new discrete function with the given name
		'''
		return self._callFunction('createNewDiscreteFunction', [functionName])
	
	def deleteDiscreteFunction(self, functionName):
		'''
		|  Deletes a discrete function with the given name
		'''
		return self._callFunction('deleteDiscreteFunction', [functionName])
	
	def renameDiscreteFunction(self, oldName, newName):
		'''
		|  Renames a discrete function with the given name
		'''
		return self._callFunction('renameDiscreteFunction', [oldName, newName])	

	def getGan3Ds(self) -> list[Gan3DFunction]:
		'''
		|  Returns a list of all Gan3DFunction objects
		'''
		activeGan3DProperties = []
		gan3DIDList = self._callFunction('getGan3Ds', [], keepReturnValueReference=True)
		for gan3DObjectID in gan3DIDList:
			activeGan3DProperties.append(Gan3DFunction(self._client, gan3DObjectID))
		return activeGan3DProperties
	
	def getGan3DFunctions(self, name: str) -> Gan3DFunction:
		'''
		|  Returns a Gan3DFunction object based on its name.
		'''
		objectID = self._callFunction('getGan3DByName', [name], keepReturnValueReference=True)
		return Gan3DFunction(self._client, objectID)
	
	def createGan3DFunction(self, name):
		'''
		|  Creates a new Gan3DFunction with the given name
		'''
		return self._callFunction('createGan3DFunction', [name])

	def deleteGan3DFunction(self, name):
		'''
		|  Deletes a Gan3DFunction with the given name
		'''
		return self._callFunction('deleteGan3DFunction', [name])

	def renameGan3DFunction(self, oldName, newName):
		'''
		|  Renames a Gan3DFunction with the given name
		'''
		return self._callFunction('renameGan3DFunction', [oldName, newName])

	def getGan3DFunctions(self) -> list[Gan3DFunction]:
		'''
		|  Returns a list of all Gan3DFunction Function objects
		'''
		activeProperties = []
		idList = self._callFunction('getGan3DFunctions', [], keepReturnValueReference=True)
		for objectID in idList:
			activeProperties.append(Gan3DFunction(self._client, objectID))
		return activeProperties
	
	def getGan3DFunctionByName(self, name: str) -> Gan3DFunction:
		'''
		|  Returns a Gan3D Function object based on its name.
		'''
		objectID = self._callFunction('getGan3DFunctionByName', [name], keepReturnValueReference=True)
		return Gan3DFunction(self._client, objectID)
	
	def createGan2DFunction(self, name):
		'''
		|  Creates a new Gan2DFunction with the given name
		'''
		return self._callFunction('createGan2DFunction', [name])

	def deleteGan2DFunction(self, name):
		'''
		|  Deletes a Gan2DFunction with the given name
		'''
		return self._callFunction('deleteGan2DFunction', [name])

	def renameGan2DFunction(self, oldName, newName):
		'''
		|  Renames a Gan2DFunction with the given name
		'''
		return self._callFunction('renameGan2DFunction', [oldName, newName])

	def getGan2DFunctions(self) -> list[Gan2DFunction]:
		'''
		|  Returns a list of all Gan2D Function objects
		'''
		activeGanProperties = []
		idList = self._callFunction('getGan2DFunctions', [], keepReturnValueReference=True)
		for objectID in idList:
			activeGanProperties.append(Gan2DFunction(self._client, objectID))
		return activeGanProperties
	
	def getGan2DFunctionByName(self, name: str) -> Gan2DFunction:
		'''
		|  Returns a Gan2D Function object based on its name.
		'''
		objectID = self._callFunction('getGan2DFunctionByName', [name], keepReturnValueReference=True)
		return Gan2DFunction(self._client, objectID)

	def createGanAngleRangeFunction(self, name):
		'''
		|  Creates a new GanAngleRange Function with the given name
		'''
		return self._callFunction('createGanAngleRangeFunction', [name])

	def deleteGanAngleRangeFunction(self, name):
		'''
		|  Deletes a GanAngleRange Function with the given name
		'''
		return self._callFunction('deleteGanAngleRangeFunction', [name])

	def renameGanAngleRangeFunction(self, oldName, newName):
		'''
		|  Renames a GanAngleRange Function with the given name
		'''
		return self._callFunction('renameGanAngleRangeFunction', [oldName, newName])


	def getGanAngleRangeFunctions(self) -> list[GanAngleRangeFunction]:
		'''
		|  Returns a list of all GanAngleRangeFunction objects
		'''
		activeGanProperties = []
		idList = self._callFunction('getGanAngleRangeFunctions', [], keepReturnValueReference=True)
		for objectID in idList:
			activeGanProperties.append(GanAngleRangeFunction(self._client, objectID))
		return activeGanProperties
	
	def getGanAngleRangeFunctionByName(self, name: str) -> GanAngleRangeFunction:
		'''
		|  Returns a GanAngleRange Function object based on its name.
		'''
		objectID = self._callFunction('getGanAngleRangeFunctionByName', [name], keepReturnValueReference=True)
		return GanAngleRangeFunction(self._client, objectID)



	def getHydroDistributionFunctions(self, variable: HydraulicVariableTypes, distribution: HydraulicDistributionTypes) -> list[HydroDistributionFunction]:
		'''
		|  Returns a list of all hydraulic distribution functions
		'''
		activeHydroDistributionFunctionProperties = []
		hydroDistributionFunctionIDList = self._callFunction('getHydroDistributionFunctions', [variable.value, distribution.value], keepReturnValueReference=True)
		for hydroDistributionFunctionObjectID in hydroDistributionFunctionIDList:
			activeHydroDistributionFunctionProperties.append(HydroDistributionFunction(self._client, hydroDistributionFunctionObjectID))
		return activeHydroDistributionFunctionProperties		


	def getHydroDistributionFunctionByName(self, variable: HydraulicVariableTypes, distribution: HydraulicDistributionTypes, HydroDistributionFunctionName : str) -> HydroDistributionFunction:
		'''
		|  Returns a hydraulic distribution function object based on its name.
		'''
		hydroDistributionFunctionObjectID = self._callFunction('getHydroDistributionFunctionByName', [variable.value, distribution.value, HydroDistributionFunctionName], keepReturnValueReference=True)
		return HydroDistributionFunction(self._client, hydroDistributionFunctionObjectID)
	
	def createNewHydroDistributionFunction(self, variable: HydraulicVariableTypes, distribution: HydraulicDistributionTypes, functionName):
		'''
		|  Creates a new hydraulic distribution function with the given name
		'''
		return self._callFunction('createNewHydroDistributionFunction', [variable.value, distribution.value, functionName])
	
	def deleteHydroDistributionFunction(self, variable: HydraulicVariableTypes, distribution: HydraulicDistributionTypes, functionName):
		'''
		|  Deletes a hydraulic discrete function with the given name
		'''
		return self._callFunction('deleteHydroDistributionFunction', [variable.value, distribution.value, functionName])
	
	def renameHydroDistributionFunction(self, variable: HydraulicVariableTypes, distribution: HydraulicDistributionTypes, oldName, newName):
		'''
		|  Renames a hydraulic distribution function with the given name
		'''
		return self._callFunction('renameHydroDistributionFunction', [variable.value, distribution.value, oldName, newName])	
	


	def ResetProperties(self):
		'''
		:ref:`Get Model Units Example`

		|  Reset all properties for your model

		'''
		return self._callFunction('ResetProperties', [])
	
