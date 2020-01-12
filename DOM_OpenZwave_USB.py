#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import Domoticz
from DOM_API import DOM_API
from hardware import *


class DOM_OpenZwave_USB:

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
                    nodes = self.__dom_api.DOM_result(
                        "type=command&param=zwavegetbatterylevels&idx={}".format(hwid)
                    )
                    for node in nodes:
                        battery = node["battery"]
                        if battery != 255:  # Domoticz standard: 255 = no battery
                            nodeID = node.get("nodeID")
                            nodeName = node.get("nodeName")
                            Domoticz.Debug(
                                "{}: Found device with battery: {} on {}".format(
                                    self.__class__.__name__,
                                    nodeID,
                                    nodeName,
                                )
                            )
                            # Make sure that the device id is unique
                            deviceid = "{}-{}".format(
                                hwid, nodeID
                            )
                            if deviceid not in self.__nodes:
                                self.__nodes[deviceid] = {}
                                self.__nodes[deviceid]["name"] = nodeName
                            #
                            self.__nodes[deviceid]["battery"] = battery
            Domoticz.Debug(
                "{}: nodes: {}".format(self.__class__.__name__, self.__nodes)
            )
