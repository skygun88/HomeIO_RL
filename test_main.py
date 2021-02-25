import sys
import time
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/utils')
import clr
clr.AddReference('EngineIO')

from EngineIO import *
from device.Section_N import *
from device.Outside import *


def main():
    light1 = RoomLight1()
    light2 = RoomLight2()
    roller = RoomRoller()
    brightness = RoomBrightness()
    thermostat = RoomBThermostat()
    heater = RoomHeater()
    outside_tem = OutsideTemperature()
    outside_bri = OutsideBrightness()
    # print('input & output')
    # print(light.input.Value)
    # print(light.output.Value)

    for i in range(3):
        light1.off()
        light2.off()
        time.sleep(0.3)
        print(f'light: {light1.state(), light2.state()}')
        print(f'brightness: {brightness.state()}')
        print(f'Curr_tem: {thermostat.state()}')
        print('-----------------------------')
        
        light1.on()
        light2.on()
        time.sleep(0.3)
        print(f'light: {light1.state(), light2.state()}')
        print(f'brightness: {brightness.state()}')
        print(f'Curr_tem: {thermostat.state()}')
        print('-----------------------------')

    # for i in range(1):
    #     heater.set_max()
    #     time.sleep(10)
    #     print(f'heater: {heater.state()}')
    #     print(f'brightness: {brightness.state()}')
    #     print(f'Curr_tem, target_tem: {thermostat.state()}')
    #     print('-----------------------------')
        
    #     heater.set_min()
    #     time.sleep(10)
    #     print(f'heater: {heater.state()}')
    #     print(f'brightness: {brightness.state()}')
    #     print(f'Curr_tem, target_tem: {thermostat.state()}')
    #     print('-----------------------------')

    # while roller.state() < 10:
    #     roller.up()
    #     time.sleep(0.5)
    #     print(roller.state())
    #     print(f'light: {light1.state(), light2.state()}')
    #     print(f'brightness: {brightness.state()}')
    #     print(f'Curr_tem: {thermostat.state()}')
    #     print('-----------------------------')
    # roller.reset_output()

    # while roller.state() > 0:
    #     roller.down()
    #     time.sleep(0.5)
    #     print(roller.state())
    #     print(f'light: {light1.state(), light2.state()}')
    #     print(f'brightness: {brightness.state()}')
    #     print(f'Curr_tem: {thermostat.state()}')
    #     print('-----------------------------')
    # roller.reset_output()
    heater.power_max()
    # heater.power_min()
    #heater.off()

    # for i in range(30):
    #     print(f'brightness: {brightness.state()}')
    #     print(f'Temperature: {thermostat.state()}')
    #     print(f'Outside: {outside_tem.state(), outside_bri.state()}')
    #     print(f'heater: {heater.state()}')
    #     print('-----------------------------')
    #     time.sleep(1)

    MemoryMap.Instance.Dispose()


if __name__ == '__main__':
    main()