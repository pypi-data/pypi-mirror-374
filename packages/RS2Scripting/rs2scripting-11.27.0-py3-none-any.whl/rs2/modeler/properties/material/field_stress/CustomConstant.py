from rs2.modeler.properties.propertyProxy import PropertyProxy
from rs2._common.Client import Client
from enum import Enum, auto
from typing import List
from rs2.modeler.properties.PropertyEnums import *
class CustomConstant(PropertyProxy):
	def getSigmaOne(self) -> float:
		return self._getDoubleProperty("MP_SIGMA_ONE")
	def setSigmaOne(self, value: float):
		return self._setDoubleProperty("MP_SIGMA_ONE", value)
	def getSigmaThree(self) -> float:
		return self._getDoubleProperty("MP_SIGMA_THREE")
	def setSigmaThree(self, value: float):
		return self._setDoubleProperty("MP_SIGMA_THREE", value)
	def getSigmaZ(self) -> float:
		return self._getDoubleProperty("MP_SIGMA_Z")
	def setSigmaZ(self, value: float):
		return self._setDoubleProperty("MP_SIGMA_Z", value)
	def getAngle(self) -> float:
		return self._getDoubleProperty("MP_ANGLE")
	def setAngle(self, value: float):
		return self._setDoubleProperty("MP_ANGLE", value)
	def setProperties(self, SigmaOne : float = None, SigmaThree : float = None, SigmaZ : float = None, Angle : float = None):
		if SigmaOne is not None:
			self._setDoubleProperty("MP_SIGMA_ONE", SigmaOne)
		if SigmaThree is not None:
			self._setDoubleProperty("MP_SIGMA_THREE", SigmaThree)
		if SigmaZ is not None:
			self._setDoubleProperty("MP_SIGMA_Z", SigmaZ)
		if Angle is not None:
			self._setDoubleProperty("MP_ANGLE", Angle)
	def getProperties(self):
		return {
		"SigmaOne" : self.getSigmaOne(), 
		"SigmaThree" : self.getSigmaThree(), 
		"SigmaZ" : self.getSigmaZ(), 
		"Angle" : self.getAngle(), 
		}
