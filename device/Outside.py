import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))+'/utils')
import clr
clr.AddReference('EngineIO')
from EngineIO import *

class OutsideTemperature:
    def __init__(self):
        self.temperature = 132 # Memory
        self.name = 'OutsideTemperature'
    
    def state(self):
        MemoryMap.Instance.Update()
        return MemoryMap.Instance.GetFloat(self.temperature, MemoryType.Memory).Value - 273
         

class OutsideBrightness:
    def __init__(self):
        self.brightness = 139 # Input
        self.name = 'OutsideBrightness'
    
    def state(self):
        MemoryMap.Instance.Update()
        return MemoryMap.Instance.GetFloat(self.brightness, MemoryType.Input).Value
