# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2017, Battelle Memorial Institute.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}

import os,pdb
import asyncio
from kasa import SmartPlug
from platform_driver.interfaces import BaseInterface, BaseRegister, BasicRevert
from csv import DictReader, DictWriter
import logging
import json
import re
#import urllib.request, urllib.error, urllib.parse
#import urllib2
from time import sleep
import threading 

_log = logging.getLogger(__name__)

type_mapping = {"string": str,
                "int": int,
                "integer": int,
                "float": float,
                "bool": bool,
                "boolean": bool}


class TpLink(BaseRegister):
    def __init__(self, adress, read_only, pointName, units, reg_type,
                 default_value=None, description=''):
        super(TpLink, self).__init__("byte", read_only, pointName, units,
                                          description=description)
        self.ip_address = adress
             
class Interface(BasicRevert, BaseInterface):
    def __init__(self, **kwargs):
        super(Interface, self).__init__(**kwargs)
        self.Device_points={'power':0.0,'priority':0.0,'state':0, 'voltage':0.0, 'current':0.0, 'total':0.0}
        self.Loss_connectivity=0

    def configure(self, config_dict, registry_config_str):
        self.ip_address = config_dict["device_address"]
        _log.info("Configuring now.......................................................................................")
        self.parse_config(registry_config_str)
        self.plug= SmartPlug(self.ip_address)

    def get_point(self, point_name):
        pass

    def _set_point(self, point_name, value):
        event=threading.Event()
        com=1
        if point_name=='priority':
            self.Device_points['priority']=int(value)

        if  int(value)==1:
            print("setting now",self.ip_address,value)
            try:
                asyncio.run( self.plug.turn_on())
            except Exception as e:
                if type(e).__name__ == 'SmartDeviceException':
                    com=0
        if  int(value)==0:
            print("setting now",self.ip_address,value)
            try:
                asyncio.run( self.plug.turn_off())
            except Exception as e:
                if type(e).__name__ == 'SmartDeviceException':
                    com=0
                    self.Device_points['state']=11
        event.wait(1)
        try:
            self.Device_points['power']=self.plug.emeter_realtime.power
            self.Device_points['voltage']=self.plug.emeter_realtime.voltage
            self.Device_points['current']=self.plug.emeter_realtime.current
            self.Device_points['state']=int(self.plug.is_on)
        except:
                pass
        return com

    def _scrape_all(self):
        result = {}
        read_registers = self.get_registers_by_type("byte", True)
        write_registers = self.get_registers_by_type("byte", False)
        
        try:
            asyncio.run( self.plug.update())
            self.Device_points['power']=self.plug.emeter_realtime.power
            self.Device_points['voltage']=self.plug.emeter_realtime.voltage
            self.Device_points['current']=self.plug.emeter_realtime.current
            self.Device_points['state']=int(self.plug.is_on)
        except Exception as e:
            if type(e).__name__ == 'SmartDeviceException':
                self.Loss_connectivity=self.Loss_connectivity+1
                if self.Loss_connectivity==3:
                   self.Device_points['state']=11
                   self.Loss_connectivity=0
            else:
                pass
                
        for register in read_registers + write_registers:
            result[register.point_name] = self.Device_points[register.point_name]
        return result

    def parse_config(self, config_dict):
       
        if config_dict is None:
            return

        for index, regDef in enumerate(config_dict):
                      # Skip lines that have no point name yet
            if not regDef.get('Point Name'):
                continue
            _log.info("Regiter is done.......................................................................................")

            # Extract the values of the configuration, and format them for our purposes
            read_only = regDef.get('Writable', "").lower() != 'true'
            point_name = regDef.get('Volttron Point Name')
            if not point_name:
                point_name = regDef.get("Point Name")
            if not point_name:
                # We require something we can use as a name for the register, so don't try to create a register without
                # the name
                raise ValueError("Registry config entry {} did not have a point name or volttron point name".format(
                    index))
            description = regDef.get('Notes', '')
            units = regDef.get('Units', None)
            default_value = regDef.get("Default Value", "").strip()
            # Truncate empty string or 0 values to None
            if not default_value:
                default_value = None
            type_name = regDef.get("Type", 'string')
            # Make sure the type specified in the configuration is mapped to an actual Python data type
            reg_type = type_mapping.get(type_name, str)
            # Create an instance of the register class based on the configuration values
            register = TpLink(
                self.ip_address,
                read_only,
                point_name,
                units,
                reg_type,
                default_value=default_value,
                description=description)
            # Update the register's value if there is a default value provided
            if default_value is not None:
                self.set_default(point_name, register.value)
            # Add the register instance to our list of registers
            self.insert_register(register)
   
