from rs2._common.ProxyObject import ProxyObject
from rs2.modeler.properties.PropertyEnums import *

class Gan3DFunction(ProxyObject):
    def setName(self, name : str):
        return self._callFunction('setName', [name])
    def getName(self):
        return self._callFunction('getName', [])
    def setBaseMaterial(self, baseMaterial : str):
        return self._callFunction('setBaseMaterial', [baseMaterial])
    def getBaseMaterial(self):
        return self._callFunction('getBaseMaterial', [])
    def set3DAnisotropyHandling(self, an: Anisotropy3DHandling):
        return self._callFunction('set3DAnisotropyHandling', [an.value])

    def get3DAnisotropyHandling(self) -> Anisotropy3DHandling:
        result = self._callFunction('get3DAnisotropyHandling', [])
        return Anisotropy3DHandling(result)

    def setAngles(self, angle : list[float]):
        return self._callFunction('setAngles', [angle])
    def getAngles(self):
        return self._callFunction('getAngles', [])

    def setDips(self, angle : list[float]):
        return self._callFunction('setDips', [angle])
    def getDips(self):
        return self._callFunction('getDips', [])

    def setDipDirections(self, angle : list[float]):
        return self._callFunction('setDipDirections', [angle])
    def getDipDirections(self):
        return self._callFunction('getDipDirections', [])

    def setUseDipBlockLevel(self, angle : list[float]):
        return self._callFunction('setUseDipBlockLevel', [angle])
    def getUseDipBlockLevel(self):
        return self._callFunction('getUseDipBlockLevel', [])

    def setUseDipDirectionBlockLevel(self, angle : list[float]):
        return self._callFunction('setUseDipDirectionBlockLevel', [angle])
    def getUseDipDirectionBlockLevel(self):
        return self._callFunction('getUseDipDirectionBlockLevel', [])

    def setAValues(self, a : list[float]):
        return self._callFunction('setAValues', [a])
    def getAValues(self):
        return self._callFunction('getAValues', [])
    def setBValues(self, b : list[float]):
        return self._callFunction('setBValues', [b])
    def getBValues(self):
        return self._callFunction('getBValues', [])
    def setMaterials(self, material : list[int]):
        return self._callFunction('setMaterials', [material])
    def getMaterials(self):
        return self._callFunction('getMaterials', [])

class Gan2DFunction(ProxyObject):
    def setName(self, name : str):
        return self._callFunction('setName', [name])
    def getName(self):
        return self._callFunction('getName', [])
    def setBaseMaterial(self, baseMaterial : str):
        return self._callFunction('setBaseMaterial', [baseMaterial])
    def getBaseMaterial(self):
        return self._callFunction('getBaseMaterial', [])
    def setAnisotropyDefinition(self, anisotropyDefinition : Anisotropy2dDefinition):
        return self._callFunction('setAnisotropyDefinition', [anisotropyDefinition.value])
    def getAnisotropyDefinition(self):
        result = self._callFunction('getAnisotropyDefinition', [])
        return Anisotropy2dDefinition(result)
    def setAngles(self, angle : list[float]):
        return self._callFunction('setAngles', [angle])
    def getAngles(self):
        return self._callFunction('getAngles', [])
    def setSurfaces(self, surfaces: list[str]):
        return self._callFunction('setSurfaces', [surfaces])
    def getSurfaces(self):
        return self._callFunction('getSurfaces', [])
    def setAValues(self, a : list[float]):
        return self._callFunction('setAValues', [a])
    def getAValues(self):
        return self._callFunction('getAValues', [])
    def setBValues(self, b : list[float]):
        return self._callFunction('setBValues', [b])
    def getBValues(self):
        return self._callFunction('getBValues', [])
    def setMaterials(self, material : list[int]):
        return self._callFunction('setMaterials', [material])
    def getMaterials(self):
        return self._callFunction('getMaterials', [])

class GanAngleRangeFunction(ProxyObject):

    def setName(self, name : str):
        return self._callFunction('setName', [name])
    def getName(self):
        return self._callFunction('getName', [])

    def setMaterials(self, material : list[int]):
        return self._callFunction('setMaterials', [material])
    def getMaterials(self):
        return self._callFunction('getMaterials', [])

    def setAngles(self, angle : list[float]):
        return self._callFunction('setAngles', [angle])
    def getAngles(self):
        return self._callFunction('getAngles', [])