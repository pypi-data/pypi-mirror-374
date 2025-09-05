from rs2.modeler.properties.propertyProxy import PropertyProxy
from rs2._common.Client import Client
from enum import Enum, auto
from typing import List
from rs2.modeler.properties.PropertyEnums import *
from rs2.modeler.properties.MaterialJointOptions import MaterialJointOptions 
from rs2.modeler.managed_properties.material.strength.JointedGeneralizedHoekBrown import JointedGeneralizedHoekBrownLegacy,JointedGeneralizedHoekBrownStageFactorLegacy,JointedGeneralizedHoekBrownDefinedStageFactorLegacy 
from rs2._common.ProxyObject import ProxyObject
from rs2.modeler.properties.AbsoluteStageFactorGettersInterface import AbsoluteStageFactorGettersInterface
class JointedGeneralizedHoekBrownStageFactor(JointedGeneralizedHoekBrownStageFactorLegacy):
	def __init__(self, client : Client, ID, propertyID):
		super().__init__(client, ID, propertyID)
		self.propertyID = propertyID
	def getAParameterFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_A_PARAMETER", self.propertyID], proxyArgumentIndices=[1])
	def getResidualAParameterFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_A_PARAMETER_RES", self.propertyID], proxyArgumentIndices=[1])
	def getUCSOfIntactRockIntactFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_UCS", self.propertyID], proxyArgumentIndices=[1])
	def getDilationParameterFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_DILATION_PARAMETER", self.propertyID], proxyArgumentIndices=[1])
	def getMbParameterFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_MB_PARAMETER", self.propertyID], proxyArgumentIndices=[1])
	def getResidualMbParameterFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_MB_PARAMETER_RES", self.propertyID], proxyArgumentIndices=[1])
	def getHoekMartinMiFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_MI_TENSION_CUTOFF", self.propertyID], proxyArgumentIndices=[1])
	def getSParameterFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_S_PARAMETER", self.propertyID], proxyArgumentIndices=[1])
	def getResidualSParameterFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_S_PARAMETER_RES", self.propertyID], proxyArgumentIndices=[1])
	def getTensileCutoffFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_UD_TENSION_CUTOFF", self.propertyID], proxyArgumentIndices=[1])
	def getGSIFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_GSI_PARAMETER", self.propertyID], proxyArgumentIndices=[1])
	def getGSIResidualFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_GSI_PARAMETER_RES", self.propertyID], proxyArgumentIndices=[1])
	def getMiFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_MI_PARAMETER", self.propertyID], proxyArgumentIndices=[1])
	def getMiResidualFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_MI_PARAMETER_RES", self.propertyID], proxyArgumentIndices=[1])
	def getDFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_D_PARAMETER", self.propertyID], proxyArgumentIndices=[1])
	def getDResidualFactor(self) -> float:
		return self._callFunction("getDoubleFactor", ["MP_D_PARAMETER_RES", self.propertyID], proxyArgumentIndices=[1])
class JointedGeneralizedHoekBrownDefinedStageFactor(JointedGeneralizedHoekBrownStageFactor, JointedGeneralizedHoekBrownDefinedStageFactorLegacy):
	def __init__(self, client : Client, ID, propertyID):
		super().__init__(client, ID, propertyID)
	def setAParameterFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_A_PARAMETER", value, self.propertyID], proxyArgumentIndices=[2])
	def setResidualAParameterFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_A_PARAMETER_RES", value, self.propertyID], proxyArgumentIndices=[2])
	def setUCSOfIntactRockIntactFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_UCS", value, self.propertyID], proxyArgumentIndices=[2])
	def setDilationParameterFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_DILATION_PARAMETER", value, self.propertyID], proxyArgumentIndices=[2])
	def setMbParameterFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_MB_PARAMETER", value, self.propertyID], proxyArgumentIndices=[2])
	def setResidualMbParameterFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_MB_PARAMETER_RES", value, self.propertyID], proxyArgumentIndices=[2])
	def setHoekMartinMiFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_MI_TENSION_CUTOFF", value, self.propertyID], proxyArgumentIndices=[2])
	def setSParameterFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_S_PARAMETER", value, self.propertyID], proxyArgumentIndices=[2])
	def setResidualSParameterFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_S_PARAMETER_RES", value, self.propertyID], proxyArgumentIndices=[2])
	def setTensileCutoffFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_UD_TENSION_CUTOFF", value, self.propertyID], proxyArgumentIndices=[2])
	def setGSIFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_GSI_PARAMETER", value, self.propertyID], proxyArgumentIndices=[2])
	def setGSIResidualFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_GSI_PARAMETER_RES", value, self.propertyID], proxyArgumentIndices=[2])
	def setMiFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_MI_PARAMETER", value, self.propertyID], proxyArgumentIndices=[2])
	def setMiResidualFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_MI_PARAMETER_RES", value, self.propertyID], proxyArgumentIndices=[2])
	def setDFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_D_PARAMETER", value, self.propertyID], proxyArgumentIndices=[2])
	def setDResidualFactor(self, value: float):
		return self._callFunction("setDoubleFactor", ["MP_D_PARAMETER_RES", value, self.propertyID], proxyArgumentIndices=[2])
class JointedGeneralizedHoekBrown(JointedGeneralizedHoekBrownLegacy):
	"""
	Attributes:
		stageFactorInterface (AbsoluteStageFactorGettersInterface[JointedGeneralizedHoekBrownDefinedStageFactor, JointedGeneralizedHoekBrownStageFactor]): Reference object for modifying stage factor property.

	Examples:
		:ref:`Material Property Strength Example`
	
	"""
	def __init__(self, client : Client, ID, documentProxyID, stageFactorInterfaceID):
		super().__init__(client, ID, documentProxyID, stageFactorInterfaceID)
		self.stageFactorInterface = AbsoluteStageFactorGettersInterface[JointedGeneralizedHoekBrownDefinedStageFactor, JointedGeneralizedHoekBrownStageFactor](self._client, stageFactorInterfaceID, ID, JointedGeneralizedHoekBrownDefinedStageFactor, JointedGeneralizedHoekBrownStageFactor)
	def getMaterialType(self) -> MaterialType:
		return MaterialType(self._getEnumEMaterialAnalysisTypesProperty("MP_MATERIAL_TYPE"))
	def setMaterialType(self, value: MaterialType):
		return self._setEnumEMaterialAnalysisTypesProperty("MP_MATERIAL_TYPE", value)
	def getUCSOfIntactRockIntact(self) -> float:
		return self._getDoubleProperty("MP_UCS")
	def setUCSOfIntactRockIntact(self, value: float):
		return self._setDoubleProperty("MP_UCS", value)
	def getMbParameter(self) -> float:
		return self._getDoubleProperty("MP_MB_PARAMETER")
	def setMbParameter(self, value: float):
		return self._setDoubleProperty("MP_MB_PARAMETER", value)
	def getSParameter(self) -> float:
		return self._getDoubleProperty("MP_S_PARAMETER")
	def setSParameter(self, value: float):
		return self._setDoubleProperty("MP_S_PARAMETER", value)
	def getAParameter(self) -> float:
		return self._getDoubleProperty("MP_A_PARAMETER")
	def setAParameter(self, value: float):
		return self._setDoubleProperty("MP_A_PARAMETER", value)
	def getGSI(self) -> float:
		return self._getDoubleProperty("MP_GSI_PARAMETER")
	def setGSI(self, value: float):
		return self._setDoubleProperty("MP_GSI_PARAMETER", value)
	def getMi(self) -> float:
		return self._getDoubleProperty("MP_MI_PARAMETER")
	def setMi(self, value: float):
		return self._setDoubleProperty("MP_MI_PARAMETER", value)
	def getD(self) -> float:
		return self._getDoubleProperty("MP_D_PARAMETER")
	def setD(self, value: float):
		return self._setDoubleProperty("MP_D_PARAMETER", value)
	def getTensileCutoffType(self) -> TensileCutoffOptions:
		return TensileCutoffOptions(self._getEnumETensileCutoffOptionsProperty("MP_TENSION_CUTOFF_OPTIONS"))
	def setTensileCutoffType(self, value: TensileCutoffOptions):
		return self._setEnumETensileCutoffOptionsProperty("MP_TENSION_CUTOFF_OPTIONS", value)
	def getTensileCutoff(self) -> float:
		return self._getDoubleProperty("MP_UD_TENSION_CUTOFF")
	def setTensileCutoff(self, value: float):
		return self._setDoubleProperty("MP_UD_TENSION_CUTOFF", value)
	def getHoekMartinMi(self) -> float:
		return self._getDoubleProperty("MP_MI_TENSION_CUTOFF")
	def setHoekMartinMi(self, value: float):
		return self._setDoubleProperty("MP_MI_TENSION_CUTOFF", value)
	def getResidualMbParameter(self) -> float:
		return self._getDoubleProperty("MP_MB_PARAMETER_RES")
	def setResidualMbParameter(self, value: float):
		return self._setDoubleProperty("MP_MB_PARAMETER_RES", value)
	def getResidualSParameter(self) -> float:
		return self._getDoubleProperty("MP_S_PARAMETER_RES")
	def setResidualSParameter(self, value: float):
		return self._setDoubleProperty("MP_S_PARAMETER_RES", value)
	def getResidualAParameter(self) -> float:
		return self._getDoubleProperty("MP_A_PARAMETER_RES")
	def setResidualAParameter(self, value: float):
		return self._setDoubleProperty("MP_A_PARAMETER_RES", value)
	def getGSIResidual(self) -> float:
		return self._getDoubleProperty("MP_GSI_PARAMETER_RES")
	def setGSIResidual(self, value: float):
		return self._setDoubleProperty("MP_GSI_PARAMETER_RES", value)
	def getMiResidual(self) -> float:
		return self._getDoubleProperty("MP_MI_PARAMETER_RES")
	def setMiResidual(self, value: float):
		return self._setDoubleProperty("MP_MI_PARAMETER_RES", value)
	def getDResidual(self) -> float:
		return self._getDoubleProperty("MP_D_PARAMETER_RES")
	def setDResidual(self, value: float):
		return self._setDoubleProperty("MP_D_PARAMETER_RES", value)
	def getDilationParameter(self) -> float:
		return self._getDoubleProperty("MP_DILATION_PARAMETER")
	def setDilationParameter(self, value: float):
		return self._setDoubleProperty("MP_DILATION_PARAMETER", value)
	def getApplySSRShearStrengthReduction(self) -> bool:
		return self._getBoolProperty("MP_APPLY_SSR")
	def setApplySSRShearStrengthReduction(self, value: bool):
		return self._setBoolProperty("MP_APPLY_SSR", value)
	def getJointOptions(self) -> MaterialJointOptions:
		return MaterialJointOptions(self._client, self._callFunction("getJointOptions", [], keepReturnValueReference = True), self.documentProxyID)
	def setProperties(self, MaterialType : MaterialType = None, UCSOfIntactRockIntact : float = None, MbParameter : float = None, SParameter : float = None, AParameter : float = None, GSI : float = None, Mi : float = None, D : float = None, TensileCutoffType : TensileCutoffOptions = None, TensileCutoff : float = None, HoekMartinMi : float = None, ResidualMbParameter : float = None, ResidualSParameter : float = None, ResidualAParameter : float = None, GSIResidual : float = None, MiResidual : float = None, DResidual : float = None, DilationParameter : float = None, ApplySSRShearStrengthReduction : bool = None):
		if MaterialType is not None:
			self._setEnumEMaterialAnalysisTypesProperty("MP_MATERIAL_TYPE", MaterialType)
		if UCSOfIntactRockIntact is not None:
			self._setDoubleProperty("MP_UCS", UCSOfIntactRockIntact)
		if MbParameter is not None:
			self._setDoubleProperty("MP_MB_PARAMETER", MbParameter)
		if SParameter is not None:
			self._setDoubleProperty("MP_S_PARAMETER", SParameter)
		if AParameter is not None:
			self._setDoubleProperty("MP_A_PARAMETER", AParameter)
		if GSI is not None:
			self._setDoubleProperty("MP_GSI_PARAMETER", GSI)
		if Mi is not None:
			self._setDoubleProperty("MP_MI_PARAMETER", Mi)
		if D is not None:
			self._setDoubleProperty("MP_D_PARAMETER", D)
		if TensileCutoffType is not None:
			self._setEnumETensileCutoffOptionsProperty("MP_TENSION_CUTOFF_OPTIONS", TensileCutoffType)
		if TensileCutoff is not None:
			self._setDoubleProperty("MP_UD_TENSION_CUTOFF", TensileCutoff)
		if HoekMartinMi is not None:
			self._setDoubleProperty("MP_MI_TENSION_CUTOFF", HoekMartinMi)
		if ResidualMbParameter is not None:
			self._setDoubleProperty("MP_MB_PARAMETER_RES", ResidualMbParameter)
		if ResidualSParameter is not None:
			self._setDoubleProperty("MP_S_PARAMETER_RES", ResidualSParameter)
		if ResidualAParameter is not None:
			self._setDoubleProperty("MP_A_PARAMETER_RES", ResidualAParameter)
		if GSIResidual is not None:
			self._setDoubleProperty("MP_GSI_PARAMETER_RES", GSIResidual)
		if MiResidual is not None:
			self._setDoubleProperty("MP_MI_PARAMETER_RES", MiResidual)
		if DResidual is not None:
			self._setDoubleProperty("MP_D_PARAMETER_RES", DResidual)
		if DilationParameter is not None:
			self._setDoubleProperty("MP_DILATION_PARAMETER", DilationParameter)
		if ApplySSRShearStrengthReduction is not None:
			self._setBoolProperty("MP_APPLY_SSR", ApplySSRShearStrengthReduction)
	def getProperties(self):
		return {
		"MaterialType" : self.getMaterialType(), 
		"UCSOfIntactRockIntact" : self.getUCSOfIntactRockIntact(), 
		"MbParameter" : self.getMbParameter(), 
		"SParameter" : self.getSParameter(), 
		"AParameter" : self.getAParameter(), 
		"GSI" : self.getGSI(), 
		"Mi" : self.getMi(), 
		"D" : self.getD(), 
		"TensileCutoffType" : self.getTensileCutoffType(), 
		"TensileCutoff" : self.getTensileCutoff(), 
		"HoekMartinMi" : self.getHoekMartinMi(), 
		"ResidualMbParameter" : self.getResidualMbParameter(), 
		"ResidualSParameter" : self.getResidualSParameter(), 
		"ResidualAParameter" : self.getResidualAParameter(), 
		"GSIResidual" : self.getGSIResidual(), 
		"MiResidual" : self.getMiResidual(), 
		"DResidual" : self.getDResidual(), 
		"DilationParameter" : self.getDilationParameter(), 
		"ApplySSRShearStrengthReduction" : self.getApplySSRShearStrengthReduction(), 
		}
