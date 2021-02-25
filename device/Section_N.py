import sys
import os
sys.path.append(os.path.dirname(__file__))
from Devices import *

''' ------------------------------------------------------------- '''
''' - actuator device                                           - '''
''' ------------------------------------------------------------- '''

class RoomLight1(Light):
    def __init__(self):
        super().__init__()
        self.output = 145
        self.name = 'RoomLight1'

class RoomLight2(Light):
    def __init__(self):
        super().__init__()
        self.output = 146
        self.name = 'RoomLight2'

class RoomRoller(Roller):
    def __init__(self):
        super().__init__()
        self.input = 130 # Float
        self.output_up = 175 # Bool
        self.output_down = 176 # Bool
        self.name = 'RoomRoller'

class RoomHeater(Heater):
    def __init__(self):
        super().__init__()
        self.output = 148 # Float
        self.output_power = 177 # Bit
        self.name = 'RoomHeater'

''' ------------------------------------------------------------- '''
''' - Sensor device                                             - '''
''' ------------------------------------------------------------- '''
class RoomBrightness(Brightness):
    def __init__(self):
        super().__init__()
        self.input = 127
        self.name = 'RoomBrightness'

class RoomTemperature(Thermostat):
    def __init__(self):
        super().__init__()
        self.input_cur = 128
        self.input_set = 129
        self.name = 'RoomTemperature'
    
