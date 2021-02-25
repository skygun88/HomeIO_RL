import sys
import os
sys.path.append(os.path.dirname(__file__))
from Devices import *

''' ------------------------------------------------------------- '''
''' - actuator device                                           - '''
''' ------------------------------------------------------------- '''

class RoomLight(Light):
    def __init__(self):
        super().__init__()
        self.output = 101

class RoomRoller(Roller):
    def __init__(self):
        super().__init__()
        self.input = 83 # Float
        self.output_up = 123 # Bool
        self.output_down = 124 # Bool

class RoomHeater(Heater):
    def __init__(self):
        super().__init__()
        self.output = 102 # Float
        self.output_power = 125 # Bit

''' ------------------------------------------------------------- '''
''' - Sensor device                                             - '''
''' ------------------------------------------------------------- '''
class RoomBrightness(Brightness):
    def __init__(self):
        super().__init__()
        self.input = 80

class RoomBThermostat(Thermostat):
    def __init__(self):
        super().__init__()
        self.input_cur = 81
        self.input_set = 82
    
    
