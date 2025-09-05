from rs2.modeler.properties.propertyProxy import PropertyProxy
from rs2._common.Client import Client
from enum import Enum, auto
from typing import List
from rs2.modeler.properties.PropertyEnums import *
class GeneralizedAnisotropic(PropertyProxy):
	def getInputType(self) -> GaNInputType:
		return GaNInputType(self._getEnumEGAInputTypeProperty("MP_GENERALIZED_ANISOTROPIC_INPUT_TYPE"))
	def setInputType(self, value: GaNInputType):
		return self._setEnumEGAInputTypeProperty("MP_GENERALIZED_ANISOTROPIC_INPUT_TYPE", value)
	def setSelectedGaNAngleRangeFunctionByName(self, name: str):
		return self._callFunction("setSelectedGaNAngleRangeFunctionByName", [name])
	def getSelectedGaNAngleRangeFunctionByName(self) -> str:
		return self._callFunction("getSelectedGaNAngleRangeFunctionByName", [])
	def setSelectedGaN2DFunctionByName(self, name: str):
		return self._callFunction("setSelectedGaN2DFunctionByName", [name])
	def getSelectedGaN2DFunctionByName(self) -> str:
		return self._callFunction("getSelectedGaN2DFunctionByName", [])
	def setSelectedGaN3DFunctionByName(self, name: str):
		return self._callFunction("setSelectedGaN3DFunctionByName", [name])
	def getSelectedGaN3DFunctionByName(self) -> str:
		return self._callFunction("getSelectedGaN3DFunctionByName", [])
	def setProperties(self, InputType : GaNInputType = None):
		if InputType is not None:
			self._setEnumEGAInputTypeProperty("MP_GENERALIZED_ANISOTROPIC_INPUT_TYPE", InputType)
	def getProperties(self):
		return {
		"InputType" : self.getInputType(), 
		}
