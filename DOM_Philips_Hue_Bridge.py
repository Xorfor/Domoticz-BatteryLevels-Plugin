#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import Domoticz
from DOM_API import DOM_API
from hardware import *


class DOM_Philips_Hue_Bridge:

    __dom_api = None
    __nodes = {}

    def __init__(self):
        self.__dom_api = DOM_API()

    def nodes(self):
        Domoticz.Debug("{}.nodes".format(self.__class__.__name__))
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
