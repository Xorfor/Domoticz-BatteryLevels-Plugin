#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import Domoticz
from DOM_API import *
from hardware import *


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

