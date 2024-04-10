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
from  platform_driver.interfaces import BaseInterface, BaseRegister, BasicRevert
from csv import DictReader, DictWriter
import logging
import sys
import json
#from master_driver.interfaces.interface_json import Interface_JSON
import urllib.request, urllib.error, urllib.parse
from time import sleep
sys.path.insert(0,'/home/sanka/volttron/services/core/PlatformDriverAgent/platform_driver/interfaces')
import aiohttp
import asyncio
import pyjuicenet

_log = logging.getLogger(__name__)

type_mapping = {"string": str,
                "int": int,
                "integer": int,
                "float": float,
                "bool": bool,
                "boolean": bool}

                
ports = [49155, 49153, 49154, 49152, 49151]


class JuiceBoxRegister(BaseRegister):
    """
    Register class for reading and writing to specific lines of a CSV file
    """
    def __init__(self, account_tocken, read_only, pointName, units, reg_type,
                 default_value=None, description=''):
        # set inherited values
        super(JuiceBoxRegister, self).__init__("byte", read_only, pointName, units,
                                          description=description)
        self.account_tocken=account_tocken
        

        
        

class Interface(BasicRevert, BaseInterface):
    """
    "Device Interface" for reading and writing rows of a CSV as a Volttron connected device
    """
    def __init__(self, **kwargs):
        # Configure the base interface
        super(Interface, self).__init__(**kwargs)
        # We wont have a path to our "device" until we've been configured
        self.JuiceBox_points={'voltage':0,'amps':0,'watts':0,
        'temperature':0,'charge_time':0,'energy_added':0,
        'override_time':0,'max_charging_amperage':0,'current_charging_amperage_limit':0,
         'set_charging_amperage_limit':0,'set_override':0}
        

    def configure(self, config_dict, registry_config_str):
        self.account_tocken = config_dict["Account_tocken"]
        
        print("Scraping now.......................................................................................",self.account_tocken)
        self.parse_config(registry_config_str)
        

    def get_point(self, point_name):
        register = self.get_register_by_name(point_name)
        # then return that register's state
        _log.info("Getting now")
        return register.get_state()

    def _set_point(self, point_name, value):
        print("haaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, setting now",self.account_tocken)
        loop = asyncio.get_event_loop()
        result=loop.run_until_complete(self.Evwrite(point_name,value))

        #output=self._send('Set','basicevent','BinaryState', value)
       # print(str(output))
       # read_registers = self.get_registers_by_type("byte", True)
        #write_registers = self.get_registers_by_type("byte", False)
        #if output != None :
         #   x=str(output).split('|')
      #
       #     self.Wemo_points.update({'power':int(x[7])/1000})
        #    self.Wemo_points.update({'average':int(x[6])})
         #   self.Wemo_points.update({'status':int(x[0])})
        #else:
         #    self.Wemo_points.update({'status':11})
            
        #print("Power")
        #print(Wemo_points.get('power'))
        #print("status")
        #print(Wemo_points.get('status'))
        #for register in read_registers + write_registers:
         #       result[register.point_name] = self.Wemo_points.get(register.point_name)
        
    
        return result
    
    async def Evread(self):  
        async with aiohttp.ClientSession() as session:
            api = pyjuicenet.Api(self.account_tocken, session)
            devices = await api.get_devices()
#    print(devices.get())
            charger = devices[0]
#    print(charger)
            await charger.update_state()
        self.JuiceBox_points.update({'voltage':charger.voltage})
        self.JuiceBox_points.update({'amps':charger.amps})
        self.JuiceBox_points.update({'watts':charger.watts})
        self.JuiceBox_points.update({'temperature':charger.temperature})
        self.JuiceBox_points.update({'charge_time':charger.charge_time})
        self.JuiceBox_points.update({'energy_added':charger.energy_added})
        self.JuiceBox_points.update({'override_time':charger.override_time})
        self.JuiceBox_points.update({'max_charging_amperage':charger.max_charging_amperage})
        self.JuiceBox_points.update({'current_charging_amperage_limit':charger.current_charging_amperage_limit})
    async def Evwrite(self,point_name,value):  
        async with aiohttp.ClientSession() as session:
            api = pyjuicenet.Api(self.account_tocken, session)
            devices = await api.get_devices()
#    print(devices.get())
            charger = devices[0]
#    print(charger)
            
            
            if point_name=="set_charging_amperage_limit": 
                await charger.set_charging_amperage_limit(value)
                print('jjjjjjjjjjjjjjjjjj',point_name)
                await charger.update_state()
                return charger.current_charging_amperage_limit
            elif point_name=="set_override": 
                out= await charger.set_override(bool(value))
                return out
            else:
                return "noo"

    def _scrape_all(self):
        
        """
        Loop over all of the registers configured for this device, then return a mapping of register name to its value
        :return: Results dictionary of the form {<register point name>: <register value>, ...}
        """
        # Create a dictionary to hold our results
        result = {}
        read_registers = self.get_registers_by_type("byte", True)
        write_registers = self.get_registers_by_type("byte", False)
        output=0 #self._get_Bergey()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.Evread())
        
        for register in read_registers + write_registers:
            result[register.point_name] = self.JuiceBox_points.get(register.point_name)
        
        
       
       
        
            #Return the results
        return result
        
    def _get_Bergey(self):
        
        #results=self._send('Get','insight','InsightParams')
        test_url = 'http://mybergey.aprsworld.com/data/jsonMyBergey.php?'+'station_id=A5527'
        #users1 = Interface_JSON(test_url)
        #data  = users1.read_json()
        response = urllib.request.urlopen(test_url)
        html = response.read()
        data=json.loads(html)


        #power = data['inverter_output_power']

        
        #power_string = "Power: {} watts".format(power)
        #print(power_string)
        #_log.info("Scraping now.......................................................................................")


        return data
        
   
   
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
            register = JuiceBoxRegister(
                self.account_tocken,
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
        
            
        

