#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Battery Levels Plugin
# Author: Xorfor
#

"""
<plugin key="xfr_batterylevels" name="Battery levels" author="Xorfor" version="1.0.0" wikilink="https://github.com/Xorfor/Domoticz-BatteryLevels-Plugin">
    <params>
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
import urllib.parse as parse
import urllib.request as request
import socket
import json
from enum import IntEnum, unique  # , auto


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
    __MINUTES = 1

    ########################################################################################

    __IMAGES = {
        "batteryfull": "batteryfull.zip",
        "batterymedium": "batterymedium.zip",
        "batterylow": "batterylow.zip",
        "batteryempty": "batteryempty.zip",
    }

    ########################################################################################

    def __init__(self):
        self.__runAgain = 0

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
        if self.__runAgain == 1:
            #
            # Find/update Philips Hue battery devices
            nodes = self.__dom_hue.nodes()
        #
        if self.__runAgain == 2:
            nodes = self.__dom_bat.nodes()
        #
        if self.__runAgain == 3:
            pass
        #
        if nodes:
            for deviceid, values in nodes.items():
                unit = None
                for dev in Devices:
                    if Devices[dev].DeviceID == deviceid:
                        unit = Devices[dev].Unit
                        Domoticz.Debug(
                            "{}: Found device {} for {}".format(
                                self.__class__.__name__, unit, deviceid
                            )
                        )
                        break
                if not unit:
                    unit = len(Devices) + 1
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
                update_device_value(
                    unit, nValue=battery, sValue=str(battery), TimedOut=False
                )
                if battery >= level.FULL:
                    image_key = "batteryfull"
                elif battery >= level.MEDIUM:
                    image_key = "batterymedium"
                elif battery >= level.LOW:
                    image_key = "batterylow"
                else:
                    image_key = "batteryempty"
                update_device_image(unit=unit, image_id=Images[image_key].ID)

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
        self.__DOM_ENDPOINT = "{}".format(Parameters["Address"])
        self.__DOM_PORT = "{}".format(Parameters["Port"])
        Domoticz.Debug(
            "{}: self.__API_ENDPOINT: {}".format(
                self.__class__.__name__, self.__DOM_ENDPOINT
            )
        )
        Domoticz.Debug(
            "{}: self.__API_PORT: {}".format(self.__class__.__name__, self.__DOM_PORT)
        )
        #
        # check if images are in database
        for key, value in self.__IMAGES.items():
            if key not in Images:
                Domoticz.Image(value).Create()
        #
        # log config
        config_2_log()
        #
        self.__dom_hue = DOM_Philips_Hue_Bridge()
        self.__dom_bat = DOM_Batteries()

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
def update_device_value(unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    Domoticz.Debug("update_device_value: {} - {} - {}".format(unit, nValue, sValue))
    if unit in Devices:
        if (
            Devices[unit].nValue != nValue
            or Devices[unit].sValue != sValue
            or Devices[unit].TimedOut != TimedOut
            or AlwaysUpdate
        ):
            Devices[unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug(
                "update_device {}: {} - '{}'".format(Devices[unit].Name, nValue, sValue)
            )


def update_device_options(unit, options={}):
    Domoticz.Debug("update_device_options: {} - {}".format(unit, image_key))
    if unit in Devices:
        if Devices[unit].Options != options:
            Devices[unit].Update(
                nValue=Devices[unit].nValue,
                sValue=Devices[unit].sValue,
                Options=options,
            )
            Domoticz.Debug(
                "update_device_options: {} = {}".format(Devices[unit].Name, options)
            )


def update_device_image(unit, image_id):
    Domoticz.Debug("update_device_image: {} - {}".format(unit, image_id))
    if unit in Devices:
        if Devices[unit].Image != image_id:
            Devices[unit].Update(
                nValue=Devices[unit].nValue,
                sValue=Devices[unit].sValue,
                Image=image_id,
            )
            Domoticz.Debug(
                "update_device_image: {} = {}".format(
                    Devices[unit].Name, image_id
                )
            )


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


# ********************************************************************************
# Calls to the devices
# ********************************************************************************

# Domoticz


class hardware:
    """
        Hardware IDs 
    """

    OPENZWAVE_USB = 21
    PHILIPS_HUE_BRIDGE = 38

    hardware = {OPENZWAVE_USB, PHILIPS_HUE_BRIDGE}


class DOM_Batteries:
    """
        Scan for battery devices which are not created by eg. Philips Hue or OpenZwave USB
    """

    __dom_api = None
    __nodes = {}

    def __init__(self):
        self.__dom_api = DOM_API()

    def nodes(self):
        self.__init_nodes()
        return self.__nodes

    def __init_nodes(self):
        # Test with a Dummy Custom device and update with /json.htm?type=command&param=udevice&idx={}&nvalue=0&svalue=123&battery=80
        # json.htm?type=devices&displayhidden=1
        payload = self.__dom_api.DOM_result("type=devices&displayhidden=1")
        if payload:
            for result_dict in payload:
                if int(result_dict.get("HardwareID")) not in hardware.hardware:
                    if result_dict.get("BatteryLevel") <= 100:
                        Domoticz.Debug(
                            "{}: Found device with battery: {} on {}".format(
                                self.__class__.__name__,
                                result_dict.get("idx"),
                                result_dict.get("Name"),
                            )
                        )
                        # Make sure that the device id is unique
                        deviceid = "{}-{}".format(
                            result_dict.get("HardwareID"), result_dict.get("ID")
                        )
                        if deviceid not in self.__nodes:
                            self.__nodes[deviceid] = {}
                            self.__nodes[deviceid]["name"] = result_dict.get("Name")
                        #
                        self.__nodes[deviceid]["battery"] = result_dict.get(
                            "BatteryLevel"
                        )
                        if deviceid in self.__nodes:
                            Domoticz.Debug(
                                "{}: {} added!!!".format(
                                    self.__class__.__name__, deviceid
                                )
                            )
            Domoticz.Debug(
                "{}: nodes: {}".format(self.__class__.__name__, self.__nodes)
            )


class DOM_OpenZwave_USB:

    __dom_api = None
    __nodes = {}

    def __init__(self):
        self.__dom_api = DOM_API()

    def nodes(self):
        self.__init_nodes()
        return self.__nodes

    def __init_nodes(self):
        payload = self.__dom_api.DOM_result("type=hardware")
        if payload:
            for result_dict in payload:
                if int(result_dict.get("Type")) == hardware.OPENZWAVE_USB:
                    Domoticz.Debug(
                        "{}: Found OpenZWave USB: {} on {}:{} - {}".format(
                            self.__class__.__name__,
                            result_dict.get("idx"),
                            result_dict.get("Address"),
                            result_dict.get("Port"),
                            result_dict.get("Username"),
                        )
                    )
                    hwid = result_dict.get("idx")
                    # type=command&param=zwavegetbatterylevels&idx={}


class DOM_Philips_Hue_Bridge:

    __dom_api = None
    __nodes = {}

    def __init__(self):
        self.__dom_api = DOM_API()

    def nodes(self):
        self.__init_nodes()
        return self.__nodes

    def __init_nodes(self):
        payload = self.__dom_api.DOM_result("type=hardware")
        if payload:
            for result_dict in payload:
                if int(result_dict.get("Type")) == hardware.PHILIPS_HUE_BRIDGE:
                    Domoticz.Debug(
                        "{}: Found Philips Hue Bridge: {} on {}:{} - {}".format(
                            self.__class__.__name__,
                            result_dict.get("idx"),
                            result_dict.get("Address"),
                            result_dict.get("Port"),
                            result_dict.get("Username"),
                        )
                    )
                    hwid = result_dict.get("idx")
                    # As far as I know, only the Philips Hue sensors have batteries
                    sensors = self.__dom_api.request(
                        "http://{}:{}/api/{}/sensors".format(
                            result_dict.get("Address"),
                            result_dict.get("Port"),
                            result_dict.get("Username"),
                        )
                    )
                    Domoticz.Debug(
                        "{}: sensors: {}".format(self.__class__.__name__, sensors)
                    )
                    for v in sensors.values():
                        battery = v.get("config").get("battery")
                        if battery is not None:
                            # Make sure that the device id is unique
                            deviceid = "{}-{}".format(hwid, v.get("uniqueid"))
                            name = v.get("name")
                            Domoticz.Debug(
                                "{}: {} - {}: {}".format(
                                    self.__class__.__name__, deviceid, name, battery
                                )
                            )
                            if deviceid not in self.__nodes:
                                self.__nodes[deviceid] = {}
                                self.__nodes[deviceid]["name"] = name
                            self.__nodes[deviceid]["battery"] = battery
                            if deviceid in self.__nodes:
                                Domoticz.Debug(
                                    "{}: {} added!!!".format(
                                        self.__class__.__name__, deviceid
                                    )
                                )
                    Domoticz.Debug(
                        "{}: nodes: {}".format(self.__class__.__name__, self.__nodes)
                    )


class DOM_API:

    __DOM_PROTOCOL = "http"
    __DOM_ENDPOINT = "localhost"
    __DOM_PORT = "8080"
    __DOM_URL = "json.htm"

    def __init__(self):
        self.__DOM_ENDPOINT = self.ip()

    def DOM_result(self, command):
        url = "{}://{}:{}/{}?{}".format(
            self.__DOM_PROTOCOL,
            self.__DOM_ENDPOINT,
            self.__DOM_PORT,
            self.__DOM_URL,
            parse.quote(command, safe="&="),
        )
        Domoticz.Debug("Calling Domoticz Json/API: {}".format(url))
        return self.DOM_request(url)

    def DOM_request(self, url):
        result = None
        content = self.request(url)
        if content.get("status") == "OK":
            result = content.get("result")
            # Domoticz.Debug("result: {}".format(result))
        else:
            Domoticz.Error(
                "Domoticz API returned an error: status = {}".format(content["status"])
            )
            result = None
        return result

    def request(self, url):
        # try:
        Domoticz.Debug("url: {}".format(url))
        req = request.Request(url, headers={"Cache-Control": "no-cache"})
        response = request.urlopen(req)
        # Domoticz.Log("response.status: {}".format(response.status))
        if response.status == 200:
            content = json.loads(response.read().decode("utf-8"))
            # Domoticz.Log("content: {}".format(content))
        else:
            Domoticz.Error("Domoticz API: http error = {}".format(response.status))
        # except:
        #     Domoticz.Error("Error calling '{}'".format(url))
        return content

    def ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 1))
        except socket.error:
            return None
        return s.getsockname()[0]
