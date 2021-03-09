import sys
import os
import time
import random

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))+'/utils')
import clr
clr.AddReference('EngineIO')
from EngineIO import *


''' ------------------------------------------------------------- '''
''' - actuator device                                           - '''
''' ------------------------------------------------------------- '''

class Light:
    def __init__(self):
        self.output = -1

    def on(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        device.Value = 10.0
        MemoryMap.Instance.Update()

    def off(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        device.Value = 0.01
        MemoryMap.Instance.Update()

    def analogue_up(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        # device.Value = min(device.Value + 0.5, 10.0)
        device.Value = min(round(device.Value + 1.0, 1), 10.0) # Handle to 0.01
        MemoryMap.Instance.Update()

    def analogue_down(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        # device.Value = max(device.Value - 0.5, 0.01)
        device.Value = max(device.Value - 1.0, 0.01)
        MemoryMap.Instance.Update()

    # def actuate(self, action):
    #     if action == 1:
    #         self.on()
    #     elif action == 2:
    #         self.off()

    def actuate(self, action):
        if action == 1:
            self.analogue_up()
        elif action == 2:
            self.analogue_down()

    # def random_choice(self):
    #     self.actuate(random.choice([1, 2]))
    #     return self.state()

    def random_choice(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        value_list = [round(1.0*i, 2) for i in range(11)]
        value_list[0] = 0.01
        device.Value = random.choice(value_list)
        MemoryMap.Instance.Update()
        return self.state()

    def state(self):
        '''
        state (Float) = 0.01 if fully closed, 10.0 if fully opened
        '''
        MemoryMap.Instance.Update()
        return MemoryMap.Instance.GetFloat(self.output, MemoryType.Output).Value

class Roller:
    def __init__(self):
        self.input = -1 # Float
        self.output_up = -1 # Bool
        self.output_down = -1 # Bool

    def up(self):
        device = MemoryMap.Instance.GetBit(self.output_up, MemoryType.Output)
        device.Value = True
        MemoryMap.Instance.Update()

    def down(self):
        device = MemoryMap.Instance.GetBit(self.output_down, MemoryType.Output)
        device.Value = True
        MemoryMap.Instance.Update()

    def actuate(self, action):
        if action == 1:
            while self.state() < 10:
                self.up()
                time.sleep(0.1)
        elif action == 2:
            while self.state() > 0:
                self.down()
                time.sleep(0.1)
        self.reset_output()

    def random_choice(self):
        self.actuate(random.choice([1, 2]))
        return self.state()

    def reset_output(self):
        device1 = MemoryMap.Instance.GetBit(self.output_up, MemoryType.Output)
        device2 = MemoryMap.Instance.GetBit(self.output_down, MemoryType.Output)
        device1.Value = False
        device2.Value = False
        MemoryMap.Instance.Update()

    def state(self):
        '''
        state (Float) = 0.0 if fully closed, 1.0 if fully opened
        '''
        MemoryMap.Instance.Update()
        return MemoryMap.Instance.GetFloat(self.input, MemoryType.Input).Value


class Heater:
    def __init__(self):
        self.output = -1 # Float
        self.output_power = -1 # Bit

    def on(self):
        device = MemoryMap.Instance.GetBit(self.output_power, MemoryType.Output)
        device.Value = True
        MemoryMap.Instance.Update()

    def off(self):
        device = MemoryMap.Instance.GetBit(self.output_power, MemoryType.Output)
        device.Value = False
        MemoryMap.Instance.Update()

    def power_max(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        device.Value = 10.0
        MemoryMap.Instance.Update()

    def power_min(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        device.Value = 0.00
        MemoryMap.Instance.Update()

    def power_up(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        device.Value = min(device.Value + 0.5, 10.0)
        MemoryMap.Instance.Update()

    def power_down(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        device.Value = max(device.Value - 0.5, 0.00)
        MemoryMap.Instance.Update()

    def actuate(self, action):
        if action == 1:
            self.power_up()
        elif action == 2:
            self.power_down()
    
    def random_choice(self):
        device = MemoryMap.Instance.GetFloat(self.output, MemoryType.Output)
        value_list = [round(0.5*i, 2) for i in range(21)]
        device.Value = random.choice(value_list)
        MemoryMap.Instance.Update()
        return self.state()

    def state(self):
        '''
        state (Float) = 0.01 if fully closed, 10.0 if fully opened
        '''
        MemoryMap.Instance.Update()
        return MemoryMap.Instance.GetFloat(self.output, MemoryType.Output).Value


''' ------------------------------------------------------------- '''
''' - Sensor device                                             - '''
''' ------------------------------------------------------------- '''
class Brightness:
    def __init__(self):
        self.input = -1

    def state(self):
        MemoryMap.Instance.Update()
        return MemoryMap.Instance.GetFloat(self.input, MemoryType.Input).Value

class Thermostat:
    def __init__(self):
        self.input_cur = -1
        self.input_set = -1


    def state(self):
        MemoryMap.Instance.Update()
        return MemoryMap.Instance.GetFloat(self.input_cur, MemoryType.Input).Value
    
