from typing import Protocol
from messages import MessageType
from messages  import Message
from csv import DictReader, DictWriter
import os
import csv
import collections
from collections import defaultdict
import operator
import numpy as np
class Device(Protocol):
    def connect(self) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def send_message(self, message: Message) -> None:
        ...
    def status_update(self) -> str:
        ...
class LPCmodule(Protocol):

    def set_lpc_control_mode(self,topic:str,message:dict)->Message:
        ...
    def read_device_configurations(self,csv_path)->Message:
        ...
    def read_device_status(self,topic,message):
        ...
    def set_priority(self,priority):
        ...
    def lpc_shedding(self,message)->Message:
        ...
    def lpc_increment(self,message)->Message:
        ...
    def get_total_device_consumption():  
        ...
class WeMoService:
    def register_devices(self,csv_path:str,lpc:LPCmodule,devices:Device):
        devicemessage=lpc.read_device_configurations(csv_path)
        devices.send_message(devicemessage)
        print("registering device")
    def device_status_update(self,topic,message,lpc:LPCmodule):
        lpc.read_device_status(topic,message)
        print("reading devices")
    def device_set_control_mode(self,topic,message,lpc:LPCmodule,devices:Device):
        devicemessage=lpc.set_lpc_control_mode(topic,message)
        print("set control", devicemessage)
        if devicemessage.control == None:
            pass
        else:
            print("HIIIIIIIIIIIIIIIIIIIIIIII")
            devices.send_message(devicemessage)


 


