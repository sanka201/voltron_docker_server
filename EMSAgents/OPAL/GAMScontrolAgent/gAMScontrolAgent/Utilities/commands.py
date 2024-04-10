import csv
import sys
from csv import DictReader, DictWriter
import os
from json import load
import copy as cp
from abc import ABC,abstractmethod
import pandas as pd

class Commands(ABC):
    @abstractmethod
    def __voltomat(self,message):
        pass
    @abstractmethod    
    def __mattovolt(self,message):
        pass
    @abstractmethod
    def __critical_power(self,message):
        pass
    @abstractmethod
    def __interuptible_power(self,message):
        pass
    @abstractmethod
    def __priority_power(self,message):
        pass 
    @abstractmethod
    def __command(self,message,topic):
        pass   
    @abstractmethod
    def __GAMSHourFlag(self,message):
        pass   
class GAMS(ABC):
    def __init__(self,vip):
        self.vip=vip
    def __voltomat(self,message):
        result=self.vip.rpc.call('platform.driver','set_point', 'building540/GAMS' ,'Flag_VoltToMat',message)
    def __mattovolt(self,message):
        result=self.vip.rpc.call('platform.driver','set_point', 'building540/GAMS' ,'Flag_MattoVolt',message)
    def __critical_power(self,message):
        result=self.vip.rpc.call('platform.driver','set_point', 'building540/GAMS' ,'Solar_1',message)
    def __interuptible_power(self,message):
        result=self.vip.rpc.call('platform.driver','set_point', 'building540/GAMS' ,'Solar_2',message)
    def __priority_power(self,message):
        result=self.vip.rpc.call('platform.driver','set_point', 'building540/GAMS' ,'Solar_3',message)
    def __GAMSHourFlag(self,message):
        result=self.vip.rpc.call('platform.driver','set_point', 'building540/GAMS' ,'GAMSHourFlag',message)

    def command(self,message,topic):
        print("################ Commanding #########################",topic,message)
        if(topic=='GAMS/control/consumption/prioritygroup/3'):
            self.__critical_power(int(message))
        if(topic=='GAMS/control/consumption/prioritygroup/2'):
            self.__interuptible_power(int(message))            
        if(topic=='GAMS/control/consumption/prioritygroup/1'):
            self.__priority_power(int(message)) 
        if(topic=='GAMS/control/hourflag'):
            self.__GAMSHourFlag(int(message)) 
        if(topic=='GAMS/control/Flag_VoltToMat'):
            self.__voltomat(int(message)) 
        if(topic=='GAMS/control/Flag_MattoVolt'):
            self.__mattovolt(int(message)) 
