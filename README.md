# Domoticz Battery levels

This is the very first version from my attempt to monitor the battery levels of ALL devices in Domoticz. There is a Domoticz Python Plugin to monitor battery levels of Z-Wave devices (https://github.com/999LV/BatteryLevel) and you can set the Battery Low Level is the Domoticz Setting. But there is no further log in Domoticz about battery levels in the devices.

**Please let me know your findings!!!**

## Currently supported

### Standard Domoticz devices
This plugin will scan for battery levels of the 'normal' Domoticz devices.

### Z-Wave devices
Implemented, using the latest Domoticz API/json url's. Not tested yet, I am not on the latest beta version of Domoticz, because of the problems with the latest Open Z-Wave interface.

### Philips Hue
This plugin will monitor the batterylevels of the sensors from eg. the Hue Dimmer Switch (even the Philips Hue app does not show you this battery level).

## Installation
1. Clone repository into your Domoticz plugins folder
    ```
    cd domoticz/plugins
    git clone https://github.com/Xorfor/Domoticz-BatteryLevels-Plugin.git
    ```
1. Restart domoticz
    ```
    sudo service domoticz.sh restart
    ```
1. Make sure that "Accept new Hardware Devices" is enabled in Domoticz settings
1. Go to "Hardware" page and add new hardware with Type "Battery levels"
1. Press Add

## Update
1. Go to plugin folder and pull new version
    ```
    cd domoticz/plugins/Domoticz-BatteryLevels-Plugin
    git pull
    ```
1. Restart domoticz
    ```
    sudo service domoticz.sh restart
    ```

## Parameters
None

## Devices
For each battery device, a new device will be created with the name 'Battery level - ' and the name of the original device. This device also gets a device id which is a combination of the hardware id and a unique device id. 