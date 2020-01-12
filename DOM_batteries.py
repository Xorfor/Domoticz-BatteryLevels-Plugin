#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import Domoticz
from DOM_API import *
from hardware import *


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
