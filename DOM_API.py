#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import json
import socket
import urllib.parse as parse
import urllib.request as request

import Domoticz


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
        try:
            Domoticz.Debug("url: {}".format(url))
            req = request.Request(url)
            response = request.urlopen(req)
            if response.status == 200:
                content = json.loads(response.read().decode("utf-8"))
            else:
                Domoticz.Error("response.status: {}".format(response.status))
        except:
            content = None
            Domoticz.Error("Error calling '{}'".format(url))
        return content

    def ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 1))
        except socket.error:
            return None
        return s.getsockname()[0]
