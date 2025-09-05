from rs2.modeler.properties.propertyProxy import PropertyProxy
from rs2._common.Client import Client
from enum import Enum, auto
from typing import List
from rs2.modeler.properties.PropertyEnums import *
from rs2.modeler.managed_properties.material.strength.GeneralizedHoekBrown import GeneralizedHoekBrownLegacy,GeneralizedHoekBrownStageFactorLegacy,GeneralizedHoekBrownDefinedStageFactorLegacy 
from rs2._common.ProxyObject import ProxyObject
from rs2.modeler.properties.AbsoluteStageFactorGettersInterface import AbsoluteStageFactorGettersInterface
class GeneralizedHoekBrownStageFactor(GeneralizedHoekBrownStageFactorLegacy):
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
class GeneralizedHoekBrownDefinedStageFactor(GeneralizedHoekBrownStageFactor, GeneralizedHoekBrownDefinedStageFactorLegacy):
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
class GeneralizedHoekBrown(GeneralizedHoekBrownLegacy):
	"""
	Attributes:
		stageFactorInterface (AbsoluteStageFactorGettersInterface[JointedGeneralizedHoekBrownDefinedStageFactor, JointedGeneralizedHoekBrownStageFactor]): Reference object for modifying stage factor property.

	Examples:
		:ref:`Material Property Strength Example`
	
	"""
	def __init__(self, client : Client, ID, documentProxyID, stageFactorInterfaceID):
		super().__init__(client, ID, documentProxyID, stageFactorInterfaceID)
		self.stageFactorInterface = AbsoluteStageFactorGettersInterface[GeneralizedHoekBrownDefinedStageFactor, GeneralizedHoekBrownStageFactor](self._client, stageFactorInterfaceID, ID, GeneralizedHoekBrownDefinedStageFactor, GeneralizedHoekBrownStageFactor)
	def getMaterialType(self) -> MaterialType:
		return MaterialType(self._getEnumEMaterialAnalysisTypesProperty("MP_MATERIAL_TYPE"))
	def setMaterialType(self, value: MaterialType):
		return self._setEnumEMaterialAnalysisTypesProperty("MP_MATERIAL_TYPE", value)
	def getUCSOfIntactRockIntact(self) -> float:
		return self._getDoubleProperty("MP_UCS")
	def setUCSOfIntactRockIntact(self, value: float):
		return self._setDoubleProperty("MP_UCS", value)
	def getDefineBy(self) -> GSIInputType:
		return GSIInputType(self._getEnumEGSIInputTypeProperty("MP_GSI_INPUT_TYPE"))
	def setDefineBy(self, value: GSIInputType):
		return self._setEnumEGSIInputTypeProperty("MP_GSI_INPUT_TYPE", value)
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
	def getUcsBlockModel(self) -> bool:
		return self._getBoolProperty("MP_UCS_BM")
	def setUcsBlockModel(self, value: bool):
		return self._setBoolProperty("MP_UCS_BM", value)
	def getGsiParameterBlockModel(self) -> bool:
		return self._getBoolProperty("MP_GSI_PARAMETER_BM")
	def setGsiParameterBlockModel(self, value: bool):
		return self._setBoolProperty("MP_GSI_PARAMETER_BM", value)
	def getMiParameterBlockModel(self) -> bool:
		return self._getBoolProperty("MP_MI_PARAMETER_BM")
	def setMiParameterBlockModel(self, value: bool):
		return self._setBoolProperty("MP_MI_PARAMETER_BM", value)
	def getDParameterBlockModel(self) -> bool:
		return self._getBoolProperty("MP_D_PARAMETER_BM")
	def setDParameterBlockModel(self, value: bool):
		return self._setBoolProperty("MP_D_PARAMETER_BM", value)
	def getGsiParameterResBlockModel(self) -> bool:
		return self._getBoolProperty("MP_GSI_PARAMETER_RES_BM")
	def setGsiParameterResBlockModel(self, value: bool):
		return self._setBoolProperty("MP_GSI_PARAMETER_RES_BM", value)
	def getMiParameterResBlockModel(self) -> bool:
		return self._getBoolProperty("MP_MI_PARAMETER_RES_BM")
	def setMiParameterResBlockModel(self, value: bool):
		return self._setBoolProperty("MP_MI_PARAMETER_RES_BM", value)
	def getDParameterResBlockModel(self) -> bool:
		return self._getBoolProperty("MP_D_PARAMETER_RES_BM")
	def setDParameterResBlockModel(self, value: bool):
		return self._setBoolProperty("MP_D_PARAMETER_RES_BM", value)
	def getComputePeakMBSA(self) -> bool:
		return self._getBoolProperty("MP_GHB_COMPUTE_PEAK")
	def setComputePeakMBSA(self, value: bool):
		return self._setBoolProperty("MP_GHB_COMPUTE_PEAK", value)
	def getComputeResidualMBSA(self) -> bool:
		return self._getBoolProperty("MP_GHB_COMPUTE_RESIDUAL")
	def setComputeResidualMBSA(self, value: bool):
		return self._setBoolProperty("MP_GHB_COMPUTE_RESIDUAL", value)
	def getComputeRockMassElasticModulus(self) -> bool:
		return self._getBoolProperty("MP_GHB_USE_COMPUTE_ROCK_MASS")
	def setComputeRockMassElasticModulus(self, value: bool):
		return self._setBoolProperty("MP_GHB_USE_COMPUTE_ROCK_MASS", value)
	def getEstimationMethod(self) -> eGHBEstimationMethod:
		return eGHBEstimationMethod(self._getEnumEGHBEstimationMethodProperty("MP_GHB_ESTIMATION_METHOD"))
	def setEstimationMethod(self, value: eGHBEstimationMethod):
		return self._setEnumEGHBEstimationMethodProperty("MP_GHB_ESTIMATION_METHOD", value)
	def getUseType(self) -> eModulusInputMethod:
		return eModulusInputMethod(self._getEnumEModulusInputMethodProperty("MP_GHB_USE_TYPE"))
	def setUseType(self, value: eModulusInputMethod):
		return self._setEnumEModulusInputMethodProperty("MP_GHB_USE_TYPE", value)
	def getEI(self) -> float:
		return self._getDoubleProperty("MP_GHB_EI")
	def setEI(self, value: float):
		return self._setDoubleProperty("MP_GHB_EI", value)
	def getMR(self) -> float:
		return self._getDoubleProperty("MP_GHB_MR")
	def setMR(self, value: float):
		return self._setDoubleProperty("MP_GHB_MR", value)
	def setProperties(self, MaterialType : MaterialType = None, UCSOfIntactRockIntact : float = None, DefineBy : GSIInputType = None, MbParameter : float = None, SParameter : float = None, AParameter : float = None, GSI : float = None, Mi : float = None, D : float = None, ResidualMbParameter : float = None, ResidualSParameter : float = None, ResidualAParameter : float = None, GSIResidual : float = None, MiResidual : float = None, DResidual : float = None, DilationParameter : float = None, ApplySSRShearStrengthReduction : bool = None, TensileCutoffType : TensileCutoffOptions = None, TensileCutoff : float = None, HoekMartinMi : float = None, UcsBlockModel : bool = None, GsiParameterBlockModel : bool = None, MiParameterBlockModel : bool = None, DParameterBlockModel : bool = None, GsiParameterResBlockModel : bool = None, MiParameterResBlockModel : bool = None, DParameterResBlockModel : bool = None, ComputePeakMBSA : bool = None, ComputeResidualMBSA : bool = None, ComputeRockMassElasticModulus : bool = None, EstimationMethod : eGHBEstimationMethod = None, UseType : eModulusInputMethod = None, EI : float = None, MR : float = None):
		if MaterialType is not None:
			self._setEnumEMaterialAnalysisTypesProperty("MP_MATERIAL_TYPE", MaterialType)
		if UCSOfIntactRockIntact is not None:
			self._setDoubleProperty("MP_UCS", UCSOfIntactRockIntact)
		if DefineBy is not None:
			self._setEnumEGSIInputTypeProperty("MP_GSI_INPUT_TYPE", DefineBy)
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
		if TensileCutoffType is not None:
			self._setEnumETensileCutoffOptionsProperty("MP_TENSION_CUTOFF_OPTIONS", TensileCutoffType)
		if TensileCutoff is not None:
			self._setDoubleProperty("MP_UD_TENSION_CUTOFF", TensileCutoff)
		if HoekMartinMi is not None:
			self._setDoubleProperty("MP_MI_TENSION_CUTOFF", HoekMartinMi)
		if UcsBlockModel is not None:
			self._setBoolProperty("MP_UCS_BM", UcsBlockModel)
		if GsiParameterBlockModel is not None:
			self._setBoolProperty("MP_GSI_PARAMETER_BM", GsiParameterBlockModel)
		if MiParameterBlockModel is not None:
			self._setBoolProperty("MP_MI_PARAMETER_BM", MiParameterBlockModel)
		if DParameterBlockModel is not None:
			self._setBoolProperty("MP_D_PARAMETER_BM", DParameterBlockModel)
		if GsiParameterResBlockModel is not None:
			self._setBoolProperty("MP_GSI_PARAMETER_RES_BM", GsiParameterResBlockModel)
		if MiParameterResBlockModel is not None:
			self._setBoolProperty("MP_MI_PARAMETER_RES_BM", MiParameterResBlockModel)
		if DParameterResBlockModel is not None:
			self._setBoolProperty("MP_D_PARAMETER_RES_BM", DParameterResBlockModel)
		if ComputePeakMBSA is not None:
			self._setBoolProperty("MP_GHB_COMPUTE_PEAK", ComputePeakMBSA)
		if ComputeResidualMBSA is not None:
			self._setBoolProperty("MP_GHB_COMPUTE_RESIDUAL", ComputeResidualMBSA)
		if ComputeRockMassElasticModulus is not None:
			self._setBoolProperty("MP_GHB_USE_COMPUTE_ROCK_MASS", ComputeRockMassElasticModulus)
		if EstimationMethod is not None:
			self._setEnumEGHBEstimationMethodProperty("MP_GHB_ESTIMATION_METHOD", EstimationMethod)
		if UseType is not None:
			self._setEnumEModulusInputMethodProperty("MP_GHB_USE_TYPE", UseType)
		if EI is not None:
			self._setDoubleProperty("MP_GHB_EI", EI)
		if MR is not None:
			self._setDoubleProperty("MP_GHB_MR", MR)
	def getProperties(self):
		return {
		"MaterialType" : self.getMaterialType(), 
		"UCSOfIntactRockIntact" : self.getUCSOfIntactRockIntact(), 
		"DefineBy" : self.getDefineBy(), 
		"MbParameter" : self.getMbParameter(), 
		"SParameter" : self.getSParameter(), 
		"AParameter" : self.getAParameter(), 
		"GSI" : self.getGSI(), 
		"Mi" : self.getMi(), 
		"D" : self.getD(), 
		"ResidualMbParameter" : self.getResidualMbParameter(), 
		"ResidualSParameter" : self.getResidualSParameter(), 
		"ResidualAParameter" : self.getResidualAParameter(), 
		"GSIResidual" : self.getGSIResidual(), 
		"MiResidual" : self.getMiResidual(), 
		"DResidual" : self.getDResidual(), 
		"DilationParameter" : self.getDilationParameter(), 
		"ApplySSRShearStrengthReduction" : self.getApplySSRShearStrengthReduction(), 
		"TensileCutoffType" : self.getTensileCutoffType(), 
		"TensileCutoff" : self.getTensileCutoff(), 
		"HoekMartinMi" : self.getHoekMartinMi(), 
		"UcsBlockModel" : self.getUcsBlockModel(), 
		"GsiParameterBlockModel" : self.getGsiParameterBlockModel(), 
		"MiParameterBlockModel" : self.getMiParameterBlockModel(), 
		"DParameterBlockModel" : self.getDParameterBlockModel(), 
		"GsiParameterResBlockModel" : self.getGsiParameterResBlockModel(), 
		"MiParameterResBlockModel" : self.getMiParameterResBlockModel(), 
		"DParameterResBlockModel" : self.getDParameterResBlockModel(), 
		"ComputePeakMBSA" : self.getComputePeakMBSA(), 
		"ComputeResidualMBSA" : self.getComputeResidualMBSA(), 
		"ComputeRockMassElasticModulus" : self.getComputeRockMassElasticModulus(), 
		"EstimationMethod" : self.getEstimationMethod(), 
		"UseType" : self.getUseType(), 
		"EI" : self.getEI(), 
		"MR" : self.getMR(), 
		}
