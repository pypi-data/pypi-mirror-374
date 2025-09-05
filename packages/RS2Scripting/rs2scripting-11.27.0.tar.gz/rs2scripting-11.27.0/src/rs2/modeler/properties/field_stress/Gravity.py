from rs2.modeler.properties.propertyProxy import PropertyProxy

class Gravity(PropertyProxy):
    def getUnitWt(self) -> float:
        return self._callFunction("getUnitWt", [])
    def setUnitWt(self, value: float):
        return self._callFunction("setUnitWt", [value])
    def getStressRatIn(self) -> float:
        return self._callFunction("getStressRatIn", [])
    def setStressRatIn(self, value: float):
        return self._callFunction("setStressRatIn", [value])
    def getStressRatOut(self) -> float:
        return self._callFunction("getStressRatOut", [])
    def setStressRatOut(self, value: float):
        return self._callFunction("setStressRatOut", [value])
    def getHStressIn(self) -> float:
        return self._callFunction("getHStressIn", [])
    def setHStressIn(self, value: float):
        return self._callFunction("setHStressIn", [value])
    def getHStressOut(self) -> float:
        return self._callFunction("getHStressOut", [])
    def setHStressOut(self, value: float):
        return self._callFunction("setHStressOut", [value])
    def getGroundElev(self) -> float:
        return self._callFunction("getGroundElev", [])
    def setGroundElev(self, value: float):
        return self._callFunction("setGroundElev", [value])
    def getKInA(self) -> float:
        return self._callFunction("getKInA", [])
    def setKInA(self, value: float):
        return self._callFunction("setKInA", [value])
    def getKInB(self) -> float:
        return self._callFunction("getKInB", [])
    def setKInB(self, value: float):
        return self._callFunction("setKInB", [value])
    def getKInC(self) -> float:
        return self._callFunction("getKInC", [])
    def setKInC(self, value: float):
        return self._callFunction("setKInC", [value])
    def getKOutA(self) -> float:
        return self._callFunction("getKOutA", [])
    def setKOutA(self, value: float):
        return self._callFunction("setKOutA", [value])
    def getKOutB(self) -> float:
        return self._callFunction("getKOutB", [])
    def setKOutB(self, value: float):
        return self._callFunction("setKOutB", [value])
    def getKOutC(self) -> float:
        return self._callFunction("getKOutC", [])
    def setKOutC(self, value: float):
        return self._callFunction("setKOutC", [value])
    def getUseActualGroundSurface(self) -> bool:
        return self._callFunction("getUseActualGroundSurface", [])
    def setUseActualGroundSurface(self, value: bool):
        return self._callFunction("setUseActualGroundSurface", [value])
    def getUseEffectiveStressRatio(self) -> bool:
        return self._callFunction("getUseEffectiveStressRatio", [])
    def setUseEffectiveStressRatio(self, value: bool):
        return self._callFunction("setUseEffectiveStressRatio", [value])
    def getUseVariableStressRatio(self) -> bool:
        return self._callFunction("getUseVariableStressRatio", [])
    def setUseVariableStressRatio(self, value: bool):
        return self._callFunction("setUseVariableStressRatio", [value])
    def setProperties(self, UnitWt : float = None, StressRatIn : float = None, StressRatOut : float = None, HStressIn : float = None, HStressOut : float = None,
                      GroundElev : float = None, KInA : float = None, KInB : float = None, KInC : float = None, KOutA : float = None, KOutB : float = None, KOutC : float = None,
                      UseActualGroundSurface : bool = None, UseEffectiveStressRatio : bool = None, UseVariableStressRatio : bool = None):
        if UnitWt is not None:
            self._callFunction("setUnitWt", [UnitWt])
        if StressRatIn is not None:
            self._callFunction("setStressRatIn", [StressRatIn])
        if StressRatOut is not None:
            self._callFunction("setStressRatOut", [StressRatOut])
        if HStressIn is not None:
            self._callFunction("setHStressIn", [HStressIn])
        if HStressOut is not None:
            self._callFunction("setHStressOut", [HStressOut])
        if GroundElev is not None:
            self._callFunction("setGroundElev", [GroundElev])
        if KInA is not None:
            self._callFunction("setKInA", [KInA])
        if KInB is not None:
            self._callFunction("setKInB", [KInB])
        if KInC is not None:
            self._callFunction("setKInC", [KInC])
        if KOutA is not None:
            self._callFunction("setKOutA", [KOutA])
        if KOutB is not None:
            self._callFunction("setKOutB", [KOutB])
        if KOutC is not None:
            self._callFunction("setKOutC", [KOutC])
        if UseActualGroundSurface is not None:
            self._callFunction("setUseActualGroundSurface", [UseActualGroundSurface])
        if UseEffectiveStressRatio is not None:
            self._callFunction("setUseEffectiveStressRatio", [UseEffectiveStressRatio])
        if UseVariableStressRatio is not None:
            self._callFunction("setUseVariableStressRatio", [UseVariableStressRatio])
        
    def getProperties(self):
        return {
            "UnitWt": self.getUnitWt(),
            "StressRatIn": self.getStressRatIn(),
            "StressRatOut": self.getStressRatOut(),
            "HStressIn": self.getHStressIn(),
            "HStressOut": self.getHStressOut(),
            "GroundElev": self.getGroundElev(),
            "KInA": self.getKInA(),
            "KInB": self.getKInB(),
            "KInC": self.getKInC(),
            "KOutA": self.getKOutA(),
            "KOutB": self.getKOutB(),
            "KOutC": self.getKOutC(),
            "UseActualGroundSurface": self.getUseActualGroundSurface(),
            "UseEffectiveStressRatio": self.getUseEffectiveStressRatio(),
            "UseVariableStressRatio": self.getUseVariableStressRatio(),
        }
