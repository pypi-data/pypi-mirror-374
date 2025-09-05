from rs2.modeler.properties.propertyProxy import PropertyProxy
from rs2._common.Client import Client
from enum import Enum, auto
from typing import List
from rs2.modeler.properties.PropertyEnums import *
from rs2._common.ProxyObject import ProxyObject
from rs2.modeler.properties.AbsoluteStageFactorGettersInterface import AbsoluteStageFactorGettersInterface
class GeneralizedHoekBrownStageFactorLegacy(ProxyObject):
	def __init__(self, client : Client, ID, propertyID):
		super().__init__(client, ID)
	def getCompressiveStrengthFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_UCS", self.propertyID], proxyArgumentIndices=[1])
class GeneralizedHoekBrownDefinedStageFactorLegacy(GeneralizedHoekBrownStageFactorLegacy):
	def __init__(self, client : Client, ID, propertyID):
		super().__init__(client, ID, propertyID)
	def setCompressiveStrengthFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_UCS", value, self.propertyID], proxyArgumentIndices=[2])
class GeneralizedHoekBrownLegacy(PropertyProxy):
	def __init__(self, client : Client, ID, documentProxyID, stageFactorInterfaceID):
		super().__init__(client, ID, documentProxyID)
	def getCompressiveStrength(self) -> float:
		return self._getDoubleProperty("MP_UCS")
	def setCompressiveStrength(self, value: float):
		return self._setDoubleProperty("MP_UCS", value)
	def getGSIParameter(self) -> float:
		return self._getDoubleProperty("MP_GSI_PARAMETER")
	def setGSIParameter(self, value: float):
		return self._setDoubleProperty("MP_GSI_PARAMETER", value)
	def getMiParameter(self) -> float:
		return self._getDoubleProperty("MP_MI_PARAMETER")
	def setMiParameter(self, value: float):
		return self._setDoubleProperty("MP_MI_PARAMETER", value)
	def getDParameter(self) -> float:
		return self._getDoubleProperty("MP_D_PARAMETER")
	def setDParameter(self, value: float):
		return self._setDoubleProperty("MP_D_PARAMETER", value)
	def getResidualGSIParameter(self) -> float:
		return self._getDoubleProperty("MP_GSI_PARAMETER_RES")
	def setResidualGSIParameter(self, value: float):
		return self._setDoubleProperty("MP_GSI_PARAMETER_RES", value)
	def getResidualMiParameter(self) -> float:
		return self._getDoubleProperty("MP_MI_PARAMETER_RES")
	def setResidualMiParameter(self, value: float):
		return self._setDoubleProperty("MP_MI_PARAMETER_RES", value)
	def getResidualDParameter(self) -> float:
		return self._getDoubleProperty("MP_D_PARAMETER_RES")
	def setResidualDParameter(self, value: float):
		return self._setDoubleProperty("MP_D_PARAMETER_RES", value)
		