from rs2.modeler.properties.propertyProxy import PropertyProxy

class Constant(PropertyProxy):
    def getSigmaOne(self) -> float:
        return self._callFunction("getSigmaOne", [])
    def setSigmaOne(self, value: float):
        return self._callFunction("setSigmaOne", [value])
    def getSigmaThree(self) -> float:
        return self._callFunction("getSigmaThree", [])
    def setSigmaThree(self, value: float):
        return self._callFunction("setSigmaThree", [value])
    def getSigmaZ(self) -> float:
        return self._callFunction("getSigmaZ", [])
    def setSigmaZ(self, value: float):
        return self._callFunction("setSigmaZ", [value])
    def getAngle(self) -> float:
        return self._callFunction("getAngle", [])
    def setAngle(self, value: float):
        return self._callFunction("setAngle", [value])
    def setProperties(self, SigmaOne: float = None, SigmaThree: float = None, SigmaZ: float = None, Angle: float = None):
        if SigmaOne is not None:
            self._callFunction("setSigmaOne", [SigmaOne])
        if SigmaThree is not None:
            self._callFunction("setSigmaThree", [SigmaThree])
        if SigmaZ is not None:
            self._callFunction("setSigmaZ", [SigmaZ])
        if Angle is not None:
            self._callFunction("setAngle", [Angle])
    def getProperties(self):
        return {
            "SigmaOne" : self.getSigmaOne(),
            "SigmaThree" : self.getSigmaThree(),
            "SigmaZ" : self.getSigmaZ(),
            "Angle" : self.getAngle(),
        }
