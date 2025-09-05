from rs2.modeler.properties.propertyProxy import PropertyProxy
from rs2._common.Client import Client
from enum import Enum, auto
from rs2.modeler.properties.PropertyEnums import *
from rs2.modeler.properties.field_stress.Constant import Constant
from rs2.modeler.properties.field_stress.Gravity import Gravity

class FieldStress(PropertyProxy):
    def __init__(self, client: Client, ID, documentProxyID):
        self.Constant = Constant(client, ID, documentProxyID)
        self.Gravity = Gravity(client, ID, documentProxyID)
        super().__init__(client, ID, documentProxyID)
    def getStressType(self) -> StressTypes:
        return StressTypes(self._callFunction("getStressType", []))
    def setStressType(self, value: StressTypes):
        return self._callFunction("setStressType", [value.value])
    def getConstant(self) -> Constant:
        constant_id = self._callFunction("getConstant", [], keepReturnValueReference=True)
        return Constant(self._client, constant_id, self.documentProxyID)
    def getGravity(self) -> Gravity:
        gravity_id = self._callFunction("getGravity", [], keepReturnValueReference=True)
        return Gravity(self._client, gravity_id, self.documentProxyID)
    def restoreDefaults(self):
        return self._callFunction('restoreDefaults', [])
