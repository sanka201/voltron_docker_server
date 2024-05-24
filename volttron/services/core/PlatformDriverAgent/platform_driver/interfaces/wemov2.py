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
from platform_driver.interfaces import BaseInterface, BaseRegister, BasicRevert
from csv import DictReader, DictWriter
import logging
import json
import re
import urllib.request, urllib.error, urllib.parse
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

                
#ports = [49155, 49153, 49154, 49152, 49151]
ports=[49153]

class WemoRegister(BaseRegister):
    """
    Register class for reading and writing to specific lines of a CSV file
    """
    def __init__(self, address, read_only, pointName, units, reg_type,
                 default_value=None, description=''):
        # set inherited values
        super(WemoRegister, self).__init__("byte", read_only, pointName, units,
                                          description=description)
        self.address=address
        
    def get_state(self):
         _log.info("get state is working")
       #  print( Wemo_points.get(self.point_name))
         return 0#Wemo_points.get(self.point_name)
         
         #self._send('Get','insight','InsightParams')

    def _get_header_xml(self, method, service, obj):
        method = method + obj
        return '"urn:Belkin:service:%s:1#%s"' % (service,method)
    def _get_body_xml(self, method, service, obj, value=0):
        method = method + obj
        return '<u:%s xmlns:u="urn:Belkin:service:%s:1"><%s>%s</%s></u:%s>' % (method, service, obj, value, obj, method)
         
    def _send(self, method, service, obj, value=None):
        body_xml = self._get_body_xml(method,service, obj, value)
        header_xml = self._get_header_xml(method,service, obj)
        properport = 0
        for i in range(len(ports)):
            result = self._try_send(self.address, ports[i], body_xml, header_xml, service, obj)
            print(str(self.address)+': '+ str(result))
            if result != None and str(result) !='None':
                self.ports = ports[i]
                return result
        return result
        raise Exception("TimeoutOnAllPorts")
   
         
    def _try_send(self, ip, port, body, header, service, data):
        try:
            request = urllib.request.Request('http://%s:%s/upnp/control/%s1' % (ip, port, service))
            request.add_header('Content-type', 'text/xml; charset="utf-8"')
            request.add_header('SOAPACTION', header)
            request_body = '<?xml version="1.0" encoding="utf-8"?>'
            request_body += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            request_body += '<s:Body>%s</s:Body></s:Envelope>' % body
            request.data = request_body.encode()
            result = urllib.request.urlopen(request, timeout=60)
            output=self._extract(result.read().decode(), data);
            x=str(output).split('|')
            print("")
            print(int(x[6])+32)
            print("")
            print(str(request))
            return output
        except Exception as e:
            print(str(e))
            return None
    def _extract(self, response, name):
        exp = '<%s>(.*?)<\/%s>' % (name, name)
        g = re.search(exp, response)
        if g:
            return g.group(1)
            return response

        
        

class Interface(BasicRevert, BaseInterface):
    """
    "Device Interface" for reading and writing rows of a CSV as a Volttron connected device
    """
    def __init__(self, **kwargs):
        # Configure the base interface
        super(Interface, self).__init__(**kwargs)
        # We wont have a path to our "device" until we've been configured
        self.Wemo_points={'power':0.0,'average':0.0,'state':0,'priority':0,'hour':0}

    def configure(self, config_dict, registry_config_str):
        self.ip_address = config_dict["device_address"]
        _log.info("Scraping now.......................................................................................")
        self.parse_config(registry_config_str)
        

    def get_point(self, point_name):
        register = self.get_register_by_name(point_name)
        _log.info("Getting now")
        result=self._send('Get','insight','InsightParams')
        # then return that register's state
        output={}
        if result != None :
            x=str(result).split('|')

            output['power']=int(x[7])
            output['average']=int(x[8])
            output['status']=int(x[0])
        else:
             output['status']=11

        _log.info("Getting now")
        return output

    def _set_point(self, point_name, value):
        result={}
        read_registers = self.get_registers_by_type("byte", True)
        write_registers = self.get_registers_by_type("byte", False)
 
        print("haaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, setting now",self.ip_address)
        if point_name=='priority':
            self.Wemo_points.update({'priority':int(value)})
        elif point_name=='hour':
            self.Wemo_points.update({'hour':int(value)})
        else:    
            output=self._send('Set','basicevent','BinaryState', value)
            print(str(output))
            if output != None :
                x=str(output).split('|')
      
                self.Wemo_points.update({'power':int(x[7])})
                self.Wemo_points.update({'average':int(x[8])})
                self.Wemo_points.update({'status':int(x[0])})
            else:
                 self.Wemo_points.update({'status':11})
            
        #print("Power")
        #print(Wemo_points.get('power'))
        #print("status")
        #print(Wemo_points.get('status'))
        for register in read_registers + write_registers:
                result[register.point_name] = self.Wemo_points.get(register.point_name)
        
    
        return result
    def _scrape_all(self):
        
        """
        Loop over all of the registers configured for this device, then return a mapping of register name to its value
        :return: Results dictionary of the form {<register point name>: <register value>, ...}
        """
        # Create a dictionary to hold our results
        result = {}
        read_registers = self.get_registers_by_type("byte", True)
        write_registers = self.get_registers_by_type("byte", False)
        output=self._get_wemos()
        if output != None :
            x=str(output).split('|')
      
            self.Wemo_points.update({'power':int(x[7])})
            self.Wemo_points.update({'average':int(x[8])})
            self.Wemo_points.update({'status':int(x[0])})
        else:
             self.Wemo_points.update({'status':11})
            
        #print("Power")
        #print(Wemo_points.get('power'))
        #print("status")
        #print(Wemo_points.get('status'))
        for register in read_registers + write_registers:
                result[register.point_name] = self.Wemo_points.get(register.point_name)
        
        
       
       
        
            #Return the results
        return result
        
    def _get_wemos(self):
        results=self._send('Get','insight','InsightParams')
        return results
        
    def _get_header_xml(self, method, service, obj):
        method = method + obj
        return '"urn:Belkin:service:%s:1#%s"' % (service,method)
    def _get_body_xml(self, method, service, obj, value=0):
        method = method + obj
        return '<u:%s xmlns:u="urn:Belkin:service:%s:1"><%s>%s</%s></u:%s>' % (method, service, obj, value, obj, method)
         
    def _send(self, method, service, obj, value=None):
        body_xml = self._get_body_xml(method,service, obj, value)
        header_xml = self._get_header_xml(method,service, obj)
        properport = 0
        for i in range(len(ports)):
            result = self._try_send(self.ip_address, ports[i], body_xml, header_xml, service, obj)
            print(str(self.ip_address)+': '+ str(result))
            if result != None and str(result) !='None':
                self.ports = ports[i]
                return result
        return result
        raise Exception("TimeoutOnAllPorts")
   
         
    def _try_send(self, ip, port, body, header, service, data):
        try:
            request = urllib.request.Request('http://%s:%s/upnp/control/%s1' % (ip, port, service))
            request.add_header('Content-type', 'text/xml; charset="utf-8"')
            request.add_header('SOAPACTION', header)
            request_body = '<?xml version="1.0" encoding="utf-8"?>'
            request_body += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            request_body += '<s:Body>%s</s:Body></s:Envelope>' % body
            request.data = request_body.encode()
            result = urllib.request.urlopen(request, timeout=60)
            
            event=threading.Event()
#            event.wait(1)


            output=self._extract(result.read().decode(), data);
            
            return output
        except Exception as e:
            print(str(e))
            return None
    def _extract(self, response, name):
        exp = '<%s>(.*?)<\/%s>' % (name, name)
        g = re.search(exp, response)
        if g:
            return g.group(1)
            return response
   
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
            register = WemoRegister(
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
        
            
        


