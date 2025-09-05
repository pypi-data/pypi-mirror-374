from rs2.modeler.properties.propertyProxy import PropertyProxy
from rs2._common.Client import Client
from enum import Enum, auto
from typing import List
from rs2.modeler.properties.PropertyEnums import *
class CustomGravity(PropertyProxy):
	def getUnitWt(self) -> float:
		return self._getDoubleProperty("MP_UNIT_WT")
	def setUnitWt(self, value: float):
		return self._setDoubleProperty("MP_UNIT_WT", value)
	def getStressRatIn(self) -> float:
		return self._getDoubleProperty("MP_STRESS_RAT_IN")
	def setStressRatIn(self, value: float):
		return self._setDoubleProperty("MP_STRESS_RAT_IN", value)
	def getStressRatOut(self) -> float:
		return self._getDoubleProperty("MP_STRESS_RAT_OUT")
	def setStressRatOut(self, value: float):
		return self._setDoubleProperty("MP_STRESS_RAT_OUT", value)
	def getHStressRatIn(self) -> float:
		return self._getDoubleProperty("MP_H_STRESS_RAT_IN")
	def setHStressRatIn(self, value: float):
		return self._setDoubleProperty("MP_H_STRESS_RAT_IN", value)
	def getHStressRatOut(self) -> float:
		return self._getDoubleProperty("MP_H_STRESS_RAT_OUT")
	def setHStressRatOut(self, value: float):
		return self._setDoubleProperty("MP_H_STRESS_RAT_OUT", value)
	def getGroundElev(self) -> float:
		return self._getDoubleProperty("MP_GROUND_ELEV")
	def setGroundElev(self, value: float):
		return self._setDoubleProperty("MP_GROUND_ELEV", value)
	def getKInA(self) -> float:
		return self._getDoubleProperty("MP_K_IN_A")
	def setKInA(self, value: float):
		return self._setDoubleProperty("MP_K_IN_A", value)
	def getKInB(self) -> float:
		return self._getDoubleProperty("MP_K_IN_B")
	def setKInB(self, value: float):
		return self._setDoubleProperty("MP_K_IN_B", value)
	def getKInC(self) -> float:
		return self._getDoubleProperty("MP_K_IN_C")
	def setKInC(self, value: float):
		return self._setDoubleProperty("MP_K_IN_C", value)
	def getKOutA(self) -> float:
		return self._getDoubleProperty("MP_K_OUT_A")
	def setKOutA(self, value: float):
		return self._setDoubleProperty("MP_K_OUT_A", value)
	def getKOutB(self) -> float:
		return self._getDoubleProperty("MP_K_OUT_B")
	def setKOutB(self, value: float):
		return self._setDoubleProperty("MP_K_OUT_B", value)
	def getKOutC(self) -> float:
		return self._getDoubleProperty("MP_K_OUT_C")
	def setKOutC(self, value: float):
		return self._setDoubleProperty("MP_K_OUT_C", value)
	def getUseActualGroundSurface(self) -> bool:
		return self._getBoolProperty("MP_USE_ACTUAL_GROUND_SURFACE")
	def setUseActualGroundSurface(self, value: bool):
		return self._setBoolProperty("MP_USE_ACTUAL_GROUND_SURFACE", value)
	def getUseEffectiveStressRatio(self) -> bool:
		return self._getBoolProperty("MP_USE_EFFECTIVE_STRESS_RATIO")
	def setUseEffectiveStressRatio(self, value: bool):
		return self._setBoolProperty("MP_USE_EFFECTIVE_STRESS_RATIO", value)
	def getUseVariableStressRatio(self) -> bool:
		return self._getBoolProperty("MP_USE_VARIABLE_STRESS_RATIO")
	def setUseVariableStressRatio(self, value: bool):
		return self._setBoolProperty("MP_USE_VARIABLE_STRESS_RATIO", value)
	def setProperties(self, UnitWt : float = None, StressRatIn : float = None, StressRatOut : float = None, HStressRatIn : float = None, HStressRatOut : float = None, GroundElev : float = None, KInA : float = None, KInB : float = None, KInC : float = None, KOutA : float = None, KOutB : float = None, KOutC : float = None, UseActualGroundSurface : bool = None, UseEffectiveStressRatio : bool = None, UseVariableStressRatio : bool = None):
		if UnitWt is not None:
			self._setDoubleProperty("MP_UNIT_WT", UnitWt)
		if StressRatIn is not None:
			self._setDoubleProperty("MP_STRESS_RAT_IN", StressRatIn)
		if StressRatOut is not None:
			self._setDoubleProperty("MP_STRESS_RAT_OUT", StressRatOut)
		if HStressRatIn is not None:
			self._setDoubleProperty("MP_H_STRESS_RAT_IN", HStressRatIn)
		if HStressRatOut is not None:
			self._setDoubleProperty("MP_H_STRESS_RAT_OUT", HStressRatOut)
		if GroundElev is not None:
			self._setDoubleProperty("MP_GROUND_ELEV", GroundElev)
		if KInA is not None:
			self._setDoubleProperty("MP_K_IN_A", KInA)
		if KInB is not None:
			self._setDoubleProperty("MP_K_IN_B", KInB)
		if KInC is not None:
			self._setDoubleProperty("MP_K_IN_C", KInC)
		if KOutA is not None:
			self._setDoubleProperty("MP_K_OUT_A", KOutA)
		if KOutB is not None:
			self._setDoubleProperty("MP_K_OUT_B", KOutB)
		if KOutC is not None:
			self._setDoubleProperty("MP_K_OUT_C", KOutC)
		if UseActualGroundSurface is not None:
			self._setBoolProperty("MP_USE_ACTUAL_GROUND_SURFACE", UseActualGroundSurface)
		if UseEffectiveStressRatio is not None:
			self._setBoolProperty("MP_USE_EFFECTIVE_STRESS_RATIO", UseEffectiveStressRatio)
		if UseVariableStressRatio is not None:
			self._setBoolProperty("MP_USE_VARIABLE_STRESS_RATIO", UseVariableStressRatio)
	def getProperties(self):
		return {
		"UnitWt" : self.getUnitWt(), 
		"StressRatIn" : self.getStressRatIn(), 
		"StressRatOut" : self.getStressRatOut(), 
		"HStressRatIn" : self.getHStressRatIn(), 
		"HStressRatOut" : self.getHStressRatOut(), 
		"GroundElev" : self.getGroundElev(), 
		"KInA" : self.getKInA(), 
		"KInB" : self.getKInB(), 
		"KInC" : self.getKInC(), 
		"KOutA" : self.getKOutA(), 
		"KOutB" : self.getKOutB(), 
		"KOutC" : self.getKOutC(), 
		"UseActualGroundSurface" : self.getUseActualGroundSurface(), 
		"UseEffectiveStressRatio" : self.getUseEffectiveStressRatio(), 
		"UseVariableStressRatio" : self.getUseVariableStressRatio(), 
		}
