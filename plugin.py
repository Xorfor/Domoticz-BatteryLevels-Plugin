#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Battery Levels Plugin
# Author: Xorfor
#

"""
<plugin key="xfr_batterylevels" name="Battery levels" author="Xorfor" version="1.1.0" wikilink="https://github.com/Xorfor/Domoticz-BatteryLevels-Plugin">
    <params>
        <param field="Address" label="Domoticz IP Address" width="200px" required="true" default="localhost"/>
        <param field="Port" label="Port" width="40px" required="true" default="8080"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="False" value="0" default="true"/>
                <option label="True" value="1"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
from enum import IntEnum, unique  # , auto
from hardware import *
from DOM_batteries import DOM_Batteries

# from DOM_Philips_Hue_Bridge import DOM_Philips_Hue_Bridge
from DOM_OpenZwave_USB import DOM_OpenZwave_USB


@unique
class used(IntEnum):
    """
        Constants which can be used to create the devices.
            used.NO, the user has to add this device manually
            used.YES, the device will be directly available
    """

    NO = 0
    YES = 1


@unique
class level(IntEnum):
    FULL = 75
    MEDIUM = 50
    LOW = 25
    EMPTY = 5


class BasePlugin:

    ########################################################################################
    """
        Constants

        The onHeartbeat method is called every 10 seconds.
            self.__HEARTBEATS2MIN is the number of heartbeats per minute. By using
            self.__HEARTBEATS2MIN * self.__MINUTES you can specify the frequency in
            minutes of updating your devices in the onHeartbeat method.
    """

    __HEARTBEATS2MIN = 6
    __MINUTES = (
        1
    )  # Now: update every minute for debugging. Will be 60 (every hour) in the future.

    ########################################################################################

    __IMAGES = {
        "full": "full.zip",
        "medium": "medium.zip",
        "low": "low.zip",
        "empty": "empty.zip",
    }

    ########################################################################################

    def __init__(self):
        self.__dom_hue = None
        self.__dom_bat = None
        self.__dom_zwave = None
        self.__runAgain = 4

    def on_command(self, unit, command, level, hue):
        Domoticz.Debug(
            "{}: on_command: {}, {}, {}, {}".format(
                self.__class__.__name__, unit, command, level, hue
            )
        )

    def on_connect(self, connection, status, description):
        Domoticz.Debug(
            "{}: on_connect: {}, {}, {}".format(
                self.__class__.__name__, connection.Name, status, description
            )
        )

    def on_disconnect(self, connection):
        Domoticz.Debug(
            "{}: on_disconnect: {}".format(self.__class__.__name__, connection.Name)
        )

    def on_heartbeat(self):
        Domoticz.Debug("{}: on_heartbeat".format(self.__class__.__name__))
        self.__runAgain -= 1
        nodes = None
        # There is no need to monitor all device at once. So check the hardware every heartbeat one.
        # if self.__runAgain == 1:
        # Find/update Philips Hue battery devices
        # nodes = self.__dom_hue.nodes()
        #
        if self.__runAgain == 2:
            settings_2_log()
            # Find/update Domoticz battery devices
            nodes = self.__dom_bat.nodes()
        #
        if self.__runAgain == 3:
            # Find/update Open Z-Wave USB battery devices
            nodes = self.__dom_zwave.nodes()
        #
        if nodes:
            for deviceid, values in nodes.items():
                max_unit = 0
                unit = None
                for dev in Devices:
                    max_unit = max(Devices[dev].Unit, max_unit)
                    if Devices[dev].DeviceID == deviceid:
                        Domoticz.Debug(
                            "{}: Found device {} for {}".format(
                                self.__class__.__name__, unit, deviceid
                            )
                        )
                        unit = Devices[dev].Unit
                        break
                if not unit:
                    unit = max_unit + 1
                    Domoticz.Debug(
                        "{}: No device found for {}! Create new one with {}".format(
                            self.__class__.__name__, deviceid, unit
                        )
                    )
                    Domoticz.Device(
                        Unit=unit,
                        DeviceID=deviceid,
                        Name=values["name"],
                        TypeName="Custom",
                        Options={"Custom": "0;%"},
                        Used=used.YES,
                    ).Create()
                battery = values["battery"]
                image_key = Parameters["Key"] + "_"
                if battery >= level.FULL:
                    image_key += "full"
                elif battery >= level.MEDIUM:
                    image_key += "medium"
                elif battery >= level.LOW:
                    image_key += "low"
                else:
                    image_key += "empty"
                update_device(
                    unit=unit,
                    nValue=battery,
                    sValue=str(battery),
                    Image=Images[image_key].ID,
                )

        if self.__runAgain <= 0:
            self.__runAgain = self.__HEARTBEATS2MIN
        #
        Domoticz.Debug(
            "{}: on_heartbeat: {} to go".format(
                self.__class__.__name__, self.__runAgain
            )
        )

    def on_message(self, connection, data):
        Domoticz.Debug(
            "{}: on_message: {}, {}".format(
                self.__class__.__name__, connection.Name, data
            )
        )

    def on_notification(self, name, subject, text, status, priority, sound, imagefile):
        Domoticz.Debug(
            "{}: on_notification: {}, {}, {}, {}, {}, {}, {}".format(
                self.__class__.__name__,
                name,
                subject,
                text,
                status,
                priority,
                sound,
                imagefile,
            )
        )

    def on_start(self):
        #
        # parameters
        Domoticz.Debugging(int(Parameters["Mode6"]))
        Domoticz.Debug("{}: on_start".format(self.__class__.__name__))
        #
        # check if images are in database
        for key, value in self.__IMAGES.items():
            if key not in Images:
                Domoticz.Image(value).Create()
        #
        # log config
        config_2_log()
        #
        # Initialize all hardware classes
        # self.__dom_hue = DOM_Philips_Hue_Bridge()
        self.__dom_bat = DOM_Batteries(
            ip=Parameters["Address"], port=Parameters["Port"]
        )
        self.__dom_zwave = DOM_OpenZwave_USB(
            ip=Parameters["Address"], port=Parameters["Port"]
        )

    def on_stop(self):
        Domoticz.Debug("{}: onstop".format(self.__class__.__name__))


global _plugin
_plugin = BasePlugin()


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.on_command(Unit, Command, Level, Hue)


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.on_connect(Connection, Status, Description)


def onDisconnect(Connection):
    global _plugin
    _plugin.on_disconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.on_heartbeat()


def onMessage(Connection, Data):
    global _plugin
    _plugin.on_message(Connection, Data)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.on_notification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onStart():
    global _plugin
    _plugin.on_start()


def onStop():
    global _plugin
    _plugin.on_stop()


################################################################################
# Log functions
################################################################################
def config_2_log():
    parameters_2_log()
    settings_2_log()
    images_2_log()
    devices_2_log()


def parameters_2_log():
    Domoticz.Debug("Parameters count...: {}".format(len(Parameters)))
    for x in Parameters:
        Domoticz.Debug("Parameter {}...: '{}'".format(x, Parameters[x]))


def settings_2_log():
    Domoticz.Debug("Settings count...: {}".format(len(Settings)))
    for x in Settings:
        Domoticz.Debug("Setting {}...: '{}'".format(x, Settings[x]))


def images_2_log():
    Domoticz.Debug("Image count...: {}".format(len(Images)))
    for x in Images:
        Domoticz.Debug("Image {}...: '{}'".format(x, Images[x]))


def devices_2_log():
    Domoticz.Debug("Device count...: {}".format(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device Idx...........: {}".format(Devices[x].ID))
        Domoticz.Debug(
            "Device Type..........: {} / {}".format(Devices[x].Type, Devices[x].SubType)
        )
        Domoticz.Debug("Device Name..........: '{}'".format(Devices[x].Name))
        Domoticz.Debug("Device nValue........: {}".format(Devices[x].nValue))
        Domoticz.Debug("Device sValue........: '{}'".format(Devices[x].sValue))
        Domoticz.Debug("Device Options.......: '{}'".format(Devices[x].Options))
        Domoticz.Debug("Device Used..........: {}".format(Devices[x].Used))
        Domoticz.Debug("Device ID............: '{}'".format(Devices[x].DeviceID))
        Domoticz.Debug("Device LastLevel.....: {}".format(Devices[x].LastLevel))
        Domoticz.Debug("Device Image.........: {}".format(Devices[x].Image))


# ********************************************************************************
# Plugin routines
# ********************************************************************************
def update_device(unit, **kwargs):
    if unit in Devices:
        update_args = {}
        # Check for the required arguments
        if "nValue" in kwargs:
            nValue = kwargs["nValue"]
        else:
            nValue = Devices[unit].nValue
        update_args["nValue"] = nValue
        Domoticz.Debug("nValue.........: {}".format(nValue))
        #
        if "sValue" in kwargs:
            sValue = kwargs["sValue"]
        else:
            sValue = Devices[unit].sValue
        update_args["sValue"] = sValue
        Domoticz.Debug("sValue.........: {}".format(sValue))
        #
        change = False
        if nValue != Devices[unit].nValue or sValue != Devices[unit].sValue:
            change = True
        # Check for the optional arguments
        for arg in kwargs:
            if arg == "TimedOut":
                if kwargs[arg] != Devices[unit].TimedOut:
                    change = True
                    update_args[arg] = kwargs[arg]
                Domoticz.Debug("TimedOut.......: {}".format(kwargs[arg]))
            if arg == "Image":
                if kwargs[arg] != Devices[unit].Image:
                    change = True
                    update_args[arg] = kwargs[arg]
                Domoticz.Debug("Image..........: {}".format(kwargs[arg]))
        if change:
            Devices[unit].Update(**update_args)


def http_2_log(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("http_2_log (" + str(len(httpDict)) + "):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug("....'" + x + " (" + str(len(httpDict[x])) + "):")
                for y in httpDict[x]:
                    Domoticz.Debug("........'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("....'" + x + "':'" + str(httpDict[x]) + "'")
